"""Đóng băng benchmark thử nghiệm có nhãn biên soạn, không lấy điểm model làm nhãn.

Đây là pilot với CV giả lập và qrels do trợ lý biên soạn từ chức danh, kỹ năng,
kinh nghiệm công khai. Cần người đánh giá độc lập rà lại trước khi dùng để kết
luận chất lượng tuyển dụng. Không tự gọi kết quả model là ground truth.
"""
from pathlib import Path
from hashlib import sha256
import json
import pandas as pd

ROOT=Path(__file__).resolve().parent
# Danh sách Job_ID được rà theo ý định nghề nghiệp, không sinh từ similarity.
POOLS={
 'da_hn':'0016 0032 0047 0061 0075 0088 0101 0114 0126 0138 0150 0162',
 'da_hcm':'0176 0188 0195 0213 0229 0245 0261 0275 0289 0302 0315 0328 0498',
 'da_dn':'0352 0370 0383 0394 0403 0410', 'da_ct':'0425 0435 0442',
 'back_hn':'0004 0021 0036 0051 0065 0078 0091 0104 0117 0129 0141 0153 0165',
 'front_hn':'0006 0023 0038 0053 0067 0080 0093 0106 0118 0130 0142 0154 0166',
 'front_hcm':'0174 0193 0211 0227 0243 0259 0273 0287 0300 0313 0326 0339 0492 0500',
 'ai_hn':'0011 0028 0043 0058', 'ai_dn':'0341 0359 0373 0385 0396 0404',
 'de_hn':'0010 0027 0042 0057 0493', 'de_hcm':'0177 0196 0214 0230 0246 0262 0276 0290 0303 0316 0329 0499',
 'ops_ct':'0428 0437', 'ux_hn':'0013 0029 0044 0059', 'ux_nt':'0422',
 'qa_nt':'0413', 'mobile_hn':'0008 0025 0040 0055', 'embedded_hp':'0446 0449 0452',
}

# id, split, pool, region, role, years (None=chưa nêu), skills, mô tả tự viết,
# Job_ID phù hợp cao (grade 2); các Job_ID còn lại trong pool là grade 1.
CASES=[
 ('D01','dev','da_hn','ha_noi','Data Analyst',2,'SQL Power BI Excel Tableau','Tôi tổng hợp số liệu kinh doanh, tạo dashboard và giải thích biến động doanh thu.','0047 0075 0088 0150'),
 ('D02','dev','back_hn','ha_noi','Backend Developer Python',3,'Python Django FastAPI PostgreSQL REST API Docker','Tôi xây dựng dịch vụ web, tối ưu truy vấn và kiểm thử API bằng Python.','0021 0104 0117'),
 ('D03','dev','front_hcm','ho_chi_minh','Frontend Developer React',2,'JavaScript TypeScript React HTML CSS Git','Tôi làm giao diện website tương tác và kết nối API cho ứng dụng bán hàng.','0193 0211 0287 0326'),
 ('D04','dev','ai_dn','da_nang','AI Engineer',3,'Python PyTorch TensorFlow NLP Docker','Tôi triển khai mô hình phân loại văn bản và dịch vụ xử lý ngôn ngữ.','0373 0385 0396 0404'),
 ('D05','dev','ops_ct','can_tho','DevOps Engineer',1,'Linux Kubernetes CI/CD AWS Terraform','Tôi tự động hóa kiểm thử, triển khai và cấu hình hạ tầng ứng dụng.','0437'),
 ('D06','dev','ux_hn','ha_noi','UI/UX Designer',1,'Figma UX UI','Tôi nghiên cứu người dùng, dựng wireframe và thử nghiệm prototype cho ứng dụng di động.','0013 0044 0059'),
 ('D07','dev','qa_nt','khanh_hoa','Tester QA Engineer',5,'SQL Postman API Testing Android iOS Agile','Tôi kiểm thử chức năng, đối chiếu dữ liệu và ghi nhận lỗi ứng dụng đặt phòng.','0413'),
 ('D08','dev','de_hcm','ho_chi_minh','Data Engineer',4,'Python SQL Spark Airflow ETL AWS','Tôi phát triển pipeline dữ liệu, kiểm tra chất lượng và thiết kế kho dữ liệu.','0177 0196 0276 0499'),
 ('D09','dev','mobile_hn','ha_noi','Mobile Developer Flutter',2,'Dart Flutter REST API Firebase Git iOS','Tôi phát triển ứng dụng Flutter, xử lý trạng thái và kết nối dịch vụ web.','0025 0040'),
 ('D10','dev','embedded_hp','hai_phong','Embedded Software Engineer',4,'C++ Embedded Linux','Tôi lập trình firmware, kiểm tra bộ nhớ và gỡ lỗi phần mềm thiết bị.','0446 0449 0452'),
 ('T01','test','da_hn','ha_noi','Data Analyst',1,'SQL Power BI Excel Statistics','Tôi chuyển dữ liệu bán hàng thành báo cáo theo tháng và chỉ số theo dõi vận hành.','0047 0138'),
 ('T02','test','da_hcm','ho_chi_minh','Data Analyst',2,'Python SQL Excel Power BI','I build reporting dashboards, reconcile sales figures and explain business performance to stakeholders.','0195 0261 0328'),
 ('T03','test','da_dn','da_nang','Data Analyst',3,'Python SQL Power BI Tableau','Tôi làm sạch dữ liệu, theo dõi KPI và xây dựng báo cáo trực quan cho nhóm kinh doanh.','0352 0394'),
 ('T04','test','da_ct','can_tho','Data Analyst',3,'SQL Excel Power BI Tableau Statistics','Tôi phân tích dữ liệu nhân sự, kiểm tra số liệu và lập dashboard theo bộ phận.','0425 0442'),
 ('T05','test','da_hcm','ho_chi_minh','Business Intelligence Analyst',1,'Excel Power BI Tableau','I prepare management dashboards, track business indicators and turn spreadsheet data into visual reports.','0188'),
 ('T06','test','back_hn','ha_noi','Backend Developer Python',2,'Python FastAPI Django SQL PostgreSQL Docker','I build server-side APIs, write database migrations and package web services for deployment.','0021 0117'),
 ('T07','test','back_hn','ha_noi','Backend Developer Java',4,'Java Spring Boot Spring SQL Kafka Docker','Tôi phát triển dịch vụ backend bằng Java và Spring Boot, xử lý dữ liệu và hàng đợi sự kiện.','0051 0078 0091 0165'),
 ('T08','test','back_hn','ha_noi','Backend Developer Node.js',1,'JavaScript TypeScript Node.js Express SQL Docker','Tôi viết API Node.js, xác thực người dùng và truy vấn cơ sở dữ liệu cho website.','0004 0036 0141'),
 ('T09','test','front_hn','ha_noi','Frontend Developer React',1,'JavaScript React Next.js HTML CSS REST API','I implement responsive pages, connect APIs and maintain reusable UI components.','0006 0038 0166'),
 ('T10','test','front_hcm','ho_chi_minh','Frontend Developer React',None,'JavaScript TypeScript React HTML CSS Git','Tôi phát triển giao diện web thích ứng, xử lý trạng thái tải dữ liệu và cải thiện khả năng truy cập. Tôi chưa ghi tổng thời gian kinh nghiệm trong hồ sơ.','0193 0211 0259 0287 0326 0500'),
 ('T11','test','front_hn','ha_noi','Frontend Developer Angular',3,'TypeScript Angular HTML CSS REST API Git','Tôi phát triển ứng dụng Angular, quản lý form và tích hợp API cho trang quản trị.','0053 0142'),
 ('T12','test','ai_hn','ha_noi','AI Engineer',2,'Python PyTorch Transformers NLP FastAPI','Tôi xây dựng mô hình xử lý ngôn ngữ, biểu diễn văn bản và phục vụ suy luận qua API.','0011 0028 0043 0058'),
 ('T13','test','ai_dn','da_nang','AI Engineer NLP',4,'Python PyTorch TensorFlow NLP Docker','I develop language processing models, assess text classification quality and deploy inference services.','0373 0385 0404'),
 ('T14','test','de_hn','ha_noi','Data Engineer',4,'Python SQL Spark ETL AWS Airflow','Tôi xây dựng pipeline thu thập dữ liệu và quản lý lịch xử lý dữ liệu lớn cho kho dữ liệu.','0010 0027 0042 0057'),
 ('T15','test','de_hcm','ho_chi_minh','Data Engineer',3,'SQL Azure Spark Airflow Python','I build cloud data pipelines, maintain warehouse tables and validate incoming data on Azure.','0177 0290 0303'),
 ('T16','test','qa_nt','khanh_hoa','Tester QA Engineer',5,'SQL Postman API Testing Android iOS','Tôi kiểm thử ứng dụng di động và API, ghi nhận lỗi có bước tái hiện và đối chiếu dữ liệu SQL.','0413'),
 ('T17','test','ux_nt','khanh_hoa','UI/UX Designer',2,'Figma UX UI','I create user journeys, wireframes and interactive prototypes, then refine designs from usability feedback.','0422'),
 ('T18','test','ops_ct','can_tho','DevOps Engineer',3,'Python Linux Docker Kubernetes CI/CD Terraform AWS','I automate deployment, manage infrastructure and diagnose failures using application and system logs.','0428 0437'),
 ('T19','test','embedded_hp','hai_phong','Embedded Software Engineer',4,'C++ Linux Embedded','Tôi lập trình phần mềm nhúng, gỡ lỗi bộ nhớ và kiểm tra giao tiếp giữa thiết bị với hệ thống.','0446 0449 0452'),
 ('T20','test',None,'quang_ninh','Cybersecurity Specialist',2,'Python Linux Security Networking','Tôi phân tích log và kiểm tra cấu hình an toàn; chỉ tìm công việc ở Quảng Ninh.',''),
]


def build():
    jobs=pd.read_csv(ROOT/'data/jobs_catalog.csv').fillna('')
    lookup=jobs.set_index('Job_ID')
    queries=[]
    for identifier,split,pool,region,role,years,skills,summary,strong in CASES:
        positive={'VN'+suffix:1 for suffix in POOLS.get(pool,'').split()}
        positive.update({'VN'+suffix:2 for suffix in strong.split()})
        assert set(positive).issubset(lookup.index)
        assert all(region in str(lookup.loc[job,'Region_Codes']).split(';') for job in positive)
        text=f'Vị trí ứng tuyển: {role}\nKỹ năng: {skills}\n'
        if years is not None: text+=f'Kinh nghiệm: {years} năm\n'
        text+=summary+'\nNơi muốn làm việc: '+{'ha_noi':'Hà Nội','ho_chi_minh':'Sài Gòn','da_nang':'Đà Nẵng','can_tho':'Cần Thơ','khanh_hoa':'Nha Trang','hai_phong':'Hải Phòng','quang_ninh':'Quảng Ninh'}[region]
        queries.append({'id':identifier,'profile_group':identifier,'split':split,'text':text,'region':region,'relevance':positive})
    output=ROOT/'data/evaluation';output.mkdir(exist_ok=True)
    data={'schema_version':1,'catalog_sha256':sha256((ROOT/'data/jobs_catalog.csv').read_bytes()).hexdigest(),
          'label_provenance':'assistant-curated pilot intent judgments on synthetic CVs; NOT independent human ground truth; sparse positive qrels, unjudged treated as 0 for conservative scoring',
          'grades':{'0':'not relevant or unjudged','1':'related role; some requirements need review','2':'strong fit for stated intent and skills'},
          'frozen_before_model_comparison':True,'queries':queries}
    (output/'benchmark.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    (output/'README.md').write_text('''# Benchmark thử nghiệm cho hệ gợi ý

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
''',encoding='utf-8')
    print('Frozen',len(queries),'queries')


if __name__=='__main__':build()
