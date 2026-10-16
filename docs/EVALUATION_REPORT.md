# Báo cáo đánh giá pilot A/B/C

Ngày thực thi: 16/10/2026. Catalog 500 tin công khai; 30 CV văn bản giả lập,
10 dev và 20 test, chia theo hồ sơ. Tập test gồm 19 truy vấn có nhãn dương và
1 truy vấn Quảng Ninh không có việc. Nhãn mức 1/2 được biên soạn trước khi so
sánh, không sinh từ điểm mô hình. Không thay nhãn hoặc chỉnh trọng số theo test.

**Giới hạn chính:** nhãn do trợ lý biên soạn, chưa được chuyên gia độc lập xác
nhận; qrels còn thưa. Tin chưa được gán nhãn bị chấm 0 dù có thể phù hợp. Các
con số dưới đây là chẩn đoán pilot, không phải độ chính xác tuyển dụng thực tế.


Đã chạy lại sau bản sửa trích xuất kinh nghiệm: phục hồi 67 tin từ yêu cầu/JD,
còn 67 tin chưa xác định. Catalog giữ nguyên Job_ID và văn bản nguồn; không sửa
CV, nhãn hay trọng số để nâng điểm. Checksum mới được ghi trong benchmark và
metadata báo cáo; nhật ký ở `outputs/data_quality/experience_repairs.csv`.

## Kết quả test đã chạy với semantic thật

| Chỉ số | A TF-IDF baseline | B Semantic baseline | C Hybrid phiên bản 2 |
|---|---:|---:|---:|
| Precision@5 | 0,7474 | 0,7053 | 0,6316 |
| StrictPrecision@5, chỉ nhãn mức 2 | 0,4105 | 0,3789 | 0,4105 |
| Recall@5 | 0,6083 | 0,5830 | 0,4771 |
| NDCG@5 | 0,8456 | 0,7553 | 0,7919 |
| MRR@5 | 0,9386 | 0,9474 | 0,9211 |
| Empty Accuracy, 1 truy vấn âm | 1/1 | 1/1 | 1/1 |
| Tổng vi phạm vùng | 0 | 0 | 0 |
| Số tin trả về trung bình | 4,75 | 4,75 | 3,85 |
| Số công ty trung bình | 4,50 | 4,45 | 3,70 |
| Số bản gần trùng dư trung bình | 0,10 | 0,10 | 0,00 |
| Độ trễ trung vị khi đã sẵn sàng, ms | 35,62 | 258,63 | 288,77 |

Precision, Recall, NDCG, MRR lấy trung bình trên 19 truy vấn có nhãn dương.
Precision luôn chia cho 5, kể cả trả ít hơn 5 tin. Số tin/công ty/trùng và độ
trễ tính trên cả 20 truy vấn; truy vấn không có tin trả 0. Không lấy tỷ lệ
tin có nhãn trên số tin đã trả để gọi thay cho Precision@5.

Semantic dùng `paraphrase-multilingual-MiniLM-L12-v2` trên CPU, vector 384
chiều, tối đa 4 luồng Torch. Model trong môi trường kiểm tra phân giải đến
revision `e8f8c211226b894fcb81acc59f3b34ba3efd5f42`; hybrid ghim revision này.
Thời gian chuẩn bị ở lần chạy cuối: A khoảng 2,60 giây, B 455,46 giây, C 12,24
giây. C dùng cache embedding **tin công khai đã xây trước**, còn B tạo lại các
ma trận đặc trưng baseline; đây không phải phép so sánh khởi động lạnh công bằng.
Độ trễ phụ thuộc máy và tải CPU, không phải cam kết tốc độ triển khai.

## Diễn giải

TF-IDF đang cao nhất về P@5 và NDCG@5 trên pilot này. Hybrid có thêm đối chiếu
kinh nghiệm, kỹ năng cụ thể và giải thích, nhưng **chưa chứng minh tăng chất
lượng xếp hạng**. Không nên tuyên bố semantic hoặc hybrid luôn chính xác hơn.

Hybrid lọc theo ý định vị trí được ghi rõ, giảm tin gần trùng và không cố lấp
đủ top 5. Điều này làm số kết quả trung bình giảm; số công ty tuyệt đối cũng
giảm, nên không thể dùng bảng này để kết luận độ đa dạng công ty đã tăng. Quy
tắc thay công ty chỉ tác động khi còn lựa chọn có điểm đủ gần.

Catalog có 3 tin Embedded tại Hải Phòng cùng nhóm gần trùng. Nhãn hiện vẫn
gán dương cho từng Job_ID, nên raw Precision/Recall có thể thưởng cho baseline
trả nhiều bản của cùng tin, còn hybrid chỉ trả một bản. Đã báo thêm số bản
trùng để người đọc thấy vấn đề; không sửa nhãn test để nâng điểm hybrid.

Điểm kỹ năng cũng có giới hạn: từ điển alias chưa hiểu đầy đủ phủ định, thí dụ
“không ứng tuyển Embedded” vẫn có thể được nhận diện từ Embedded. Kỹ năng
nhận diện không phải bằng chứng ứng viên có kỹ năng. Vị trí được ghi rõ giúp
lọc ý định nghề nghiệp nhưng không thay thế việc người dùng kiểm tra nội dung.

## Tái lập và bước nghiên cứu tiếp theo

```powershell
python -m pip install -r requirements-preview.txt -r requirements-semantic.txt
python evaluation.py --split dev --output outputs/evaluation/dev
python evaluation.py --split test --output outputs/evaluation/test
```

Các tệp đi kèm:

- `outputs/evaluation/test/summary.csv`: toàn bộ chỉ số tổng hợp.
- `outputs/evaluation/test/per_query.csv`: chỉ số và số kết quả từng CV.
- `outputs/evaluation/test/predictions.json`: danh sách Job_ID và nhãn tương ứng.
- `outputs/evaluation/test/run_metadata.json`: SHA256 benchmark/catalog, trọng số,
  revision và phiên bản Python. Kết quả dev cùng cấu trúc ở thư mục `dev/`.

Trong notebook có bảng kết quả đã lưu và ô kiểm tra công thức metric bằng ví
dụ có thể tính tay. Bộ test phần mềm kiểm tra công thức, lọc vùng, thiếu dữ
liệu, không trùng và cách chuẩn hóa trọng số; số test đạt không phải độ chính
xác của mô hình.

Trước khi đưa ra kết luận nghiên cứu, cần nhờ người độc lập chấm pool top K
của cả ba hệ, bổ sung cả nhãn âm và các tin chưa được chấm, thống nhất nhãn
theo nhóm gần trùng, mở rộng CV có sự đồng ý. Sau đó chỉ hiệu chỉnh trên dev
và dùng tập test mới đã khóa. Chưa triển khai fine-tune hay Cross Encoder.
