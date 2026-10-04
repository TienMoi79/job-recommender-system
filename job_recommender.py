"""Giai đoạn 2: hệ gợi ý dựa trên nội dung (content-based recommendation).

Luồng xử lý: chuẩn hóa dữ liệu -> vector hóa -> cosine similarity -> top-N.
Không huấn luyện dựa trên hành vi người dùng và không gọi dịch vụ AI trả phí.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from numbers import Integral
from pathlib import Path
import re
import unicodedata
import warnings

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from generate_mock_data import JOB_COLUMNS


DEFAULT_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
Vectors = np.ndarray | csr_matrix


class TextPreprocessor:
    """Chuẩn hóa nhẹ, giữ dấu và ngữ cảnh thay vì xóa từ quá mạnh."""

    @staticmethod
    def normalize(text: str) -> str:
        # NFC giúp hai chuỗi Unicode tiếng Việt tương đương có cùng biểu diễn.
        return " ".join(unicodedata.normalize("NFC", text).split())

    @staticmethod
    def for_tfidf(text: str) -> str:
        # Tokenizer mặc định có thể làm mất '+' và '#'. Đổi tên kỹ thuật sang
        # token ổn định để C++, C#, .NET không bị coi là cùng một từ 'c'/'net'.
        text = TextPreprocessor.normalize(text).lower()
        aliases = {
            r"(?<!\w)c\+\+(?!\w)": "cplusplus",
            r"(?<!\w)c#(?!\w)": "csharp",
            r"(?<!\w)asp\.net(?!\w)": "aspnet",
            r"(?<!\w)\.net(?!\w)": "dotnet",
            r"(?<!\w)node\.js(?!\w)": "nodejs",
            r"(?<!\w)ci/cd(?!\w)": "cicd",
        }
        for pattern, replacement in aliases.items():
            text = re.sub(pattern, replacement, text)
        return text


class TextVectorizer(ABC):
    """Giao diện chung: thay thuật toán biểu diễn mà không đổi logic xếp hạng."""

    @abstractmethod
    def fit_transform(self, texts: list[str]) -> Vectors:
        """Xây không gian đặc trưng từ danh sách việc làm và trả ma trận vector."""

    @abstractmethod
    def transform(self, texts: list[str]) -> Vectors:
        """Biểu diễn truy vấn trong đúng không gian đặc trưng đã xây dựng."""


class TfidfTextVectorizer(TextVectorizer):
    """Baseline nhẹ, không tải mô hình và chạy được hoàn toàn offline."""

    def __init__(self) -> None:
        self._vectorizer = TfidfVectorizer(
            preprocessor=TextPreprocessor.for_tfidf,
            # Giữ cả token 1 ký tự (R, C) và số năm; bigram giữ cụm 'power bi'.
            token_pattern=r"(?u)\b\w+\b",
            ngram_range=(1, 2),
            sublinear_tf=True,
            norm="l2",
        )

    def fit_transform(self, texts: list[str]) -> csr_matrix:
        return self._vectorizer.fit_transform(texts)

    def transform(self, texts: list[str]) -> csr_matrix:
        # Không fit lại trên CV: fit lại sẽ thay vocabulary/IDF và làm lệch
        # không gian vector so với những việc làm đã được lưu trong bộ nhớ.
        return self._vectorizer.transform(texts)


class SentenceTransformerVectorizer(TextVectorizer):
    """Dùng mô hình pretrained để biểu diễn ý nghĩa của câu/đoạn văn."""

    def __init__(self, model_name: str = DEFAULT_MODEL, device: str = "cpu") -> None:
        # Lazy import: người chỉ dùng TF-IDF không cần cài PyTorch/transformers.
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise ImportError(
                "Backend semantic cần: python -m pip install -r requirements-semantic.txt. "
                "Hoặc chọn backend='tfidf' để chạy nhẹ."
            ) from exc
        self._model = SentenceTransformer(model_name, device=device)

    def fit_transform(self, texts: list[str]) -> np.ndarray:
        # Mô hình đã được huấn luyện trước; đồ án này chỉ chạy suy luận,
        # không fine-tune trên 20 việc làm giả lập.
        return self.transform(texts)

    def transform(self, texts: list[str]) -> np.ndarray:
        # Chia văn bản dài thành các đoạn token trước khi encode để phần cuối
        # CV không bị cắt bỏ bởi giới hạn ngữ cảnh của mô hình.
        tokenizer = self._model.tokenizer
        chunk_size = self._model.max_seq_length - tokenizer.num_special_tokens_to_add(False)
        if chunk_size < 1:
            raise ValueError("Mô hình có giới hạn token không hợp lệ.")
        chunks, groups = [], []
        for text in texts:
            tokens = tokenizer.encode(text, add_special_tokens=False)
            start = len(chunks)
            for offset in range(0, len(tokens), chunk_size):
                chunks.append(tokenizer.decode(tokens[offset:offset + chunk_size]))
            if len(chunks) == start:
                chunks.append(text)
            groups.append((start, len(chunks)))
        chunk_vectors = self._model.encode(
            chunks, batch_size=16, convert_to_numpy=True,
            normalize_embeddings=True, show_progress_bar=False,
        )
        # Lấy trung bình các đoạn rồi chuẩn hóa L2 về một vector cho mỗi hồ sơ.
        # Đây là phép gộp đơn giản; chưa phải mô hình hiểu cấu trúc CV đầy đủ.
        vectors = np.vstack([chunk_vectors[start:end].mean(axis=0) for start, end in groups])
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        return vectors / np.maximum(norms, 1e-12)


class JobRecommenderSystem:
    """Gợi ý việc làm tương tự và ghép CV với việc làm bằng cosine similarity.

    Args:
        jobs: DataFrame chứa đúng các trường yêu cầu (có thể có cột bổ sung).
        backend: 'sentence-transformers' (mặc định) hoặc 'tfidf'.
        model_name: Tên mô hình hoặc đường dẫn model local cho backend semantic.
        device: 'cpu' mặc định; có thể dùng 'cuda' nếu môi trường hỗ trợ.

    Mỗi kết quả là DataFrame gồm 6 cột gốc và Similarity_Score, Rank.
    Experience_Years được đưa vào văn bản, KHÔNG là điều kiện lọc cứng.
    """

    def __init__(
        self,
        jobs: pd.DataFrame,
        backend: str = "sentence-transformers",
        model_name: str = DEFAULT_MODEL,
        device: str = "cpu",
    ) -> None:
        self._jobs = self._validate_jobs(jobs)
        self.backend = backend
        if backend == "tfidf":
            self._encoder: TextVectorizer = TfidfTextVectorizer()
        elif backend == "sentence-transformers":
            self._encoder = SentenceTransformerVectorizer(model_name, device)
        else:
            raise ValueError("backend phải là 'tfidf' hoặc 'sentence-transformers'.")

        # Vị trí hàng trong ma trận luôn dùng index mới 0..N-1, không dùng
        # index bên ngoài của DataFrame vì index đó có thể bị xáo trộn/trùng.
        self._id_to_position = {
            job_id: position for position, job_id in enumerate(self._jobs["Job_ID"])
        }
        documents = [self._job_to_text(row) for _, row in self._jobs.iterrows()]
        # Tính vector một lần khi khởi tạo; các truy vấn sau tái sử dụng ma trận.
        self._job_vectors = self._encoder.fit_transform(documents)

    @classmethod
    def from_csv(cls, path: str | Path, **kwargs) -> "JobRecommenderSystem":
        """Đọc CSV mà vẫn bảo toàn Job_ID có số 0 ở đầu."""
        return cls(pd.read_csv(path, encoding="utf-8-sig", dtype={"Job_ID": str}), **kwargs)

    @staticmethod
    def _validate_jobs(jobs: pd.DataFrame) -> pd.DataFrame:
        if not isinstance(jobs, pd.DataFrame):
            raise TypeError("jobs phải là pandas.DataFrame.")
        if not jobs.columns.is_unique:
            raise ValueError("Tên cột không được trùng nhau.")
        missing = set(JOB_COLUMNS) - set(jobs.columns)
        if missing:
            raise ValueError(f"Thiếu cột: {', '.join(sorted(missing))}")
        if jobs.empty:
            raise ValueError("Dữ liệu việc làm không được rỗng.")
        result = jobs.loc[:, JOB_COLUMNS].copy(deep=True).reset_index(drop=True)
        text_columns = [column for column in JOB_COLUMNS if column != "Experience_Years"]
        for column in text_columns:
            if not result[column].map(lambda value: isinstance(value, str) and bool(value.strip())).all():
                raise ValueError(f"Cột {column} phải chứa chuỗi không rỗng, không có giá trị thiếu.")
            result[column] = result[column].map(TextPreprocessor.normalize)
        if result["Job_ID"].duplicated().any():
            raise ValueError("Job_ID phải duy nhất.")
        if result["Experience_Years"].map(lambda value: isinstance(value, (bool, np.bool_))).any():
            raise ValueError("Experience_Years không nhận giá trị boolean.")
        years = pd.to_numeric(result["Experience_Years"], errors="coerce")
        if not np.isfinite(years.to_numpy(dtype=float)).all() or (years < 0).any():
            raise ValueError("Experience_Years phải là số hữu hạn, không âm.")
        result["Experience_Years"] = years
        return result

    @staticmethod
    def _job_to_text(row: pd.Series) -> str:
        # Job_ID chỉ là khóa định danh, không biểu thị nội dung nên không encode.
        # Ghép đủ 5 trường nội dung giúp cả hai loại truy vấn so sánh đồng nhất.
        return TextPreprocessor.normalize(
            f"{row['Title']}. Skills: {row['Skills']}. "
            f"Minimum experience: {row['Experience_Years']:g} years. "
            f"Domain: {row['Domain']}. {row['Job_Description']}"
        )

    @staticmethod
    def _validate_top_n(top_n: int) -> None:
        if isinstance(top_n, bool) or not isinstance(top_n, Integral) or top_n <= 0:
            raise ValueError("top_n phải là số nguyên dương.")

    def _rank(self, scores: np.ndarray, top_n: int, exclude_position: int | None = None) -> pd.DataFrame:
        result = self._jobs.copy(deep=True)
        # Clip chỉ xử lý sai số dấu phẩy động (ví dụ 1.00000001).
        result["Similarity_Score"] = np.clip(scores, -1.0, 1.0)
        if exclude_position is not None:
            result = result.drop(index=exclude_position)
        # Quy tắc phụ theo Job_ID giúp thứ tự ổn định khi hai điểm bằng nhau.
        result = result.sort_values(
            ["Similarity_Score", "Job_ID"], ascending=[False, True]
        ).head(int(top_n)).reset_index(drop=True)
        result["Rank"] = np.arange(1, len(result) + 1)
        return result

    def recommend_similar_jobs(self, job_id: str, top_n: int = 5) -> pd.DataFrame:
        """So một việc làm với tất cả việc làm khác, loại chính nó khỏi top-N.

        Raises:
            KeyError: Job_ID không tồn tại.
            ValueError: top_n không phải số nguyên dương.
        """
        self._validate_top_n(top_n)
        if not isinstance(job_id, str):
            raise TypeError("job_id phải là chuỗi, ví dụ 'J001'.")
        job_id = TextPreprocessor.normalize(job_id)
        if job_id not in self._id_to_position:
            raise KeyError(f"Không tìm thấy Job_ID: {job_id}")
        position = self._id_to_position[job_id]
        # Chỉ tính vector 1 x N, tránh lưu ma trận N x N không cần thiết.
        query_vector = self._job_vectors[position:position + 1]
        scores = cosine_similarity(query_vector, self._job_vectors).ravel()
        return self._rank(scores, top_n, exclude_position=position)

    def match_cv_to_jobs(self, cv_text: str, top_n: int = 5) -> pd.DataFrame:
        """Vector hóa toàn văn CV rồi xếp hạng độ tương đồng với mỗi tin.

        Không dùng regex để suy đoán số năm kinh nghiệm/thuộc tính cá nhân.
        Đây là trích xuất đặc trưng văn bản, chưa phải trích xuất trường CV.
        CV rỗng bị từ chối. Với TF-IDF, CV không có từ nào trong vocabulary
        trả bảng rỗng kèm cảnh báo thay vì gợi ý tùy ý từ các điểm đều bằng 0.
        """
        self._validate_top_n(top_n)
        if not isinstance(cv_text, str) or not cv_text.strip():
            raise ValueError("cv_text phải là chuỗi văn bản không rỗng.")
        query_vector = self._encoder.transform([TextPreprocessor.normalize(cv_text)])
        if self.backend == "tfidf" and query_vector.nnz == 0:
            warnings.warn(
                "CV không có từ thuộc vocabulary TF-IDF; không có đủ tín hiệu để gợi ý.",
                UserWarning, stacklevel=2,
            )
            return self._rank(np.zeros(len(self._jobs)), top_n).iloc[:0].copy()
        scores = cosine_similarity(query_vector, self._job_vectors).ravel()
        return self._rank(scores, top_n)
