"""Rating nhu cầu từ lượt ghép CV, vận dụng pandas và weighted rating của Lab 3.

Không gọi số lượt bấm là số người. Actor là mã ngẫu nhiên của trình duyệt;
một actor chỉ đóng góp nguyện vọng mới nhất trong 30 ngày. Không lưu CV, tên,
email, địa chỉ hay nội dung tìm kiếm vào SQLite này.
"""
from __future__ import annotations
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from contextlib import contextmanager
import json
import sqlite3
import time
import pandas as pd
from resume_profile import ROLES

ROLE_CODES=tuple(role[0] for role in ROLES)


def weighted_rating(R, v, m, C):
    """Cùng công thức Lab 3: WR = v/(v+m)*R + m/(v+m)*C."""
    return (v/(v+m))*R+(m/(v+m))*C


class DemandRatingStore:
    def __init__(self, path: str|Path):
        self.path=Path(path)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.connect() as connection:
            connection.execute('CREATE TABLE IF NOT EXISTS demand (actor TEXT PRIMARY KEY, roles TEXT NOT NULL, updated_at REAL NOT NULL)')

    @contextmanager
    def connect(self):
        connection=sqlite3.connect(self.path,timeout=10)
        try:
            with connection:
                yield connection
        finally:
            # sqlite3.Connection.__exit__ chỉ commit/rollback, KHÔNG đóng file.
            # Đóng tường minh để không rò handle và khóa DB trên Windows.
            connection.close()

    def record(self, actor_id: str, role_codes, *, now=None):
        roles=sorted(set(role_codes)&set(ROLE_CODES))
        if not actor_id or not roles:return False
        # Không lưu mã client nguyên dạng. Đây vẫn chỉ là định danh thiết bị,
        # không thể chống giả nhiều thiết bị nếu chưa có hệ thống đăng nhập.
        actor=sha256(actor_id.encode()).hexdigest();now=time.time() if now is None else now
        with self.connect() as connection:
            connection.execute('INSERT INTO demand VALUES (?,?,?) ON CONFLICT(actor) DO UPDATE SET roles=excluded.roles,updated_at=excluded.updated_at',
                               (actor,json.dumps(roles),now))
            connection.execute('DELETE FROM demand WHERE updated_at < ?', (now-30*86400,))
        return True

    def snapshot(self, *, now=None):
        now=time.time() if now is None else now
        with self.connect() as connection:
            events=pd.read_sql_query('SELECT actor, roles, updated_at FROM demand WHERE updated_at >= ?',connection,params=(now-30*86400,))
        return self.aggregate(events)

    @staticmethod
    def aggregate(events: pd.DataFrame):
        """Lab 3: to_numeric -> sort/drop_duplicates -> explode -> groupby -> merge.

        Một CV có nhiều mục tiêu chia đều 1 lượt. R=5*nhu_cầu/N, v=N,
        C=5/K, m=5 lượt prior. Đây là độ phổ biến, KHÔNG phải số sao người dùng
        chấm hay chất lượng nhà tuyển dụng. Khác Lab: không loại nghề ít lượt;
        làm trơn và giới hạn trọng số để nghề hiếm vẫn có cơ hội.
        """
        frame=events.copy(); total=0
        if not frame.empty:
            frame['updated_at']=pd.to_numeric(frame.updated_at,errors='coerce')
            frame=frame.dropna(subset=['actor','updated_at']).sort_values('updated_at',kind='mergesort').drop_duplicates('actor',keep='last')
            frame['roles']=frame.roles.map(lambda value: sorted(set(json.loads(value) if isinstance(value,str) else value)&set(ROLE_CODES)))
            frame=frame.loc[frame.roles.map(bool)];total=len(frame)
        scores=pd.DataFrame({'role_code':ROLE_CODES})
        if total:
            frame['weight']=1/frame.roles.str.len()
            counts=frame.explode('roles').groupby('roles',as_index=False).agg(demand_count=('weight','sum'),actors=('actor','nunique'))
            scores=scores.merge(counts.rename(columns={'roles':'role_code'}),on='role_code',how='left')
        else:scores=scores.assign(demand_count=0.,actors=0)
        scores[['demand_count','actors']]=scores[['demand_count','actors']].fillna(0)
        scores['vote_average']=5*scores.demand_count/total if total else 0.
        scores['vote_count']=total
        prior=5/len(ROLE_CODES);m=5.
        scores['rating']=weighted_rating(scores.vote_average,total,m,prior) if total else 0.
        return {'total_actors':total,'window_days':30,'m':m,'C':prior,'ready':total>=5,
                'roles':scores.to_dict('records'),
                'meaning':'Browser-based implicit demand, not verified people or employer quality.'}

    @staticmethod
    def rerank(jobs, snapshot):
        by_role={row['role_code']:row for row in snapshot['roles']}
        active=snapshot['ready']
        result=[]
        for job in jobs:
            stat=by_role.get(job.get('role_code'),{})
            base=job.get('personal_score',job.get('score',0.))
            # Rating chỉ sắp lại pool đã qua kiểm tra nội dung; tuyệt đối không
            # kéo việc trái nghề lên chỉ vì nghề đang được tìm nhiều.
            value=.9*base+.1*stat.get('rating',0.)/5 if active else base
            result.append({**job,'content_score':base,'demand_rating':round(stat.get('rating',0.),4),
                           'demand_count':round(stat.get('demand_count',0.),2),
                           'demand_actors':snapshot['total_actors'],'demand_weight':.1 if active else 0.,
                           'personal_score':round(value,4)})
        return sorted(result,key=lambda job:(-job['personal_score'],-job.get('score',0.),job['id']))
