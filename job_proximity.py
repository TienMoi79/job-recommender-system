"""Đối chiếu phù hợp nghề và gần nơi ở bằng điểm đại diện vùng GeoNames.

Không biết địa chỉ nhà/công ty cụ thể nên chỉ ước tính đường chim bay giữa
hai điểm đại diện thành phố. Cùng vùng không có nghĩa là đi làm 0 km.
"""
from pathlib import Path
import json
import math
import re
from locations import find_regions, plain_text

COORDINATES=json.loads((Path(__file__).resolve().parent/'data/region_coordinates.json').read_text(encoding='utf-8'))['regions']

# Chính sách thử nghiệm, ưu tiên chuyên môn; không phải trọng số học từ dữ liệu.
# 50 km là tham số làm giảm điểm gần, KHÔNG phải giới hạn loại công việc.
BALANCE_POLICY={'fit_weight':.7,'proximity_weight':.3,'distance_scale_km':50.,
                'version':'career-distance-v1'}


def home_locations(text):
    result=[]
    lines=text.splitlines()
    for index,line in enumerate(lines):
        norm=plain_text(line)
        if re.search(r'preferred|desired|noi muon|mong muon|muon lam viec|work location',norm):continue
        if re.search(r'dia chi|address|noi o|hien song|currently live|current location',norm):
            result.extend(find_regions(line) or find_regions(' '.join(lines[index+1:index+2])))
    return list(dict.fromkeys(code for code in result if code!='remote'))


def distance_km(left,right):
    if left not in COORDINATES or right not in COORDINATES:return None
    a,b=COORDINATES[left],COORDINATES[right]
    lat1,lat2=map(math.radians,[a['lat'],b['lat']]);dlon=math.radians(b['lon']-a['lon'])
    value=math.sin((lat2-lat1)/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 6371.0088*2*math.asin(min(1,math.sqrt(value)))


def annotate_distance(jobs,home_region):
    result=[]
    for job in jobs:
        candidates=[(code,distance_km(home_region,code)) for code in job['regions'] if code!='remote']
        known=[(code,d) for code,d in candidates if d is not None]
        nearest=min(known,key=lambda item:item[1]) if known else (None,None)
        result.append({**job,'distance_km':round(nearest[1]) if nearest[1] is not None else None,
                       'distance_region':nearest[0],'same_region':home_region in job['regions'] if home_region else False,
                       'home_region':home_region,'distance_kind':'region_centers' if nearest[1] is not None else 'unknown'})
    return result


def compare_options(jobs,home_region,top_n=3):
    """Ba góc nhìn trên cùng pool đã đạt ngưỡng nghề nghiệp của CV Engine.

    Điểm gần = 1/(1+d/50); điểm cân bằng = 70% CV + 30% điểm gần.
    Chỉ cân bằng khi có nơi ở và khoảng cách hợp lệ, không gán khoảng cách 0
    cho tin thiếu địa điểm/remote. Không sửa điểm CV hoặc trộn điểm nhu cầu.
    Khoảng cách vùng không phải thời gian hay số km đi làm thực tế.
    """
    annotated=annotate_distance(jobs,home_region)
    best=sorted(annotated,key=lambda job:(-job.get('score',0.),job['id']))[:top_n]
    located=[job for job in annotated if home_region and job['distance_km'] is not None]
    near=sorted(located,
                key=lambda job:(job['distance_km'],-job.get('score',0.),job['id']))[:top_n]
    balanced=[]
    for job in located:
        proximity=1/(1+job['distance_km']/BALANCE_POLICY['distance_scale_km'])
        fit=float(job.get('score',0.))
        value=BALANCE_POLICY['fit_weight']*fit+BALANCE_POLICY['proximity_weight']*proximity
        balanced.append({**job,'proximity_score':proximity,'balanced_score':value})
    balanced=sorted(balanced,key=lambda job:(-job['balanced_score'],-job.get('score',0.),job['distance_km'],job['id']))[:top_n]
    return {'home_region':home_region,'balanced':balanced,'balance_policy':dict(BALANCE_POLICY),
            'best_fit':best,'near_home':near,
            'scope':'nationwide_comparison','distance_kind':'region_centers',
            'note':'Approximate straight-line distance between representative city points, not commuting distance.'}
