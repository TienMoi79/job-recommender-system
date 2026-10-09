# Đồ án: Hệ gợi ý việc làm trực tuyến

Mã nguồn cho **Giai đoạn 1: Mock Data**, **Giai đoạn 2: AI Engine** và
**giao diện web Streamlit (Giai đoạn 4)**, kèm Jupyter Notebook để trình bày.
Python theo hướng đối tượng, có comment/docstring tiếng Việt. Evaluation metrics
trên dữ liệu có nhãn (Giai đoạn 3) chưa triển khai.

## 1. Cài đặt và chạy

Tải mã nguồn bằng Git:

```powershell
git clone https://github.com/TienMoi79/job-recommender-system.git
cd job-recommender-system
```

Nếu không dùng Git, mở [repository trên GitHub](https://github.com/TienMoi79/job-recommender-system),
chọn **Code → Download ZIP**, giải nén rồi mở terminal trong thư mục vừa giải nén.

### Chạy giao diện web Streamlit

Sau khi tải repo, mở terminal tại thư mục dự án:

```powershell
$env:PYTHONIOENCODING='utf-8'
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-web.txt
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
```

Nếu đã có `.venv`, bỏ qua lệnh tạo môi trường. Mở **http://127.0.0.1:8501** trên
máy đang chạy ứng dụng. Đây là địa chỉ cục bộ; đưa mã nguồn lên GitHub không tự
triển khai thành website công khai. Nhấn `Ctrl+C` trong terminal để dừng server.

- **Khám phá việc làm:** tìm theo chức danh, kỹ năng, mô tả (hỗ trợ không dấu),
  lọc lĩnh vực/kinh nghiệm yêu cầu, xóa bộ lọc, mở chi tiết và xem gợi ý tương tự.
- **Tìm việc theo CV:** chọn một trong ba CV mẫu hoặc dán văn bản, chọn số kết quả,
  bấm tìm. Có thể mở chi tiết kết quả rồi quay lại mà không mất CV/kết quả.
- Mặc định dùng `data/jobs_vie.cvs` và TF-IDF. Có thể chọn dữ liệu tiếng Anh ở
  sidebar; CV mẫu đổi theo ngôn ngữ. Kết quả cũ được xóa khi đổi dữ liệu/backend.
- Trong **Cài đặt nâng cao**, có thể chọn Sentence Transformers sau khi cài
  `requirements-semantic.txt`. Lỗi tải mô hình hiển thị thông báo để quay lại TF-IDF;
  ứng dụng không âm thầm thay phương pháp hoặc tạo điểm giả.

**Tích hợp:** Streamlit gọi trực tiếp `JobRecommenderSystem`, không cần API server
riêng. `engine.jobs` trả bản sao danh mục để giao diện không sửa được dữ liệu của
engine dùng chung. Cache engine theo nội dung file, backend và model: sửa CSV sẽ
được nhận biết ở lần tương tác/rerun kế tiếp. CV/kết quả chỉ lưu trong bộ nhớ từng
phiên, không vào cache dùng chung, file, hoặc log ứng dụng. Nút **Xóa CV** xóa cả hai.

Điểm hiển thị là cosine nguyên gốc, không quy thành xác suất trúng tuyển. Bộ lọc
kinh nghiệm trong danh sách là bộ lọc theo yêu cầu của tin; chức năng ghép CV chưa
kiểm tra điều kiện kinh nghiệm bắt buộc.

Kiểm thử backend và các luồng giao diện bằng Streamlit AppTest:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

`tests/test_web.py` kiểm tra điểm UI khớp engine thật, điều hướng CV → chi tiết →
quay lại, tìm ký tự đặc biệt, đặt lại bộ lọc, đổi ngôn ngữ, CV rỗng/ngoài từ vựng,
tách phiên, cache đổi theo dữ liệu, thiếu file và lỗi tải semantic. Khi chỉ cài
requirements cơ bản, các test AppTest được bỏ qua với thông báo cần cài thư viện web.

### Chạy bằng Jupyter Notebook để trình bày đồ án

Mở **[job_recommender_notebook.ipynb](job_recommender_notebook.ipynb)**. Notebook có
giải thích tiếng Việt, đọc 20 tin từ `data/jobs_vie.cvs`, chuẩn bị 3 CV tiếng Việt,
minh họa TF-IDF/cosine, chạy hai chức năng gợi ý và lưu kết quả. Mặc định dùng TF-IDF
để không cần tải trọng số mô hình. Các lớp OOP được import từ module trong repo,
vì vậy cần tải **toàn bộ repository**, không chỉ riêng file notebook.

Trong PowerShell tại thư mục dự án:

```powershell
$env:PYTHONIOENCODING='utf-8'
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-notebook.txt
.\.venv\Scripts\python.exe -m notebook job_recommender_notebook.ipynb
```

Nếu đã có `.venv`, bỏ qua lệnh tạo môi trường. Khi notebook mở trong trình duyệt,
chọn kernel **Python 3 (ipykernel)**, rồi chạy toàn bộ từ đầu bằng **Restart Kernel
and Run All Cells**; hoặc nhấn **Shift + Enter** để chạy từng ô. Nếu báo thiếu thư
viện, kiểm tra kernel đang dùng môi trường vừa cài. Có thể đăng ký kernel riêng:

```powershell
.\.venv\Scripts\python.exe -m ipykernel install --user --name job-recommender --display-name "Python (Job Recommender)"
```

Sau đó chọn **Python (Job Recommender)** trong notebook. Đổi `JOB_ID`, `TOP_N`,
`LANGUAGE` hoặc `my_cv` để thử dữ liệu khác. Hướng dẫn bật Sentence Transformers
nằm ở cuối notebook. Xem trên GitHub chỉ hiển thị mã và kết quả đã lưu; cần mở
bằng Jupyter để chạy và sửa các ô.

### Chạy bằng script Python

Yêu cầu Python 3.10 trở lên; môi trường đã dùng để kiểm tra là Python 3.12.
Các lệnh dưới đây chạy tại thư mục gốc dự án bằng PowerShell. Gọi trực tiếp
Python trong virtual environment để không phải thay đổi Execution Policy.

```powershell
$env:PYTHONIOENCODING='utf-8'
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe generate_mock_data.py
.\.venv\Scripts\python.exe demo.py --backend tfidf
```

**Semantic Embedding — lựa chọn mặc định của AI Engine:**

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-semantic.txt
.\.venv\Scripts\python.exe demo.py --backend sentence-transformers
```

Backend semantic dùng `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
Lần đầu cần Internet để tải trọng số từ Hugging Face; các lần sau có thể dùng
cache/local model. Suy luận chạy trên CPU mặc định, không yêu cầu API key.
TF-IDF không tải mô hình, phù hợp khi cần tiết kiệm RAM/dung lượng.
Không tự động đổi backend khi tải mô hình lỗi: lỗi được giữ rõ ràng để kết quả
không bị nhầm giữa hai phương pháp. Có thể chủ động chạy lại với `--backend tfidf`.

Lựa chọn truy vấn và CV riêng:

```powershell
.\.venv\Scripts\python.exe demo.py --backend tfidf --job-id J005 --top-n 3
.\.venv\Scripts\python.exe demo.py --backend tfidf --cv-file my_cv.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

`my_cv.txt` là file văn bản UTF-8 do bạn tự cung cấp, không phải PDF/DOCX.
Nếu terminal hiển thị lỗi dấu tiếng Việt, chạy `$env:PYTHONIOENCODING='utf-8'` trước.
Script tạo dữ liệu **ghi lại** `jobs.csv` và `resumes.json`; demo chỉ tự sinh dữ liệu
khi chưa có cả hai file. Demo lưu lại kết quả của lần chạy gần nhất theo backend.

## 2. Cấu trúc

```text
generate_mock_data.py       # MockDataGenerator: tạo và lưu dữ liệu
job_recommender.py          # Tiền xử lý, hai vectorizer, JobRecommenderSystem
demo.py                    # Chạy item-to-item và cả 3 CV, in/lưu kết quả
app.py                     # Giao diện web Streamlit, quản lý phiên và cache engine
ui_helper.py               # Phong cách giao diện và CV mẫu tiếng Việt
web_support.py             # Tìm kiếm, lọc, hiển thị thẻ và chọn CV mẫu theo ngôn ngữ
requirements-web.txt       # Thư viện chạy giao diện web
.streamlit/config.toml     # Chủ đề sáng, màu sắc giao diện
job_recommender_notebook.ipynb # Chạy từng bước bằng Jupyter Notebook
requirements-notebook.txt  # Thư viện để mở và thực thi notebook
requirements.txt           # Thư viện cho TF-IDF
requirements-semantic.txt  # Thêm Sentence Transformers
data/
  jobs.csv                 # 20 công việc giả lập
  jobs_vie.cvs             # 20 công việc tương ứng bằng tiếng Việt
  resumes.json             # 3 đoạn CV giả lập
outputs/<backend>/
  similar_jobs.csv          # Kết quả truy vấn việc làm gần nhất
  cv_matches.csv            # Kết quả các CV trong lần chạy gần nhất
tests/test_recommender.py   # Kiểm thử chức năng phần mềm
tests/test_web.py           # Kiểm thử tích hợp thật và luồng giao diện
```

## 3. Giai đoạn 1 — dữ liệu

| Cột | Ý nghĩa | Ví dụ |
|---|---|---|
| `Job_ID` | Khóa định danh duy nhất dạng chuỗi | `J001` |
| `Title` | Chức danh | Data Analyst |
| `Skills` | Kỹ năng, phân cách bằng `;` | SQL; Python; Pandas; Excel; Power BI |
| `Experience_Years` | Số năm kinh nghiệm tối thiểu, không âm | 1 |
| `Domain` | Nhóm chuyên môn | Data Analytics |
| `Job_Description` | Mô tả nhiệm vụ/yêu cầu | Analyze sales and customer data... |

20 việc làm bao phủ Data Analyst, BI Analyst, Data Scientist, Data Engineer,
AI Engineer, ML Engineer, NLP Engineer, Computer Vision, Python/Java/Node.js/.NET
Backend, Frontend, Full Stack, Mobile, DevOps, Cloud, QA, Cybersecurity và DBA.
`Domain` ở đây là nhóm chuyên môn IT, chưa phải ngành kinh doanh như tài chính/y tế.

Ba CV thuộc nhóm phân tích dữ liệu, backend Python và AI/NLP. Nội dung việc làm/CV
bằng tiếng Anh nhất quán để baseline TF-IDF dễ thử; mô hình semantic đa ngôn ngữ
có thể nhận cả tiếng Việt. TF-IDF không tự dịch và không hiểu hai từ đồng nghĩa
ở hai ngôn ngữ khác nhau. Dữ liệu cố định để mỗi lần sinh cho cùng kết quả.

## 4. Giai đoạn 2 — thiết kế OOP

### Dùng dữ liệu việc làm tiếng Việt

`data/jobs_vie.cvs` có 20 tin đã dịch chức danh, lĩnh vực, mô tả và các kỹ năng
khái niệm sang tiếng Việt; giữ tên công nghệ như Python, SQL, PyTorch. File giữ
nguyên 6 cột, Job_ID và số năm kinh nghiệm tương ứng với bản tiếng Anh. Dùng
riêng từng file vì ghép cả hai sẽ làm trùng Job_ID. CSV dùng UTF-8 BOM để mở
bằng Excel đúng dấu. Đây vẫn là dữ liệu giả lập.

Tạo lại **chỉ file tiếng Việt** bằng script pandas:

```powershell
.\.venv\Scripts\python.exe generate_mock_data.py --language vi
```

Nạp trực tiếp vào engine (chạy Python tại thư mục gốc dự án):

```python
from job_recommender import JobRecommenderSystem

engine = JobRecommenderSystem.from_csv("data/jobs_vie.cvs", backend="tfidf")
print(engine.recommend_similar_jobs("J001", top_n=5))
print(engine.match_cv_to_jobs(
    "Tôi có 1 năm kinh nghiệm phân tích dữ liệu, sử dụng SQL, Python, Pandas, "
    "Excel và Power BI để làm sạch dữ liệu bán hàng và xây dựng báo cáo."
))
```

`demo.py` vẫn dùng `jobs.csv` và ba CV tiếng Anh như trước. Với TF-IDF, nên
dùng CV tiếng Việt khi truy vấn file tiếng Việt để so khớp từ vựng nhất quán.

### Các lớp và thuật toán

| Class | Trách nhiệm |
|---|---|
| `MockDataGenerator` | Sinh DataFrame việc làm, CV mẫu và lưu file |
| `TextPreprocessor` | Chuẩn hóa Unicode/khoảng trắng; bảo toàn tên kỹ thuật cho TF-IDF |
| `TextVectorizer` | Abstract class, định nghĩa `fit_transform` và `transform` |
| `TfidfTextVectorizer` | Học vocabulary/IDF từ việc làm, vector hóa văn bản |
| `SentenceTransformerVectorizer` | Encode bằng pretrained model, gộp đoạn cho CV dài |
| `JobRecommenderSystem` | Kiểm tra dữ liệu, lưu vector, tính cosine và xếp hạng |

Mỗi tin được ghép thành: `Title + Skills + Experience_Years + Domain + Job_Description`.
`Job_ID` không được vector hóa vì không mô tả nội dung nghề nghiệp.

**TF-IDF:** dùng unigram và bigram, trọng số tần suất log, chuẩn hóa L2. Fit một
lần trên việc làm; CV chỉ dùng `transform` trong cùng không gian đặc trưng.
Giữ token một ký tự và số; chuẩn hóa C++, C#, .NET, Node.js để không mất ký hiệu
quan trọng. TF-IDF biểu diễn mức trùng khớp từ/cụm từ, không phải semantic embedding.

**Sentence Transformers:** dùng mô hình pretrained đa ngôn ngữ, tạo vector 384
chiều với mô hình mặc định. Không fine-tune trên mock data. Văn bản dài được
chia đoạn theo token; lấy trung bình vector các đoạn và chuẩn hóa L2. Cách gộp
này tránh bỏ toàn bộ phần cuối CV nhưng có thể làm loãng kỹ năng quan trọng.
Không cần loại stopword hay stem mạnh vì mô hình cần ngữ cảnh câu.

Cosine similarity giữa vector truy vấn `q` và công việc `j`:

```text
cosine(q, j) = (q · j) / (||q||₂ × ||j||₂)
```

- `recommend_similar_jobs(job_id, top_n=5)`: lấy vector tin đang xem, so với các
  tin, loại chính nó rồi xếp hạng giảm dần.
- `match_cv_to_jobs(cv_text, top_n=5)`: encode toàn văn CV, so với vector việc làm
  và xếp hạng giảm dần. Đây là trích xuất **đặc trưng văn bản**, chưa tách CV thành
  các trường kỹ năng/số năm kinh nghiệm có cấu trúc.
- Kết quả là DataFrame gồm 6 cột gốc, `Similarity_Score` và `Rank`. Đồng điểm
  thì sắp theo `Job_ID`. `top_n` vượt số ứng viên trả về tất cả ứng viên hiện có.
- CV rỗng, dữ liệu sai schema, mã trùng hoặc kinh nghiệm âm được báo lỗi.
  TF-IDF gặp CV hoàn toàn ngoài vocabulary trả bảng rỗng kèm cảnh báo.
- Ma trận vector được lưu trong bộ nhớ khi khởi tạo. Mỗi truy vấn chỉ tính
  một hàng điểm `1 × N`, không dựng ma trận toàn bộ cặp việc làm `N × N`.
  Sau khi sửa CSV, khởi tạo lại engine để cập nhật vector.

## 5. Dùng trực tiếp hai hàm chính

```python
from generate_mock_data import MockDataGenerator
from job_recommender import JobRecommenderSystem

generator = MockDataGenerator()
jobs = generator.create_jobs()

# Đổi sang backend="sentence-transformers" khi đã cài requirements-semantic.txt.
recommender = JobRecommenderSystem(jobs, backend="tfidf")
similar_jobs = recommender.recommend_similar_jobs("J001", top_n=5)
print(similar_jobs[["Title", "Similarity_Score"]])

cv_text = generator.create_resumes()[0]["CV_Text"]
matched_jobs = recommender.match_cv_to_jobs(cv_text, top_n=5)
print(matched_jobs[["Title", "Similarity_Score"]])
```

## 6. Giải thích kết quả và giới hạn để đưa vào báo cáo

Điểm cao nghĩa là biểu diễn nội dung gần nhau hơn. Điểm TF-IDF nằm trong [0, 1];
cosine của dense embedding nói chung thuộc [-1, 1]. Không diễn giải điểm 0.8 là
"80% khả năng trúng tuyển" và không so sánh trực tiếp thang điểm giữa hai backend.
Ngoại trừ CV TF-IDF có vector bằng 0, engine luôn lấy top-N dù độ phù hợp thấp;
ngưỡng chấp nhận cần được xác lập trên dữ liệu đánh giá ở giai đoạn sau.

**Số năm kinh nghiệm hiện là tín hiệu văn bản, chưa được tính chênh lệch số học
hay lọc điều kiện bắt buộc.** Mô hình có thể gợi ý tin yêu cầu kinh nghiệm cao hơn
CV. Không nên tuyên bố engine đã kiểm tra đủ điều kiện tuyển dụng. Bước nâng cấp
sau này có thể trích xuất kinh nghiệm có cấu trúc, thêm bộ lọc hoặc điểm kết hợp.

Đây là hệ content-based: "item-based" trong đồ án nghĩa là so nội dung giữa các
tin việc làm, chưa phải item-based collaborative filtering từ lịch sử tương tác.
Không dùng thông tin cá nhân ngoài văn bản được truyền vào để xây hồ sơ người dùng.

Dữ liệu giả lập nhỏ và CV cố ý có nhiều kỹ năng trùng tin tuyển dụng. Kết quả
demo minh họa cách chạy thuật toán, chưa chứng minh chất lượng trên dữ liệu thực.
Unit tests kiểm tra tính đúng của phần mềm; **không thay thế** Precision@K,
Recall@K, MRR hoặc NDCG của Giai đoạn 3.

## 7. Phạm vi Agile đã chuẩn bị

| Phần việc | Tiêu chí nghiệm thu |
|---|---|
| Giai đoạn 1 | Sinh ít nhất 15 tin với đủ 6 cột và 3 CV; có file đọc lại được |
| Giai đoạn 2 | Hai hàm trả top-N theo cosine; có OOP, comment, demo, kiểm tra đầu vào |
| Giai đoạn 3 — để sau | Xây ground truth, chia dữ liệu, đo metrics và so sánh backend |
| Giai đoạn 4 — đã triển khai | Streamlit hiển thị/lọc tin, nhập CV, mở chi tiết và xem gợi ý thật |

## 8. Tài liệu thuật toán và API

- [Sentence Transformers: encode](https://www.sbert.net/docs/package_reference/sentence_transformer/model.html)
- [Model card của mô hình mặc định](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)
- [scikit-learn: TfidfVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)
- [scikit-learn: cosine_similarity](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.pairwise.cosine_similarity.html)
- [Streamlit: Session State](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state)
- [Streamlit: AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest)

## 9. Trạng thái kiểm chứng khi bàn giao

- Đã sinh `data/jobs.csv` (20 tin) và `data/resumes.json` (3 CV).
- Đã chạy demo TF-IDF cho truy vấn `J001` và cả 3 CV, lưu kết quả trong
  `outputs/tfidf/`. Top-1 của CV001/CV002/CV003 lần lượt là Data Analyst,
  Python Backend Developer và AI Engineer.
- Đã chạy thành công 34 kiểm thử engine, tiện ích web và Streamlit AppTest trên
  Python 3.12.5/Streamlit 1.65.0. Nhánh web đã chạy với TF-IDF và hai bộ dữ liệu.
- Notebook gồm 21 ô (10 ô mã) đã được thực thi từ đầu đến cuối bằng kernel
  Jupyter với dữ liệu tiếng Việt và TF-IDF, không có ô lỗi. File `.ipynb` lưu sẵn
  kết quả; các bảng được xuất vào `outputs/notebook/vi/tfidf/`.
- Đã cài Sentence Transformers, nhưng quá trình tải trọng số Hugging Face
  chưa hoàn tất trong lần kiểm tra. Đã dừng tiến trình tải thử; **chưa xác nhận
  chạy end-to-end backend semantic**, không có kết quả semantic để báo cáo.
  Có thể chạy lại lệnh semantic khi đường tải ổn định; TF-IDF dùng được ngay.
- Phiên bản môi trường kiểm tra: Python 3.12.5, pandas 2.2.3, NumPy 2.2.2,
  SciPy 1.15.2, scikit-learn 1.8.0. Nhánh semantic đã cài sentence-transformers
  5.7.0, transformers 5.18.0 và dùng torch 2.12.1 có sẵn.

Các phiên bản trên ghi nhận môi trường đã dùng, không phải kết luận rằng mọi
phiên bản trong khoảng `requirements` đều đã được kiểm thử.
