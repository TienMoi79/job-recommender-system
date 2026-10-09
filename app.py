"""Giao diện Streamlit kết nối trực tiếp với JobRecommenderSystem.

Chạy: python -m streamlit run app.py
Cache chỉ chứa engine/dữ liệu việc làm. CV và kết quả chỉ ở RAM của từng phiên.
"""
from __future__ import annotations

from hashlib import sha256
from io import BytesIO
from pathlib import Path
import warnings

import pandas as pd
import streamlit as st

from job_recommender import DEFAULT_MODEL, JobRecommenderSystem
from ui_helper import CUSTOM_CSS
from web_support import filter_jobs, job_card_html, sample_resumes

BASE_DIR = Path(__file__).resolve().parent
DATASETS = {"Tiếng Việt": ("vi", BASE_DIR / "data/jobs_vie.cvs"),
            "Tiếng Anh": ("en", BASE_DIR / "data/jobs.csv")}
EXPLORE, MATCH, ABOUT = "Khám phá việc làm", "Tìm việc theo CV", "Về đồ án"


@st.cache_resource(show_spinner=False, max_entries=4)
def get_recommender_engine(csv_content: bytes, backend: str,
                           model_name: str = DEFAULT_MODEL) -> JobRecommenderSystem:
    """Nội dung file nằm trong khóa cache: sửa CSV sẽ tự tạo lại engine.

    Không dùng đường dẫn làm khóa duy nhất, vì cùng đường dẫn có thể đã đổi dữ liệu.
    Không cache truy vấn hay CV của người dùng trong cache dùng chung.
    """
    jobs = pd.read_csv(BytesIO(csv_content), encoding="utf-8-sig", dtype={"Job_ID": str})
    return JobRecommenderSystem(jobs, backend=backend, model_name=model_name)


def initialize_state() -> None:
    defaults = {
        "page": EXPLORE, "selected_job_id": None, "detail_origin": EXPLORE,
        "filter_keyword": "", "filter_domain": "Tất cả", "filter_exp": "Tất cả",
        "cv_text": "", "cv_results": None, "cv_notice": None, "cv_top_n": 5,
        "similar_top_n": 5,
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
    if reset_cv:
        invalidate_cv()


def set_cv(text: str) -> None:
    st.session_state.cv_text = text
    invalidate_cv()


def reset_filters() -> None:
    st.session_state.filter_keyword = ""
    st.session_state.filter_domain = st.session_state.filter_exp = "Tất cả"


def open_job(job_id: str, origin: str) -> None:
    st.session_state.selected_job_id = job_id
    st.session_state.detail_origin = origin
    st.session_state.page = EXPLORE


def back_from_detail() -> None:
    st.session_state.selected_job_id = None
    st.session_state.page = st.session_state.detail_origin


def render_cards(jobs: pd.DataFrame, prefix: str, origin: str) -> None:
    # Từng hàng chứa hai thẻ giúp thứ tự xếp hạng trái -> phải rõ ràng.
    rows = list(jobs.iterrows())
    for start in range(0, len(rows), 2):
        columns = st.columns(2, gap="medium")
        for column, (_, row) in zip(columns, rows[start:start + 2]):
            with column:
                with st.container(border=True):
                    st.markdown(job_card_html(row), unsafe_allow_html=True)
                    st.button("Xem chi tiết", key=f"{prefix}_{row['Job_ID']}",
                              use_container_width=True, on_click=open_job,
                              args=(row["Job_ID"], origin))


def top_n_widget(label: str, key: str, count: int, *, reset_cv: bool = False) -> int:
    limit = max(1, min(10, count))
    st.session_state[key] = min(st.session_state[key], limit)
    st.session_state[f"_{key}"] = st.session_state[key]
    return int(st.number_input(label, min_value=1, max_value=limit, step=1,
                               key=f"_{key}", on_change=save_widget_value,
                               args=(key, reset_cv)))


def render_detail(engine: JobRecommenderSystem, jobs: pd.DataFrame) -> None:
    origin = st.session_state.detail_origin
    st.button("← Quay lại kết quả CV" if origin == MATCH else "← Quay lại danh sách",
              key="back_detail", on_click=back_from_detail)
    selected = jobs[jobs["Job_ID"] == st.session_state.selected_job_id]
    if selected.empty:
        st.warning("Việc làm này không còn trong danh mục. Hãy quay lại danh sách.")
        return
    row = selected.iloc[0]
    st.markdown(job_card_html(row, detail=True), unsafe_allow_html=True)
    st.subheader("Việc làm tương tự")
    st.caption("Xếp theo độ tương đồng nội dung. Điểm số không phải xác suất trúng tuyển.")
    if len(jobs) <= 1:
        st.info("Chưa có việc làm khác để gợi ý.")
        return
    count = top_n_widget("Số việc làm tương tự", "similar_top_n", len(jobs) - 1)
    try:
        similar = engine.recommend_similar_jobs(row["Job_ID"], top_n=count)
    except Exception:
        st.error("Chưa thể lấy gợi ý. Hãy thử lại hoặc chọn TF-IDF trong Cài đặt nâng cao.")
        return
    render_cards(similar, "similar", origin)


def render_explore(engine: JobRecommenderSystem, jobs: pd.DataFrame) -> None:
    if st.session_state.selected_job_id is not None:
        render_detail(engine, jobs)
        return
    st.subheader("Tìm cơ hội phù hợp với kỹ năng của bạn")
    search, domain, experience = st.columns([2, 1, 1])
    domains = ["Tất cả"] + sorted(jobs["Domain"].unique())
    experiences = ["Tất cả"] + [f"{v:g} năm" for v in sorted(jobs["Experience_Years"].unique())]
    if st.session_state.filter_domain not in domains:
        st.session_state.filter_domain = "Tất cả"
    if st.session_state.filter_exp not in experiences:
        st.session_state.filter_exp = "Tất cả"
    for key in ("filter_keyword", "filter_domain", "filter_exp"):
        st.session_state[f"_{key}"] = st.session_state[key]
    with search:
        st.text_input("Chức danh hoặc kỹ năng", placeholder="Python, SQL, phân tích dữ liệu...",
                      key="_filter_keyword", on_change=save_widget_value, args=("filter_keyword",))
    with domain:
        st.selectbox("Lĩnh vực", domains, key="_filter_domain",
                     on_change=save_widget_value, args=("filter_domain",))
    with experience:
        st.selectbox("Kinh nghiệm yêu cầu", experiences, key="_filter_exp",
                     on_change=save_widget_value, args=("filter_exp",))
    st.button("Xóa bộ lọc", key="reset_filters", on_click=reset_filters)
    filtered = filter_jobs(jobs, st.session_state.filter_keyword,
                           st.session_state.filter_domain, st.session_state.filter_exp)
    st.caption(f"Hiển thị {len(filtered)} / {len(jobs)} việc làm · Có thể tìm kiếm không dấu")
    if filtered.empty:
        st.info("Không tìm thấy việc làm phù hợp. Hãy đổi từ khóa hoặc xóa bộ lọc.")
    else:
        render_cards(filtered, "job", EXPLORE)


def render_cv(engine: JobRecommenderSystem, jobs: pd.DataFrame, language: str) -> None:
    st.subheader("Tìm việc từ kinh nghiệm của bạn")
    st.write("Dán nội dung CV để khám phá những công việc có kỹ năng và mô tả gần nhất.")
    st.caption("CV chỉ được giữ trong bộ nhớ của phiên hiện tại; không ghi vào file hoặc nhật ký ứng dụng.")
    samples = sample_resumes(language)
    columns = st.columns(3)
    labels = ["Phân tích dữ liệu", "Backend Python", "AI / NLP"]
    for column, (cv_id, sample), label in zip(columns, samples.items(), labels):
        with column:
            st.button(label, key=f"sample_{cv_id}", use_container_width=True,
                      on_click=set_cv, args=(sample["text"],), help="Điền CV mẫu")
    st.session_state._cv_text = st.session_state.cv_text
    st.text_area("Nội dung CV", height=220, max_chars=30000, key="_cv_text",
                 placeholder="Kinh nghiệm làm việc, kỹ năng, dự án và công nghệ bạn đã sử dụng...",
                 on_change=save_widget_value, args=("cv_text", True))
    count = top_n_widget("Số việc làm muốn xem", "cv_top_n", len(jobs), reset_cv=True)
    submit, clear = st.columns([2, 1])
    with clear:
        st.button("Xóa CV", key="clear_cv", on_click=set_cv, args=("",), use_container_width=True)
    with submit:
        clicked = st.button("Tìm việc phù hợp", key="match_cv", type="primary", use_container_width=True)
    st.caption("Điểm tương đồng nội dung không phải xác suất trúng tuyển. Yêu cầu kinh nghiệm chưa được lọc bắt buộc.")
    if clicked:
        invalidate_cv()
        if not st.session_state.cv_text.strip():
            st.session_state.cv_notice = "Vui lòng nhập hoặc dán nội dung CV, hoặc chọn một CV mẫu."
        else:
            with st.spinner("Đang so sánh CV với các việc làm..."):
                try:
                    # Chặn cảnh báo vocabulary rỗng đã biết; bảng rỗng có thông báo riêng.
                    with warnings.catch_warnings():
                        warnings.filterwarnings("ignore", message="CV không có từ thuộc vocabulary TF-IDF.*")
                        st.session_state.cv_results = engine.match_cv_to_jobs(st.session_state.cv_text, count)
                except Exception:
                    # Không in exception/CV ra log hoặc UI vì có thể chứa nội dung người dùng.
                    st.session_state.cv_notice = "Chưa xử lý được CV. Hãy thử lại hoặc chọn TF-IDF trong Cài đặt nâng cao."
    if st.session_state.cv_notice:
        st.warning(st.session_state.cv_notice)
    results = st.session_state.cv_results
    if results is not None:
        if results.empty:
            st.info("Chưa đủ từ khóa trùng khớp để gợi ý. Hãy bổ sung kỹ năng và kinh nghiệm chuyên môn vào CV.")
        else:
            st.success(f"Đã tìm thấy {len(results)} việc làm có nội dung gần nhất với CV.")
            render_cards(results, "match", MATCH)


def render_about() -> None:
    st.subheader("Hệ gợi ý việc làm trực tuyến")
    st.write("Đồ án môn Trí tuệ nhân tạo ứng dụng. Tin tuyển dụng và CV mẫu là dữ liệu giả lập.")
    st.markdown("""
    **Luồng xử lý:** đọc CSV → chuẩn hóa văn bản → biểu diễn vector → cosine similarity → xếp hạng.

    - **TF-IDF:** so khớp từ và cụm từ, chạy offline sau khi cài thư viện.
    - **Sentence Transformers:** dùng mô hình pretrained đa ngôn ngữ; cần tải trọng số lần đầu.
    - **Việc làm tương tự:** gọi `recommend_similar_jobs`, loại công việc đang xem.
    - **Ghép CV:** gọi `match_cv_to_jobs`, xử lý toàn văn CV trong cùng không gian vector.

    Điểm cosine là độ tương đồng nội dung, không phải đánh giá năng lực hay xác suất trúng tuyển.
    Hệ thống chưa lọc cứng theo kinh nghiệm và chưa đặt ngưỡng chấp nhận độ phù hợp.
    Dữ liệu nhỏ chỉ phục vụ minh họa; chưa có evaluation metrics trên dữ liệu gán nhãn (Giai đoạn 3).

    CV và kết quả ở bộ nhớ từng phiên; nút **Xóa CV** xóa cả nội dung và kết quả trong phiên đó.
    Giao diện gọi trực tiếp class Python, không cần API server riêng.
    """)


def main() -> None:
    st.set_page_config(page_title="Việc làm phù hợp | AI Job Finder", page_icon="💼", layout="wide")
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    initialize_state()
    with st.sidebar:
        st.markdown("### 💼 AI Job Finder")
        st.caption("Từ kỹ năng đến cơ hội mới")
        dataset = st.selectbox("Ngôn ngữ việc làm", list(DATASETS), key="dataset")
        language, path = DATASETS[dataset]
        with st.expander("Cài đặt nâng cao"):
            backend = st.radio("Phương pháp gợi ý", ["tfidf", "sentence-transformers"], key="backend",
                               format_func=lambda x: "TF-IDF · nhẹ, offline" if x == "tfidf" else "Sentence Transformers · ngữ nghĩa")
            st.caption("Semantic cần requirements-semantic.txt và tải trọng số mô hình lần đầu.")
        st.info("Bản demo học tập · Dữ liệu giả lập")
    try:
        csv_content = path.read_bytes()
        context = (dataset, backend, sha256(csv_content).hexdigest())
        if st.session_state.get("data_context") != context:
            reset_filters()
            set_cv("")
            st.session_state.selected_job_id = None
            st.session_state.data_context = context
        with st.spinner("Đang chuẩn bị danh mục việc làm..."):
            engine = get_recommender_engine(csv_content, backend)
    except FileNotFoundError:
        st.error("Thiếu dữ liệu việc làm. Hãy khôi phục file trong thư mục data hoặc chọn ngôn ngữ khác.")
        return
    except Exception:
        st.error("Không thể nạp dữ liệu hoặc mô hình. Hãy chọn TF-IDF để chạy nhẹ. Nếu dùng semantic, kiểm tra thư viện và kết nối tải mô hình.")
        return

    jobs = engine.jobs
    st.markdown(
        '<div class="hero-box"><div class="hero-eyebrow">KHÁM PHÁ CƠ HỘI TRONG NGÀNH IT</div>'
        '<h1>Kỹ năng của bạn.<br>Cơ hội phù hợp.</h1>'
        '<p>Khám phá việc làm, tìm những vị trí tương tự và kết nối kinh nghiệm của bạn với cơ hội mới.</p>'
        f'<div class="hero-badges"><span class="hero-pill">{len(jobs)} việc làm mẫu</span>'
        f'<span class="hero-pill">{jobs["Domain"].nunique()} lĩnh vực</span>'
        '<span class="hero-pill">Gợi ý từ nội dung thực tế của tin</span></div></div>', unsafe_allow_html=True)
    page = st.radio("Điều hướng", [EXPLORE, MATCH, ABOUT], horizontal=True,
                    key="page", label_visibility="collapsed")
    if page == EXPLORE:
        render_explore(engine, jobs)
    elif page == MATCH:
        render_cv(engine, jobs, language)
    else:
        render_about()
    st.divider()
    st.caption("Đồ án Trí tuệ nhân tạo ứng dụng · Hệ gợi ý việc làm trực tuyến · Dữ liệu giả lập")


if __name__ == "__main__":
    main()
