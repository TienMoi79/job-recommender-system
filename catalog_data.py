"""Chọn phần văn bản Việt/Anh của cùng 500 tin, không tạo thêm tin mới."""
from __future__ import annotations
import pandas as pd
import re

from resume_profile import ROLES
from locations import region_label


def localize_jobs(jobs: pd.DataFrame, language: str) -> pd.DataFrame:
    localized = jobs.copy(deep=True)
    # Giữ văn bản gốc cho bộ hybrid: đổi ngôn ngữ hiển thị không thay đổi
    # tài liệu được so khớp. Không cần sửa hoặc nhân đôi catalog CSV trên đĩa.
    for field in ("Title", "Domain", "Job_Description", "Requirements", "Company"):
        if field in jobs and f"Original_{field}" not in localized:
            localized[f"Original_{field}"] = jobs[field]
    if language == "en":
        for column in ("Title", "Skills", "Domain", "Job_Description", "Salary", "Requirements", "Company"):
            english = f"{column}_EN"
            if english in localized:
                localized[column] = localized[english]
    elif "Role_Code" in localized:
        # Tin IT thực tế thường có mô tả tiếng Anh. Giữ nguyên bản gốc trong
        # CSV, nhưng bản Việt dùng tóm tắt có cấu trúc để giao diện dễ đọc.
        # Không gọi dịch vụ dịch bên ngoài hoặc tuyên bố đây là bản dịch toàn văn.
        roles = {role[0]: role for role in ROLES}
        for index, row in localized.iterrows():
            description = str(row["Job_Description"])
            if not re.search(r"[À-ỹ]", description) and re.search(r"\b(the|with|and|responsibilities|develop)\b", description, re.I):
                role = roles.get(str(row["Role_Code"]))
                title = role[1] if role else str(row["Title"])
                locations = ", ".join(region_label(code, "vi") for code in str(row["Region_Codes"]).split(";"))
                experience = f"{float(row['Experience_Years']):g} năm (cận dưới)" if row.get("Experience_Known", False) else "chưa rõ"
                localized.at[index, "Job_Description"] = (
                    f"{row['Company']} tuyển vị trí {title} tại {locations}. "
                    f"Lĩnh vực: {row['Domain']}. Kỹ năng được nhắc trong tin gốc: {row['Skills']}. "
                    f"Yêu cầu kinh nghiệm: {experience}. Đây là tóm tắt từ mô tả gốc tiếng Anh; "
                    "xem bản ghi nguồn để đọc đầy đủ nhiệm vụ và yêu cầu."
                )
            requirements = str(row.get("Requirements", ""))
            if not re.search(r"[À-ỹ]", requirements) and re.search(r"\b(the|with|and|experience|skills|knowledge)\b", requirements, re.I):
                localized.at[index, "Requirements"] = (
                    f"Kỹ năng được nhắc trong tin gốc: {row['Skills']}. "
                    "Yêu cầu gốc bằng tiếng Anh; xem bản ghi nguồn để đối chiếu đầy đủ điều kiện."
                )
    return localized
