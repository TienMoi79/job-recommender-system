"""Các hàm tiện ích và giao diện phụ trợ cho ứng dụng gợi ý việc làm Streamlit."""

from __future__ import annotations
from typing import Dict, List

# Bộ 3 CV mẫu tiếng Việt chuẩn phục vụ người dùng thử nghiệm nhanh
SAMPLE_RESUMES: Dict[str, Dict[str, str]] = {
    "CV001": {
        "title": "Chuyên viên Phân tích Dữ liệu (Data Analyst)",
        "domain": "Phân tích dữ liệu",
        "badge": "1 năm kinh nghiệm",
        "description": "Kỹ năng: SQL, Python, Pandas, Power BI, Excel, DAX",
        "text": (
            "Tôi là Chuyên viên phân tích dữ liệu với 1 năm kinh nghiệm làm việc trong lĩnh vực kinh doanh và bán lẻ. "
            "Kỹ năng chuyên môn chính: SQL, Python, Pandas, Excel nâng cao, Power BI, DAX. "
            "Kinh nghiệm thực tế: "
            "- Sử dụng SQL và Python (Pandas) để trích xuất, làm sạch và phân tích tập dữ liệu khách hàng và doanh số bán hàng. "
            "- Thiết kế và phát triển các bảng điều khiển trực quan (dashboard) trên Power BI giúp ban lãnh đạo theo dõi chỉ số KPI kinh doanh. "
            "- Lập báo cáo doanh thu định kỳ trên Excel, giải thích xu hướng dữ liệu và đề xuất giải pháp tối ưu kinh doanh. "
            "- Mong muốn tìm công việc trong lĩnh vực phân tích dữ liệu hoặc kinh doanh thông minh (BI)."
        ),
    },
    "CV002": {
        "title": "Lập trình viên Backend Python (Python Developer)",
        "domain": "Phát triển phần mềm",
        "badge": "2 năm kinh nghiệm",
        "description": "Kỹ năng: Python, FastAPI, Django, PostgreSQL, REST API, Docker",
        "text": (
            "Tôi là Lập trình viên Backend Python với 2 năm kinh nghiệm phát triển phần mềm và dịch vụ web. "
            "Kỹ năng chuyên môn chính: Python, FastAPI, Django, PostgreSQL, REST API, Docker, Git. "
            "Kinh nghiệm thực tế: "
            "- Thiết kế kiến trúc và phát triển các dịch vụ REST API phía máy chủ bằng Python kết hợp FastAPI và Django. "
            "- Thiết kế cơ sở dữ liệu quan hệ PostgreSQL, viết câu truy vấn và tối ưu hóa hiệu năng cơ sở dữ liệu. "
            "- Triển khai chức năng xác thực người dùng bảo mật, phân quyền truy cập và viết kiểm thử đơn vị (unit tests). "
            "- Đóng gói ứng dụng vào container bằng Docker và phối hợp cùng lập trình viên Frontend tích hợp hệ thống."
        ),
    },
    "CV003": {
        "title": "Kỹ sư Trí tuệ Nhân tạo & NLP (AI / NLP Engineer)",
        "domain": "Trí tuệ nhân tạo",
        "badge": "2 năm kinh nghiệm",
        "description": "Kỹ năng: Python, PyTorch, Transformers, NLP, FastAPI, Docker",
        "text": (
            "Tôi là Kỹ sư Trí tuệ Nhân tạo với 2 năm kinh nghiệm nghiên cứu và ứng dụng học máy, học sâu. "
            "Kỹ năng chuyên môn chính: Python, PyTorch, Transformers, Xử lý ngôn ngữ tự nhiên (NLP), Phân loại văn bản, FastAPI. "
            "Kinh nghiệm thực tế: "
            "- Xây dựng ứng dụng xử lý ngôn ngữ tự nhiên sử dụng mô hình Transformers và thư viện PyTorch. "
            "- Phát triển mô hình tìm kiếm ngữ nghĩa, trích xuất véc-tơ biểu diễn tài liệu và xây dựng hệ gợi ý việc làm thông minh. "
            "- Triển khai các dịch vụ dự đoán của mô hình học máy thành REST API thông qua FastAPI và đóng gói bằng Docker. "
            "- Đam mê nghiên cứu các bài toán trí tuệ nhân tạo ứng dụng trong thực tế."
        ),
    },
}

CUSTOM_CSS = """
<style>
/* Font và định dạng nền chung */
html, body, .stApp {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

/* Ẩn bớt khoảng trắng mặc định phía trên của Streamlit */
.block-container {
    padding-top: 3.5rem;
    padding-bottom: 3rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 1200px;
}

/* Hero Header */
.hero-box {
    background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 50%, #3B82F6 100%);
    border-radius: 16px;
    padding: 28px 32px;
    color: #FFFFFF;
    margin-bottom: 24px;
    box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.25);
}

.hero-box h1 {
    font-size: clamp(1.9rem, 4vw, 3rem);
    font-weight: 800;
    margin: 0 0 8px 0;
    color: #FFFFFF;
    letter-spacing: -0.02em;
}

.hero-box p {
    font-size: 0.98rem;
    margin: 0;
    opacity: 0.92;
    line-height: 1.5;
}

.hero-badges {
    display: flex;
    gap: 8px;
    margin-top: 14px;
    flex-wrap: wrap;
}

.hero-pill {
    background: rgba(255, 255, 255, 0.18);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 9999px;
    padding: 4px 12px;
    font-size: 0.8rem;
    font-weight: 600;
    color: #FFFFFF;
}

/* Job Card Styling */
.job-card {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 20px 22px;
    margin-bottom: 16px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03);
    transition: all 0.2s ease;
}

.job-card:hover {
    border-color: #93C5FD;
    box-shadow: 0 8px 16px -4px rgba(37, 99, 235, 0.1);
    transform: translateY(-2px);
}

.job-card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 10px;
    gap: 12px;
}

.job-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #0F172A;
    margin: 0 0 4px 0;
    line-height: 1.35;
}

.job-id-tag {
    background-color: #F1F5F9;
    color: #475569;
    font-weight: 700;
    font-size: 0.75rem;
    padding: 3px 8px;
    border-radius: 6px;
    display: inline-block;
    border: 1px solid #E2E8F0;
    white-space: nowrap;
}

.meta-row {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
}

.domain-pill {
    background-color: #EEF2FF;
    color: #4338CA;
    border: 1px solid #C7D2FE;
    font-size: 0.78rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 9999px;
}

.exp-pill {
    background-color: #FFF7ED;
    color: #C2410C;
    border: 1px solid #FFEDD5;
    font-size: 0.78rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 9999px;
}

.skills-wrapper {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 8px;
    margin-bottom: 12px;
}

.skill-tag {
    background-color: #F8FAFC;
    color: #334155;
    border: 1px solid #E2E8F0;
    border-radius: 6px;
    padding: 3px 8px;
    font-size: 0.76rem;
    font-weight: 500;
}

.job-desc-snippet {
    color: #64748B;
    font-size: 0.88rem;
    line-height: 1.5;
    margin-bottom: 14px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* Similarity Badge */
.similarity-badge {
    background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
    border: 1px solid #93C5FD;
    border-radius: 10px;
    padding: 8px 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
}

.similarity-label {
    font-size: 0.82rem;
    font-weight: 600;
    color: #1E40AF;
}

.similarity-val {
    font-size: 0.95rem;
    font-weight: 800;
    color: #1D4ED8;
}

/* Rank Badge */
.rank-badge {
    background: #2563EB;
    color: #FFFFFF;
    font-weight: 800;
    font-size: 0.8rem;
    padding: 4px 10px;
    border-radius: 8px;
    display: inline-block;
    box-shadow: 0 2px 4px rgba(37, 99, 235, 0.25);
}

/* Notice Box */
.academic-notice {
    background-color: #F8FAFC;
    border-left: 4px solid #3B82F6;
    padding: 12px 16px;
    border-radius: 0 8px 8px 0;
    font-size: 0.85rem;
    color: #475569;
    margin-bottom: 18px;
}

/* Detail Card */
.detail-card {
    background: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 16px;
    padding: 28px;
    box-shadow: 0 4px 12px -2px rgba(0, 0, 0, 0.05);
    margin-bottom: 24px;
}

.detail-title {
    font-size: 1.6rem;
    font-weight: 800;
    color: #0F172A;
    margin: 8px 0 12px 0;
}

.section-label {
    font-size: 0.9rem;
    font-weight: 700;
    color: #1E293B;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 18px;
    margin-bottom: 8px;
}

.desc-full-text {
    background-color: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 16px 18px;
    font-size: 0.95rem;
    line-height: 1.65;
    color: #1E293B;
}

/* Empty State */
.empty-state {
    text-align: center;
    padding: 40px 20px;
    background-color: #F8FAFC;
    border: 2px dashed #CBD5E1;
    border-radius: 16px;
    margin: 20px 0;
}

.empty-state-icon {
    font-size: 2.5rem;
    margin-bottom: 12px;
}

.empty-state-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #334155;
    margin-bottom: 6px;
}

.empty-state-text {
    font-size: 0.9rem;
    color: #64748B;
    max-width: 450px;
    margin: 0 auto;
}

.hero-eyebrow { font-size: .72rem; letter-spacing: .14em; font-weight: 700; opacity: .85; margin-bottom: 16px; }
.recommendation-heading { display: flex; align-items: center; gap: 10px; margin-bottom: 14px; }
.recommendation-heading .similarity-badge { margin: 0; flex: 1; font-size: .78rem; gap: 8px; }
.job-card { padding: 4px 2px; border: 0; box-shadow: none; margin: 0; background: transparent; }
.job-card:hover { transform: none; box-shadow: none; }
.job-title { overflow-wrap: anywhere; }
div.job-card h3.job-title { font-size: 1.12rem; line-height: 1.45; padding: 0; margin: 0 0 4px; }
.detail-card { padding: 24px; background: #fff; border: 1px solid #CBD5E1; margin: 16px 0 28px; }
.desc-full-text { white-space: pre-wrap; }
[data-testid="stVerticalBlockBorderWrapper"] { background: #fff; border-radius: 14px; }
[data-testid="stRadio"] [role="radiogroup"] { flex-wrap: wrap; gap: .5rem 1.25rem; }
@media (max-width: 1050px) {
    [data-testid="stHorizontalBlock"] { flex-wrap: wrap; }
    [data-testid="stColumn"] { width: 100%; flex: 1 1 100%; min-width: 0; }
}
@media (max-width: 640px) {
    .block-container { padding-left: 1rem; padding-right: 1rem; }
    .hero-box { padding: 24px 20px; }
    .hero-box p { font-size: .9rem; }
    .detail-card { padding: 18px; }
    .recommendation-heading { align-items: flex-start; }
    .similarity-badge { flex-wrap: wrap; }
}
</style>
"""

def parse_skills(skills_str: str) -> List[str]:
    """Tách danh sách kỹ năng từ chuỗi phân cách bởi dấu chấm phẩy."""
    if not isinstance(skills_str, str):
        return []
    return [s.strip() for s in skills_str.split(";") if s.strip()]
