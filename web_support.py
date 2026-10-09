"""Hàm phục vụ giao diện, không thay đổi thuật toán gợi ý của đồ án."""

from html import escape
import unicodedata

import pandas as pd

from generate_mock_data import MockDataGenerator
from ui_helper import SAMPLE_RESUMES, parse_skills


def search_text(value: str) -> str:
    """Bỏ dấu khi tìm kiếm để 'du lieu' tìm được 'dữ liệu'; không đổi embedding."""
    decomposed = unicodedata.normalize("NFD", value.casefold().replace("đ", "d"))
    return " ".join("".join(c for c in decomposed if not unicodedata.combining(c)).split())


def filter_jobs(jobs: pd.DataFrame, keyword: str = "", domain: str = "Tất cả",
                experience: str = "Tất cả") -> pd.DataFrame:
    """Lọc từ khóa theo nghĩa đen, không diễn giải C++ hoặc dấu [ như regex."""
    result = jobs.copy()
    query = search_text(keyword)
    if query:
        text = result["Title"] + " " + result["Skills"] + " " + result["Job_Description"]
        result = result[text.map(search_text).str.contains(query, regex=False, na=False)]
    if domain != "Tất cả":
        result = result[result["Domain"] == domain]
    if experience != "Tất cả":
        result = result[result["Experience_Years"] == float(experience.removesuffix(" năm"))]
    return result


def sample_resumes(language: str) -> dict:
    """CV mẫu luôn cùng ngôn ngữ với danh mục, đặc biệt cần thiết với TF-IDF."""
    if language == "vi":
        return SAMPLE_RESUMES
    return {
        resume["Resume_ID"]: {"title": resume["Profile"], "text": resume["CV_Text"]}
        for resume in MockDataGenerator().create_resumes()
    }


def job_card_html(row: pd.Series, *, detail: bool = False) -> str:
    """Escape mọi nội dung dữ liệu trước khi ghép HTML để hiển thị đúng và an toàn."""
    value = lambda column: escape(str(row[column]))
    skills = "".join(f'<span class="skill-tag">{escape(skill)}</span>' for skill in parse_skills(row["Skills"]))
    score = ""
    if "Similarity_Score" in row:
        score = (
            f'<div class="recommendation-heading"><span class="rank-badge">#{int(row["Rank"])}</span>'
            f'<span class="similarity-badge">Điểm tương đồng nội dung '
            f'<strong>{float(row["Similarity_Score"]):.4f}</strong></span></div>'
        )
    description_class = "desc-full-text" if detail else "job-desc-snippet"
    # Không quy đổi điểm cosine thành %, vì đây không phải xác suất tuyển dụng.
    return (
        f'<div class="job-card {"detail-card" if detail else ""}">{score}'
        f'<div class="job-card-header"><h3 class="job-title">{value("Title")}</h3>'
        f'<span class="job-id-tag">{value("Job_ID")}</span></div>'
        f'<div class="meta-row"><span class="domain-pill">{value("Domain")}</span>'
        f'<span class="exp-pill">{float(row["Experience_Years"]):g} năm kinh nghiệm</span></div>'
        f'<div class="skills-wrapper">{skills}</div>'
        f'<div class="{description_class}">{value("Job_Description")}</div></div>'
    )
