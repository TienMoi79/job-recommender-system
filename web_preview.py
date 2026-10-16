"""Giao diện JobVista: chạy bằng ``python web_preview.py``.

FastAPI chỉ là lớp kết nối. Đọc CV và tính cosine vẫn dùng các class của đồ án.
HTML/CSS/JavaScript được phục vụ cùng địa chỉ nên không cần Node hay hai terminal.
Bản Streamlit cũ và notebook tiếp tục chạy độc lập.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal
from urllib.parse import unquote
import json

import pandas as pd
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from catalog_data import localize_jobs
from cv_documents import CVReadError, MAX_FILE_BYTES, MAX_TEXT_CHARS, ResumeDocumentReader
from job_recommender import JobRecommenderSystem
from locations import REGIONS, region_label
from resume_profile import ResumeAnalyzer
from ui_text import TEXT

ROOT = Path(__file__).resolve().parent
Language = Literal["vi", "en"]


class CatalogService:
    """Một catalog và engine dùng chung; tuyệt đối không cache nội dung CV."""

    def __init__(self, language: str):
        self.language = language
        original = pd.read_csv(ROOT / "data/jobs_catalog.csv", encoding="utf-8-sig").fillna("")
        self.company_count = int(original["Company"].nunique())
        self.jobs = localize_jobs(original, language)
        self.engine = JobRecommenderSystem(self.jobs, backend="tfidf")

    def serialize(self, row, *, detail=False):
        codes = [code for code in str(row.get("Region_Codes", "")).split(";") if code in REGIONS]
        result = {
            "id": str(row["Job_ID"]), "title": str(row["Title"]),
            "company": str(row.get("Company", "")), "domain": str(row["Domain"]),
            "skills": [skill.strip() for skill in str(row["Skills"]).split(";") if skill.strip()],
            "regions": codes, "location": " · ".join(region_label(code, self.language) for code in codes),
            "salary": str(row.get("Salary", "")), "experience": float(row["Experience_Years"]),
            "experience_known": bool(row.get("Experience_Known", False)),
            "excerpt": str(row["Job_Description"])[:200],
        }
        if detail:
            result.update(description=str(row["Job_Description"]), requirements=str(row.get("Requirements", "")),
                          source=str(row.get("Source_URL", "")))
        if "Similarity_Score" in row:
            result["score"] = round(float(row["Similarity_Score"]), 4)
            result["matched_skills"] = [s.strip() for s in str(row.get("Matched_Skills", "")).split(";") if s.strip()]
            result["components"] = {field: round(float(row[f"Score_{field}"]), 4)
                                    for field in ("Title", "Skills", "Domain", "Job_Description")
                                    if f"Score_{field}" in row}
        return result

    def records(self, frame):
        return [self.serialize(row) for _, row in frame.iterrows()]


@lru_cache(maxsize=2)
def catalog(language: str) -> CatalogService:
    return CatalogService(language)


def profile_data(text: str, *, ocr=False):
    profile = ResumeAnalyzer().analyze(text, ocr=ocr)
    return {"skills": list(profile.skills), "title": profile.title_text,
            "locations": list(profile.location_candidates)}


app = FastAPI(title="JobVista · Job recommendation preview", docs_url="/api/docs")


@app.middleware("http")
async def private_responses(request: Request, call_next):
    response = await call_next(request)
    # Kết quả phân tích CV không được lưu vào HTTP cache của trình duyệt/proxy.
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.get("/api/catalog")
def get_catalog(language: Language = "vi"):
    service = catalog(language)
    codes = {code for values in service.jobs["Region_Codes"] for code in str(values).split(";")}
    return {
        "jobs": service.records(service.jobs),
        "regions": [{"id": code, "label": region_label(code, language)} for code in REGIONS if code in codes],
        "all_regions": [{"id": code, "label": region_label(code, language)} for code in REGIONS],
        "domains": sorted(service.jobs["Domain"].unique().tolist()),
        "companies": service.company_count,
    }


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str, language: Language = "vi", location: str | None = None):
    service = catalog(language)
    found = service.jobs.loc[service.jobs["Job_ID"] == job_id]
    if found.empty:
        raise HTTPException(404, "job_not_found")
    if location is not None and location not in REGIONS:
        raise HTTPException(422, "invalid_location")
    return {"job": service.serialize(found.iloc[0], detail=True),
            "similar": service.records(service.engine.recommend_similar_jobs(job_id, 3, location=location))}


@app.get("/api/samples")
def samples():
    return json.loads((ROOT / "data/resumes.json").read_text(encoding="utf-8-sig"))


@app.post("/api/cv/read")
async def read_cv(request: Request, language: Language = "vi"):
    # Nhận raw bytes theo từng đoạn, giới hạn 15 MB ngay khi đọc. Không dùng
    # UploadFile vì multipart mặc định có thể spool tệp lớn xuống ổ đĩa.
    content = bytearray()
    async for chunk in request.stream():
        content.extend(chunk)
        if len(content) > MAX_FILE_BYTES:
            raise HTTPException(413, TEXT[language]["cv_file_large"])
    filename = unquote(request.headers.get("X-CV-Filename", ""))
    try:
        document = await run_in_threadpool(ResumeDocumentReader().read, bytes(content), filename)
    except CVReadError as exc:
        raise HTTPException(400, TEXT[language].get(exc.code, TEXT[language]["cv_file_invalid"])) from None
    return {"text": document.text, "ocr": document.used_ocr, "pages": document.page_count,
            "profile": profile_data(document.text, ocr=document.used_ocr)}


class MatchRequest(BaseModel):
    text: str = Field(min_length=1, max_length=MAX_TEXT_CHARS)
    location: str | None = None
    top_n: int = Field(default=12, ge=1, le=50)
    language: Language = "vi"


@app.post("/api/cv/match")
def match_cv(payload: MatchRequest):
    if not payload.text.strip():
        raise HTTPException(422, "empty_cv")
    if payload.location is not None and payload.location not in REGIONS:
        raise HTTPException(422, "invalid_location")
    service = catalog(payload.language)
    result = service.engine.match_cv_to_jobs(payload.text, payload.top_n, location=payload.location)
    return {"jobs": service.records(result), "profile": profile_data(payload.text)}


app.mount("/assets", StaticFiles(directory=ROOT / "web_ui"), name="assets")


@app.get("/")
def index():
    return FileResponse(ROOT / "web_ui/index.html", headers={"Cache-Control": "no-cache"})


if __name__ == "__main__":
    import uvicorn
    print("\nJobVista: http://127.0.0.1:8000\n")
    uvicorn.run(app, host="127.0.0.1", port=8000, access_log=False)
