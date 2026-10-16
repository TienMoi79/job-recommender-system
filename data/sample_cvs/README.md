# 10 CV giả lập để thử JobVista

Có 10 hồ sơ khác nhau, mỗi hồ sơ gồm 3 định dạng cùng nội dung: Word, PDF có chữ và ảnh PNG (30 tệp). Tất cả là dữ liệu giả lập; email dùng tên miền example.com, không phải liên hệ thật.

## Cách thử

Mở http://127.0.0.1:8000 → Tìm việc với CV → chọn tệp → Đọc và phân tích CV → kiểm tra nơi muốn làm → Tìm công việc phù hợp. Có thể dùng cùng mã CV ở ba định dạng để so sánh việc đọc chữ trực tiếp và OCR.

PDF trong thư mục pdf là PDF có chữ. Ảnh PNG dùng để thử OCR. Để thử PDF scan, in/chuyển ảnh PNG sang PDF bằng trình đọc ảnh; không cần dùng CV thật.

| Mã | Vị trí | Nơi muốn làm | Kinh nghiệm | Ca kiểm tra |
|---|---|---|---|---|
| CV01 | Data Analyst | Hà Nội | 1 năm | Ưu tiên các việc phân tích dữ liệu hoặc BI tại Hà Nội. |
| CV02 | Backend Developer Python | Hà Nội | 2 năm | Ca ưu tiên nguyện vọng: địa chỉ TP. Hồ Chí Minh nhưng phải gợi ý Hà Nội trước. |
| CV03 | Frontend Developer React | Sài Gòn | 2 năm | Chuẩn hóa tên Sài Gòn thành vùng Hồ Chí Minh, ưu tiên công việc Frontend/React. |
| CV04 | AI Engineer | Đà Nẵng | 3 năm | Ưu tiên nhóm AI/Machine Learning tại Đà Nẵng, không trả việc ngoài vùng đã chọn. |
| CV05 | Data Engineer | TP. Hồ Chí Minh | 3 năm | Phân biệt Data Engineer với Data Analyst, dù cùng có Python và SQL. |
| CV06 | Tester QA Engineer | Nha Trang | 2 năm | Nhận diện Nha Trang là nhóm Nha Trang/Khánh Hòa; ưu tiên Tester/QC trong vùng. |
| CV07 | DevOps Engineer | Cần Thơ | 3 năm | Ưu tiên DevOps/Cloud tại Cần Thơ, đối chiếu kỹ năng hạ tầng thay vì chỉ Python. |
| CV08 | Embedded Software Engineer | Hải Phòng | 3 năm | Ưu tiên Embedded/C++ tại Hải Phòng; kiểm tra C++ không bị đồng nhất với C hay C#. |
| CV09 | UI/UX Designer | Nha Trang | 2 năm | CV tiếng Anh: ưu tiên Preferred location Nha Trang thay vì Address Da Nang; nhận diện UI/UX. |
| CV10 | Cybersecurity Specialist | Quảng Ninh | 2 năm | Ca không có tin: catalog 500 tin hiện không có vùng Quảng Ninh. Chọn vùng này phải trả rỗng, không tự chuyển vùng. |

## Khi đối chiếu kết quả

- CV02 ở TP. Hồ Chí Minh nhưng muốn làm Hà Nội; vùng được gợi ý phải là Hà Nội.
- CV09 viết bằng tiếng Anh, ở Da Nang nhưng muốn làm Nha Trang; nguyện vọng phải được ưu tiên.
- CV10 là ca kết quả rỗng có chủ đích: catalog hiện không có tin Quảng Ninh. Giữ nguyên vùng Quảng Ninh để thử; hệ thống không được tự đưa việc ở nơi khác vào.
- Các CV còn lại nên có tín hiệu nghề nghiệp và kỹ năng liên quan, nhưng không bắt buộc một Job_ID luôn đứng đầu. Đây là kiểm tra chức năng, chưa phải bộ nhãn đánh giá chất lượng mô hình.
- OCR có thể sai dấu tiếng Việt hoặc bỏ sót chữ. Hãy xem nội dung đã đọc và xác nhận vùng trước khi tìm. Mức kinh nghiệm là nội dung so khớp, không phải điều kiện loại ứng viên cứng.
- File expected_profiles.json lưu kỹ năng, mã vùng và đường dẫn của mỗi hồ sơ để đối chiếu tự động.
