"""Chuẩn hóa phần đọc cho người dùng, độc lập với văn bản dùng để tính embedding.

Không suy đoán tiền tệ/kỳ trả, không coi phụ cấp hay bảo hiểm là lương. Văn bản
nguồn được chia đoạn bằng quy tắc; chỉ renderer mới sinh HTML đã escape.
"""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from html import unescape
from html.parser import HTMLParser
import re
from locations import plain_text


class _TextParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True);self.parts=[];self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style'):self.skip+=1
        elif not self.skip:
            if tag=='li':self.parts.append('\n• ')
            elif tag in ('p','div','br','h1','h2','h3','h4','tr'):self.parts.append('\n')
    def handle_endtag(self,tag):
        if tag in ('script','style'):self.skip=max(0,self.skip-1)
        elif not self.skip and tag in ('p','div','li','h1','h2','h3','h4','tr'):self.parts.append('\n')
    def handle_data(self,data):
        if not self.skip:self.parts.append(data)


HEADINGS=(
    'THỜI GIAN VÀ ĐỊA ĐIỂM LÀM VIỆC','CƠ CHẾ THU NHẬP, PHÚC LỢI',
    'MÔ TẢ CÔNG VIỆC','YÊU CẦU ỨNG VIÊN','YÊU CẦU CÔNG VIỆC',
    'THU NHẬP VÀ PHÚC LỢI','CHẾ ĐỘ ĐÃI NGỘ','MÔI TRƯỜNG LÀM VIỆC',
    'THỜI GIAN LÀM VIỆC','ĐỊA ĐIỂM LÀM VIỆC','QUYỀN LỢI','PHÚC LỢI','YÊU CẦU',
    'Job Description','Responsibilities','Requirements','Qualifications','Benefits',
    'Must-have','Nice-to-have',
)


def format_job_text(value: str) -> str:
    """Khôi phục cấu trúc khi nguồn cũng đã bị dồn đoạn.

    Giữ nguyên nội dung/từ ngữ; tách tiêu đề, bullet và ranh giới câu rõ ràng.
    Không cắt dấu gạch trong back-end/Node.js, khoảng 3 - 4 năm hoặc 12h–13h.
    Với nguồn không dấu chấm dùng ngắt mềm ở các cụm nhiệm vụ Việt rõ nghĩa.
    Đây là phục hồi bằng quy tắc, không tuyên bố khôi phục layout gốc chính xác.
    """
    text=unescape(str(value or '')).replace('\r\n','\n').replace('\r','\n')
    if re.search(r'</?(?:p|div|li|ul|br|h[1-6]|script|style)\b',text,re.I):
        parser=_TextParser();parser.feed(text);text=''.join(parser.parts)
    text=re.sub(r'[\t\xa0 ]+',' ',text)
    protected={}
    def protect(match):
        token=f'\x00URL{len(protected)}\x00';protected[token]=match.group(0);return token
    text=re.sub(r'https?://\S+|www\.\S+|\b[\w-]+\.(?:com|org|net|io|vn)\b(?:/\S*)?|\b(?:Node|Vue|Next|React)\.js\b',protect,text,flags=re.I)
    # Nguồn còn có câu dính liền như "CSV).Clean" / "tin cậy.Xử lý".
    # Chỉ thêm khoảng ngắt nếu ký tự tiếp theo thực sự là chữ hoa Unicode.
    def no_space_break(match):
        return match[0]+'\n' if text[match.end():match.end()+1].isupper() else match[0]
    text=re.sub(r'(?<=[\w)])([.!?;:：])(?=[^\W\d_])',no_space_break,text)
    # Tránh lồng các heading ngắn trong heading dài vừa nhận diện.
    markers={}
    for index,heading in enumerate(HEADINGS):
        pattern=r'(?<!\w)'+re.escape(heading)+r'(?!\w)\s*[:：]?'
        token=f'\x00H{index}\x00'
        def mark(match):
            label=match.group(0).strip().rstrip(':：')
            before=text[:match.start()].rstrip(' ')
            after=text[match.end():]
            heading_like=(label.isupper() or label[:1].isupper() and
                          (not before or before.endswith(('\n','.','!','?')) or match.group(0).rstrip().endswith((':','：'))
                           or re.match(r'\s*[-–—•]',after)))
            if not heading_like:return match.group(0)
            markers[token]=label;return '\n'+token+'\n'
        text=re.sub(pattern,mark,text,flags=re.I)
    # Bullet có khoảng trắng hai bên, ký tự sau phải bắt đầu một mục (không số).
    text=re.sub(r'(?:^|[ \n])[-–—•▪●·∙*+]\s+(?=[A-ZÀ-ỸĐ(])','\n• ',text)
    text=re.sub(r'(?:^|[ \n])(\d{1,2}[.)])\s+(?=[A-ZÀ-ỸĐ(])',r'\n\1 ',text)
    # Dấu câu chỉ tách trước chữ hoa: không đụng dấu thập phân, email, Node.js,
    # dấu ba chấm, viết tắt e.g./i.e. hay token công nghệ C#/CI/CD.
    text=re.sub(r'(?<![.\d])([.!?;])\s+(?=[A-ZÀ-ỸĐ])',r'\1\n',text)
    # Một số nguồn ghép các nhiệm vụ không có dấu câu (ví dụ tin WOORI).
    text=re.sub(r'(?<=[a-zà-ỹđ)\]])\s+(?=(?:Trao đổi|Lên ý tưởng|Nghiệp vụ|Phân tích[ ,]|Thiết kế UX/UI|So sánh, đối chiếu|Các yêu cầu khác))','\n',text)
    for token,heading in markers.items():text=text.replace(token,heading+':')
    lines=[line.strip() for line in text.splitlines() if line.strip()]
    # Nhiều tin nguồn đã mất cả dấu chấm, không chỉ mất newline. Với dòng dài,
    # nhận diện cụm mở đầu nhiệm vụ có chữ hoa; không sửa câu từ của ứng viên.
    tasks=('Thiết kế','Xây dựng','Đóng vai trò','Xử lý','Trình bày','Phối hợp','Tham gia','Quản lý',
           'Giám sát','Cập nhật','Làm việc','Triển khai','Chịu trách nhiệm','Đề xuất','Sửa chữa',
           'Đảm bảo','Định hướng','Đánh giá','Tích hợp','Áp dụng','Theo dõi','Hỗ trợ','Nghiên cứu',
           'Phát triển','Tối ưu','Kiểm thử','Lập trình','Cải thiện','Tư vấn','Thực hiện','Hướng dẫn',
           'Vận hành','Bảo trì','Báo cáo','Phân tích','Lập kế hoạch','Lập roadmap',
           'Build','Develop','Design','Maintain','Manage','Collaborate','Participate','Implement',
           'Support','Ensure','Fix','Integrate','Monitor','Create','Work','Review','Analyze',
           'Research','Lead','Optimize','Test','Prepare','Contribute','Plan','Provide','Report','Deliver')
    boundary=r'(?<=\w) +(?=(?:'+'|'.join(re.escape(task) for task in tasks)+r')\b)'
    lines=[re.sub(boundary,'\n',line) if len(line)>280 else line for line in lines]
    text='\n'.join(lines)
    for token,value in protected.items():text=text.replace(token,value)
    return text


@dataclass(frozen=True)
class SalaryDisplay:
    vi: str
    en: str
    status: str
    currency: str=''
    period: str='unspecified'
    minimum: float|None=None
    maximum: float|None=None
    evidence: str=''


def _number(value):
    value=value.strip()
    if re.fullmatch(r'\d{1,3}(?:[.,]\d{3})+',value):value=re.sub(r'[.,]','',value)
    elif ',' in value and '.' in value:
        # Dấu cuối cùng là dấu thập phân; các dấu còn lại là nhóm nghìn.
        separator=',' if value.rfind(',')>value.rfind('.') else '.'
        value=value.replace('.' if separator==',' else ',','').replace(separator,'.')
    else:value=value.replace(',','.')
    try:return Decimal(value)
    except InvalidOperation:return None


def _decimal(value,language):
    return format(value.normalize(),'f').replace('.',',' if language=='vi' else '.')


def normalize_salary(raw: str, evidence: str='') -> SalaryDisplay:
    """VND/đồng/nghìn/triệu -> triệu VND; USD giữ USD. Không tự quy đổi tháng.

    Những số không có đơn vị (105/500/50-300), 0, khoảng đảo chiều và số liệu
    thiếu chỉ hiện chưa rõ. Nguồn có lương thỏa thuận rõ ràng có thể khôi phục
    nhãn đó, nhưng không lấy số tiền bảo hiểm/phụ cấp làm lương cơ bản.
    """
    unknown=lambda status:SalaryDisplay('Chưa rõ mức lương','Salary not specified',status)
    text=plain_text(unescape(str(raw or '')))
    context=plain_text(evidence)
    negotiated=re.search(r'(?:muc luong(?: cung)?|luong(?: cung)?|salary|base salary)\s*[:：()\-–]*\s*(?:\(\s*)?(?:thoa thuan|thuong luong|negotiable)',context)
    if re.search(r'thoa thuan|thuong luong|negotiable|canh tranh|competitive',text):
        return SalaryDisplay('Lương thỏa thuận' if 'canh tranh' not in text and 'competitive' not in text else 'Lương cạnh tranh',
                             'Negotiable' if 'canh tranh' not in text and 'competitive' not in text else 'Competitive','negotiable')
    compound=re.fullmatch(r'(.+?)\s*[x×]\s*(\d+)\s*thang luong/nam(?:\s*\+\s*thuong)?',text)
    if compound:
        base=normalize_salary(compound[1])
        if base.status=='normalized':
            bonus_vi=' + thưởng' if '+ thuong' in text else '';bonus_en=' + bonus' if bonus_vi else ''
            return SalaryDisplay(base.vi+f' × {compound[2]} tháng lương/năm'+bonus_vi,base.en+f' × {compound[2]} salary payments/year'+bonus_en,
                                 'normalized',base.currency,base.period,base.minimum,base.maximum,str(raw))
    periods={'tháng':('month','thang|month|monthly'),'tuần':('week','tuan|week|weekly'),
             'ngày':('day','ngay|day|daily'),'giờ':('hour','gio|hour|hourly'),'năm':('year','nam|year|annual')}
    period=next(((vi,en) for vi,(en,pattern) in periods.items() if re.search(r'\b(?:'+pattern+r')\b',text)),None)
    matches=re.findall(r'\d+(?:[.,]\d+)*',text)
    usd=bool(re.search(r'\busd\b|\$',text))
    million=bool(re.search(r'\b(?:trieu|million)\b|(?<=\d)\s*tr\b',text))
    thousand=bool(re.search(r'\b(?:nghin|ngan|thousand)\b|(?<=\d)k\b',text))
    dong=bool(re.search(r'\bvnd\b|\bvndong\b|\bdong\b|\d\s*d\b|₫',text))
    if not matches or len(matches)>2 or sum((usd,million,thousand))>1:
        return unknown('missing_or_ambiguous')
    numbers=[_number(value) for value in matches]
    if any(value is None or value<=0 for value in numbers) or len(numbers)==2 and numbers[0]>numbers[1]:
        return unknown('invalid_amount')
    if not (usd or million or thousand or dong):
        if negotiated:return SalaryDisplay('Lương thỏa thuận','Negotiable','negotiable_from_source',evidence=negotiated.group(0))
        return unknown('missing_unit')
    # Nếu nguồn nói lương thỏa thuận nhưng salary lại ghép hai khoản phụ cấp
    # nghìn/ngày-tuần thì đánh dấu nhiễu. Không làm điều này với lương triệu
    # hoặc USD hợp lệ chỉ vì nguồn cũng cho phép đàm phán.
    if negotiated and thousand and period and period[1] in ('day','week','hour'):
        allowances=[]
        for match in re.finditer(r'(?:phu cap|ho tro|tro cap|allowance)\b[^;\n]{0,45}?(\d+(?:[.,]\d+)*)\s*(k\b|nghin\b|ngan\b|vnd\b|d\b)',context):
            value=_number(match[1])
            if value is not None:allowances.append(value*(Decimal('.001') if match[2] in ('k','nghin','ngan') else Decimal('.000001')))
        if allowances and all(value*Decimal('.001') in allowances for value in numbers):
            return SalaryDisplay('Lương thỏa thuận','Negotiable','allowance_conflict',evidence=negotiated.group(0))
    factor=Decimal(1) if usd or million else Decimal('0.001') if thousand else Decimal('0.000001')
    amounts=[value*factor for value in numbers]
    qualifier=''
    if re.search(r'\b(?:duoi|under|below)\b',text):qualifier='below'
    elif re.search(r'\b(?:tren|over|above)\b',text):qualifier='above'
    elif re.search(r'\b(?:up to|upto|toi da|den)\b',text):qualifier='upper'
    elif re.search(r'\b(?:tu|from)\b',text):qualifier='lower'
    def label(language):
        values=[_decimal(value,language) for value in amounts]
        amount='–'.join(values)
        if qualifier:amount=({'vi':{'upper':'Tối đa ','lower':'Từ ','below':'Dưới ','above':'Trên '},'en':{'upper':'Up to ','lower':'From ','below':'Below ','above':'Over '}}[language][qualifier])+amount
        unit=' USD' if usd else ' triệu' if language=='vi' else ' million VND'
        suffix=('/'+(period[0] if language=='vi' else period[1])) if period else ''
        return amount+unit+suffix
    return SalaryDisplay(label('vi'),label('en'),'normalized','USD' if usd else 'VND',period[1] if period else 'unspecified',
                         float(amounts[0]),float(amounts[-1]),str(raw))


def presentation_fields(description,requirements,salary,context=''):
    parsed=normalize_salary(salary,context)
    return {'Job_Description_Display':format_job_text(description),
            'Requirements_Display':format_job_text(requirements),
            'Salary_Original':str(salary or ''),'Salary':parsed.vi,'Salary_EN':parsed.en,
            'Salary_Status':parsed.status,'Salary_Currency':parsed.currency,'Salary_Period':parsed.period,
            'Salary_Min':parsed.minimum,'Salary_Max':parsed.maximum,'Salary_Evidence':parsed.evidence}


def display_job_field(row,field):
    """Chọn layout nguồn chỉ khi ngôn ngữ hiển thị vẫn dùng chính nội dung đó.

    Bản tóm tắt Việt/Anh phải định dạng từ bản tóm tắt, không lộ nguyên văn
    tiếng Việt ở chế độ English hoặc thay tóm tắt Việt bằng source English.
    """
    current=str(row.get(field,''));original=str(row.get('Original_'+field,current))
    layout=row.get(field+'_Display','')
    if layout and ' '.join(current.split())==' '.join(original.split()):return str(layout)
    return format_job_text(current)
