"""Chọn phần văn bản Việt/Anh của cùng 500 tin, không tạo thêm tin mới."""
from __future__ import annotations
import pandas as pd


def localize_jobs(jobs: pd.DataFrame, language: str) -> pd.DataFrame:
    localized = jobs.copy(deep=True)
    if language == "en":
        for column in ("Title", "Skills", "Domain", "Job_Description", "Salary", "Requirements", "Company"):
            english = f"{column}_EN"
            if english in localized:
                localized[column] = localized[english]
    return localized
