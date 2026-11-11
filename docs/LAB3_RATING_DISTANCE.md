# Bổ sung theo góp ý giảng viên — 05/11/2026

## 1. Dữ liệu lớn hơn, có nguồn để trích dẫn

Catalog web tăng từ **500 lên 7.050 tin**, 3.594 công ty, 24 nhóm địa điểm chính.
Nguồn chưa hết nên chưa cần ghép một nguồn khác có schema/giấy phép khác.
Đã quét **606.878 bản ghi**, tiền lọc 14.373 bản ghi bằng pandas, giữ 7.050 tin
IT có kỹ năng, mô tả và địa điểm đủ dùng. Trong đó giữ nguyên ID/nội dung
500 tin đã bàn giao, bổ sung 6.550 tin; không nhân bản tin để tăng số lượng.

- Dataset: TiniX AI, **Vietnamese Job Descriptions**:
  https://huggingface.co/datasets/tinixai/vietnamese-job-descriptions
- Snapshot tái lập:
  https://huggingface.co/datasets/tinixai/vietnamese-job-descriptions/tree/679c3a17347ff6ce769d9bf510c122a087493cf6
- File nguồn:
  https://huggingface.co/datasets/tinixai/vietnamese-job-descriptions/resolve/679c3a17347ff6ce769d9bf510c122a087493cf6/data.parquet
- Giấy phép dữ liệu: **CC BY-NC 4.0**, dùng phi thương mại và ghi công nguồn.
  https://creativecommons.org/licenses/by-nc/4.0/
- Mỗi tin có Source_Dataset, Source_Revision, Source_Row_ID/Index, Source_URL,
  Source_License và Content_Fingerprint để truy vết. Chưa xác minh còn tuyển.
- Số liệu kiểm tra và checksum: `data/catalog_manifest.json`.

Script `expand_job_catalog.py` đọc Parquet từng batch **4.096 dòng** rồi dùng
pandas: `fillna`, chuẩn hóa chuỗi, mặt nạ `str.contains`, `drop_duplicates`,
`concat`, `astype('category')`, `value_counts`. Không nạp đồng thời toàn bộ
606.878 mô tả vào RAM. Sau tiền lọc, mới chạy từ điển NLP và kiểm tra kinh nghiệm.
Web chỉ nạp tập đã làm sạch 7.050 tin, không nạp toàn nguồn.
Bộ embedding ngữ nghĩa được làm nóng ở nền và cache theo nội dung catalog.
Lần đầu có thể mất vài phút trên CPU; trong lúc đó CV vẫn được ghép bằng
từ khóa/kỹ năng/vị trí/kinh nghiệm và ghi rõ ngữ nghĩa chưa sẵn sàng. Các lượt
ghép sau khi index sẵn sàng mới dùng ngữ nghĩa; không báo là hybrid ngữ nghĩa
cho một truy vấn đã tính bằng lexical.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-catalog.txt
.\.venv\Scripts\python.exe expand_job_catalog.py
```

Chạy lại giữ ID các tin đã có. Nếu muốn tái tạo đúng bản 05/11, bắt đầu từ
`data/evaluation/jobs_catalog_500.csv` trong một thư mục đầu ra riêng. Không chạy
`build_job_catalog.py` đè lên catalog mới: đó là công cụ chọn bản 500 cũ.

## 2. Vận dụng Lab 3 pandas và rating

Đã đọc Lab3 Phần 1_2 notebook và Phần 3 `recommender.py` của sinh viên. Lab
làm sạch rating, giữ tương tác gần nhất của một người với một mục, `groupby`
tính số lượt/trung bình, rồi weighted rating. Đồ án tái dùng cách xử lý và công
thức, không đưa dataset phim/sách vào dữ liệu việc làm.

Chọn phương án **rating ngầm bằng code**. Khi người dùng chủ động bấm **Tìm
công việc phù hợp** sau khi đọc CV, hệ thống nhận diện nhóm nghề rồi ghi:
`actor_hash`, danh sách mã nghề, thời gian. Không ghi văn bản CV, email, tên,
địa chỉ nhà hoặc từ khóa vào bảng nhu cầu.

Một actor là mã ngẫu nhiên của trình duyệt, **không phải người dùng đã xác minh**.
Nhấn tìm lại/thay CV chỉ thay nguyện vọng mới nhất của trình duyệt đó. Tính trong
30 ngày, mỗi actor tổng trọng số 1; nhiều nghề cùng được nhận diện chia đều trọng
số. Thống kê chỉ cộng dồn giữa các trình duyệt cùng sử dụng **một server**.
Mỗi bạn tự chạy localhost có DB riêng; chưa có đăng nhập nên không chống được
việc một người tạo nhiều trình duyệt hoặc giả mã. Không gọi đây là nhu cầu của
toàn thị trường lao động.

Áp dụng pandas `to_numeric → sort_values → drop_duplicates → explode → groupby
→ merge`, tương ứng thao tác Lab 3. Với một nghề:

- N = số actor hợp lệ trong cửa sổ 30 ngày.
- n = tổng trọng số actor quan tâm nghề đó.
- R = 5 × n/N: rating nhu cầu thô trong [0,5].
- C = 5/K, K là số nhóm nghề; m = 5 lượt prior.
- **WR = N/(N+m) × R + m/(N+m) × C**: làm trơn theo công thức Lab 3.

Ví dụ **8/10** actor quan tâm Data Analyst: rating thô là 4/5; WR nhỏ hơn do
làm trơn với prior. Đó là điểm **quan tâm**, không phải chất lượng công việc
hay điểm sao ứng viên chấm. Không đổi tất cả lượt tìm thành sao 5, vì cách đó
không còn phân biệt được mức quan tâm giữa các nghề.

Khác Lab: không loại nghề ít lượt theo phân vị 80%, vì sẽ loại mất nghề hiếm.
Khi chưa đủ 5 actor, rating chỉ hiển thị tham khảo và có trọng số 0 khi xếp hạng.
Khi đủ mẫu: **điểm gợi ý = 90% điểm nội dung/quan tâm cá nhân + 10% WR/5**.
CV cosine/kỹ năng/kinh nghiệm và lịch sử quan tâm vẫn là căn cứ chính. Rating
chỉ sắp lại pool đã qua ngưỡng chuyên môn và điều kiện vùng, không tạo thêm ứng
viên trái nghề. Điểm CV gốc/sáu thành phần giữ nguyên để giải thích độc lập.

File: `demand_rating.py`. DB runtime: `.local/jobvista.sqlite3` được gitignore;
không push tương tác thật lên GitHub. `GET /api/demand` chỉ xuất bảng tổng hợp.
Refresh trang chủ không tăng lượt; API gợi ý luôn vô hiệu hóa cờ ghi nhận.
Notebook minh họa 8/10 dùng dữ liệu mô phỏng **tách khỏi DB thật**.

## 3. Phù hợp nhất hay gần nơi ở nhất?

Tách **nơi ở hiện tại** với **nơi muốn làm việc**. CV02 ở TP.HCM nhưng muốn
Hà Nội: hai trường được đọc riêng và đều cho phép sửa. Không lấy nơi muốn làm
hoặc địa điểm dự án cũ để giả làm địa chỉ nhà. Không có nơi ở thì yêu cầu xác
nhận trước khi kết luận việc gần nhà.

Sau khi ghép CV, bản cập nhật 11/11/2026 hiển thị **Cân bằng chuyên môn và khoảng
cách** trước: `P = 1/(1+d/50)` và `B = 0,7×điểm CV + 0,3×P`. Chỉ dùng việc
đã đạt ngưỡng chuyên môn và có khoảng cách xác định; thiếu nơi ở thì yêu cầu
xác nhận. Đây là trọng số thử nghiệm, không phải kết quả đã chứng minh tăng
độ chính xác. Xem [công thức, ca thiếu dữ liệu và backup](BALANCED_RECOMMENDATIONS.md).

Bên dưới giữ hai cột đối chiếu:

- **Phù hợp chuyên môn nhất:** các tin có điểm CV cao nhất trên toàn quốc.
- **Gần nơi ở nhất trong các việc đạt ngưỡng:** các tin đủ phù hợp được sắp
  theo khoảng cách ước tính, rồi theo điểm CV khi cùng khoảng cách.

Mỗi lựa chọn ghi điểm chuyên môn và cùng vùng/khoảng cách để người dùng tự
cân nhắc. Tin phù hợp nhất có thể xa, tin gần nhất có thể điểm chuyên môn thấp
hơn; không sửa điểm CV để làm việc gần trông có vẻ phù hợp hơn.
**Bảng đối chiếu toàn quốc riêng**; danh sách chính vẫn lọc cứng nơi muốn làm.
Không lấp chỗ trống trong vùng đã chọn bằng việc ở tỉnh khác.

Nguồn tọa độ **GeoNames cities15000**, truy cập 05/11/2026:
https://download.geonames.org/export/dump/
https://download.geonames.org/export/dump/cities15000.zip
Giấy phép CC BY 4.0: https://creativecommons.org/licenses/by/4.0/
Tệp `data/region_coordinates.json` giữ ID GeoNames và tọa độ của 25 điểm đại
diện thành phố. Haversine tính đường chim bay giữa hai điểm, **không phải thời
gian di chuyển, đường đi hoặc khoảng cách địa chỉ nhà–công ty**. Cùng vùng chỉ
ghi “Cùng khu vực nơi ở”, không tuyên bố đi làm 0 km. Không gọi GPS/geocoding
ngoài máy và không gửi địa chỉ CV đến dịch vụ bản đồ.

## 4. Giới hạn và kiểm chứng

Rating mới là heuristic cần đánh giá, không mặc định cộng điểm sẽ tăng độ chính
xác. Chưa có ground truth độc lập cho 7.050 tin hoặc tương tác người dùng thực.
Benchmark và kết quả A/B/C cũ giữ nguyên trên **snapshot 500 tin** ở
`data/evaluation/jobs_catalog_500.csv`; không dùng kết quả đó như số đo cho bản
mới. Để chứng minh cải thiện, cần gán nhãn lại pool mới và so sánh ablation
content-only / content+rating / content+rating+distance trên cùng bộ truy vấn.

`job_recommender_notebook.ipynb` là bài demo giai đoạn cũ. Notebook bổ sung
`lab3_jobvista.ipynb` trình bày pandas, rating, mở rộng dữ liệu và so sánh địa điểm.
