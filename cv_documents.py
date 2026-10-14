"""Đọc CV từ PDF, Word (.docx) và ảnh bằng thư viện chạy trên máy chủ.

Tệp của người dùng được xử lý từ bytes trong RAM, không ghi xuống ổ đĩa và
không gửi nội dung sang dịch vụ OCR/AI bên ngoài. Chỉ trọng số OCR công khai
được tải và lưu cache lần đầu. Mọi lỗi trả mã cố định, không chứa nội dung CV.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from io import BytesIO
from pathlib import Path
import threading
import warnings
from zipfile import BadZipFile, ZipFile

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError


MAX_FILE_BYTES = 15 * 1024 * 1024
MAX_PAGES = 20
MAX_TEXT_CHARS = 60000
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}


class CVReadError(ValueError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


@dataclass(frozen=True)
class CVDocument:
    text: str
    page_count: int
    used_ocr: bool
    format: str


class LocalOCR:
    """Model dùng chung chỉ chứa trọng số; khóa tránh chạy đồng thời trên model.

    PP-OCRv6 small hỗ trợ Việt/Anh theo bảng ngôn ngữ của RapidOCR. Giới hạn
    luồng CPU để không làm máy treo khi đọc nhiều trang; không nhận diện khuôn mặt.
    """
    def __init__(self):
        try:
            from rapidocr import RapidOCR, LangRec, LangDet, OCRVersion, ModelType
            self.engine = RapidOCR(params={
                "Det.ocr_version": OCRVersion.PPOCRV4,
                "Det.model_type": ModelType.MOBILE,
                "Det.lang_type": LangDet.CH,
                "Rec.ocr_version": OCRVersion.PPOCRV6,
                "Rec.model_type": ModelType.SMALL,
                "Rec.lang_type": LangRec.CH,
                "Global.log_level": "critical",
                "Global.model_root_dir": str(Path(__file__).resolve().parent / ".cache/ocr_models"),
                "EngineConfig.onnxruntime.intra_op_num_threads": 2,
                "EngineConfig.onnxruntime.inter_op_num_threads": 2,
            })
        except Exception as exc:
            raise CVReadError("cv_ocr_unavailable") from exc
        self.lock = threading.Lock()

    def read(self, image: Image.Image) -> str:
        try:
            rgb = image.convert("RGB")
            rgb.thumbnail((2400, 3200))
            with self.lock:
                result = self.engine(np.asarray(rgb))
            texts = getattr(result, "txts", None)
            return "\n".join(str(text) for text in texts) if texts is not None else ""
        except CVReadError:
            raise
        except Exception as exc:
            raise CVReadError("cv_ocr_unavailable") from exc


@lru_cache(maxsize=1)
def get_local_ocr() -> LocalOCR:
    return LocalOCR()


class ResumeDocumentReader:
    def __init__(self, ocr=None):
        # Cho phép truyền OCR vào kiểm thử; khi dùng thật luôn dùng LocalOCR.
        self._ocr = ocr

    def _read_image(self, image: Image.Image) -> str:
        if image.width * image.height > 30_000_000:
            raise CVReadError("cv_image_too_large")
        return (self._ocr or get_local_ocr()).read(ImageOps.exif_transpose(image))

    def read(self, content: bytes, filename: str) -> CVDocument:
        if not isinstance(content, bytes) or not content:
            raise CVReadError("cv_file_empty")
        if len(content) > MAX_FILE_BYTES:
            raise CVReadError("cv_file_large")
        extension = Path(filename).suffix.lower()
        try:
            if extension == ".pdf":
                result = self._pdf(content)
            elif extension == ".docx":
                result = self._docx(content)
            elif extension in IMAGE_EXTENSIONS:
                with warnings.catch_warnings():
                    warnings.simplefilter("error", Image.DecompressionBombWarning)
                    with Image.open(BytesIO(content)) as image:
                        frames = getattr(image, "n_frames", 1)
                        if frames > MAX_PAGES:
                            raise CVReadError("cv_too_many_pages")
                        texts = []
                        for frame in range(frames):
                            image.seek(frame)
                            texts.append(self._read_image(image))
                result = CVDocument("\n".join(texts), frames, True, "image")
            else:
                raise CVReadError("cv_format_unsupported")
        except CVReadError:
            raise
        except (Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
            raise CVReadError("cv_image_too_large") from exc
        except Exception as exc:
            raise CVReadError("cv_file_invalid") from exc
        text = result.text.replace("\x00", "").strip()
        if len(text) > MAX_TEXT_CHARS:
            raise CVReadError("cv_text_too_long")
        if len(text) < 20:
            raise CVReadError("cv_no_text")
        return CVDocument(text, result.page_count, result.used_ocr, result.format)

    def _pdf(self, content: bytes) -> CVDocument:
        from pypdf import PdfReader
        reader = PdfReader(BytesIO(content))
        if reader.is_encrypted:
            raise CVReadError("cv_pdf_locked")
        if len(reader.pages) > MAX_PAGES:
            raise CVReadError("cv_too_many_pages")
        texts, used_ocr, renderer = [], False, None
        try:
            for index, page in enumerate(reader.pages):
                try:
                    text = page.extract_text() or ""
                except Exception:
                    text = ""
                # PDF scan thường không có lớp chữ, hoặc chỉ có vài ký tự header.
                if len("".join(c for c in text if c.isalpha())) < 40:
                    import pypdfium2 as pdfium
                    if renderer is None:
                        renderer = pdfium.PdfDocument(content)
                    pdf_page = renderer[index]
                    try:
                        scale = min(2.5, 2400 / max(pdf_page.get_size()))
                        bitmap = pdf_page.render(scale=scale)
                        try:
                            ocr_text = self._read_image(bitmap.to_pil())
                        finally:
                            bitmap.close()
                        if ocr_text:
                            text = ocr_text
                        used_ocr = True
                    finally:
                        pdf_page.close()
                texts.append(text)
        finally:
            if renderer is not None:
                renderer.close()
        return CVDocument("\n".join(texts), len(reader.pages), used_ocr, "pdf")

    def _docx(self, content: bytes) -> CVDocument:
        from docx import Document
        from docx.oxml.ns import qn
        with ZipFile(BytesIO(content)) as archive:
            entries = archive.infolist()
            if sum(entry.file_size for entry in entries) > 100 * 1024 * 1024:
                raise CVReadError("cv_file_large")
            if "word/document.xml" not in archive.namelist():
                raise CVReadError("cv_file_invalid")
            document = Document(BytesIO(content))
            # XML bao gồm đoạn văn, bảng và text box theo thứ tự tài liệu.
            paragraphs = []
            for paragraph in document.element.body.iter(qn("w:p")):
                value = "".join(node.text or "" for node in paragraph.iter(qn("w:t"))).strip()
                if value:
                    paragraphs.append(value)
            for section in document.sections:
                for part in (section.header, section.footer):
                    paragraphs += [p.text for p in part.paragraphs if p.text.strip()]
            text = "\n".join(dict.fromkeys(paragraphs))
            used_ocr = False
            if len(text.strip()) < 40:
                images = [entry for entry in entries if entry.filename.startswith("word/media/")
                          and Path(entry.filename).suffix.lower() in IMAGE_EXTENSIONS]
                if len(images) > MAX_PAGES:
                    raise CVReadError("cv_too_many_pages")
                for entry in images:
                    with Image.open(BytesIO(archive.read(entry))) as image:
                        text += "\n" + self._read_image(image)
                used_ocr = bool(images)
        # DOCX không có ranh giới trang ổn định khi chưa render bằng Word.
        return CVDocument(text, 0, used_ocr, "docx")
