"""Đóng gói phần cài đặt và demo: trích code thật, giữ nguyên ảnh chụp UI.

Chạy sau khi chụp ảnh vào outputs/implementation_demo_20261114/images.
Không chạy ứng dụng, không tạo điểm giả, không truy cập hồ sơ người dùng.
Các file code .txt là trích đoạn để đưa vào báo cáo, không phải module độc lập.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import html
import inspect
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/implementation_demo_20261114'
PARTS: list[str] = []
EXCERPTS: list[dict] = []
REF = ''


def add(text):
    PARTS.append(inspect.cleandoc(text).strip() + '\n')


def excerpt(path, label, *, symbol=None, js=None, lines=None, language='python'):
    """Tìm vị trí theo AST Python hoặc biên hàm JS; không viết lại code."""
    source = (ROOT / path).read_text(encoding='utf-8-sig')
    source_lines = source.splitlines()
    if symbol:
        body = ast.parse(source).body
        for name in symbol.split('.'):
            node = next(n for n in body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.name == name)
            body = getattr(node, 'body', [])
        start = min([node.lineno] + [n.lineno for n in getattr(node, 'decorator_list', [])])
        end = node.end_lineno
    elif js:
        starts = list(re.finditer(r'^(?:async )?function (\w+)\(', source, re.M))
        index = next(i for i, match in enumerate(starts) if match.group(1) == js)
        begin = starts[index].start()
        finish = starts[index + 1].start() if index + 1 < len(starts) else len(source)
        start = source[:begin].count('\n') + 1
        end = source[:finish].count('\n')
        while end >= start and not source_lines[end - 1].strip():
            end -= 1
    else:
        start, end = lines or (1, len(source_lines))
    code = '\n'.join(source_lines[start - 1:end])
    name = f'{len(EXCERPTS)+1:02d}_{label}.txt'
    (OUT / 'code' / name).write_text(code + '\n', encoding='utf-8')
    EXCERPTS.append({'file': path, 'start_line': start, 'end_line': end,
                     'symbol': symbol or js, 'excerpt': 'code/' + name})
    url = f'https://github.com/TienMoi79/job-recommender-system/blob/{REF}/{path}#L{start}-L{end}'
    add(f'Nguồn: [{path}, dòng {start}–{end}]({url}). Bản trích riêng: [{name}](code/{name}).\n\n```{language}\n{code}\n```')


SHOTS = [
    ('Anh_01_Trang_chu', 'Giao diện trang chủ hệ thống JobVista', 'Trang chủ hiển thị 7.050 tin, 3.594 công ty và 24 khu vực chính. Thẻ Backend Developer trong banner là minh họa giao diện, không phải một kết quả xếp hạng.'),
    ('Anh_02_Ca_nhan_hoa_trang_chu', 'Khối gợi ý cá nhân hóa trên trang chủ', 'Hồ sơ CV07 được tự lưu trên trình duyệt; khu vực Cần Thơ và 3 năm kinh nghiệm được giữ lại cho các lần gợi ý sau.'),
    ('Anh_03_Danh_sach_va_bo_loc', 'Danh sách việc làm và bộ lọc', 'Khi đóng chi tiết, màn hình rộng có bốn thẻ mỗi hàng. Bộ lọc gồm địa điểm, lĩnh vực và kinh nghiệm; phân trang tám tin mỗi trang.'),
    ('Anh_04_Chi_tiet_cong_viec', 'Bảng chi tiết tin tuyển dụng', 'Nhấp Fullstack Java Developer để mở chi tiết: lương 12–20 triệu và tối thiểu 2 năm. Nhấp lại cùng tin, nút X hoặc ESC để đóng.'),
    ('Anh_05_Goi_y_cong_viec_tuong_tu', 'Gợi ý công việc tương tự theo nội dung', 'Cuộn trong bảng chi tiết đến Cơ hội tương tự. Hệ thống trả về các tin gần nội dung với tin đang xem, loại chính tin đó và nhóm gần trùng.'),
    ('Anh_06_Tai_CV', 'Giao diện tải tệp CV', 'Tại Tìm việc với CV, chọn PDF, Word .docx hoặc ảnh. Nút đọc chỉ bật sau khi chọn một tệp hợp lệ.'),
    ('Anh_07_Ket_qua_phan_tich_CV', 'Kết quả nhận diện kỹ năng, nơi ở và kinh nghiệm', 'CV07 PDF được đọc thực tế: tám kỹ năng, nơi muốn làm Cần Thơ, nơi ở Cần Thơ, ba năm kinh nghiệm. Người dùng có thể xác nhận hoặc sửa.'),
    ('Anh_08_Xem_sua_noi_dung_CV', 'Kiểm tra và chỉnh sửa văn bản CV đã đọc', 'Mở Xem và sửa nội dung đã đọc để đối chiếu văn bản trước khi bấm tìm việc. Hồ sơ trong ảnh hoàn toàn là dữ liệu giả lập.'),
    ('Anh_09_Goi_y_can_bang', 'Khuyến nghị kết hợp chuyên môn và khoảng cách', 'Nhóm kết hợp được đưa lên đầu: chuyên môn CV 0,671, điểm gần 1,000, điểm cân bằng 0,770 ở tin đứng đầu trong lần demo này.'),
    ('Anh_10_Doi_chieu_chuyen_mon_va_gan_nha', 'Đối chiếu chuyên môn tốt nhất và việc gần nhà', 'Tin đứng đầu theo chuyên môn ở Hà Nội đạt 0,801 nhưng cách vùng Cần Thơ khoảng 1.222 km; tin gần nơi ở đạt 0,671. Đây là đối chiếu toàn quốc, tách khỏi danh sách chính.'),
    ('Anh_11_Ket_qua_CV_theo_khu_vuc', 'Danh sách công việc phù hợp CV tại khu vực đã chọn', 'CV07 với nơi muốn làm Cần Thơ trả bốn tin trong lần demo. Số lượng không bị ép đủ 24 nếu không có đủ tin qua điều kiện.'),
    ('Anh_12_Giai_thich_diem_CV', 'Giải thích điểm chuyên môn và kỹ năng trùng', 'Mở tin Junior/ Senior DevOps Engineer: sáu trong mười hai kỹ năng của tin đã thấy trong CV. Hệ thống hiển thị kỹ năng chưa thấy và từng thành phần điểm.'),
    ('Anh_13_Rating_nhu_cau_nganh', 'Giải thích rating nhu cầu nghề nghiệp', 'Ảnh tiếp nối phần giải thích điểm. Có hai trình duyệt tham gia trong dữ liệu demo, chưa đủ năm nên rating chưa tác động thứ hạng; không tạo lượt giả để làm đẹp ảnh.'),
    ('Anh_14_Viec_da_luu', 'Chức năng lưu công việc yêu thích', 'Bấm biểu tượng lưu một tin rồi vào Việc đã lưu. Danh sách chỉ lưu trong trình duyệt; tin thử đã được bỏ lưu sau khi chụp để khôi phục trạng thái ban đầu.'),
    ('Anh_15_Tim_kiem_va_loc_khu_vuc', 'Tìm kiếm DevOps kết hợp bộ lọc Hồ Chí Minh', 'Gõ DevOps, chọn Hồ Chí Minh, bấm Tìm việc: 72 tin phù hợp bộ lọc trong catalog hiện tại. Đây là kết quả tìm kiếm từ khóa, không phải 72 khuyến nghị CV.'),
    ('Anh_16_Danh_sach_ca_nhan_hoa', 'Xem toàn bộ danh sách gợi ý cá nhân', 'Từ khối Phù hợp với bạn, bấm Xem tất cả gợi ý. Hồ sơ Cần Thơ vẫn được ưu tiên; một lượt tìm ở Hồ Chí Minh không tự thay nơi muốn làm của CV.'),
]


def image(index):
    stem, caption, explanation = SHOTS[index - 1]
    add(f'![Ảnh {index:02d}. {caption}](images/{stem}.jpg)\n\n**Ảnh {index:02d}. {caption}.** {explanation}')


def build():
    add(f'''# JobVista — Cài đặt hệ thống và demo chức năng

    Tài liệu cung cấp đúng 10 mục theo yêu cầu làm báo cáo. Ngày chụp: 14/11/2026.
    Mã nguồn đối chiếu: `{REF}`; ứng dụng thật tại `http://127.0.0.1:8000/`.
    Các đoạn code dưới đây được trích nguyên văn từ project, có đường dẫn và số dòng để kiểm tra.
    Chúng cần các import và class liên quan trong repo; không chạy riêng các file trích `.txt`.
    Phần giải thích bên ngoài code dùng để biên tập vào Word. Ảnh là ảnh chụp trình duyệt thật,
    không dựng lại giao diện, không chỉnh sửa điểm kết quả. CV demo là hồ sơ tổng hợp giả lập CV07.

    Cách dùng: đọc `CAI_DAT_VA_DEMO_JOBVISTA.md`, hoặc mở bản HTML cùng tên để xem code và ảnh.
    Khi chèn Word, dùng Insert → Pictures với ảnh gốc trong `images`; tự đánh số hình theo chương
    của báo cáo. Các ảnh 01–16 ở đây chưa gán số chương để tránh trùng Hình 3.1–3.7 đã cung cấp.
    ''')
    add('''## 1. Công cụ và môi trường cài đặt

    Hệ thống được phát triển bằng Python theo hướng đối tượng, giao diện HTML/CSS/JavaScript
    và Backend FastAPI. VS Code là môi trường lập trình, Jupyter Notebook phục vụ trình bày
    và thực nghiệm thuật toán. Python thực tế của môi trường chụp demo là 3.12.5; repo yêu cầu
    Python từ 3.10. Không cần Node.js để chạy web; Node chỉ dùng cho kiểm thử JavaScript.

    | Thành phần | Thư viện/công cụ và vai trò |
    |---|---|
    | Xử lý dữ liệu | pandas, NumPy: chuẩn hóa, lọc, tổng hợp và xử lý dữ liệu theo batch |
    | Biểu diễn nội dung | scikit-learn TF-IDF; sentence-transformers cho embedding ngữ nghĩa |
    | API | FastAPI, Pydantic, Uvicorn |
    | Đọc tệp CV | pypdf, pypdfium2, python-docx, Pillow, RapidOCR, ONNX Runtime |
    | Lưu trữ | CSV catalog; JSON cấu hình; SQLite nhu cầu nghề; localStorage hồ sơ và sở thích |
    | Quản lý mã nguồn | Git/GitHub |

    Lệnh PowerShell khi tải project về máy mới:

    ```powershell
    git clone --branch main https://github.com/TienMoi79/job-recommender-system.git
    cd job-recommender-system
    python -m venv .venv
    .\\.venv\\Scripts\\python.exe -m pip install -r requirements-preview.txt -r requirements-semantic.txt
    .\\.venv\\Scripts\\python.exe web_preview.py
    ```

    Mở `http://127.0.0.1:8000/`. Nếu đang ở đúng thư mục và đã có môi trường, chỉ cần lệnh cuối.
    Dừng server bằng Ctrl+C. Lần đầu tải mô hình cần Internet và tạo embedding có thể mất vài phút.
    Không dùng lệnh Streamlit cũ. Các file requirements sau là khai báo khoảng phiên bản,
    không phải bản khóa toàn bộ dependency chính xác.
    ''')
    excerpt('requirements-preview.txt', 'requirements_web', language='text')
    excerpt('requirements-semantic.txt', 'requirements_semantic', language='text')
    add('''Cài và mở notebook để thuyết trình thuật toán:

    ```powershell
    .\\.venv\\Scripts\\python.exe -m pip install -r requirements-notebook.txt
    .\\.venv\\Scripts\\python.exe -m notebook
    ```

    Mở `job_recommender_notebook.ipynb` hoặc `lab3_jobvista.ipynb`, chọn kernel của `.venv`.
    Notebook và giao diện web dùng chung các module xử lý của đồ án.
    ''')
    add('''## 2. Cài đặt giao diện người dùng (Frontend)

    Frontend dùng JavaScript thuần để dựng giao diện và cập nhật trạng thái mà không tải lại trang.
    `index.html` nạp CSS, module lưu trữ cá nhân và logic giao diện; cùng server FastAPI phục vụ
    các tài nguyên tại `/assets`. Giao diện gồm trang khám phá, tìm việc theo CV và việc đã lưu.
    Có chuyển Việt/Anh, bộ lọc, phân trang, bảng chi tiết bật/tắt và bố cục thích ứng màn hình.
    Nội dung bản địa hóa của các tin tiếng Anh có thể là bản tóm tắt theo quy tắc, không phải
    bản dịch đầy đủ bằng một mô hình dịch.

    Khung HTML thực tế:
    ''')
    excerpt('web_ui/index.html', 'khung_frontend', language='html')
    add('Bộ lọc được dựng từ dữ liệu catalog và từ điển giao diện `t(...)`; `escape(...)` bảo vệ nội dung khi ghép vào HTML:')
    excerpt('web_ui/app.js', 'frontend_bo_loc', js='filters', language='javascript')
    add('Hàm chuyển trạng thái mở/đóng chi tiết công việc:')
    excerpt('web_ui/app.js', 'frontend_bat_tat_chi_tiet', js='toggleJobDetails', language='javascript')
    add('''## 3. Cài đặt Backend xử lý yêu cầu

    Backend nhận dữ liệu, kiểm tra đầu vào, gọi các class nghiệp vụ rồi trả JSON.
    `CatalogService` nạp CSV bằng pandas, chuẩn bị dữ liệu theo ngôn ngữ và khởi tạo engine.
    Catalog/embedding tin công khai có thể được cache dùng chung; văn bản CV truy vấn không
    được đưa vào cache embedding công khai. Server phục vụ cả HTML và API trên cổng 8000.

    | API | Mục đích |
    |---|---|
    | GET `/api/catalog` | Dữ liệu khám phá và các lựa chọn bộ lọc |
    | GET `/api/jobs/{job_id}` | Chi tiết và gợi ý công việc tương tự |
    | POST `/api/cv/read` | Đọc nội dung tệp CV, trả văn bản và hồ sơ nhận diện |
    | POST `/api/cv/match` | Ghép CV, đối chiếu chuyên môn và khoảng cách |
    | POST `/api/recommendations` | Cá nhân hóa từ hồ sơ CV và mối quan tâm |
    | GET `/api/demand` | Thống kê rating nhu cầu nghề |

    Lớp dịch vụ nạp catalog:
    ''')
    excerpt('web_preview.py', 'khoi_tao_catalog', symbol='CatalogService.__init__')
    add('Pydantic kiểm tra độ dài CV, giới hạn số kết quả, năm kinh nghiệm và cấu trúc request trước khi chạy engine:')
    excerpt('web_preview.py', 'request_kiem_tra_dau_vao', symbol='MatchRequest')
    add('Endpoint đọc CV nhận từng phần dữ liệu, chặn quá 15 MB và đưa tác vụ đọc/OCR sang thread pool:')
    excerpt('web_preview.py', 'api_doc_cv', symbol='read_cv')
    add('''## 4. Tích hợp các mô hình học máy và thuật toán gợi ý

    JobVista là **hệ gợi ý lai lấy nội dung làm chính**: kết hợp TF-IDF, embedding ngữ nghĩa,
    kỹ năng, vị trí nghề, lĩnh vực và kinh nghiệm. Các lớp quy tắc bổ sung cá nhân hóa,
    nhu cầu nghề và khoảng cách địa lý. Hiện không có lọc cộng tác bằng ma trận user–item,
    không huấn luyện lại mô hình ngôn ngữ từ 7.050 tin.

    TF-IDF được fit trên tin tuyển dụng, CV chỉ transform vào cùng không gian vector.
    Sentence Transformer dùng mô hình pretrained `paraphrase-multilingual-MiniLM-L12-v2`,
    embedding 384 chiều; chia văn bản dài thành các đoạn token, encode rồi trung bình và chuẩn hóa L2.
    Dot product của vector đã chuẩn hóa tương đương cosine similarity. Model dùng CPU;
    phiên bản trọng số được ghim trong `semantic_index.py`. Nếu model chưa sẵn sàng, hệ thống
    thông báo chế độ `hybrid-lexical`, bỏ thành phần ngữ nghĩa và chuẩn hóa lại trọng số.
    ''')
    excerpt('job_recommender.py', 'tfidf_vectorizer', symbol='TfidfTextVectorizer')
    excerpt('job_recommender.py', 'semantic_embedding', symbol='SentenceTransformerVectorizer.transform')
    excerpt('semantic_index.py', 'cosine_semantic_index', symbol='PublicSemanticIndex.similarity')
    add('''Trọng số mặc định: từ khóa 15%, ngữ nghĩa 25%, kỹ năng 30%, vị trí 15%, lĩnh vực 5%,
    kinh nghiệm 10%. Đây là tham số thử nghiệm, không phải xác suất trúng tuyển và không được
    suy ra là độ chính xác 100%. Thành phần thiếu bằng chứng được bỏ rồi chuẩn hóa lại.
    ''')
    excerpt('hybrid_recommender.py', 'trong_so_sau_thanh_phan', lines=(25,25))
    add('''## 5. Cài đặt chức năng đọc và phân tích CV ứng viên

    Chức năng gồm hai tầng: trích xuất văn bản từ tệp và phân tích văn bản thành hồ sơ.
    PDF có chữ dùng pypdf; trang PDF quét được render bằng pypdfium2 và OCR;
    ảnh dùng Pillow/RapidOCR; Word dùng python-docx. Giới hạn 15 MB, 20 trang và
    60.000 ký tự. Định dạng `.doc` cần đổi sang `.docx`; OCR có thể sai nên luôn cho người dùng kiểm tra.

    `ResumeAnalyzer` nhận diện theo từ điển kỹ năng, alias nhóm nghề, quy tắc số năm kinh nghiệm
    và địa danh. Nó ưu tiên vị trí mong muốn, tách dòng liên hệ khỏi văn bản so khớp chuyên môn.
    Đây chưa phải bộ phân tích cấu trúc CV bằng LLM. Nơi ở phục vụ khoảng cách được xử lý riêng
    với nơi muốn làm việc; người dùng xác nhận hai trường này trước khi gợi ý.
    ''')
    excerpt('cv_documents.py', 'doc_tep_cv_da_dinh_dang', symbol='ResumeDocumentReader.read')
    excerpt('resume_profile.py', 'phan_tich_ho_so_cv', symbol='ResumeAnalyzer.analyze')
    add('''Frontend gửi tệp gốc đến API nội bộ rồi nhận văn bản/hồ sơ. Sau khi đọc thành công,
    nội dung và lựa chọn được tự lưu trong localStorage của trình duyệt, không lưu tệp gốc.
    CV không được gửi đến dịch vụ AI/OCR bên ngoài. Nút Xóa hồ sơ giúp xóa dữ liệu trên trình duyệt.
    ''')
    excerpt('web_ui/app.js', 'frontend_goi_api_doc_cv', js='readCv', language='javascript')
    add('''## 6. Cài đặt chức năng gợi ý công việc tương tự (Job-to-Job Recommendation)

    Khi xem một tin, hệ thống lấy vector nội dung của tin làm truy vấn, tính cosine với
    catalog, kết hợp 50% TF-IDF và 50% semantic nếu model sẵn sàng; nếu chưa thì dùng lexical.
    Chính tin đang xem và nhóm tin gần trùng với nó bị loại. Danh sách được sắp điểm giảm dần,
    có xử lý đa dạng công ty. Đây là item-to-item dựa nội dung, không cần lịch sử tương tác
    của nhiều người dùng. API trả ba gợi ý để hiển thị trong bảng chi tiết.
    ''')
    excerpt('hybrid_recommender.py', 'job_to_job', symbol='HybridJobRecommenderSystem.recommend_similar_jobs')
    excerpt('web_preview.py', 'api_chi_tiet_va_tuong_tu', symbol='get_job')
    add('''## 7. Cài đặt chức năng gợi ý việc làm theo CV (CV-to-Job Recommendation)

    Từ hồ sơ đã đọc, engine tạo sáu thành phần điểm rồi cộng theo trọng số đang có bằng chứng.
    Điểm kỹ năng kết hợp độ phủ kỹ năng CV và độ phủ kỹ năng trong tin, giảm khi thiếu yêu cầu
    bắt buộc được nêu rõ. Kinh nghiệm thiếu không bị coi bằng 0; thiếu năm so với yêu cầu
    bị giảm điểm mềm. Engine kiểm tra mục tiêu nghề/stack, ngưỡng nội dung, địa điểm,
    giảm gần trùng và đa dạng công ty trước khi trả kết quả.

    Cần phân biệt: `score` là điểm chuyên môn từ engine; `personal_score` là điểm gợi ý
    sau các lớp sắp xếp phù hợp luồng. Badge trên thẻ dùng `personal_score` nếu có, nếu không
    dùng `score`. Ở lần demo rating chưa đủ mẫu nên hai điểm có thể bằng nhau.
    ''')
    excerpt('hybrid_recommender.py', 'cv_to_job', symbol='HybridJobRecommenderSystem.match_cv_to_jobs')
    add('Endpoint giữ danh sách chính theo nơi muốn làm, đồng thời chuẩn bị một pool toàn quốc riêng để đối chiếu ba góc nhìn:')
    excerpt('web_preview.py', 'api_ghep_cv', symbol='match_cv')
    add('''## 8. Cài đặt chức năng cá nhân hóa và gợi ý theo khoảng cách địa lý, chuyên môn

    **Cá nhân hóa:** web ghi nhớ ngầm các điều kiện tìm kiếm hợp lệ, không có bảng lịch sử tìm
    kiếm trên giao diện. Dữ liệu nằm trong trình duyệt, tối đa 20 điều kiện và 90 ngày;
    ảnh hưởng giảm với chu kỳ bán rã 14 ngày. Khi có CV và lịch sử hữu ích, điểm kết hợp
    85% nền CV và 15% mối quan tâm trên pool đã phù hợp. Nơi muốn làm trong CV vẫn là ràng buộc.
    Không có CV thì có thể gợi ý dựa mối quan tâm gần đây.
    ''')
    excerpt('interest_recommender.py', 'ca_nhan_hoa_tu_moi_quan_tam', symbol='SearchInterestRecommender.recommend')
    add('''**Rating nhu cầu vận dụng pandas/Lab 3:** mỗi mã trình duyệt chỉ đóng góp nguyện vọng
    mới nhất trong 30 ngày; nhiều nhóm nghề chia đều một lượt. pandas dùng to_numeric,
    drop_duplicates, explode, groupby và merge. R = 5 × nhu cầu nghề / N, C = 5/K, m = 5,
    WR = N/(N+m) × R + m/(N+m) × C. Khi có ít nhất năm trình duyệt, điểm gợi ý cuối
    kết hợp 90% nền hiện có với 10% WR/5. Đây là nhu cầu ẩn danh, không phải sao đánh giá
    chất lượng công việc, không phải số người đã xác minh. Chỉ rerank pool đúng chuyên môn.
    ''')
    excerpt('demand_rating.py', 'pandas_rating_nhu_cau', symbol='DemandRatingStore.aggregate')
    excerpt('demand_rating.py', 'rating_sap_xep_lai', symbol='DemandRatingStore.rerank')
    add('''**Chuyên môn và địa lý:** Haversine ước tính đường chim bay giữa các điểm đại diện
    thành phố, không tính quãng đường đi làm thực tế. Khi biết nơi ở và tọa độ tin,
    P = 1/(1+d/50), B = 0,7 × điểm chuyên môn CV + 0,3 × P.
    50 km là tham số giảm điểm, không phải bán kính loại tin. Nhóm cân bằng B được hiển thị
    trước hai nhóm chuyên môn tốt nhất/gần nơi ở nhất. Ba nhóm đối chiếu toàn quốc;
    danh sách chính bên dưới vẫn theo khu vực người dùng chọn. Không trộn rating vào B,
    không đổi điểm CV gốc. Thiếu nơi ở hoặc tọa độ thì không tự gán khoảng cách bằng 0.
    Cùng thành phố được ghi Cùng khu vực nơi ở, không khẳng định nhà sát công ty.
    ''')
    excerpt('job_proximity.py', 'haversine_khoang_cach', symbol='distance_km')
    excerpt('job_proximity.py', 'can_bang_chuyen_mon_khoang_cach', symbol='compare_options')
    add('''## 9. Giới thiệu hệ thống và kịch bản Demo

    JobVista hỗ trợ khám phá việc làm IT từ catalog công khai, so sánh tin tuyển dụng
    và tìm việc theo CV. Dữ liệu hiện gồm 7.050 tin đã chuẩn hóa, không phải 7.050 tin còn
    đang tuyển đã được xác minh. Thông tin nguồn và giấy phép nằm tại
    [DATA_SOURCE.md](https://github.com/TienMoi79/job-recommender-system/blob/main/data/DATA_SOURCE.md).

    Lời giới thiệu có thể đọc: “JobVista là hệ gợi ý việc làm lấy nội dung làm chính.
    Hệ thống đọc CV, đối chiếu kỹ năng và kinh nghiệm với tin tuyển dụng, sau đó giúp
    người dùng cân nhắc cả chuyên môn và nơi muốn làm. Các kết quả có giải thích để
    người dùng tự kiểm tra và quyết định.”
    ''')
    image(1)
    add('''Kịch bản trình diễn khoảng 7–10 phút:

    | Bước | Thao tác | Điểm cần giải thích | Ảnh |
    |---|---|---|---|
    | 1 | Mở trang chủ | Catalog 7.050 tin, 3.594 công ty, 24 vùng | 01 |
    | 2 | Gõ DevOps, chọn Hồ Chí Minh, tìm kiếm | Kết hợp từ khóa và bộ lọc, 72 tin trong lần chụp | 15 |
    | 3 | Đặt lại, mở Fullstack Java Developer | Chi tiết bật/tắt, lương và kinh nghiệm thống nhất | 03–04 |
    | 4 | Cuộn đến Cơ hội tương tự | Item-to-item dựa nội dung, ba gợi ý | 05 |
    | 5 | Tìm việc với CV, tải CV07 PDF | Đọc tệp thật; Word/ảnh có nhánh xử lý tương ứng | 06 |
    | 6 | Đọc và kiểm tra thông tin | Tám kỹ năng, Cần Thơ, ba năm; có thể chỉnh sửa | 07–08 |
    | 7 | Bấm Tìm công việc phù hợp | Nhóm cân bằng đứng đầu, giải thích 70/30 | 09 |
    | 8 | So sánh hai nhóm bên dưới | Chuyên môn tốt nhất có thể ở xa, việc gần nhà đạt ngưỡng | 10 |
    | 9 | Xem danh sách chính, mở một tin | Bốn việc Cần Thơ, lý do khớp và điểm thành phần | 11–13 |
    | 10 | Lưu một tin, về trang chủ | Việc đã lưu; hồ sơ được nhớ để cá nhân hóa | 14, 02, 16 |

    Tệp demo kèm theo: `CV_demo/CV07_devops_can_tho.pdf`, sao chép nguyên bản từ bộ CV giả lập
    của project. Có thể thử thêm ảnh và Word trong `data/sample_cvs` của repo.
    Kết quả/số thập phân có thể đổi theo lịch sử trình duyệt, số mẫu rating, trạng thái semantic
    và phiên bản catalog. Không khẳng định luôn phải giống hệt ảnh.
    ''')
    add('''## 10. Demo các chức năng chính của hệ thống JobVista

    Các ảnh dưới được chụp ngày 14/11/2026 ở viewport 1265 × 712, giữ nguyên JPEG của công cụ
    chụp. Khi đưa vào Word, nên dùng khổ ngang hoặc chiều rộng trang cho các ảnh nhiều cột.
    Ảnh 12 và 13 bổ sung nhau để đọc toàn bộ phần giải thích, không phải hai lần chấm khác nhau.
    ''')
    for index in [15, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 2, 16]:
        image(index)
    add('''Lưu ý khi viết kết luận: ảnh minh họa chức năng hoạt động, không đo độ chính xác mô hình.
    Kết quả đánh giá A/B/C hiện có thuộc benchmark pilot 500 tin và CV tổng hợp, không áp dụng
    trực tiếp cho toàn bộ catalog 7.050 tin hay chất lượng tuyển dụng thực tế. Các trọng số
    và chính sách khoảng cách là cấu hình thử nghiệm, còn cần đánh giá thêm bằng người dùng thật.

    Gói này chỉ bổ sung tài liệu/code trích/ảnh minh họa, không thay đổi thuật toán hoặc giao diện ứng dụng.
    ''')


def to_html(markdown):
    """Render tập con Markdown của tài liệu này; không phụ thuộc thư viện mới."""
    def inline(s):
        s = html.escape(s)
        s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
        s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
        return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', s)
    output, paragraph, fenced, code, table = [], [], False, [], False
    def flush():
        if paragraph:
            output.append('<p>' + inline(' '.join(paragraph)) + '</p>')
            paragraph.clear()
    for line in markdown.splitlines():
        if line.startswith('```'):
            flush()
            if fenced:
                output.append('<pre><code>' + html.escape('\n'.join(code)) + '</code></pre>')
                code.clear()
            fenced = not fenced
            continue
        if fenced:
            code.append(line)
            continue
        if line.startswith('|'):
            flush()
            if not table:
                output.append('<table>')
                table = True
            cells = line.strip('|').split('|')
            if all(re.fullmatch(r'\s*:?-+:?\s*', c) for c in cells):
                continue
            output.append('<tr>' + ''.join('<td>'+inline(c.strip())+'</td>' for c in cells)+'</tr>')
            continue
        if table:
            output.append('</table>')
            table = False
        if not line.strip():
            flush()
        elif (match := re.match(r'^(#{1,3}) (.*)', line)):
            flush()
            n = len(match[1])
            output.append(f'<h{n}>{inline(match[2])}</h{n}>')
        elif (match := re.fullmatch(r'!\[([^\]]*)\]\(([^)]+)\)', line)):
            flush()
            output.append(f'<img alt="{html.escape(match[1])}" src="{html.escape(match[2])}">')
        else:
            paragraph.append(line)
    flush()
    return '<!doctype html><html lang="vi"><meta charset="utf-8"><title>JobVista – Cài đặt và Demo</title><style>body{font:16px/1.7 Segoe UI,Arial,sans-serif;max-width:1120px;margin:40px auto;padding:0 26px;color:#173d34}h1,h2{line-height:1.35}h2{margin-top:52px;border-top:2px solid #c9ddd3;padding-top:20px}pre{background:#f2f5f4;color:#172f29;padding:18px;overflow:auto;font:13px/1.6 Consolas,monospace;white-space:pre-wrap;overflow-wrap:anywhere}img{width:100%;height:auto;border:1px solid #d9e6df;margin-top:24px}table{border-collapse:collapse;width:100%;font-size:14px}td{border:1px solid #c9d9d2;padding:9px}tr:first-child{background:#e5f0e9;font-weight:bold}a{color:#13795d}code{font-family:Consolas,monospace}@media print{body{max-width:none;margin:0}img,table{break-inside:avoid}h2{break-before:page}pre{font-size:9pt}a{color:inherit}}</style><body>' + '\n'.join(output) + '</body></html>'


def main():
    global REF
    sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-ref', default=None, help='Git revision của code được trích')
    parser.add_argument('--desktop', action='store_true', help='Sao chép gói mới lên Desktop và tạo ZIP')
    args = parser.parse_args()
    REF = args.source_ref or subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
    for stem, _, _ in SHOTS:
        if not (OUT/'images'/f'{stem}.jpg').is_file():
            raise FileNotFoundError(f'Thiếu ảnh thật: {stem}.jpg')
    (OUT/'code').mkdir(parents=True, exist_ok=True)
    (OUT/'CV_demo').mkdir(exist_ok=True)
    shutil.copy2(ROOT/'data/sample_cvs/pdf/CV07_devops_can_tho.pdf', OUT/'CV_demo/CV07_devops_can_tho.pdf')
    build()
    markdown = '\n'.join(PARTS)
    (OUT/'CAI_DAT_VA_DEMO_JOBVISTA.md').write_text(markdown, encoding='utf-8')
    (OUT/'CAI_DAT_VA_DEMO_JOBVISTA.html').write_text(to_html(markdown), encoding='utf-8')
    (OUT/'DANH_MUC_ANH.md').write_text('# Danh mục ảnh JobVista\n\n' + '\n\n'.join(
        f'**Ảnh {i:02d}. {caption}.**\n\nTệp: [images/{stem}.jpg](images/{stem}.jpg)\n\n{note}'
        for i,(stem,caption,note) in enumerate(SHOTS,1)), encoding='utf-8')
    (OUT/'README.md').write_text('# Tài liệu cài đặt và demo JobVista\n\nMở CAI_DAT_VA_DEMO_JOBVISTA.html bằng trình duyệt để đọc, hoặc file Markdown để biên tập.\n\n- Phần 1–8: giải thích và code trích nguyên văn, có vị trí nguồn.\n- Phần 9: giới thiệu, trang chủ, kịch bản demo.\n- Phần 10: 16 ảnh thật; DANH_MUC_ANH.md ghi chú thích riêng.\n- code/: các đoạn trích .txt để chèn báo cáo, không chạy độc lập.\n- CV_demo/: CV PDF giả lập đã dùng chụp ảnh.\n- manifest.json: revision nguồn, danh mục đoạn code, checksum các tệp.\n\nKhi gửi bạn làm Word, gửi cả ZIP và giải nén trước khi mở HTML. Ảnh chương 3 nằm trong gói Hinh_Chuong_3_JobVista đã cung cấp trước đó.\n', encoding='utf-8')
    files = [{'path': p.relative_to(OUT).as_posix(), 'bytes':p.stat().st_size,
              'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
             for p in sorted(OUT.rglob('*')) if p.is_file() and p.name != 'manifest.json']
    manifest = {'date':'2026-11-14','source_revision':REF,'ui_url':'http://127.0.0.1:8000/',
                'screenshots':16,'screenshot_kind':'Unmodified real browser screenshots, JPEG, 1265x712',
                'sample_cv':'CV07_devops_can_tho.pdf (synthetic)',
                'excerpts':EXCERPTS,'files':files}
    (OUT/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    if args.desktop:
        desktop = Path(subprocess.check_output(['powershell','-NoProfile','-Command',"[Environment]::GetFolderPath('Desktop')"],text=True).strip())
        destination = desktop/'JobVista_Cai_dat_va_Demo_20261114'
        if destination.exists():
            # Không ghi đè tài liệu mà người dùng có thể đã sửa trên Desktop.
            raise FileExistsError(destination)
        shutil.copytree(OUT, destination)
        archive = desktop/(destination.name+'.zip')
        with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
            for p in sorted(destination.rglob('*')):
                if p.is_file():z.write(p, destination.name+'/'+p.relative_to(destination).as_posix())
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None
        for entry in files:
            assert hashlib.sha256((destination/entry['path']).read_bytes()).hexdigest() == entry['sha256']
        print(json.dumps({'desktop':str(destination),'zip':str(archive),'zip_bytes':archive.stat().st_size},ensure_ascii=False))
    print(json.dumps({'output':str(OUT),'source_revision':REF,'code_excerpts':len(EXCERPTS),
                      'screenshots':len(SHOTS),'markdown_chars':len(markdown)},ensure_ascii=False))


if __name__ == '__main__':
    main()
