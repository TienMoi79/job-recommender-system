"""Giai đoạn 1: tạo dữ liệu giả lập có thể tái lập, không cần tải dữ liệu ngoài."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


DATA_DIR = Path(__file__).resolve().parent / "data"
JOB_COLUMNS = [
    "Job_ID", "Title", "Skills", "Experience_Years", "Domain", "Job_Description"
]


class MockDataGenerator:
    """Đóng gói việc tạo và lưu dữ liệu để tái sử dụng trong demo và kiểm thử.

    Các bản ghi được viết có chủ đích thay vì chọn từ khóa ngẫu nhiên: những
    nghề gần nhau chia sẻ kỹ năng thực tế, nhưng vẫn có nhiệm vụ riêng biệt.
    Toàn bộ công việc và hồ sơ dưới đây đều là dữ liệu giả lập.
    """

    def create_jobs(self) -> pd.DataFrame:
        """Trả về 20 việc làm. Skills là chuỗi phân cách bằng dấu chấm phẩy.

        Experience_Years được hiểu là số năm kinh nghiệm tối thiểu trong tin.
        Dùng nội dung tiếng Anh nhất quán giúp baseline TF-IDF dễ kiểm chứng;
        tên kỹ thuật vẫn được giữ nguyên trong CV và mô tả việc làm.
        """
        rows = [
            ("J001", "Data Analyst", "SQL; Python; Pandas; Excel; Power BI", 1,
             "Data Analytics",
             "Analyze sales and customer data using SQL and Python Pandas. Clean datasets, "
             "build Power BI dashboards and Excel reports, explain business trends."),
            ("J002", "Business Intelligence Analyst", "SQL; Power BI; Tableau; Excel; DAX", 2,
             "Data Analytics",
             "Build business intelligence dashboards and sales reports with Power BI, "
             "DAX and SQL. Define business KPIs and communicate insights to stakeholders."),
            ("J003", "Data Scientist", "Python; Pandas; SQL; Statistics; Scikit-learn", 2,
             "Artificial Intelligence",
             "Explore customer data with Python and Pandas. Apply statistics, train machine "
             "learning models for churn prediction and measure experiments."),
            ("J004", "Data Engineer", "Python; SQL; Spark; Airflow; ETL", 2,
             "Data Engineering",
             "Develop ETL pipelines using Python, SQL, Spark and Airflow. Maintain a data "
             "warehouse and provide clean datasets for analytics and machine learning."),
            ("J005", "AI Engineer", "Python; PyTorch; Transformers; NLP; FastAPI", 2,
             "Artificial Intelligence",
             "Build NLP applications using Transformers and PyTorch. Create semantic search "
             "and recommendation models, serve machine learning predictions through FastAPI."),
            ("J006", "Machine Learning Engineer", "Python; Scikit-learn; PyTorch; Docker; MLflow", 3,
             "Artificial Intelligence",
             "Train and deploy machine learning models with Python, Scikit-learn and PyTorch. "
             "Track experiments using MLflow and package inference services with Docker."),
            ("J007", "NLP Engineer", "Python; NLP; Transformers; PyTorch; Text Classification", 2,
             "Artificial Intelligence",
             "Process text and build NLP models for text classification, semantic search "
             "and document embeddings using Python, Transformers and PyTorch."),
            ("J008", "Computer Vision Engineer", "Python; PyTorch; OpenCV; Deep Learning; CNN", 2,
             "Artificial Intelligence",
             "Build image classification and object detection systems. Prepare image datasets "
             "with OpenCV and train deep learning CNN models with PyTorch."),
            ("J009", "Python Backend Developer", "Python; FastAPI; Django; PostgreSQL; REST API", 2,
             "Software Development",
             "Develop REST API services with Python, FastAPI and Django. Design PostgreSQL "
             "databases, implement authentication and write backend unit tests."),
            ("J010", "Java Backend Developer", "Java; Spring Boot; PostgreSQL; REST API; Docker", 2,
             "Software Development",
             "Develop backend microservices and REST API endpoints with Java and Spring Boot. "
             "Optimize PostgreSQL queries and deploy services using Docker."),
            ("J011", "Node.js Backend Developer", "JavaScript; TypeScript; Node.js; Express; PostgreSQL", 1,
             "Software Development",
             "Build backend REST API services using Node.js, TypeScript and Express. "
             "Implement authentication and maintain PostgreSQL databases."),
            ("J012", "Frontend Developer", "JavaScript; TypeScript; React; HTML; CSS", 1,
             "Software Development",
             "Build responsive web interfaces using React, TypeScript, HTML and CSS. "
             "Integrate REST API endpoints and improve browser accessibility."),
            ("J013", "Full Stack Developer", "TypeScript; React; Node.js; PostgreSQL; REST API", 3,
             "Software Development",
             "Develop React web interfaces and Node.js backend services using TypeScript. "
             "Design PostgreSQL schemas and integrate REST API endpoints end to end."),
            ("J014", "Mobile Developer", "Dart; Flutter; Firebase; REST API; Android", 1,
             "Mobile Development",
             "Build Android and iOS mobile applications using Flutter and Dart. Integrate "
             "Firebase authentication, push notifications and REST API services."),
            ("J015", "DevOps Engineer", "Linux; Docker; Kubernetes; CI/CD; AWS", 2,
             "Cloud Infrastructure",
             "Automate CI/CD pipelines, containerize services with Docker and operate "
             "Kubernetes clusters on AWS. Monitor Linux servers and deployment reliability."),
            ("J016", "Cloud Engineer", "AWS; Terraform; Linux; Docker; Networking", 3,
             "Cloud Infrastructure",
             "Provision AWS cloud infrastructure with Terraform. Configure Linux servers, "
             "networking and Docker workloads, improve availability and cloud costs."),
            ("J017", "QA Automation Engineer", "Python; Selenium; Pytest; API Testing; CI/CD", 1,
             "Quality Assurance",
             "Write automated browser tests with Selenium and Python Pytest. Perform API "
             "testing and integrate regression tests into CI/CD pipelines."),
            ("J018", "Cybersecurity Analyst", "Python; Linux; SIEM; Networking; Security", 2,
             "Cybersecurity",
             "Investigate security alerts in SIEM, inspect network traffic and Linux logs. "
             "Automate incident analysis with Python and assess system vulnerabilities."),
            ("J019", "Database Administrator", "SQL; PostgreSQL; MySQL; Linux; Backup", 3,
             "Database Management",
             "Administer PostgreSQL and MySQL databases on Linux. Optimize SQL queries, "
             "configure replication and test backup and recovery procedures."),
            ("J020", ".NET Backend Developer", "C#; .NET; ASP.NET; SQL Server; REST API", 2,
             "Software Development",
             "Develop backend REST API services using C# and ASP.NET Core. Design SQL Server "
             "databases, implement authentication and maintain enterprise applications."),
        ]
        return pd.DataFrame(rows, columns=JOB_COLUMNS)

    def create_resumes(self) -> list[dict[str, str]]:
        """Ba đoạn CV theo ba hướng nghề nghiệp khác nhau để thử truy vấn."""
        return [
            {
                "Resume_ID": "CV001",
                "Profile": "Ứng viên phân tích dữ liệu",
                "CV_Text": (
                    "I am a Data Analyst with 1 year of experience in data analytics. "
                    "I use SQL, Python and Pandas to clean and analyze sales and customer data. "
                    "I build Power BI dashboards and Excel reports to explain business trends "
                    "and KPIs. I want to work in data analytics or business intelligence."
                ),
            },
            {
                "Resume_ID": "CV002",
                "Profile": "Ứng viên backend Python",
                "CV_Text": (
                    "I am a Python Backend Developer with 2 years of experience in software "
                    "development. I build REST API services using FastAPI and Django, design "
                    "PostgreSQL databases and implement authentication. I write unit tests, "
                    "use Docker and collaborate with frontend developers."
                ),
            },
            {
                "Resume_ID": "CV003",
                "Profile": "Ứng viên AI và xử lý ngôn ngữ",
                "CV_Text": (
                    "I am an AI Engineer with 2 years of experience in artificial intelligence. "
                    "I use Python, PyTorch and Transformers for NLP and text classification. "
                    "I have built semantic search, document embeddings and recommendation "
                    "models. I deploy machine learning inference services with FastAPI and Docker."
                ),
            },
        ]

    def save(self, output_dir: str | Path = DATA_DIR) -> tuple[Path, Path]:
        """CSV tương thích Excel; JSON giữ nguyên dấu tiếng Việt bằng UTF-8."""
        folder = Path(output_dir)
        folder.mkdir(parents=True, exist_ok=True)
        jobs_path, resumes_path = folder / "jobs.csv", folder / "resumes.json"
        self.create_jobs().to_csv(jobs_path, index=False, encoding="utf-8-sig")
        resumes_path.write_text(
            json.dumps(self.create_resumes(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return jobs_path, resumes_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tạo 20 việc làm và 3 CV giả lập.")
    parser.add_argument("--output-dir", type=Path, default=DATA_DIR)
    args = parser.parse_args()
    for path in MockDataGenerator().save(args.output_dir):
        print(f"Đã tạo: {path}")
