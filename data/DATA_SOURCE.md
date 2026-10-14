# Nguồn và cách chuẩn hóa catalog 500 tin IT

Catalog chính: `jobs_catalog.csv`. Hai giao diện Việt/Anh dùng cùng 500 `Job_ID`,
không phải 1.000 tin riêng. Các CSV 20 tin cũ là mẫu nhỏ phục vụ bài học và kiểm thử.

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

`build_job_catalog.py` đọc Parquet theo batch, chọn tin IT có mô tả ít nhất 160
ký tự, địa điểm nhận diện được và ít nhất hai kỹ năng trong từ điển. Loại công ty
trống/nhãn lỗi như “Quy mô:”, loại bản ghi trùng nội dung và giới hạn kinh nghiệm
bất thường. Lấy mẫu tái lập với seed 42, xen kẽ nhóm nghề trong từng khu vực.

- `Company`, `Location`, `Salary`, `Job_Description`, `Requirements` giữ thông
  tin nguồn đã bỏ HTML/khoảng trắng dư. Không tự tạo công ty, lương hoặc địa điểm.
- `Skills`, `Role_Code`, `Domain`, `Region_Codes` được suy ra bằng từ điển alias
  Việt/Anh. Đây không phải nhãn gán tay hoàn hảo hay danh mục hành chính chính thức.
- `Experience_Years` là cận dưới khi phân tích được chuỗi số năm. Nếu không rõ,
  dùng 0 như giá trị kỹ thuật kèm `Experience_Known=False`; UI ghi “Kinh nghiệm
  chưa rõ”, không khẳng định tin không yêu cầu kinh nghiệm. `Experience_Text`
  giữ chuỗi gốc. Ghép CV chưa lọc cứng theo số năm kinh nghiệm.
- Nhóm `khanh_hoa` được ghi **Nha Trang / Khánh Hòa**. Tin chỉ ghi tỉnh không
  bị trình bày như một địa chỉ chính xác ở trung tâm Nha Trang.
- Khi một tin có nhiều vùng, bộ lọc chấp nhận từng vùng được ghi trong nguồn.

## Phiên bản tiếng Anh

Các cột `_EN` dùng chức danh/mô tả tiếng Anh gốc nếu có; nếu không thì dùng tên
nhóm nghề và tóm tắt có cấu trúc từ kỹ năng, kinh nghiệm và vùng của nguồn. Bản
tóm tắt **không phải bản dịch đầy đủ** của mô tả/yêu cầu. Tên công ty bản Anh bỏ
tiền tố pháp nhân tiếng Việt và chuyển tên riêng về dạng không dấu; tên gốc vẫn
còn trong CSV. Lương và số năm chưa rõ được ghi rõ, không bổ sung số liệu giả.

## Tái tạo và kiểm tra

Sau khi cài `requirements-web.txt`, chạy:

```powershell
.\.venv\Scripts\python.exe build_job_catalog.py
```

Script tải snapshot vào `.cache/tinix-jobs.parquet` nếu chưa có, không đưa toàn
bộ nguồn vào Git. Manifest ghi số hàng quét, số tin đủ điều kiện, phân bố thực,
số công ty, seed và SHA-256 của CSV. Nếu vùng có ít tin hợp lệ hơn kế hoạch,
script lấy bù từ tin thật của vùng khác, không tạo thêm tin giả.

`catalog_manifest.json` là thống kê của bản bàn giao; kiểm tra bằng
`tests/test_catalog.py`. Việc kiểm tra cấu trúc và xếp hạng đúng thứ tự chưa thay
thế đánh giá độ chính xác gợi ý trên các cặp CV–việc làm được gán nhãn.

Trích dẫn do dataset card đề xuất: Le, Ngoc-Quang; Hoang, Duc Duong; Tran, Mai Vu;
Vuong, Thi-Hai-Yen (2026). *CareerPathKG: Knowledge Graph Integrated Framework
for Career Intelligence*. EACL Industry Track, pp. 813–822.
[DOI](https://doi.org/10.18653/v1/2026.eacl-industry.60).
