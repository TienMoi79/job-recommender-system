# Rà soát mô tả và lương — 05/11/2026

Phạm vi: toàn bộ **7.050 tin** trong `data/jobs_catalog.csv`, đối chiếu từng
`Source_Row_ID` với snapshot Parquet TiniX AI đang được dùng cho đồ án.

## Mô tả và yêu cầu

Nguồn cũng đã bị dồn nhiều mục thành một chuỗi. Bản sửa khôi phục cách đọc bằng
quy tắc: giữ newline/HTML paragraph nếu có; tách tiêu đề, bullet, câu và cụm
mở đầu nhiệm vụ rõ ràng trong những dòng dài thiếu dấu chấm. Không tự viết lại
nội dung công việc hay cam kết khôi phục chính xác layout của tin gốc.

- `Job_Description` và `Requirements` giữ nguyên để làm đầu vào NLP và đối chiếu
  nguồn; `Content_Fingerprint`, 7.050 ID và các trường chuyên môn không thay đổi.
- `Job_Description_Display` / `Requirements_Display` giữ bản dễ đọc có newline.
- API chọn bản display đúng ngôn ngữ. Khi dùng tóm tắt Việt/Anh, định dạng lại
  bản tóm tắt đó, không đưa toàn văn tiếng Việt vào giao diện English.
- Web hiển thị tiêu đề phụ, từng đoạn, danh sách gạch đầu dòng và đánh số. Câu
  dính liền như `CSV).Clean` cũng được ngắt; URL và tên Node.js được bảo vệ.
  Mọi nội dung
  được escape, không chạy HTML/script từ dataset.
- Không cắt dấu `-` trong back-end, Node.js, số thập phân, khoảng 3–4 năm hoặc
  15–25 triệu thành bullet. Bản gốc cho thuật toán và benchmark500 được giữ nguyên.

## Lương

Chỉ quy đổi **đơn vị tiền Việt** sang triệu; giữ nguyên kỳ trả nếu nguồn ghi rõ.
Không tự nhân tuần/ngày thành tháng, không áp tỷ giá đoán cho USD. Nguồn không
ghi kỳ trả thì không tự thêm `/tháng`.

| Bản ghi / dữ liệu nguồn | Hiển thị sau sửa | Lý do |
|---|---|---|
| VN0005: `1000 - 2000 nghìn/tuần` | `1–2 triệu/tuần` | Quy đổi đúng nghìn → triệu; giữ tuần |
| `50 - 300 nghìn/ngày`, nếu thực sự là lương | `0,05–0,3 triệu/ngày` | Giữ ngày, không tự thành lương tháng |
| VN0142 ATOMI: `50 - 300 nghìn/ngày` | `Lương thỏa thuận` | Nguồn quyền lợi nêu lương thỏa thuận, ăn trưa 50k/ngày và gửi xe300k/tháng; metadata đã ghép nhầm phụ cấp |
| VN0059 WOORI: `105` | `Chưa rõ mức lương` | Không có đơn vị; quyền lợi ghi bảo hiểm105 triệu/năm, không được coi là lương |
| VN0172: `500` | `Lương thỏa thuận` | Nguồn nêu lương cứng thỏa thuận; 500.000đ là phụ cấp ăn trưa |
| `15000000 - 50000000 VND MONTH` | `15–50 triệu/tháng` | Có đủ tiền tệ và kỳ trả |
| `2,000 - 4,000 USD` | `2000–4000 USD` | Giữ tiền tệ USD, không đoán tỷ giá |
| `0 VND`, khoảng đảo chiều, số thiếu đơn vị | `Chưa rõ mức lương` | Không tự bịa lương hoặc gán thành0 triệu |

Các dấu “Dưới”, “Trên”, “Từ”, “Tối đa” được giữ đúng ý nghĩa. Khoản lương hợp
lệ không bị xóa chỉ vì công ty cho phép đàm phán; chỉ loại nhiễu phụ cấp khi có
đồng thời nhãn lương thỏa thuận và các số tiền trùng khoản hỗ trợ trong nguồn.

Các cột kiểm chứng mới: `Salary_Original`, `Salary_Status`, `Salary_Currency`,
`Salary_Period`, `Salary_Min`, `Salary_Max`, `Salary_Evidence`. Min/Max dùng
**triệu VND** nếu currency=VND, hoặc USD nếu currency=USD; giá trị trống nghĩa
là chưa biết. Không so sánh lẫn tiền tệ hoặc kỳ trả bằng các số này.

`Salary` và `Salary_EN` là nhãn đã chuẩn hóa để hiển thị, không dùng làm nhãn
huấn luyện. Giá trị nguồn vẫn giữ ở `Salary_Original`; snapshot500 đánh giá cũ
không sửa, nên việc hiển thị lương mới không thay đổi qrels hay kết quả cũ.

## Chạy và kiểm tra

```powershell
python repair_job_presentation.py          # rà soát, chưa thay catalog
python repair_job_presentation.py --apply  # backup CSV/manifest rồi áp dụng
python -m unittest discover -s tests -p test_job_presentation.py -v
node --test tests/test_personalization.cjs
```

Cần `requirements-catalog.txt` và snapshot `.cache/tinix-jobs.parquet` để chạy
script đối chiếu; file CSV đã sửa được đưa lên GitHub, người tải web không cần
tải lại toàn nguồn để sử dụng.

Báo cáo từng tin: `outputs/data_quality/presentation_audit.csv`. Thống kê:
`outputs/data_quality/presentation_summary.json`; checksum catalog mới trong
`data/catalog_manifest.json`. Trường `salary_changed` so với nguồn gốc;
`salary_changed_since_last_run` chỉ tính thay đổi so với lần chạy script gần nhất.
Các bản CSV/manifest trước sửa được lưu tại `.cache/presentation-before-*`.
`.gitattributes` giữ nguyên byte của catalog và snapshot đánh giá khi clone
trên Windows/Linux, tránh Git đổi xuống dòng làm lệch checksum trong manifest.

Nguồn dữ liệu và giấy phép:
https://huggingface.co/datasets/tinixai/vietnamese-job-descriptions
https://huggingface.co/datasets/tinixai/vietnamese-job-descriptions/tree/679c3a17347ff6ce769d9bf510c122a087493cf6
CC BY-NC 4.0, tin lịch sử chưa xác minh còn tuyển.
