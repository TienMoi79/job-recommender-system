"""Hàm phục vụ giao diện, không thay đổi thuật toán gợi ý của đồ án."""

from html import escape
import unicodedata

import pandas as pd

from generate_mock_data import MockDataGenerator
from ui_helper import SAMPLE_RESUMES, parse_skills
from ui_text import experience_text, tr
from locations import region_label
from urllib.parse import urlparse


def search_text(value: str) -> str:
    """Bỏ dấu khi tìm kiếm để 'du lieu' tìm được 'dữ liệu'; không đổi embedding."""
    decomposed = unicodedata.normalize("NFD", value.casefold().replace("đ", "d"))
    return " ".join("".join(c for c in decomposed if not unicodedata.combining(c)).split())


def filter_jobs(jobs: pd.DataFrame, keyword: str = "", domain: str | None = "Tất cả",
                experience: str | float | None = "Tất cả") -> pd.DataFrame:
    """Lọc từ khóa theo nghĩa đen, không diễn giải C++ hoặc dấu [ như regex."""
    result = jobs.copy()
    query = search_text(keyword)
    if query:
        text = result["Title"] + " " + result["Skills"] + " " + result["Job_Description"]
        result = result[text.map(search_text).str.contains(query, regex=False, na=False)]
    if domain not in (None, "Tất cả"):
        result = result[result["Domain"] == domain]
    if experience not in (None, "Tất cả"):
        # Web truyền giá trị số, không phải nhãn đã dịch. Chuỗi tiếng Việt cũ
        # vẫn được hỗ trợ để giữ tương thích với các lời gọi bên ngoài.
        years = float(experience.removesuffix(" năm")) if isinstance(experience, str) else float(experience)
        result = result[result["Experience_Years"] == years]
    return result


def sample_resumes(language: str) -> dict:
    """CV mẫu luôn cùng ngôn ngữ với danh mục, đặc biệt cần thiết với TF-IDF."""
    if language == "vi":
        return SAMPLE_RESUMES
    return {
        resume["Resume_ID"]: {"title": resume["Profile"], "text": resume["CV_Text"]}
        for resume in MockDataGenerator().create_resumes()
    }


def job_card_html(row: pd.Series, *, detail: bool = False, language: str = "vi") -> str:
    """Escape mọi nội dung dữ liệu trước khi ghép HTML để hiển thị đúng và an toàn."""
    value = lambda column: escape(str(row[column]))
    skills = "".join(f'<span class="skill-tag">{escape(skill)}</span>' for skill in parse_skills(row["Skills"]))
    score = ""
    if "Similarity_Score" in row:
        score = (
            f'<div class="recommendation-heading"><span class="rank-badge">#{int(row["Rank"])}</span>'
            f'<span class="similarity-badge">{escape(tr(language, "cv_similarity" if "Score_Title" in row else "similarity"))} '
            f'<strong>{float(row["Similarity_Score"]):.4f}</strong></span></div>'
        )
    description_class = "desc-full-text" if detail else "job-desc-snippet"
    metadata = ""
    if row.get("Company", ""):
        metadata += f'<p><strong>{escape(tr(language, "company"))}:</strong> {escape(str(row["Company"]))}</p>'
    if row.get("Region_Codes", ""):
        regions = ", ".join(region_label(code, language) for code in str(row["Region_Codes"]).split(";"))
        metadata += f'<p><strong>{escape(tr(language, "location"))}:</strong> {escape(regions)}</p>'
    if row.get("Salary", ""):
        metadata += f'<p><strong>{escape(tr(language, "salary"))}:</strong> {escape(str(row["Salary"]))}</p>'
    requirements = ""
    if detail and row.get("Requirements", ""):
        requirements = f'<p><strong>{escape(tr(language, "requirements"))}:</strong> {escape(str(row["Requirements"]))}</p>'
    matched = ""
    if row.get("Matched_Skills", ""):
        matched = f'<p><strong>{escape(tr(language, "matched_skills"))}:</strong> {escape(str(row["Matched_Skills"]))}</p>'
    source = ""
    url = str(row.get("Source_URL", ""))
    if urlparse(url).scheme == "https" and urlparse(url).netloc == "huggingface.co":
        source = f'<p><a href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{escape(tr(language, "source"))}</a></p>'
    known = row.get("Experience_Known", True)
    exp_label = experience_text(language, float(row["Experience_Years"]), badge=True) if known else tr(language, "experience_unknown")
    # Không quy đổi điểm cosine thành %, vì đây không phải xác suất tuyển dụng.
    return (
        f'<div class="job-card {"detail-card" if detail else ""}">{score}'
        f'<div class="job-card-header"><h3 class="job-title">{value("Title")}</h3>'
        f'<span class="job-id-tag">{value("Job_ID")}</span></div>'
        f'<div class="meta-row"><span class="domain-pill">{value("Domain")}</span>'
        f'<span class="exp-pill">{escape(exp_label)}</span></div>'
        f'<div class="job-metadata">{metadata}</div>'
        f'<div class="skills-wrapper">{skills}</div>'
        f'<div class="{description_class}">{value("Job_Description")}</div>{requirements}{matched}{source}</div>'
    )
