# Nguồn và cách chuẩn hóa catalog 7.050 tin IT

Catalog chính: `jobs_catalog.csv`. Hai giao diện Việt/Anh dùng cùng 7.050 `Job_ID`,
không phải hai tập tin riêng. 500 ID đầu giữ nguyên; 6.550 tin được bổ sung ngày
05/11/2026 từ cùng nguồn. Bản 500 đóng băng ở `evaluation/jobs_catalog_500.csv`
để tái lập benchmark cũ. Các CSV 20 tin cũ là mẫu nhỏ phục vụ bài học và kiểm thử.

## Nguồn

- Dataset: [TiniX AI — Vietnamese Job Descriptions](https://huggingface.co/datasets/tinixai/vietnamese-job-descriptions).
- Snapshot: `679c3a17347ff6ce769d9bf510c122a087493cf6`.
- Giấy phép của dữ liệu: [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/).
  Tập con này dùng cho đồ án phi thương mại, ghi công TiniX AI; giấy phép áp dụng
  cho dữ liệu và phần điều chỉnh từ nguồn, không phải tuyên bố giấy phép cho toàn bộ code.
- Bản nguồn có 606.878 tin (2022–2026), gồm chức danh, công ty, lương, địa điểm,
  ngành, kinh nghiệm, mô tả và yêu cầu. Catalog là tập con tham khảo, không có
  kiểm chứng rằng các tin vẫn còn tuyển hoặc link ứng tuyển trực tiếp.
- Mỗi hàng giữ `Source_Row_ID`, `Source_Row_Index`, `Source_URL`, revision và
  license để đối chiếu bản ghi nguồn. `Source_URL` mở bản ghi trong dataset viewer.

## Quy tắc lựa chọn và các trường suy ra

`expand_job_catalog.py` dùng pandas trên batch Parquet 4.096 dòng để tiền lọc,
bỏ thiếu và trùng; sau đó chuẩn hóa tin IT có mô tả ít nhất 160
ký tự, địa điểm nhận diện được và ít nhất hai kỹ năng trong từ điển. Loại công ty
trống/nhãn lỗi như “Quy mô:”, loại bản ghi trùng nội dung và giới hạn kinh nghiệm
bất thường. Bản 500 cũ lấy mẫu seed42; bản mở rộng giữ tất cả tin đạt quy tắc
trong các nhóm vùng đã nhận diện, không còn quota 10 vùng. Quét 606.878 hàng,
tiền lọc 14.373 hàng, thu được tổng 7.050 tin; 3.594 công ty và 24 vùng chính.

- `Company`, `Location`, `Salary`, `Job_Description`, `Requirements` giữ thông
  tin nguồn đã bỏ HTML/khoảng trắng dư. Không tự tạo công ty, lương hoặc địa điểm.
- `Skills`, `Role_Code`, `Domain`, `Region_Codes` được suy ra bằng từ điển alias
  Việt/Anh. Đây không phải nhãn gán tay hoàn hảo hay danh mục hành chính chính thức.
- `Experience_Years` là cận dưới khi phân tích được chuỗi số năm. Nếu không rõ,
  dùng 0 như giá trị kỹ thuật kèm `Experience_Known=False`; UI ghi “Kinh nghiệm
  chưa rõ”, không khẳng định tin không yêu cầu kinh nghiệm. `Experience_Text`
  giữ chuỗi gốc. Ghép CV chưa lọc cứng theo số năm kinh nghiệm.
- Khi trường kinh nghiệm nguồn không rõ (ví dụ `Không`), bộ chuẩn hóa đọc tiếp
  phần `Requirements`, rồi phần yêu cầu trong `Job_Description`. Chỉ nhận số
  gắn với kinh nghiệm; hỗ trợ khoảng năm, số thập phân và tháng quy đổi ra năm.
  Không lấy tuổi/năm học/thâm niên công ty hay số năm chỉ được ghi là ưu tiên.
  `Experience_Source` và `Experience_Evidence` ghi nơi suy ra và đoạn bằng chứng
  chuẩn hóa không dấu; toàn văn gốc vẫn giữ nguyên. Đây là quy tắc suy ra có giới
  hạn, không phải nhãn đã được nhà tuyển dụng kiểm chứng.
- Nhóm `khanh_hoa` được ghi **Nha Trang / Khánh Hòa**. Tin chỉ ghi tỉnh không
  bị trình bày như một địa chỉ chính xác ở trung tâm Nha Trang.
- Khi một tin có nhiều vùng, bộ lọc chấp nhận từng vùng được ghi trong nguồn.

## Phiên bản tiếng Anh

Trong giao diện tiếng Việt, tin có mô tả gốc bằng tiếng Anh dùng tóm tắt tiếng
Việt có cấu trúc từ các trường của cùng bản ghi. CSV vẫn giữ toàn văn nguyên
ngôn ngữ để đối chiếu; tóm tắt không được trình bày như bản dịch đầy đủ.

Các cột `_EN` dùng chức danh/mô tả tiếng Anh gốc nếu có; nếu không thì dùng tên
nhóm nghề và tóm tắt có cấu trúc từ kỹ năng, kinh nghiệm và vùng của nguồn. Bản
tóm tắt **không phải bản dịch đầy đủ** của mô tả/yêu cầu. Tên công ty bản Anh bỏ
tiền tố pháp nhân tiếng Việt và chuyển tên riêng về dạng không dấu; tên gốc vẫn
còn trong CSV. Lương và số năm chưa rõ được ghi rõ, không bổ sung số liệu giả.

## Tái tạo và kiểm tra

Để tạo lại catalog, cài thư viện riêng cho công cụ xử lý nguồn rồi chạy:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-catalog.txt
.\.venv\Scripts\python.exe expand_job_catalog.py
```

Script tải snapshot vào `.cache/tinix-jobs.parquet` nếu chưa có, không đưa toàn
bộ nguồn vào Git. Manifest ghi số hàng quét, số tin đủ điều kiện, phân bố thực,
số công ty và SHA-256 của CSV/Parquet. Không tạo thêm tin giả. Script cũ
`build_job_catalog.py` chỉ phục vụ tái tạo bản500, không chạy đè catalog mới.

`catalog_manifest.json` là thống kê của bản bàn giao; kiểm tra bằng
`tests/test_catalog.py`. Việc kiểm tra cấu trúc và xếp hạng đúng thứ tự chưa thay
thế đánh giá độ chính xác gợi ý trên các cặp CV–việc làm được gán nhãn.

Bản sửa 16/10/2026 trên snapshot500 phục hồi 67 tin từng thiếu số năm; số tin chưa xác định còn
67/500. Giữ nguyên 500 Job_ID, công ty, địa điểm và văn bản nguồn, không lấy mẫu
lại catalog. Bản ghi sửa ở `outputs/data_quality/experience_repairs.csv`; manifest
có checksum trước/sau. `python repair_catalog_experience.py` chỉ xem trước;
thêm `--apply` mới áp dụng và lưu bản cũ trong `.cache/experience-before-*`.
Catalog7050 có 556 tin chưa xác định kinh nghiệm. Chưa có qrels độc lập cho tập
mới: không dùng kết quả benchmark500 như kết quả đo cho7050. Khởi động lại web
để nạp catalog mới. Chi tiết rating và nguồn tọa độ GeoNames phục vụ đối chiếu
khoảng cách tại [Lab 3, rating và khoảng cách](../docs/LAB3_RATING_DISTANCE.md).

Trích dẫn do dataset card đề xuất: Le, Ngoc-Quang; Hoang, Duc Duong; Tran, Mai Vu;
Vuong, Thi-Hai-Yen (2026). *CareerPathKG: Knowledge Graph Integrated Framework
for Career Intelligence*. EACL Industry Track, pp. 813–822.
[DOI](https://doi.org/10.18653/v1/2026.eacl-industry.60).
