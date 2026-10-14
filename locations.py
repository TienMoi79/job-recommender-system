"""Chuẩn hóa địa điểm Việt Nam và nhận diện gợi ý từ CV, không suy đoán GPS.

Các nhóm dưới đây phục vụ tìm việc, không phải danh mục đơn vị hành chính.
Nha Trang được hiển thị cùng Khánh Hòa để tránh gán các tin chỉ ghi tỉnh thành
địa chỉ chính xác trong thành phố. Địa điểm nhận diện luôn cần người dùng xem lại.
"""
from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher


def plain_text(text: str) -> str:
    text = unicodedata.normalize("NFD", str(text).casefold().replace("đ", "d"))
    return " ".join("".join(c for c in text if not unicodedata.combining(c)).split())


# Mã ổn định được lưu trong CSV/state; nhãn giao diện có hai ngôn ngữ.
REGIONS = {
    "ha_noi": ("Hà Nội", "Hanoi", ("ha noi", "hanoi")),
    "ho_chi_minh": ("Hồ Chí Minh (Sài Gòn)", "Ho Chi Minh City (Saigon)",
                     ("ho chi minh", "hcm", "tphcm", "tp hcm", "sai gon", "saigon", "thu duc")),
    "da_nang": ("Đà Nẵng", "Da Nang", ("da nang", "danang")),
    "khanh_hoa": ("Nha Trang / Khánh Hòa", "Nha Trang / Khanh Hoa", ("nha trang", "khanh hoa")),
    "can_tho": ("Cần Thơ", "Can Tho", ("can tho", "cantho")),
    "hai_phong": ("Hải Phòng", "Hai Phong", ("hai phong", "haiphong")),
    "hue": ("Huế", "Hue", ("hue", "thua thien")),
    "binh_duong": ("Bình Dương", "Binh Duong", ("binh duong", "thu dau mot")),
    "dong_nai": ("Đồng Nai", "Dong Nai", ("dong nai", "bien hoa")),
    "bac_ninh": ("Bắc Ninh", "Bac Ninh", ("bac ninh",)),
    "quang_ninh": ("Quảng Ninh", "Quang Ninh", ("quang ninh", "ha long")),
    "ba_ria_vung_tau": ("Bà Rịa / Vũng Tàu", "Ba Ria / Vung Tau", ("ba ria", "vung tau")),
    "lam_dong": ("Đà Lạt / Lâm Đồng", "Da Lat / Lam Dong", ("da lat", "lam dong")),
    "quy_nhon": ("Quy Nhơn / Bình Định", "Quy Nhon / Binh Dinh", ("quy nhon", "binh dinh")),
    "nghe_an": ("Nghệ An", "Nghe An", ("nghe an", "vinh")),
    "thai_nguyen": ("Thái Nguyên", "Thai Nguyen", ("thai nguyen",)),
    "hai_duong": ("Hải Dương", "Hai Duong", ("hai duong",)),
    "hung_yen": ("Hưng Yên", "Hung Yen", ("hung yen",)),
    "long_an": ("Long An", "Long An", ("long an",)),
    "tien_giang": ("Tiền Giang", "Tien Giang", ("tien giang", "my tho")),
    "thanh_hoa": ("Thanh Hóa", "Thanh Hoa", ("thanh hoa",)),
    "quang_nam": ("Quảng Nam", "Quang Nam", ("quang nam", "hoi an")),
    "quang_ngai": ("Quảng Ngãi", "Quang Ngai", ("quang ngai",)),
    "dak_lak": ("Đắk Lắk", "Dak Lak", ("dak lak", "buon ma thuot")),
    "gia_lai": ("Gia Lai", "Gia Lai", ("gia lai", "pleiku")),
    "remote": ("Làm việc từ xa", "Remote", ("remote", "lam viec tu xa", "work from home")),
}


def region_label(code: str, language: str = "vi") -> str:
    if code not in REGIONS:
        return "Chưa xác định" if language == "vi" else "Not identified"
    return REGIONS[code][0 if language == "vi" else 1]


REGION_PATTERNS = {code: re.compile(r"(?<!\w)(?:" + "|".join(re.escape(alias) for alias in aliases) + r")(?!\w)")
                   for code, (_, _, aliases) in REGIONS.items()}


def find_regions(text: str) -> list[str]:
    """Khớp toàn từ: 'Huế' không khớp 'thuê', 'HCM' không khớp tên dài khác."""
    normalized = plain_text(text)
    found = []
    for code, pattern in REGION_PATTERNS.items():
        match = pattern.search(normalized)
        if match:
            found.append((match.start(), code))
    return [code for _, code in sorted(found)]


def _ocr_region_hint(line: str) -> list[str]:
    """Chỉ sửa gần đúng tên vùng trong dòng có nhãn địa chỉ/nguyện vọng.

    Ví dụ OCR 'Hà Ni' thiếu chữ o. Ngưỡng cao và khoảng cách với vùng thứ hai
    giúp bỏ qua kết quả mơ hồ. Đây là gợi ý phải xác nhận, không là định vị.
    """
    exact = find_regions(line)
    if exact:
        return exact
    tokens = re.findall(r"\w+", plain_text(line))
    scores = {}
    for code, (_, _, aliases) in REGIONS.items():
        for alias in aliases:
            if len(alias.split()) < 2:
                continue
            length = len(alias.split())
            for start in range(max(0, len(tokens) - length + 1)):
                candidate = " ".join(tokens[start:start + length])
                score = SequenceMatcher(None, candidate, alias).ratio()
                scores[code] = max(scores.get(code, 0), score)
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    if ranked and ranked[0][1] >= 0.84 and (len(ranked) < 2 or ranked[0][1] - ranked[1][1] >= 0.06):
        return [ranked[0][0]]
    return []


def cv_location_candidates(text: str, *, tolerant: bool = False) -> list[str]:
    """Ưu tiên nơi muốn làm, rồi địa chỉ liên hệ; không lấy tỉnh từ dự án cũ.

    OCR có thể làm mất dấu nên cùng dùng plain_text. Nếu nhiều nơi xuất hiện,
    giữ nhiều gợi ý cho người dùng chọn, không tự coi một địa chỉ là nguyện vọng.
    """
    preference, address, has_preference = [], [], False
    lines = text.splitlines()
    detect = _ocr_region_hint if tolerant else find_regions
    for index, line in enumerate(lines):
        norm = plain_text(line)
        if re.search(r"noi mu[o]?n lam|dia diem mong muon|mong muon lam|muon lam viec|preferred location|desired location|work location", norm):
            has_preference = True
            preference += detect(line) or detect(" ".join(lines[index + 1:index + 2]))
        elif re.search(r"d[i]?a chi|address|noi o|hien song|location", norm):
            address += detect(line) or detect(" ".join(lines[index + 1:index + 2]))
    # Header thường chứa địa chỉ nhưng không có nhãn; chỉ xem đầu CV để tránh
    # thành phố trong phần kinh nghiệm làm việc bị coi là nơi muốn làm.
    # Nếu dòng nguyện vọng có nhưng OCR không đọc được thành phố, không thay
    # nguyện vọng đó bằng địa chỉ nhà. Giao diện sẽ yêu cầu người dùng chọn lại.
    candidates = preference if has_preference else (address or find_regions("\n".join(lines[:8])[:500]))
    return list(dict.fromkeys(candidates))
