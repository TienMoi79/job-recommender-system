"""Tách và đối chiếu kinh nghiệm; giá trị không rõ không bị biến thành 0 năm.

Chỉ nhận các câu nêu rõ số năm kinh nghiệm/thực hành. Không lấy tuổi, năm tốt
nghiệp hay cộng thời gian các dự án vì các khoảng này có thể trùng nhau.
"""
from dataclasses import dataclass
import math
import re
from locations import plain_text


@dataclass(frozen=True)
class ExperienceEstimate:
    years: float | None
    status: str


def extract_experience(text: str) -> ExperienceEstimate:
    normalized = plain_text(text)
    # Chưa có kinh nghiệm là thông tin xác định, khác với không đọc được.
    if re.search(r"\b(chua co kinh nghiem|no (?:professional |work )?experience|zero years? of experience)\b", normalized):
        return ExperienceEstimate(0.0, "explicit")
    number = r"(\d{1,2}(?:[.,]\d+)?)"
    suffix = r"\+?\s*(?:nam|years?|yrs?)\b"
    # Ưu tiên tổng kinh nghiệm được ghi rõ, tránh lấy số năm của từng kỹ năng.
    total = re.findall(r"(?:tong(?: cong)?|total|overall)\s*(?:kinh nghiem|experience)?\s*[:：]?\s*" + number + suffix, normalized)
    if total:
        values = {float(value.replace(',', '.')) for value in total}
    else:
        patterns = [
            number + suffix + r"\s*(?:of\s+)?(?:(?:professional|work|hands-on)\s+)?(?:kinh nghiem|experience|practice|thuc hanh)\b",
            r"(?:kinh nghiem|experience)\s*[:：]\s*" + number + suffix,
        ]
        values = {float(value.replace(',', '.')) for pattern in patterns for value in re.findall(pattern, normalized)}
        # Không rút một đầu của '2-3 năm' thành một con số chính xác.
        if re.search(number + r"\s*[-–]\s*" + number + suffix, normalized):
            return ExperienceEstimate(None, "ambiguous")
    values = {value for value in values if 0 <= value <= 60}
    if len(values) == 1:
        return ExperienceEstimate(values.pop(), "explicit")
    return ExperienceEstimate(None, "ambiguous" if values else "unknown")


def experience_fit(candidate_years: float | None, required_years: float, *, known=True) -> tuple[float, str]:
    """Điểm mềm [0,1]. Thiếu một năm giảm vừa phải; vượt mức không bị phạt.

    Tin chỉ có cận dưới (không đủ thông tin kết luận overqualified). Không rõ
    kinh nghiệm trả trạng thái unknown; bộ xếp hạng sẽ bỏ thành phần này và
    chuẩn hóa lại các trọng số còn lại, không cộng điểm giả cho dữ liệu thiếu.
    """
    if candidate_years is None or not known:
        return 0.0, "unknown"
    if not math.isfinite(candidate_years) or not 0 <= candidate_years <= 60:
        raise ValueError("experience_years must be finite and between 0 and 60")
    gap = max(0.0, float(required_years) - candidate_years)
    return math.exp(-gap / 2.0), "meets_minimum" if gap == 0 else "below_minimum"
