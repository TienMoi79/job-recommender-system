"""Tạo catalog 500 tin IT THẬT từ snapshot công khai, không nhân bản mock data.

Nguồn: tinixai/vietnamese-job-descriptions (CC BY-NC 4.0).
File Parquet nguồn chỉ ở .cache, CSV đã chuẩn hóa và manifest được đưa vào repo.
Mọi thông tin bổ sung suy ra (kỹ năng, nhóm nghề, số năm) có quy tắc và provenance.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from html import unescape
import json
from pathlib import Path
import random
import re

import pandas as pd
import pyarrow.parquet as pq
import requests

from locations import find_regions, plain_text, region_label
from resume_profile import extract_skills, identify_roles, ROLES

SOURCE = "tinixai/vietnamese-job-descriptions"
REVISION = "679c3a17347ff6ce769d9bf510c122a087493cf6"
LICENSE = "CC-BY-NC-4.0"
QUOTAS = {"ha_noi": 170, "ho_chi_minh": 170, "da_nang": 70,
          "khanh_hoa": 25, "can_tho": 20, "hai_phong": 20, "hue": 10,
          "binh_duong": 5, "dong_nai": 5, "bac_ninh": 5}


def clean(value) -> str:
    text = unescape(str(value or ""))
    text = re.sub(r"<[^>]*>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def experience_years(raw: str) -> tuple[float, bool]:
    """Không dùng 0 để khẳng định không cần kinh nghiệm nếu dữ liệu không rõ."""
    norm = plain_text(raw)
    if "khong yeu cau" in norm or "chua co kinh nghiem" in norm:
        return 0.0, True
    if "duoi 1" in norm:
        return 0.0, True  # Cận dưới, vẫn giữ nguyên chuỗi nguồn trong Experience_Text.
    match = re.search(r"(\d+(?:[.,]\d+)?)\s*(?:[-–]\s*\d+\s*)?(?:nam|years?|year|\+)", norm)
    return (float(match.group(1).replace(",", ".")), True) if match else (0.0, False)


def salary_english(raw: str) -> str:
    norm = plain_text(raw)
    if not raw or norm in ("dang cap nhat", "thoa thuan", "thuong luong"):
        return "Not specified" if norm != "thoa thuan" else "Negotiable"
    if "trieu" in norm:
        numbers = re.findall(r"\d+(?:[.,]\d+)?", raw)
        return "VND " + " - ".join(numbers[:2]) + " million" if numbers else "Not specified"
    if "usd" in norm or "$" in raw:
        return "USD " + " - ".join(re.findall(r"\d+(?:[.,]\d+)?", raw)[:2])
    return "See source listing"


def company_english(raw: str) -> str:
    """Giữ tên riêng thương hiệu; bỏ tiền tố pháp nhân Việt trong bản tóm tắt."""
    name = plain_text(raw)
    name = re.sub(r"^(?:cong ty\s+)?(?:co phan|tnhh|trach nhiem huu han)?\s*", "", name)
    return name.title() or "Source employer"


class PublicJobCatalogBuilder:
    """Đọc nguồn theo batch để không nạp hơn 600 nghìn mô tả vào RAM cùng lúc."""

    def download(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            return
        url = f"https://huggingface.co/datasets/{SOURCE}/resolve/{REVISION}/data.parquet"
        temporary = path.with_suffix(".download")
        with requests.get(url, stream=True, timeout=(20, 120)) as response:
            response.raise_for_status()
            with temporary.open("wb") as output:
                for chunk in response.iter_content(1024 * 1024):
                    output.write(chunk)
        temporary.replace(path)

    def normalize_row(self, raw: dict, row_index: int) -> dict | None:
        title, company = clean(raw.get("job_title")), clean(raw.get("company_name"))
        if plain_text(company).strip(": ") in ("quy mo", "dia chi", "cong ty", "company", "n/a", "trang chu"):
            return None
        roles = identify_roles(title)
        industry = plain_text(clean(raw.get("job_industry")))
        industry_is_it = "it phan mem" in industry or "cong nghe thong tin" in industry
        if not roles and not industry_is_it:
            return None
        description, requirements = clean(raw.get("job_description")), clean(raw.get("requirements"))
        location = clean(raw.get("location"))
        regions = [code for code in find_regions(location) if code != "remote"]
        if not title or not company or len(description) < 160 or not regions:
            return None
        skills = extract_skills(title + " " + requirements + " " + description)
        if not roles and industry_is_it and len(skills) >= 3:
            roles = [ROLES[-1]]
        if not roles or len(skills) < 2:
            return None
        role = roles[0]
        company_en = company_english(company)
        years, known = experience_years(clean(raw.get("experience_level")))
        if years > 15:
            return None
        main_region = next((code for code in regions if code in QUOTAS), None)
        if main_region is None:
            return None
        technologies = [skill for skill in skills if skill in ("Python", "Java", "C#", "C++", "PHP", "React", "Flutter", "SQL")]
        # Tiêu đề gốc giữ nguyên ở bản Việt; bản Anh dùng tiêu đề tiếng Anh gốc
        # nếu có, nếu không thì dùng tên nhóm nghề + công nghệ đọc được từ nguồn.
        en_title = title if not re.search(r"[À-ỹ]", title) else role[2] + (" (" + ", ".join(technologies[:3]) + ")" if technologies else "")
        known_text = f"{years:g} years (parsed lower bound)" if known else "Not specified"
        en_description = (
            f"{company_en} advertises a {role[2]} role in {', '.join(region_label(code, 'en') for code in regions)}. "
            f"Professional area: {role[4]}. Skills mentioned in the source listing: {', '.join(skills)}. "
            f"Experience requirement: {known_text}. This is a structured English summary of the source posting, "
            "not a full translation of its responsibilities or a newly verified vacancy."
        )
        # Khi mô tả gốc đã là tiếng Anh, dùng toàn văn thay vì bỏ chi tiết.
        if not re.search(r"[À-ỹ]", description) and re.search(r"\b(the|with|and|responsibilities|develop)\b", description, re.I):
            en_description = description
        return {
            "Title": title, "Title_EN": en_title, "Skills": "; ".join(skills),
            "Experience_Years": years, "Experience_Known": known,
            "Experience_Text": clean(raw.get("experience_level")) or "Chưa rõ",
            "Domain": role[3], "Domain_EN": role[4], "Role_Code": role[0],
            "Job_Description": description, "Job_Description_EN": en_description,
            "Requirements": requirements,
            "Requirements_EN": f"Skills mentioned: {', '.join(skills)}. Experience: {known_text}.",
            "Company": company, "Company_EN": company_en,
            "Location": location, "Region_Codes": ";".join(regions),
            "Primary_Region": main_region, "Salary": clean(raw.get("salary")) or "Đang cập nhật",
            "Salary_EN": salary_english(clean(raw.get("salary"))),
            "Employment_Type": clean(raw.get("job_type")),
            "Source_Industry": clean(raw.get("job_industry")),
            "Source_Year": int(raw.get("year") or 0), "Source_Row_ID": str(raw["id"]),
            "Source_Row_Index": row_index, "Source_Dataset": SOURCE,
            "Source_Revision": REVISION, "Source_License": LICENSE,
            "Source_URL": f"https://huggingface.co/datasets/{SOURCE}/viewer/default/train?row={row_index}",
        }

    def build(self, source_path: Path, output_dir: Path, count: int = 500) -> pd.DataFrame:
        if count != 500:
            raise ValueError("Catalog hiện dùng kế hoạch phân bổ đúng 500 tin.")
        pools = {region: [] for region in QUOTAS}
        seen, source_index, eligible = set(), 0, 0
        for batch in pq.ParquetFile(source_path).iter_batches(batch_size=512):
            for raw in batch.to_pylist():
                index = source_index
                source_index += 1
                row = self.normalize_row(raw, index)
                if row is None:
                    continue
                fingerprint = sha256(plain_text(row["Company"] + " " + row["Title"] + " " + row["Location"] + " " + row["Job_Description"]).encode()).hexdigest()
                if fingerprint in seen:
                    continue
                seen.add(fingerprint)
                eligible += 1
                pool = pools[row["Primary_Region"]]
                # Giữ đủ dự phòng để lấy mẫu đa dạng, không giữ toàn bộ nguồn.
                if len(pool) < max(QUOTAS[row["Primary_Region"]] * 4, 100):
                    row["Content_Fingerprint"] = fingerprint
                    pool.append(row)
        rng = random.Random(42)
        selected, remaining = [], []
        for region, quota in QUOTAS.items():
            pool = pools[region]
            # Các nhóm nghề khác nhau được xen kẽ để không lấy toàn Java/Tester.
            groups = {}
            for row in pool:
                groups.setdefault(row["Role_Code"], []).append(row)
            for group in groups.values():
                rng.shuffle(group)
            diverse = []
            while any(groups.values()):
                for group in groups.values():
                    if group:
                        diverse.append(group.pop())
            selected += diverse[:quota]
            remaining += diverse[quota:]
        if len(selected) < count:
            rng.shuffle(remaining)
            selected += remaining[:count - len(selected)]
        if len(selected) != count:
            raise ValueError(f"Chỉ có {len(selected)} tin hợp lệ; không tự tạo thêm dữ liệu giả.")
        for index, row in enumerate(selected, 1):
            row["Job_ID"] = f"VN{index:04d}"
        jobs = pd.DataFrame(selected)
        columns = ["Job_ID", "Title", "Skills", "Experience_Years", "Domain", "Job_Description"]
        jobs = jobs[columns + [column for column in jobs.columns if column not in columns]]
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / "jobs_catalog.csv"
        temporary_csv = output_dir / "jobs_catalog.tmp.csv"
        jobs.to_csv(temporary_csv, index=False, encoding="utf-8-sig")
        temporary_csv.replace(path)
        manifest = {
            "dataset": SOURCE, "revision": REVISION, "license": LICENSE,
            "source_url": f"https://huggingface.co/datasets/{SOURCE}",
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "source_rows_scanned": source_index, "eligible_unique_rows": eligible,
            "selected_rows": len(jobs), "selection_seed": 42,
            "requested_quotas": QUOTAS,
            "actual_region_counts": dict(Counter(jobs["Primary_Region"])),
            "role_counts": dict(Counter(jobs["Role_Code"])),
            "company_count": jobs["Company"].nunique(),
            "unknown_experience_count": int((~jobs["Experience_Known"]).sum()),
            "csv_sha256": sha256(path.read_bytes()).hexdigest(),
            "english_content": "Source English descriptions when available; otherwise rule-based structured summaries, not full translations.",
            "skills": "Dictionary-derived from source title, description and requirements; not exhaustive annotations.",
            "vacancy_status": "Historical public dataset; no claim that listings are currently open.",
        }
        (output_dir / "catalog_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        return jobs


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path(".cache/tinix-jobs.parquet"))
    parser.add_argument("--output", type=Path, default=Path("data"))
    args = parser.parse_args()
    builder = PublicJobCatalogBuilder()
    builder.download(args.source)
    result = builder.build(args.source, args.output)
    print(json.dumps({"rows": len(result), "regions": result["Primary_Region"].value_counts().to_dict(),
                      "companies": result["Company"].nunique()}, ensure_ascii=False))
