# Bộ hình Chương 3 — JobVista

Ngày xuất: 14/11/2026. Dùng số liệu catalog 7.050 tin và mã chức năng `7206ab7` (repo đối chiếu: `bebcf9b`).

## Cách chèn vào Word

Dùng 7 file PNG ở thư mục chính: Insert → Pictures → This Device. Chọn In Line with Text, căn giữa, khóa tỷ lệ; không kéo méo ảnh. PNG 300 dpi; thư mục SVG giữ bản vector.

Nên đặt chiều rộng khoảng 16–17 cm khi dùng trang A4 dọc. Hình 3.7 có hai khung nên có thể đặt trên một trang ngang rộng khoảng 22–24 cm để chữ lớn hơn. Không bật nén ảnh mạnh; có thể chọn High fidelity trong File → Options → Advanced → Image Size and Quality.

Dùng Insert Caption để đánh số bên dưới. Tên/chú thích cần chèn:

- **Hình 3.1. Biểu đồ phân bố tin tuyển dụng theo khu vực chính** → `Hinh_3_1_Phan_bo_tin_theo_khu_vuc.png`

- **Hình 3.2. Biểu đồ phân bố tin tuyển dụng theo lĩnh vực chuyên môn** → `Hinh_3_2_Phan_bo_tin_theo_linh_vuc.png`

- **Hình 3.3. Biểu đồ mức độ sẵn có của thông tin kinh nghiệm và tiền lương** → `Hinh_3_3_Muc_do_san_co_kinh_nghiem_va_luong.png`

- **Hình 3.4. Sơ đồ kiến trúc tổng thể của hệ thống JobVista** → `Hinh_3_4_Kien_truc_tong_the_JobVista.png`

- **Hình 3.5. Sơ đồ tổ chức cơ sở tri thức của hệ thống JobVista** → `Hinh_3_5_To_chuc_co_so_tri_thuc_JobVista.png`

- **Hình 3.6. Sơ đồ luồng xử lý gợi ý việc làm của hệ thống JobVista** → `Hinh_3_6_Luong_xu_ly_goi_y_viec_lam.png`

- **Hình 3.7. Sơ đồ bố cục giao diện tìm việc theo CV của JobVista** → `Hinh_3_7_Bo_cuc_giao_dien_tim_viec_CV.png`

## Số liệu và cách diễn giải

- Hình 3.1: mỗi Job_ID đếm một lần theo Primary_Region. Hà Nội 3.794 và TP.HCM 2.685 tin; 24 nhóm vùng không phải danh mục hành chính đầy đủ.

- Hình 3.2: mỗi tin đếm một lần theo Domain. Có 14 lĩnh vực; không nhầm với 20 Role_Code. Lĩnh vực được chuẩn hóa bằng từ điển/quy tắc, không phải nhãn chuyên gia đã xác nhận.

- Hình 3.3: kinh nghiệm rõ 6.494 (92,1%), chưa rõ 556 (7,9%). Lương có mức tiền 5.167 (73,3%); thỏa thuận/cạnh tranh 811 (11,5%); chưa rõ 1.072 (15,2%).

- Nhóm lương thỏa thuận/cạnh tranh gồm Salary_Status=negotiable, negotiable_from_source, allowance_conflict; chỉ nhóm normalized được gọi là có mức tiền. Nhóm còn lại chưa rõ. Đây là trạng thái sau làm sạch, không phải đánh giá độ đúng của nguồn.

- Hình 3.4–3.6 là sơ đồ tổng hợp từ mã nguồn. Catalog ở CSV; SQLite chỉ lưu nhu cầu nghề. Cơ sở tri thức là dữ kiện, từ điển và quy tắc, chưa phải knowledge graph.

- Hình 3.6 tách đối chiếu toàn quốc khỏi danh sách chính theo nơi muốn làm. Công thức cân bằng: P=1/(1+d/50); B=0,7×CV+0,3×P. Khoảng cách giữa điểm đại diện vùng, không phải đường đi. Thiếu nơi ở/tọa độ không tạo điểm cân bằng.

- Hình 3.7 là wireframe hai trạng thái, không phải ảnh chụp hoặc tuyên bố cả hai trang hiện đồng thời. Chi tiết chỉ mở khi chọn tin; bản mobile tự đổi số cột.

## Nguồn trích dẫn

- TiniX AI — Vietnamese Job Descriptions: https://huggingface.co/datasets/tinixai/vietnamese-job-descriptions

- Snapshot: https://huggingface.co/datasets/tinixai/vietnamese-job-descriptions/tree/679c3a17347ff6ce769d9bf510c122a087493cf6

- Giấy phép dữ liệu CC BY-NC 4.0; tin lịch sử chưa xác minh còn tuyển. Số liệu lấy từ catalog bàn giao, không phải thống kê toàn thị trường.

- Mã nguồn: https://github.com/TienMoi79/job-recommender-system/tree/bebcf9b732a32b3d98cee2078b7c9e62a73017fe

- Các CSV trong So_lieu và manifest.json lưu số đếm/checksum để kiểm chứng. Không dùng kết quả benchmark 500 tin làm số liệu cho 7.050 tin.

## Tái tạo

Chạy `python scripts/generate_report_figures.py` từ repo, cần pandas và matplotlib. Script không sửa catalog hay dữ liệu CV.
