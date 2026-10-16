"""Giao diện Streamlit kết nối trực tiếp với JobRecommenderSystem.

Chạy: python -m streamlit run app.py
Cache chỉ chứa engine/dữ liệu việc làm. CV và kết quả chỉ ở RAM của từng phiên.
"""
from __future__ import annotations

from hashlib import sha256
from io import BytesIO
from pathlib import Path
import warnings
import math

import pandas as pd
import streamlit as st

from job_recommender import DEFAULT_MODEL, JobRecommenderSystem
from hybrid_recommender import HybridJobRecommenderSystem
from ui_helper import CUSTOM_CSS
from web_support import filter_jobs, job_card_html, sample_resumes
from ui_text import experience_text, tr
from catalog_data import localize_jobs
from cv_documents import ResumeDocumentReader, CVReadError
from resume_profile import ResumeAnalyzer, ROLES
from locations import REGIONS, region_label

BASE_DIR = Path(__file__).resolve().parent
EXPLORE, MATCH = "explore", "match"
FILTER_ALL = "__all__"


def dataset_path(language: str) -> Path:
    """Nhận tên CSV mới; vẫn đọc được bản repo cũ sử dụng đuôi .cvs."""
    catalog = BASE_DIR / "data/jobs_catalog.csv"
    if catalog.exists():
        return catalog
    if language == "en":
        return BASE_DIR / "data/jobs.csv"
    csv_path = BASE_DIR / "data/jobs_vie.csv"
    return csv_path if csv_path.exists() else BASE_DIR / "data/jobs_vie.cvs"


@st.cache_resource(show_spinner=False, max_entries=4)
def get_recommender_engine(csv_content: bytes, backend: str,
                           model_name: str = DEFAULT_MODEL, language: str = "vi") -> JobRecommenderSystem:
    """Nội dung file nằm trong khóa cache: sửa CSV sẽ tự tạo lại engine.

    Không dùng đường dẫn làm khóa duy nhất, vì cùng đường dẫn có thể đã đổi dữ liệu.
    Không cache truy vấn hay CV của người dùng trong cache dùng chung.
    """
    jobs = pd.read_csv(BytesIO(csv_content), encoding="utf-8-sig", dtype={"Job_ID": str})
    localized=localize_jobs(jobs, language)
    if backend=='hybrid':
        return HybridJobRecommenderSystem(localized,model_name=model_name)
    return JobRecommenderSystem(localized, backend=backend, model_name=model_name)


def initialize_state() -> None:
    defaults = {
        "page": EXPLORE, "selected_job_id": None, "detail_origin": EXPLORE,
        "filter_keyword": "", "filter_domain": FILTER_ALL, "filter_exp": FILTER_ALL,
        "cv_text": "", "cv_results": None, "cv_notice": None, "cv_top_n": 5,
        "similar_top_n": 5,
        "cv_profile": None, "cv_document": None, "cv_upload_notice": None,
        "cv_upload_generation": 0, "cv_location": FILTER_ALL,
        "filter_location": FILTER_ALL, "browse_page": 1,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def invalidate_cv() -> None:
    st.session_state.cv_results = None
    st.session_state.cv_notice = None


def save_widget_value(key: str, reset_cv: bool = False) -> None:
    # Dùng khóa riêng cho giá trị bền trong phiên: Streamlit dọn widget bị ẩn
    # khi chuyển trang, nhưng các giá trị này vẫn cần tồn tại để quay lại CV.
    st.session_state[key] = st.session_state[f"_{key}"]
    if key == "cv_text":
        text = st.session_state.cv_text
        document = st.session_state.cv_document
        st.session_state.cv_profile = ResumeAnalyzer().analyze(text, ocr=bool(document and document.used_ocr)) if text.strip() else None
    if key.startswith("filter_"):
        st.session_state.browse_page = 1
    if reset_cv:
        invalidate_cv()


def set_cv(text: str) -> None:
    st.session_state.cv_text = text
    profile = ResumeAnalyzer().analyze(text) if text.strip() else None
    st.session_state.cv_profile = profile
    st.session_state.cv_location = profile.location_candidates[0] if profile and profile.location_candidates else FILTER_ALL
    st.session_state.cv_document = None
    st.session_state.cv_upload_notice = None
    # Đổi key để Streamlit dọn tệp cũ khi xóa CV/chọn mẫu/đổi ngôn ngữ.
    st.session_state.cv_upload_generation = st.session_state.get("cv_upload_generation", 0) + 1
    invalidate_cv()


def use_keyword_matching() -> None:
    """Nút phục hồi khi cách tìm theo ý nghĩa chưa sẵn sàng; không xóa CV."""
    st.session_state.backend = "tfidf"
    invalidate_cv()


def reset_uploaded_analysis() -> None:
    """Tệp mới/xóa tệp làm mất kết quả cũ nhưng phải giữ chính widget upload.

    Không gọi set_cv ở đây vì hàm đó đổi key và sẽ xóa tệp vừa được chọn.
    """
    st.session_state.cv_text = ""
    st.session_state.cv_profile = st.session_state.cv_document = None
    st.session_state.cv_upload_notice = None
    st.session_state.cv_location = FILTER_ALL
    invalidate_cv()


def reset_filters() -> None:
    st.session_state.filter_keyword = ""
    st.session_state.filter_domain = st.session_state.filter_exp = FILTER_ALL
    st.session_state.filter_location = FILTER_ALL
    st.session_state.browse_page = 1


def open_job(job_id: str, origin: str) -> None:
    st.session_state.selected_job_id = job_id
    st.session_state.detail_origin = origin
    st.session_state.page = EXPLORE


def back_from_detail() -> None:
    st.session_state.selected_job_id = None
    st.session_state.page = st.session_state.detail_origin


def render_cards(jobs: pd.DataFrame, prefix: str, origin: str, language: str) -> None:
    # Từng hàng chứa hai thẻ giúp thứ tự xếp hạng trái -> phải rõ ràng.
    rows = list(jobs.iterrows())
    for start in range(0, len(rows), 2):
        columns = st.columns(2, gap="medium")
        for column, (_, row) in zip(columns, rows[start:start + 2]):
            with column:
                with st.container(border=True):
                    st.markdown(job_card_html(row, language=language), unsafe_allow_html=True)
                    st.button(tr(language, "details"), key=f"{prefix}_{row['Job_ID']}",
                              use_container_width=True, on_click=open_job,
                              args=(row["Job_ID"], origin))
                    if "Score_Title" in row:
                        with st.expander(tr(language, "score_breakdown")):
                            for field, key in (("Title", "score_title"), ("Skills", "score_skills"),
                                               ("Domain", "score_domain"), ("Job_Description", "score_description"),
                                               ("Lexical","score_lexical"),("Semantic","score_semantic"),("Experience","score_experience")):
                                if f'Score_{field}' in row:
                                    weights=row.get('Component_Weights')
                                    weight=weights.get(field,0.) if isinstance(weights,dict) else None
                                    value=f"{row[f'Score_{field}']:.4f}" if weight is None or weight>0 else '—'
                                    label=tr(language,key)+(f' ({weight:.1%})' if weight is not None else '')
                                    st.write(f"{label}: {value}")
                            if isinstance(row.get('Component_Weights'),dict):
                                st.caption(tr(language,'hybrid_score_note'))
                            if row.get('Not_Mentioned_Skills',''):
                                st.caption(tr(language,'not_mentioned_skills')+': '+row['Not_Mentioned_Skills'])


def top_n_widget(label: str, key: str, count: int, *, reset_cv: bool = False) -> int:
    limit = max(1, min(10, count))
    st.session_state[key] = min(st.session_state[key], limit)
    st.session_state[f"_{key}"] = st.session_state[key]
    return int(st.number_input(label, min_value=1, max_value=limit, step=1,
                               key=f"_{key}", on_change=save_widget_value,
                               args=(key, reset_cv)))


def render_detail(engine: JobRecommenderSystem, jobs: pd.DataFrame, language: str) -> None:
    origin = st.session_state.detail_origin
    st.button(tr(language, "back_cv" if origin == MATCH else "back_jobs"),
              key="back_detail", on_click=back_from_detail)
    selected = jobs[jobs["Job_ID"] == st.session_state.selected_job_id]
    if selected.empty:
        st.warning(tr(language, "job_missing"))
        return
    row = selected.iloc[0]
    st.markdown(job_card_html(row, detail=True, language=language), unsafe_allow_html=True)
    st.subheader(tr(language, "similar_title"))
    st.caption(tr(language, "similar_help"))
    region = st.session_state.cv_location if origin == MATCH and st.session_state.cv_location != FILTER_ALL and "Region_Codes" in jobs else None
    available = jobs if region is None else jobs[jobs["Region_Codes"].map(lambda codes: region in str(codes).split(";"))]
    count_available = len(available[available["Job_ID"] != row["Job_ID"]])
    if count_available == 0:
        st.info(tr(language, "no_similar"))
        return
    count = top_n_widget(tr(language, "similar_count"), "similar_top_n", count_available)
    try:
        similar = engine.recommend_similar_jobs(row["Job_ID"], top_n=count, location=region)
    except Exception:
        st.error(tr(language, "similar_error"))
        return
    render_cards(similar, "similar", origin, language)


def render_explore(engine: JobRecommenderSystem, jobs: pd.DataFrame, language: str) -> None:
    if st.session_state.selected_job_id is not None:
        render_detail(engine, jobs, language)
        return
    st.subheader(tr(language, "explore_title"))
    search, domain, experience = st.columns([2, 1, 1])
    # Không dùng None làm mục "Tất cả": Streamlit coi None là chưa chọn và
    # sẽ hiện placeholder mặc định tiếng Anh thay vì nhãn đã dịch.
    domains = [FILTER_ALL] + sorted(jobs["Domain"].unique())
    experiences = [FILTER_ALL] + sorted(jobs["Experience_Years"].unique())
    if st.session_state.filter_domain not in domains:
        st.session_state.filter_domain = FILTER_ALL
    if st.session_state.filter_exp not in experiences:
        st.session_state.filter_exp = FILTER_ALL
    for key in ("filter_keyword", "filter_domain", "filter_exp"):
        st.session_state[f"_{key}"] = st.session_state[key]
    with search:
        st.text_input(tr(language, "keyword"), placeholder=tr(language, "keyword_placeholder"),
                      key="_filter_keyword", on_change=save_widget_value, args=("filter_keyword",))
    with domain:
        st.selectbox(tr(language, "domain"), domains, key="_filter_domain",
                     format_func=lambda value: tr(language, "all") if value == FILTER_ALL else value,
                     on_change=save_widget_value, args=("filter_domain",))
    with experience:
        st.selectbox(tr(language, "experience"), experiences, key="_filter_exp",
                     format_func=lambda value: tr(language, "all") if value == FILTER_ALL else experience_text(language, value),
                     on_change=save_widget_value, args=("filter_exp",))
    st.button(tr(language, "clear_filters"), key="reset_filters", on_click=reset_filters)
    filtered = filter_jobs(jobs, st.session_state.filter_keyword,
                           None if st.session_state.filter_domain == FILTER_ALL else st.session_state.filter_domain,
                           None if st.session_state.filter_exp == FILTER_ALL else st.session_state.filter_exp)
    if "Region_Codes" in jobs:
        choices = [FILTER_ALL] + sorted({code for value in jobs["Region_Codes"] for code in str(value).split(";") if code in REGIONS})
        if st.session_state.filter_location not in choices:
            st.session_state.filter_location = FILTER_ALL
        st.session_state._filter_location = st.session_state.filter_location
        st.selectbox(tr(language, "location"), choices, key="_filter_location",
                     format_func=lambda code: tr(language, "all_locations") if code == FILTER_ALL else region_label(code, language),
                     on_change=save_widget_value, args=("filter_location",))
        if st.session_state.filter_location != FILTER_ALL:
            filtered = filtered[filtered["Region_Codes"].map(lambda codes: st.session_state.filter_location in str(codes).split(";"))]
    st.caption(tr(language, "filtered_count", count=len(filtered), total=len(jobs)))
    if filtered.empty:
        st.info(tr(language, "no_jobs"))
    else:
        pages = max(1, math.ceil(len(filtered) / 20))
        st.session_state.browse_page = min(st.session_state.browse_page, pages)
        st.session_state._browse_page = st.session_state.browse_page
        if pages > 1:
            st.selectbox(tr(language, "page_number"), list(range(1, pages + 1)), key="_browse_page",
                         on_change=save_widget_value, args=("browse_page",))
        page = st.session_state.browse_page
        st.caption(tr(language, "page_count", page=page, pages=pages, size=20))
        render_cards(filtered.iloc[(page - 1) * 20:page * 20], "job", EXPLORE, language)


def render_cv(engine: JobRecommenderSystem, jobs: pd.DataFrame, language: str) -> None:
    st.subheader(tr(language, "cv_upload_title"))
    st.write(tr(language, "cv_upload_intro"))
    st.caption(tr(language, "cv_privacy"))
    # Chỉ thay cách hiển thị nút/instruction mặc định tiếng Anh của Streamlit.
    # Loại tệp và giới hạn luôn được kiểm tra lại trong ResumeDocumentReader.
    browse_label = tr(language, "cv_browse")
    st.markdown(f'''<style>
        [data-testid="stFileUploaderDropzoneInstructions"] {{display:none;}}
        [data-testid="stFileUploaderDropzone"] button:has(p) {{font-size:0;}}
        [data-testid="stFileUploaderDropzone"] button:has(p) > * {{display:none;}}
        [data-testid="stFileUploaderDropzone"] button:has(p)::after {{content:"{browse_label}";font-size:14px;}}
        </style>''', unsafe_allow_html=True)
    uploaded = st.file_uploader(tr(language, "cv_upload"),
                                type=["pdf", "docx", "png", "jpg", "jpeg", "webp", "tif", "tiff"],
                                key=f"cv_upload_{st.session_state.cv_upload_generation}",
                                on_change=reset_uploaded_analysis)
    st.caption(tr(language, "cv_upload_hint"))
    if st.button(tr(language, "cv_read"), key="read_cv", disabled=uploaded is None):
        with st.spinner(tr(language, "cv_reading")):
            try:
                document = ResumeDocumentReader().read(uploaded.getvalue(), uploaded.name)
                profile = ResumeAnalyzer().analyze(document.text, ocr=document.used_ocr)
                st.session_state.cv_text = document.text
                st.session_state.cv_document = document
                st.session_state.cv_profile = profile
                st.session_state.cv_location = profile.location_candidates[0] if profile.location_candidates else FILTER_ALL
                st.session_state.cv_upload_notice = None
                invalidate_cv()
            except CVReadError as exc:
                st.session_state.cv_upload_notice = exc.code
                st.session_state.cv_text = ""
                st.session_state.cv_profile = None
                st.session_state.cv_document = None
                invalidate_cv()
    if st.session_state.cv_upload_notice:
        st.warning(tr(language, st.session_state.cv_upload_notice))
    with st.expander(tr(language, "cv_try_sample")):
        samples = sample_resumes(language)
        columns = st.columns(3)
        labels = [tr(language, key) for key in ("sample_data", "sample_backend", "sample_ai")]
        for column, (cv_id, sample), label in zip(columns, samples.items(), labels):
            with column:
                st.button(label, key=f"sample_{cv_id}", use_container_width=True,
                          on_click=set_cv, args=(sample["text"],), help=tr(language, "sample_help"))
    document = st.session_state.cv_document
    if document is not None:
        st.success(tr(language, "cv_read_done_word" if document.format == "docx" else "cv_read_done", pages=document.page_count))
        if document.used_ocr:
            st.info(tr(language, "cv_ocr_review"))
    profile = st.session_state.cv_profile
    if profile is not None:
        roles = [role[1 if language == "vi" else 2] for role in ROLES if role[0] in profile.role_codes]
        st.write(f"**{tr(language, 'cv_role')}:** " + (", ".join(roles) or tr(language, "cv_not_identified")))
        st.write(f"**{tr(language, 'cv_skills')}:** " + (", ".join(profile.skills) or tr(language, "cv_not_identified")))
        if profile.experience_years is not None:
            st.caption(tr(language,'cv_experience_detected',years=f'{profile.experience_years:g}'))
        if profile.location_candidates:
            st.info(tr(language, "cv_location_hint", locations=", ".join(region_label(code, language) for code in profile.location_candidates)))
        else:
            st.caption(tr(language, "cv_location_missing"))
    with st.expander(tr(language, "cv_review")):
        st.session_state._cv_text = st.session_state.cv_text
        st.text_area(tr(language, "cv_content"), height=220, max_chars=60000, key="_cv_text",
                     placeholder=tr(language, "cv_placeholder"),
                     on_change=save_widget_value, args=("cv_text", True))
    if "Region_Codes" in jobs:
        st.session_state._cv_location = st.session_state.cv_location
        st.selectbox(tr(language, "cv_work_location"), [FILTER_ALL] + list(REGIONS), key="_cv_location",
                     format_func=lambda code: tr(language, "all_locations") if code == FILTER_ALL else region_label(code, language),
                     on_change=save_widget_value, args=("cv_location", True))
    count = top_n_widget(tr(language, "cv_count"), "cv_top_n", len(jobs), reset_cv=True)
    submit, clear = st.columns([2, 1])
    with clear:
        st.button(tr(language, "clear_cv"), key="clear_cv", on_click=set_cv, args=("",), use_container_width=True)
    with submit:
        clicked = st.button(tr(language, "find_matches"), key="match_cv", type="primary", use_container_width=True)
    st.caption(tr(language, "cv_match_help"))
    if clicked:
        invalidate_cv()
        if not st.session_state.cv_text.strip():
            st.session_state.cv_notice = "cv_empty"
        else:
            with st.spinner(tr(language, "cv_loading")):
                try:
                    # Chặn cảnh báo vocabulary rỗng đã biết; bảng rỗng có thông báo riêng.
                    with warnings.catch_warnings():
                        warnings.filterwarnings("ignore", message="CV không có từ thuộc vocabulary TF-IDF.*")
                        region = None if st.session_state.cv_location == FILTER_ALL or "Region_Codes" not in jobs else st.session_state.cv_location
                        st.session_state.cv_results = engine.match_cv_to_jobs(st.session_state.cv_text, count,
                                                                              location=region, profile=st.session_state.cv_profile)
                except Exception:
                    # Không in exception/CV ra log hoặc UI vì có thể chứa nội dung người dùng.
                    st.session_state.cv_notice = "cv_error"
    if st.session_state.cv_notice:
        st.warning(tr(language, st.session_state.cv_notice))
    results = st.session_state.cv_results
    if results is not None:
        if isinstance(engine,HybridJobRecommenderSystem) and engine.semantic_status=='unavailable':
            st.info(tr(language,'hybrid_fallback'))
        if results.empty:
            region = st.session_state.cv_location
            no_region_jobs = region != FILTER_ALL and "Region_Codes" in jobs and not jobs["Region_Codes"].map(lambda codes: region in str(codes).split(";")).any()
            st.info(tr(language, "cv_region_empty" if no_region_jobs else "cv_no_matches"))
        else:
            st.success(tr(language, "cv_found", count=len(results)))
            render_cards(results, "match", MATCH, language)


def main() -> None:
    # Tương thích phiên đang mở bằng bản cũ. State mới dùng mã, không dùng nhãn.
    st.session_state.dataset = {"Tiếng Việt": "vi", "Tiếng Anh": "en"}.get(
        st.session_state.get("dataset", "vi"), st.session_state.get("dataset", "vi"))
    # Gửi lại giá trị nội bộ để widget đang mở cập nhật cả lựa chọn khi nhãn
    # format_func đổi ngôn ngữ; tránh giữ nhãn Việt cũ trong radio tiếng Anh.
    current_page = st.session_state.get("page")
    if current_page == "Tìm việc theo CV":
        current_page = MATCH
    st.session_state.page = current_page if current_page in (EXPLORE, MATCH) else EXPLORE
    current_backend = st.session_state.get("backend")
    st.session_state.backend = current_backend if current_backend in ("tfidf", "sentence-transformers", "hybrid") else "tfidf"
    language = st.session_state.dataset
    st.set_page_config(page_title=tr(language, "page_title"), page_icon="💼", layout="wide")
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    initialize_state()
    with st.sidebar:
        st.markdown(f"### 💼 {tr(language, 'brand')}")
        st.caption(tr(language, "tagline"))
        st.selectbox(tr(language, "language"), ["vi", "en"], key="dataset",
                     format_func=lambda value: tr(language, f"language_{value}"))
        path = dataset_path(language)
        with st.expander(tr(language, "advanced"), expanded=True):
            st.caption(tr(language, "method_intro"))
            backend = st.radio(tr(language, "method"), ["tfidf", "sentence-transformers","hybrid"], key="backend",
                               format_func=lambda value: tr(language, {"tfidf":"tfidf","sentence-transformers":"semantic","hybrid":"hybrid"}[value]))
            st.caption(tr(language, {"tfidf":"keyword_summary","sentence-transformers":"semantic_summary","hybrid":"hybrid_summary"}[backend]))
            if backend == "sentence-transformers":
                st.info(tr(language, "semantic_help"))
            # Giải thích dài ở hộp riêng có nhiều chiều ngang hơn sidebar,
            # giúp người dùng đọc ví dụ mà không phải cuộn qua một khối chữ dài.
            with st.popover(tr(language, "method_guide"), use_container_width=True):
                st.markdown(tr(language, "keyword_description"))
                st.caption(tr(language, "keyword_example"))
                st.markdown(tr(language, "semantic_description"))
                st.caption(tr(language, "semantic_example"))
                st.markdown('**'+tr(language,'hybrid')+'**')
                st.caption(tr(language,'hybrid_summary'))
                st.info(tr(language, "method_scope"))
            st.caption(tr(language, "method_change"))
        is_catalog = path.name == "jobs_catalog.csv"
        st.info(tr(language, "catalog_notice" if is_catalog else "demo"))
    try:
        csv_content = path.read_bytes()
        context = (language, backend, sha256(csv_content).hexdigest())
        previous_context = st.session_state.get("data_context")
        if previous_context != context:
            reset_filters()
            # Đổi cách so sánh chỉ làm mất hiệu lực kết quả cũ, không buộc
            # người dùng nhập lại CV. Đổi ngôn ngữ vẫn bắt đầu bằng CV trống.
            if previous_context is None or previous_context[0] != language:
                set_cv("")
            else:
                invalidate_cv()
            st.session_state.selected_job_id = None
            st.session_state.data_context = context
        with st.spinner(tr(language, "loading_semantic" if backend == "sentence-transformers" else "loading")):
            engine = get_recommender_engine(csv_content, backend, language=language)
        if backend=='hybrid' and engine.semantic_status=='unavailable':
            st.info(tr(language,'hybrid_fallback'))
    except FileNotFoundError:
        st.error(tr(language, "missing_data"))
        return
    except Exception:
        st.error(tr(language, "load_error"))
        if backend == "sentence-transformers":
            st.button(tr(language, "keyword_recovery"), key="recover_keyword",
                      on_click=use_keyword_matching, type="primary")
        return

    jobs = engine.jobs
    st.markdown(
        f'<div class="hero-box"><div class="hero-eyebrow">{tr(language, "eyebrow")}</div>'
        f'<h1>{tr(language, "hero_title")}</h1>'
        f'<p>{tr(language, "hero_description")}</p>'
        f'<div class="hero-badges"><span class="hero-pill">{tr(language, "catalog_badge" if is_catalog else "job_count", count=len(jobs))}</span>'
        f'<span class="hero-pill">{tr(language, "domain_count", count=jobs["Domain"].nunique())}</span>'
        f'<span class="hero-pill">{tr(language, "hero_badge")}</span></div></div>', unsafe_allow_html=True)
    page = st.radio(tr(language, "navigation"), [EXPLORE, MATCH], horizontal=True,
                    key="page", label_visibility="collapsed", format_func=lambda value: tr(language, value))
    if is_catalog and language == "en":
        st.caption(tr(language, "catalog_english"))
    if page == EXPLORE:
        render_explore(engine, jobs, language)
    elif page == MATCH:
        render_cv(engine, jobs, language)
    st.divider()
    st.caption(tr(language, "catalog_notice" if is_catalog else "footer"))


if __name__ == "__main__":
    main()
