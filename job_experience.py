"""Đọc cận dưới kinh nghiệm tuyển dụng, khác với số năm tự khai trong CV.

Một số dòng nguồn ghi experience_level='Không' nhưng yêu cầu nằm trong JD.
Chỉ dùng số gắn với kinh nghiệm, không lấy tuổi, năm học, thưởng/thử việc.
Giữ chuỗi nguồn và bằng chứng để việc sửa dữ liệu có thể đối chiếu.
"""
from dataclasses import dataclass
import re
from locations import plain_text


@dataclass(frozen=True)
class JobExperience:
    years: float = 0.0
    known: bool = False
    source: str = 'unknown'
    evidence: str = ''  # Đoạn nguồn chuẩn hóa không dấu; toàn văn gốc vẫn giữ.


NUMBER = r'\d{1,2}(?:[.,]\d+)?'
DURATION = re.compile(
    rf'(?<![\w\d.,])(?P<low>{NUMBER})\s*'
    rf'(?:(?:[-–—~]|den|to)\s*(?P<high>{NUMBER})\s*)?'
    r'\+?\s*(?P<unit>nam|years?|yrs?|thang|months?)\b\+?')
EXPERIENCE = r'(?:kinh\s+(?:nghiem|lam viec)|experience|exeperience)'
PREFERRED = r'(?:uu tien|loi the|diem cong|nice\s*[- ]\s*to\s*[- ]\s*have|preferred|optional|a plus|khong bat buoc|not required)'
NO_EXPERIENCE = re.compile(
    rf'(?:khong (?:yeu cau|can|doi hoi)(?:\s+co)?\s+{EXPERIENCE}|'
    rf'chua co\s+kinh nghiem|no (?:prior |previous |work |professional )?experience (?:is )?(?:required|necessary))')


def metadata_experience(text: str) -> JobExperience:
    """Trường kinh nghiệm có cấu trúc; 'Không' đơn lẻ không có nghĩa 0 năm."""
    norm = plain_text(text)
    if not norm:
        return JobExperience()
    if NO_EXPERIENCE.search(norm) or norm in ('khong yeu cau','no experience','none required'):
        return JobExperience(0.,True,'experience_level',norm)
    match=DURATION.search(norm)
    if not match:
        return JobExperience()
    years=float(match['low'].replace(',','.'))
    if match['unit'] in ('thang','month','months'):
        years/=12
    before=norm[:match.start()]
    if re.search(r'(?:duoi|toi da|khong qua|under|up to|less than|[≤<])\s*$',before) and not re.search(r'(?:khong duoi|not less than)\s*$',before):
        years=0.  # Chỉ lưu cận dưới; không biến 'dưới 1 năm' thành tối thiểu 1.
    return JobExperience(years,True,'experience_level',norm)


def _requirements_section(description: str) -> str:
    """Không quét lịch sử công ty/phúc lợi như điều kiện tuyển dụng.

    Nếu JD gộp toàn văn, chỉ xét phần có nhãn yêu cầu. Không có nhãn thì giữ
    unknown thay vì đoán từ một con số trong phần giới thiệu công ty.
    """
    norm=plain_text(description)
    heading=re.search(r'\b(?:yeu cau(?: ung vien| cong viec)?|requirements?|required qualifications|qualifications|required skills\s*(?:&|and)\s*experience|your skills and experience|what you bring|who you are)\b',norm)
    if not heading:
        return ''
    section=norm[heading.end():]
    ending=re.search(r'\b(?:quyen loi|phuc loi|dai ngo|benefits|compensation|what we offer|why you.ll love)\b',section)
    return section[:ending.start()] if ending else section


def text_experience(text: str, source: str) -> JobExperience:
    norm=plain_text(text)
    # Tách các bullet/câu trước khi tìm số để dấu hiệu 'ưu tiên' của một điều
    # kiện không bị áp lên câu bắt buộc kế tiếp. Không cắt dấu thập phân 1.5.
    clauses=re.split(r'\n|;|(?<=[.!?])\s+|\s+[•+]\)?\s*|\s+-\s+',norm)
    candidates=[]
    cursor=0
    for clause in clauses:
        offset=norm.find(clause,cursor)
        cursor=offset+len(clause)
        if not re.search(EXPERIENCE,clause):
            continue
        for match in DURATION.finditer(clause):
            before=clause[max(0,match.start()-85):match.start()]
            after=clause[match.end():match.end()+95]
            # Chỉ nhận số ngay trước 'năm kinh nghiệm' hoặc sau nhãn kinh
            # nghiệm, cho phép 'kinh nghiệm ... tối thiểu 2 năm'.
            follows=re.match(rf'\s*(?:(?:of|work|working|professional|hands[- ]on)\s+){{0,3}}{EXPERIENCE}\b',after)
            precedes=re.search(rf'{EXPERIENCE}(?:\s+(?:lam viec|thuc te|lap trinh))?\s*[:：]?\s*(?:(?:co|tu|tren|toi thieu|it nhat|minimum|min|at least|over|more than)\s*)*$',before)
            if not follows and not precedes:
                continue
            # '2 năm kinh nghiệm (ưu tiên React)' vẫn bắt buộc 2 năm; ưu tiên
            # chỉ bổ nghĩa React. Một mục Nice-to-have kế tiếp cũng không làm
            # câu tối thiểu trước nó thành tùy chọn.
            after_context=re.split(r'nice\s*[- ]\s*to\s*[- ]\s*have|preferred qualifications|required qualifications|must\s*[- ]\s*have|bat buoc\s*:|[()]',after)[0]
            if re.search(PREFERRED,before) or re.search(r'loi the|diem cong|preferred|optional|a plus|not required|khong bat buoc',after_context):
                continue  # Ưu tiên không phải số năm tối thiểu bắt buộc.
            # Các tiêu đề 'Preferred qualifications'/'Nice-to-have' có thể
            # áp dụng cho nhiều câu, tới khi có tiêu đề bắt buộc kế tiếp.
            prefix=norm[:offset+match.start()]
            blocks=list(re.finditer(r'preferred qualifications|nice\s*[- ]\s*to\s*[- ]\s*have|uu tien\s*:|required qualifications|must\s*[- ]\s*have|bat buoc\s*:',prefix))
            if blocks and re.match(r'preferred|nice|uu tien',blocks[-1].group()):
                continue
            years=float(match['low'].replace(',','.'))
            if match['unit'] in ('thang','month','months'):
                years/=12
            if re.search(r'(?:duoi|toi da|khong qua|under|up to|less than|[≤<]=?)\s*$',before) and not re.search(r'(?:khong duoi|not less than)\s*$',before):
                years=0.
            if years<=60:
                candidates.append(JobExperience(years,True,source,clause[max(0,match.start()-100):match.end()+150]))
        zero=NO_EXPERIENCE.search(clause)
        if zero and not re.search(r'khong (?:nhan|tuyen)|not accept',clause):
            if not re.match(r'\s*(?:su dung|ve|voi|in|with)\b',clause[zero.end():]):
                candidates.append(JobExperience(0.,True,source,clause[max(0,zero.start()-40):zero.end()+80]))
    if not candidates:
        return JobExperience()
    values={candidate.years for candidate in candidates}
    # Tin tuyển đồng thời Junior/Senior không có một mức tối thiểu chung rõ.
    if len(values)>1 and (0. in values or len(set(re.findall(r'\b(?:junior|middle|senior|intern|fresher)\b',norm)))>1):
        return JobExperience(source='ambiguous',evidence=' | '.join(c.evidence for c in candidates)[:600])
    # Nhiều điều kiện bắt buộc cùng lúc: đáp ứng cận dưới lớn nhất. Không cộng
    # các khoảng kinh nghiệm vì chúng có thể chồng lấn thời gian.
    return max(candidates,key=lambda candidate:candidate.years)


def resolve_job_experience(raw: str, requirements: str='', description: str='') -> JobExperience:
    metadata=metadata_experience(raw)
    if metadata.known:
        return metadata
    required=text_experience(requirements,'requirements')
    if required.known or required.source=='ambiguous':
        return required
    return text_experience(_requirements_section(description),'job_description')
