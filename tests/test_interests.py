"""Ca kiểm thử có đáp án xác định cho lớp cá nhân hóa hành vi."""
import time
import unittest

import pandas as pd

from hybrid_recommender import JobDiversifier
from interest_recommender import DAY_MS, SearchInterestRecommender


class InterestTests(unittest.TestCase):
    def setUp(self):
        self.now = time.time()*1000
        jobs = pd.DataFrame([
            {'Job_ID':'a','Title':'Backend Python','Skills':'Python; SQL','Domain':'Software Development',
             'Company':'A','Region_Codes':'ha_noi','Experience_Years':2,'Experience_Known':True,'Job_Description':'a'},
            {'Job_ID':'b','Title':'Frontend React','Skills':'React; CSS','Domain':'Software Development',
             'Company':'B','Region_Codes':'ha_noi','Experience_Years':0,'Experience_Known':True,'Job_Description':'b'},
            {'Job_ID':'c','Title':'Backend Python','Skills':'Python; SQL','Domain':'Software Development',
             'Company':'C','Region_Codes':'ho_chi_minh','Experience_Years':3,'Experience_Known':True,'Job_Description':'c'},
        ])
        self.engine = SearchInterestRecommender(jobs, JobDiversifier(jobs))
        self.candidates = [{'id':identifier,'score':score} for identifier,score in [('a',.7),('b',.69),('c',.9)]]

    def event(self, **changes):
        return {'q':'Python','region':'ha_noi','domain':'','exp':'','category':'all',
                'count':1,'updatedAt':self.now,**changes}

    def test_no_cv_uses_interests_and_latest_location_without_padding(self):
        result, meta=self.engine.recommend(self.candidates,[self.event()],now_ms=self.now)
        self.assertEqual([job['id'] for job in result],['a'])
        self.assertEqual(meta['mode'],'interest')
        self.assertEqual(meta['location'],'ha_noi')
        self.assertEqual(self.engine.recommend(self.candidates,[self.event(q='unrelated')],now_ms=self.now)[0],[])
        self.assertEqual(self.engine.recommend(self.candidates,[],now_ms=self.now)[0],[])

    def test_recent_interest_changes_cv_order_but_not_cv_scores_or_candidate_pool(self):
        pool=self.candidates[:2]
        result,meta=self.engine.recommend(pool,[self.event(q='React')],has_cv=True,now_ms=self.now)
        self.assertEqual([job['id'] for job in result],['b','a'])
        self.assertEqual(result[0]['score'],.69)
        self.assertAlmostEqual(result[0]['personal_score'],.85*.69+.15,places=4)
        self.assertEqual(meta['interest_weight'],.15)
        # Một lượt ở HCM không thể đưa ứng viên ngoài pool Hà Nội vào kết quả.
        other,_=self.engine.recommend(pool,[self.event(region='ho_chi_minh')],has_cv=True,now_ms=self.now)
        self.assertEqual([job['id'] for job in other],['a','b'])
        self.assertTrue(all(job['interest_weight']==0 for job in other))

    def test_no_history_preserves_cv_score_and_unknowns(self):
        result,_=self.engine.recommend(self.candidates,[],has_cv=True,now_ms=self.now)
        self.assertEqual([job['id'] for job in result],['c','a','b'])
        self.assertTrue(all(job['personal_score']==job['score'] and job['interest_weight']==0 for job in result))

    def test_recency_frequency_decay_and_expiry(self):
        events=[self.event(q='React'),self.event(updatedAt=self.now-28*DAY_MS)]
        result,_=self.engine.recommend(self.candidates,events,now_ms=self.now)
        self.assertEqual(result[0]['id'],'b')
        expired=self.event(updatedAt=self.now-91*DAY_MS)
        self.assertEqual(self.engine.recommend(self.candidates,[expired],now_ms=self.now)[0],[])
        counted,_=self.engine.recommend(self.candidates,[self.event(count=5),self.event(q='React')],now_ms=self.now)
        self.assertEqual(counted[0]['id'],'a')

    def test_duplicate_empty_and_future_events_cannot_multiply_interest(self):
        events=[self.event(),self.event(),self.event(q='',region=''),self.event(q='React',updatedAt=self.now+DAY_MS)]
        active=self.engine.active_events(events,self.now)
        self.assertEqual(len(active),2)
        self.assertTrue(all(event['updatedAt']<=self.now for event in active))

    def test_experience_and_category_are_real_filters(self):
        self.assertEqual(self.engine.recommend(self.candidates,[self.event(exp='0')],now_ms=self.now)[0],[])
        self.assertEqual(self.engine.recommend(self.candidates,[self.event(category='ai')],now_ms=self.now)[0],[])
        result,_=self.engine.recommend(self.candidates,[self.event(q='React',exp='0')],now_ms=self.now)
        self.assertEqual([job['id'] for job in result],['b'])


if __name__=='__main__':
    unittest.main()
