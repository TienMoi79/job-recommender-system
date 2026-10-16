# Benchmark thử nghiệm cho hệ gợi ý

30 CV văn bản giả lập khác nhau, chia cố định 10 dev và 20 test. Không dùng
30 bản Word/PDF/PNG của 10 CV mẫu làm 30 ứng viên độc lập. File benchmark được
đóng băng trước khi chạy so sánh A/B/C; mã SHA256 catalog giúp phát hiện nhãn cũ.

Nhãn pilot do trợ lý biên soạn từ các tin công khai đã rà chức danh, kỹ năng,
kinh nghiệm. Đây KHÔNG phải nhãn của chuyên gia tuyển dụng hoặc ứng viên thật.
Grade 2 là phù hợp cao với ý định trong CV; grade 1 là nghề liên quan nhưng có
điều kiện cần kiểm tra. Qrels dương còn thưa: tin chưa được gán nhãn bị tính 0
khi chấm, nên số liệu chỉ là chẩn đoán trên pilot, không chứng minh độ chính xác
thực tế. Báo cáo JudgedCoverage@5 cho biết bao nhiêu tin top 5 có nhãn dương.
Cần mở rộng pool và nhờ người độc lập rà nhãn trước kết luận nghiên cứu.

Precision@5 đếm grade >= 1 chia cố định 5; StrictPrecision@5 đếm grade 2;
NDCG@5 dùng gain 2^grade - 1 và discount log2(rank+1). CV T20 yêu cầu Quảng
Ninh không có tin, được đo Empty_Accuracy riêng và loại khỏi macro NDCG/Precision.
Không làm đẹp kết quả bằng cách chia Precision cho số tin thực sự trả về.

Mỗi profile_group chỉ thuộc một split. Không chỉnh trọng số dựa vào test.
So sánh chạy cùng catalog, cùng CV, cùng lọc vùng và top 5. A là TF-IDF cũ;
B là semantic cũ; C là hybrid thêm kỹ năng, kinh nghiệm, lọc gần trùng và đa dạng.
Độ trễ khởi tạo model/index được báo riêng với thời gian truy vấn khi đã sẵn sàng.
