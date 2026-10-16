"""Trích xuất tín hiệu nghề nghiệp minh bạch bằng từ điển, không đoán năng lực.

Từ điển alias giải quyết cách viết Việt/Anh và dấu tiếng Việt bị mất khi OCR.
Đây là baseline có thể kiểm chứng, không phải mô hình đọc CV hoàn hảo.
"""
from __future__ import annotations

from dataclasses import dataclass
import re

from locations import plain_text, cv_location_candidates


SKILLS = {
    "Python": ("python",), "SQL": ("sql",), "Pandas": ("pandas",),
    "Excel": ("excel",), "Power BI": ("power bi", "powerbi"), "Tableau": ("tableau",),
    "DAX": ("dax",), "Statistics": ("statistics", "thong ke"),
    "Scikit-learn": ("scikit-learn", "scikit learn", "sklearn"),
    "PyTorch": ("pytorch",), "TensorFlow": ("tensorflow",),
    "Transformers": ("transformers", "transformer"),
    "NLP": ("nlp", "natural language processing", "xu ly ngon ngu tu nhien"),
    "OpenCV": ("opencv",), "Deep Learning": ("deep learning", "hoc sau"),
    "Machine Learning": ("machine learning", "hoc may"), "CNN": ("cnn",),
    "FastAPI": ("fastapi",), "Django": ("django",), "Flask": ("flask",),
    "PostgreSQL": ("postgresql", "postgres"), "MySQL": ("mysql",),
    "SQL Server": ("sql server", "mssql"), "MongoDB": ("mongodb", "mongo db"),
    "Oracle": ("oracle",), "Redis": ("redis",), "Elasticsearch": ("elasticsearch",),
    "REST API": ("rest api", "restful", "restful api"), "GraphQL": ("graphql",),
    "Java": ("java",), "Spring Boot": ("spring boot", "springboot"),
    "Spring": ("spring",), "Hibernate": ("hibernate",),
    "JavaScript": ("javascript", "java script"), "TypeScript": ("typescript",),
    "Node.js": ("node.js", "nodejs", "node js"), "Express": ("express", "expressjs"),
    "React": ("react", "reactjs", "react.js"), "Vue": ("vue", "vuejs", "vue.js"),
    "Angular": ("angular", "angularjs"), "Next.js": ("next.js", "nextjs"),
    "HTML": ("html", "html5"), "CSS": ("css", "css3", "scss"),
    "C#": ("c#", "csharp"), "C++": ("c++", "cplusplus"),
    ".NET": (".net", "dotnet", "asp.net", "aspnet"),
    "PHP": ("php",), "Laravel": ("laravel",), "Go": ("golang", "go language"),
    "Ruby": ("ruby",), "Rails": ("rails",), "Kotlin": ("kotlin",), "Swift": ("swift",),
    "Dart": ("dart",), "Flutter": ("flutter",), "Firebase": ("firebase",),
    "Android": ("android",), "iOS": ("ios",), "React Native": ("react native",),
    "Linux": ("linux", "ubuntu",), "Docker": ("docker",),
    "Kubernetes": ("kubernetes", "k8s"), "CI/CD": ("ci/cd", "cicd", "ci cd"),
    "Git": ("git", "gitlab", "github"), "Jenkins": ("jenkins",),
    "AWS": ("aws", "amazon web services"), "Azure": ("azure",),
    "GCP": ("gcp", "google cloud"), "Terraform": ("terraform",),
    "Spark": ("spark", "pyspark"), "Airflow": ("airflow",), "ETL": ("etl",),
    "Kafka": ("kafka",), "Hadoop": ("hadoop",), "dbt": ("dbt",),
    "MLflow": ("mlflow",), "Selenium": ("selenium",), "Pytest": ("pytest",),
    "Playwright": ("playwright",), "Cypress": ("cypress",),
    "API Testing": ("api testing", "kiem thu api"), "Postman": ("postman",),
    "JUnit": ("junit",), "TestNG": ("testng",), "JMeter": ("jmeter",),
    "SIEM": ("siem",), "Security": ("security", "bao mat", "an ninh mang"),
    "Networking": ("networking", "tcp/ip", "mang may tinh"),
    "Figma": ("figma",), "UX": ("ux", "user experience"), "UI": ("ui", "user interface"),
    "Agile": ("agile",), "Scrum": ("scrum",), "Jira": ("jira",),
    "Business Analysis": ("business analysis", "phan tich nghiep vu"),
    "Unity": ("unity",), "Unreal Engine": ("unreal engine",), "Embedded": ("embedded", "nhung"),
}

# (mã, chức danh Việt, chức danh Anh, lĩnh vực Việt, lĩnh vực Anh, alias)
ROLES = [
    ("data_analyst", "Chuyên viên phân tích dữ liệu", "Data Analyst", "Phân tích dữ liệu", "Data Analytics", ("data analyst", "phan tich du lieu")),
    ("bi_analyst", "Chuyên viên BI", "Business Intelligence Analyst", "Phân tích dữ liệu", "Data Analytics", ("business intelligence", "bi analyst", "bao cao du lieu")),
    ("data_scientist", "Nhà khoa học dữ liệu", "Data Scientist", "Trí tuệ nhân tạo", "Artificial Intelligence", ("data scientist", "khoa hoc du lieu")),
    ("data_engineer", "Kỹ sư dữ liệu", "Data Engineer", "Kỹ thuật dữ liệu", "Data Engineering", ("data engineer", "ky su du lieu")),
    ("ai_engineer", "Kỹ sư trí tuệ nhân tạo", "AI Engineer", "Trí tuệ nhân tạo", "Artificial Intelligence", ("ai engineer", "ky su tri tue nhan tao", "ai developer", "nlp", "machine learning", "hoc may", "computer vision")),
    ("backend", "Lập trình viên Backend", "Backend Developer", "Phát triển phần mềm", "Software Development", ("backend", "back-end", "back end", "phia may chu")),
    ("frontend", "Lập trình viên Frontend", "Frontend Developer", "Phát triển phần mềm", "Software Development", ("frontend", "front-end", "front end")),
    ("fullstack", "Lập trình viên Full Stack", "Full Stack Developer", "Phát triển phần mềm", "Software Development", ("fullstack", "full-stack", "full stack")),
    ("mobile", "Lập trình viên di động", "Mobile Developer", "Phát triển ứng dụng di động", "Mobile Development", ("mobile developer", "android developer", "ios developer", "flutter", "ung dung di dong")),
    ("devops", "Kỹ sư DevOps", "DevOps Engineer", "Hạ tầng điện toán đám mây", "Cloud Infrastructure", ("devops", "site reliability", "sre")),
    ("cloud", "Kỹ sư đám mây", "Cloud Engineer", "Hạ tầng điện toán đám mây", "Cloud Infrastructure", ("cloud engineer", "cloud architect", "dien toan dam may")),
    ("qa", "Kỹ sư kiểm thử phần mềm", "Software Test Engineer", "Đảm bảo chất lượng phần mềm", "Quality Assurance", ("tester", "test engineer", "quality assurance", "qa engineer", "kiem thu", "qa/qc", "automation test", "autotest")),
    ("security", "Chuyên viên an ninh mạng", "Cybersecurity Specialist", "An ninh mạng", "Cybersecurity", ("cybersecurity", "security engineer", "security analyst", "an ninh mang", "bao mat")),
    ("dba", "Quản trị cơ sở dữ liệu", "Database Administrator", "Quản trị cơ sở dữ liệu", "Database Administration", ("database administrator", "dba", "quan tri co so du lieu")),
    ("ba", "Chuyên viên phân tích nghiệp vụ", "Business Analyst", "Phân tích nghiệp vụ", "Business Analysis", ("business analyst", "phan tich nghiep vu")),
    ("design", "Thiết kế UI/UX", "UI/UX Designer", "Thiết kế sản phẩm", "Product Design", ("ui/ux", "ux designer", "ui designer", "product designer")),
    ("embedded", "Lập trình viên nhúng", "Embedded Software Engineer", "Phát triển phần mềm nhúng", "Embedded Software", ("embedded", "lap trinh nhung", "firmware")),
    ("game", "Lập trình viên trò chơi", "Game Developer", "Phát triển trò chơi", "Game Development", ("game developer", "unity developer", "unreal", "lap trinh game")),
    ("support", "Chuyên viên hỗ trợ IT", "IT Support Specialist", "Hỗ trợ kỹ thuật", "Technical Support", ("it support", "helpdesk", "it help desk", "ho tro ky thuat", "quan tri mang", "system administrator", "nhan vien it")),
    ("software", "Kỹ sư phần mềm", "Software Engineer", "Phát triển phần mềm", "Software Development", ("software engineer", "software developer", "lap trinh vien", "ky su phan mem", "programmer", "java developer", "python developer", ".net developer", "php developer")),
]


def contains_phrase(text: str, alias: str) -> bool:
    return bool(re.search(r"(?<!\w)" + re.escape(plain_text(alias)) + r"(?!\w)", text))


def alias_pattern(aliases) -> re.Pattern:
    return re.compile(r"(?<!\w)(?:" + "|".join(re.escape(plain_text(alias)) for alias in aliases) + r")(?!\w)")


SKILL_PATTERNS = {name: alias_pattern(aliases) for name, aliases in SKILLS.items()}
ROLE_PATTERNS = {role[0]: alias_pattern(role[5]) for role in ROLES}


def extract_skills(text: str) -> list[str]:
    normalized = plain_text(text)
    return [name for name, pattern in SKILL_PATTERNS.items() if pattern.search(normalized)]


def identify_roles(text: str) -> list[tuple]:
    normalized = plain_text(text)
    roles = [role for role in ROLES if ROLE_PATTERNS[role[0]].search(normalized)]
    # Full Stack cũng có chữ 'backend/frontend' trong mô tả; không loại bỏ
    # các vai trò thực sự khác, chỉ bỏ nhóm generic nếu đã có nhóm cụ thể.
    if len(roles) > 1:
        roles = [role for role in roles if role[0] != "software"]
    return roles


@dataclass(frozen=True)
class ResumeProfile:
    text: str
    matching_text: str
    skills: tuple[str, ...]
    role_codes: tuple[str, ...]
    title_text: str
    domain_text: str
    location_candidates: tuple[str, ...]
    experience_years: float | None = None
    experience_status: str = "unknown"
    target_skills: tuple[str, ...] = ()
    role_explicit: bool = False


class ResumeAnalyzer:
    def analyze(self, text: str, *, ocr: bool = False) -> ResumeProfile:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("CV text is empty")
        lines = text.splitlines()
        # Ưu tiên dòng vị trí mong muốn trước khi tìm trong phần đầu CV.
        title_lines = [line for line in lines if re.search(
            r"vi tri ung tuyen|vi tri mong muon|desired role|target role|job title|career objective", plain_text(line))]
        roles = identify_roles(" ".join(title_lines)) if title_lines else []
        role_explicit = bool(roles)
        if not roles:
            roles = identify_roles("\n".join(lines[:12])[:1500])
        if not roles:
            roles = identify_roles(text)
        # Địa chỉ phục vụ gợi ý vùng riêng; các dòng liên hệ/cá nhân có nhãn
        # không được đưa vào vector so sánh nghề nghiệp.
        professional_lines = [line for line in lines if not re.match(
            r"^(?:dia chi|address|noi o|noi muon lam(?: viec)?|dia diem mong muon|preferred location|desired location|ho ten|full name|name|email|e-mail|dien thoai|phone|ngay sinh|date of birth|gioi tinh|gender)\s*[:：]", plain_text(line))]
        matching_text = "\n".join(professional_lines)
        matching_text = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", " ", matching_text)
        from experience_matching import extract_experience
        experience = extract_experience(text)
        return ResumeProfile(
            text=text, matching_text=matching_text, skills=tuple(extract_skills(matching_text)),
            role_codes=tuple(role[0] for role in roles),
            title_text="; ".join(role[1] + " " + role[2] for role in roles),
            domain_text="; ".join(dict.fromkeys(role[3] + " " + role[4] for role in roles)),
            location_candidates=tuple(cv_location_candidates(text, tolerant=ocr)),
            experience_years=experience.years, experience_status=experience.status,
            target_skills=tuple(extract_skills(" ".join(title_lines) if title_lines else "\n".join(lines[:2]))),
            role_explicit=role_explicit,
        )
