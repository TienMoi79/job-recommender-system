"""Chạy thử Giai đoạn 1 và 2, xuất kết quả để đối chiếu trong báo cáo."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from generate_mock_data import DATA_DIR, MockDataGenerator
from job_recommender import DEFAULT_MODEL, JobRecommenderSystem


def show_results(title: str, results: pd.DataFrame) -> None:
    print(f"\n{title}")
    columns = ["Rank", "Job_ID", "Title", "Experience_Years", "Similarity_Score"]
    print(results[columns].to_string(index=False, float_format=lambda value: f"{value:.4f}"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Demo hệ gợi ý việc làm dựa trên nội dung.")
    parser.add_argument("--backend", choices=["tfidf", "sentence-transformers"], default="sentence-transformers")
    parser.add_argument("--job-id", default="J001")
    parser.add_argument("--top-n", type=int, default=5)
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    parser.add_argument("--model-name", default=DEFAULT_MODEL)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--cv-file", type=Path, help="CV dạng văn bản UTF-8; bỏ qua để chạy 3 CV mẫu.")
    args = parser.parse_args()

    jobs_path, resumes_path = args.data_dir / "jobs.csv", args.data_dir / "resumes.json"
    # Chỉ tự tạo khi chưa có cả hai file, tránh ghi đè dữ liệu người dùng đã sửa.
    if not jobs_path.exists() and not resumes_path.exists():
        MockDataGenerator().save(args.data_dir)
    if not jobs_path.exists() or (args.cv_file is None and not resumes_path.exists()):
        parser.error("Thiếu dữ liệu. Hãy chạy generate_mock_data.py hoặc cung cấp đủ file.")

    print(f"Đang khởi tạo backend: {args.backend}...", flush=True)
    if args.backend == "sentence-transformers":
        print("Lần đầu có thể cần tải trọng số mô hình từ Hugging Face.", flush=True)
    engine = JobRecommenderSystem.from_csv(
        jobs_path, backend=args.backend, model_name=args.model_name, device=args.device
    )
    print(f"Backend: {engine.backend}")
    output_dir = Path(__file__).resolve().parent / "outputs" / args.backend
    output_dir.mkdir(parents=True, exist_ok=True)
    similar = engine.recommend_similar_jobs(args.job_id, top_n=args.top_n)
    show_results(f"Việc làm tương tự {args.job_id}:", similar)
    similar.to_csv(output_dir / "similar_jobs.csv", index=False, encoding="utf-8-sig")

    if args.cv_file:
        resumes = [{"Resume_ID": "CUSTOM", "Profile": "CV từ file", "CV_Text": args.cv_file.read_text(encoding="utf-8-sig")}]
    else:
        resumes = json.loads(resumes_path.read_text(encoding="utf-8"))
    matches = []
    for resume in resumes:
        result = engine.match_cv_to_jobs(resume["CV_Text"], top_n=args.top_n)
        show_results(f"{resume['Resume_ID']} — {resume['Profile']}:", result)
        result.insert(0, "Resume_ID", resume["Resume_ID"])
        matches.append(result)
    pd.concat(matches, ignore_index=True).to_csv(
        output_dir / "cv_matches.csv", index=False, encoding="utf-8-sig"
    )
    print(f"\nKết quả đã lưu tại: {output_dir}")


if __name__ == "__main__":
    main()
