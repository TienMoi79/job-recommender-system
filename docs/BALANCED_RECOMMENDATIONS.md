# Gợi ý kết hợp chuyên môn và khoảng cách — 11/11/2026

Theo góp ý giảng viên, sau khi ghép CV, phần đối chiếu hiển thị theo thứ tự:

1. **Cân bằng chuyên môn và khoảng cách**: tối đa 3 công việc kết hợp hai yếu tố.
2. Hai nhóm đối chiếu phía dưới: **Phù hợp chuyên môn nhất** và **Gần nơi ở nhất trong các việc đạt ngưỡng**.

## Cách tính

Giữ nguyên `score` là điểm chuyên môn CV từ Hybrid Engine. Trên các công việc
đã qua kiểm tra nguyện vọng nghề và ngưỡng phù hợp, có khoảng cách xác định:

```text
d = khoảng cách ước tính giữa hai điểm đại diện vùng, đơn vị km
P = 1 / (1 + d / 50)
B = 0,70 × score + 0,30 × P
```

- `P` là `proximity_score`; `B` là `balanced_score`, đều từ 0 đến 1 với đầu vào hợp lệ.
- Ở cùng điểm đại diện, P=1; 50 km có P=0,5; 100 km có P≈0,333. 50 km là
  tham số giảm điểm, không phải khoảng cách tối đa để công việc được gợi ý.
- Chọn cách giảm liên tục để không tạo ranh giới cứng ở một số km, và không
  phụ thuộc công việc xa nhất/gần nhất trong mỗi lượt truy vấn.
- Sắp B giảm dần; đồng điểm thì ưu tiên điểm CV, khoảng cách và Job_ID ổn định.
- Không sửa sáu thành phần CV, không dùng rating nhu cầu hoặc điểm hành vi thay
  cho điểm chuyên môn trong phép cân bằng này. Điểm nhu cầu trong danh sách
  chính tiếp tục có vai trò riêng.
- 70/30 và 50 km là **cấu hình thử nghiệm**, chưa được tối ưu bằng ground truth
  hoặc chứng minh làm tăng chất lượng xếp hạng. B không phải xác suất tuyển dụng.

Ví dụ minh họa với các khoảng cách giả định để tính tay:

| Công việc | Điểm CV | Khoảng cách vùng | P | B |
|---|---:|---:|---:|---:|
| A — chuyên môn cao, xa | 0,90 | 1.200 km | 0,040 | 0,642 |
| B — chuyên môn khá, cùng vùng | 0,70 | 0 km ở điểm đại diện | 1,000 | 0,790 |
| C — gần hơn A, chuyên môn tốt | 0,85 | 50 km | 0,500 | 0,745 |

Thứ tự kết hợp là B, C, A; nhóm chuyên môn riêng vẫn ưu tiên A. Việc gần không
mặc định thắng: nếu điểm CV của B chỉ 0,20 thì B=0,44 và A vẫn xếp trên B.
Đầu vào phải là pool đã đạt ngưỡng CV; không lấy việc sai nghề vào chỉ vì gần.

## Trường hợp thiếu thông tin

- Chưa xác nhận nơi ở: `balanced=[]`, `near_home=[]`; nhóm chuyên môn vẫn có
  thể có kết quả. UI yêu cầu xác nhận nơi ở.
- Tin thiếu vùng có tọa độ hoặc chỉ remote: không gán 0 km và không bịa điểm
  cân bằng. Tin vẫn có thể xuất hiện trong nhóm chuyên môn nếu đủ phù hợp.
- Tin nhiều vùng: dùng vùng có khoảng cách đã biết gần nhất.
- Cùng vùng: UI ghi “Cùng khu vực nơi ở”, không gọi đó là 0 km đi làm.
- Pool rỗng: cả ba nhóm rỗng; không thêm tin ngoài điều kiện để lấp chỗ.

Đây là **đối chiếu toàn quốc** như phiên bản trước. Danh sách chính bên dưới
vẫn theo **nơi muốn làm việc** đã chọn; nơi ở chỉ là mốc so khoảng cách.
Haversine giữa điểm vùng không phải đường đi, thời gian di chuyển hoặc địa chỉ
nhà–công ty. UI giữ ghi chú này và có mục mở rộng giải thích tỷ trọng 70/30.

## Mã nguồn, API và notebook

- `job_proximity.py`: `BALANCE_POLICY`, `compare_options` trả thêm `balanced`
  và `balance_policy`, giữ nguyên `best_fit`/`near_home`.
- `web_preview.py`: luồng so CV toàn quốc hiện có tiếp tục gọi hàm so sánh;
  danh sách chính giữ lọc vùng, `/api/cv/match` bổ sung dữ liệu nhóm mới qua hàm này.
- `web_ui/app.js`, `styles.css`: nhóm kết hợp ở trên, 3 thẻ trên desktop,
  2 thẻ trên màn hình vừa, 1 thẻ trên mobile; hai nhóm cũ ở dưới. Có nhãn Việt/Anh.
- `lab3_jobvista.ipynb`: demo lần lượt `balanced`, `best_fit`, `near_home`,
  hiển thị điểm CV, điểm gần, điểm cân bằng và chính sách.

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_demand_proximity tests.test_web_preview -v
node --test tests/test_personalization.cjs
```

Các ca kiểm tra gồm lựa chọn thỏa hiệp khác cả hai cực, ưu tiên chuyên môn,
thiếu nơi ở, tin remote/thiếu vùng, nhiều vùng, đồng điểm, điểm gốc không bị sửa,
không trộn nhu cầu, lọc vùng danh sách chính và thứ tự hiển thị/Việt–Anh/escape HTML.

## Backup trước khi sửa

Đã chép 11 tệp liên quan (mã Python, frontend, test, README, tài liệu, notebook)
và đối chiếu SHA-256 từng tệp trước thay đổi vào:

```text
D:\Trí tuệ nhân tạo và ứng dụng\ProJeat_backup_20261111_before_balanced_recommendations_143544
D:\Trí tuệ nhân tạo và ứng dụng\ProJeat_backup_20261111_before_balanced_recommendations_143544.zip
```

`manifest.json` trong backup giữ checksum. Đây là bản sao các tệp liên quan đợt
này, không phải bản sao mới của toàn bộ virtualenv/cache; bản backup toàn dự án
trước Lab 3 vẫn được giữ bên ngoài repo.
