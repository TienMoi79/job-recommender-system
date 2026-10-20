"""Cá nhân hóa từ hành vi tìm kiếm, không huấn luyện lại model hay sửa catalog.

Mỗi lượt tìm gồm từ khóa và bộ lọc. Hệ thống đối chiếu lại với tin công khai,
giảm trọng số của lượt cũ, giới hạn ảnh hưởng của việc tìm lặp. Nếu có CV,
chỉ sắp xếp lại các tin đã qua ngưỡng ghép CV và lọc vùng của Hybrid Engine.
"""
from __future__ import annotations

import math
import re
import time
import pandas as pd

from locations import plain_text

DAY_MS = 86400_000


class SearchInterestRecommender:
    """CV chiếm 85%, quan tâm chiếm tối đa 15%; không diễn giải là xác suất.

    Đây là quy tắc cá nhân hóa thử nghiệm. Các điểm CV và sáu thành phần gốc
    được giữ nguyên để phần giải thích không gán điểm hành vi cho thuật toán NLP.
    Lịch sử được gửi từ từng trình duyệt, không đặt trong state/cache dùng chung.
    """
    def __init__(self, jobs: pd.DataFrame, diversifier):
        self.diversifier = diversifier
        self.lookup = {}
        for _, row in jobs.iterrows():
            self.lookup[str(row['Job_ID'])] = {
                'text': plain_text(' '.join(str(row.get(field, '')) for field in (
                    'Original_Title', 'Title_EN', 'Skills', 'Original_Domain', 'Domain_EN',
                    'Original_Company', 'Company_EN', 'Title', 'Domain', 'Company'))),
                'domain': str(row.get('Original_Domain', row['Domain'])),
                'regions': str(row.get('Region_Codes', '')).split(';'),
                'experience': float(row['Experience_Years']),
                'known': bool(row.get('Experience_Known', False)),
            }

    @staticmethod
    def active_events(events, now_ms):
        """Chỉ giữ 20 điều kiện khác nhau trong 90 ngày, bỏ tìm kiếm rỗng."""
        unique = {}
        for event in events:
            event = {**event, 'updatedAt': min(event['updatedAt'], now_ms)}
            if not (str(event.get('q', '')).strip() or event.get('region') or event.get('domain')
                    or event.get('exp') or event.get('category', 'all') != 'all'):
                continue
            age = max(0., now_ms - event['updatedAt'])
            if age > 90 * DAY_MS:
                continue
            key = (plain_text(event.get('q', '')), event.get('region', ''), event.get('domain', ''),
                   event.get('exp', ''), event.get('category', 'all'))
            if key not in unique or event['updatedAt'] > unique[key]['updatedAt']:
                unique[key] = event
        return sorted(unique.values(), key=lambda e: e['updatedAt'], reverse=True)[:20]

    def _matches(self, identifier, event):
        row = self.lookup[identifier]
        if plain_text(event.get('q', '')) not in row['text']:
            return False
        if event.get('region') and event['region'] not in row['regions']:
            return False
        if event.get('domain') and event['domain'] != row['domain']:
            return False
        exp = event.get('exp', '')
        if exp and (not row['known'] or (exp == '0' and row['experience'] >= 1)
                    or (exp == '1' and not 1 <= row['experience'] <= 3)
                    or (exp == '3' and row['experience'] <= 3)):
            return False
        category = event.get('category', 'all')
        patterns = {'data': r'du lieu|data', 'dev': r'phat trien|development|software',
                    'ai': r'tri tue|intelligence'}
        return category == 'all' or bool(re.search(patterns[category], plain_text(row['domain'])))

    def recommend(self, candidates, events, top_n=24, *, has_cv=False, now_ms=None):
        now_ms = time.time() * 1000 if now_ms is None else now_ms
        active = self.active_events(events, now_ms)
        # Không có CV: lựa chọn vùng của lượt tìm mới nhất là ràng buộc hiện tại.
        # Có CV: candidates đã được Hybrid Engine lọc theo khu vực của hồ sơ.
        location = active[0].get('region', '') if active and not has_cv else ''
        weighted = [(event, 2 ** (-max(0., now_ms-event['updatedAt']) / (14*DAY_MS)) *
                     (1 + math.log(min(max(event.get('count', 1), 1), 5)))) for event in active]
        total = sum(weight for _, weight in weighted)
        scored = []
        for job in candidates:
            if location and location not in self.lookup[job['id']]['regions']:
                continue
            interest = sum(weight for event, weight in weighted if self._matches(job['id'], event)) / total if total else 0.
            if not has_cv and interest <= 0:
                continue
            scored.append((job, interest))
        use_interest = bool(active) and any(score > 0 for _, score in scored)
        alpha = .15 if has_cv and use_interest else 0. if has_cv else 1.
        result = []
        for job, interest in scored:
            score = (1-alpha)*job.get('score', 0.) + alpha*interest
            result.append({**job, 'personal_score': round(score, 4), 'interest_score': round(interest, 4),
                           'interest_weight': alpha,
                           'personalization_mode': 'cv+interest' if has_cv and use_interest else 'cv' if has_cv else 'interest'})
        result.sort(key=lambda job: (-job['personal_score'], -job.get('score', 0.), job['id']))
        if result:
            frame = pd.DataFrame({'Job_ID': [job['id'] for job in result],
                                  'Similarity_Score': [job['personal_score'] for job in result]})
            selected = list(self.diversifier.select(frame, top_n)['Job_ID'])
            lookup = {job['id']: job for job in result}
            result = [lookup[identifier] for identifier in selected]
        return result, {'mode': 'cv+interest' if has_cv and use_interest else 'cv' if has_cv else 'interest',
                        'interest_weight': alpha, 'history_used': len(active), 'location': location}
