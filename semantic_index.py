"""Cache embedding của tin công khai, không cache CV hoặc truy vấn người dùng."""
from __future__ import annotations
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import json
import os
import threading
import tempfile
import numpy as np
from job_recommender import DEFAULT_MODEL, SentenceTransformerVectorizer

MODEL_REVISION = "e8f8c211226b894fcb81acc59f3b34ba3efd5f42"
_model_lock = threading.RLock()


@lru_cache(maxsize=2)
def encoder(model_name=DEFAULT_MODEL):
    # Giới hạn luồng CPU để lần đọc CV đầu không chiếm hết tài nguyên máy.
    import torch
    torch.set_num_threads(min(4, os.cpu_count() or 1))
    return SentenceTransformerVectorizer(model_name, revision=MODEL_REVISION if model_name == DEFAULT_MODEL else None)


class PublicSemanticIndex:
    def __init__(self, documents: list[str], *, model_name=DEFAULT_MODEL, cache_dir: Path | None = None):
        self.model_name = model_name
        cache_dir = cache_dir or Path(__file__).resolve().parent / ".cache/semantic_indexes"
        signature = json.dumps({"schema":1,"model":model_name,"revision":MODEL_REVISION,"documents":documents}, ensure_ascii=False)
        self.signature = sha256(signature.encode('utf-8')).hexdigest()
        path = cache_dir / (self.signature + '.npz')
        with _model_lock:
            self.model = encoder(model_name)
            self.vectors = None
            if path.is_file():
                try:
                    with np.load(path, allow_pickle=False) as stored:
                        vectors = stored['vectors']
                    if vectors.shape == (len(documents), self.model._model.get_sentence_embedding_dimension()) and np.isfinite(vectors).all():
                        self.vectors = vectors
                except (ValueError, OSError, KeyError):
                    pass
            if self.vectors is None:
                self.vectors = self.model.fit_transform(documents).astype(np.float32)
                cache_dir.mkdir(parents=True, exist_ok=True)
                with tempfile.NamedTemporaryFile(dir=cache_dir,suffix='.npz.tmp',delete=False) as stream:
                    np.savez_compressed(stream, vectors=self.vectors)
                    temporary=Path(stream.name)
                temporary.replace(path)

    def similarity(self, text: str) -> np.ndarray:
        # Model không giữ văn bản truy vấn sau khi encode. Chỉ ma trận tin công
        # khai ở self.vectors mới được ghi xuống đĩa.
        with _model_lock:
            vector = self.model.transform([text])[0]
        return np.clip(self.vectors @ vector, 0, 1)
