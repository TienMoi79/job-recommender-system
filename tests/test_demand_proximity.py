"""Test rating với đáp án 8/10, không bơm dữ liệu giả vào DB của ứng dụng."""
from tempfile import TemporaryDirectory
from copy import deepcopy
import unittest
import json
import pandas as pd
from demand_rating import DemandRatingStore, weighted_rating, ROLE_CODES
from job_proximity import home_locations, distance_km, compare_options, COORDINATES
from locations import REGIONS


class DemandTests(unittest.TestCase):
    def test_eight_of_ten_and_lab3_formula(self):
        events=pd.DataFrame([{'actor':str(i),'roles':json.dumps(['data_analyst' if i<8 else 'backend']),
                              'updated_at':100+i} for i in range(10)])
        snapshot=DemandRatingStore.aggregate(events)
        data=next(row for row in snapshot['roles'] if row['role_code']=='data_analyst')
        backend=next(row for row in snapshot['roles'] if row['role_code']=='backend')
        self.assertEqual(snapshot['total_actors'],10);self.assertEqual(data['demand_count'],8)
        self.assertEqual(data['vote_average'],4.)
        self.assertAlmostEqual(data['rating'],weighted_rating(4.,10,5,5/len(ROLE_CODES)))
        self.assertGreater(data['rating'],backend['rating']);self.assertTrue(snapshot['ready'])

    def test_repeated_browser_replaces_intent_and_old_events_expire(self):
        with TemporaryDirectory() as folder:
            store=DemandRatingStore(folder+'/test.sqlite3')
            store.record('browser1',['data_analyst'],now=100)
            store.record('browser1',['backend'],now=101)
            snapshot=store.snapshot(now=102)
            self.assertEqual(snapshot['total_actors'],1)
            self.assertEqual(next(r for r in snapshot['roles'] if r['role_code']=='data_analyst')['demand_count'],0)
            self.assertFalse(snapshot['ready'])
            self.assertEqual(store.snapshot(now=102+31*86400)['total_actors'],0)
            # DB không chứa CV/nội dung tìm, chỉ actor hash, role và thời gian.
            with store.connect() as connection:
                actor,roles,_=connection.execute('SELECT * FROM demand').fetchone()
            self.assertNotEqual(actor,'browser1');self.assertEqual(json.loads(roles),['backend'])

    def test_multiple_roles_split_one_vote_and_cold_start_keeps_scores(self):
        events=pd.DataFrame([{'actor':'a','roles':['data_analyst','backend'],'updated_at':1}])
        snapshot=DemandRatingStore.aggregate(events)
        self.assertEqual(sum(row['demand_count'] for row in snapshot['roles']),1)
        jobs=[{'id':'j','role_code':'backend','score':.8}]
        result=DemandRatingStore.rerank(jobs,snapshot)
        self.assertEqual(result[0]['personal_score'],.8);self.assertEqual(result[0]['demand_weight'],0)

    def test_rating_cannot_invent_candidates_and_content_remains_primary(self):
        events=pd.DataFrame([{'actor':str(i),'roles':['data_analyst'],'updated_at':i} for i in range(10)])
        snapshot=DemandRatingStore.aggregate(events)
        result=DemandRatingStore.rerank([{'id':'a','role_code':'backend','score':.9},
                                         {'id':'b','role_code':'data_analyst','score':.3}],snapshot)
        self.assertEqual(result[0]['id'],'a');self.assertEqual(len(result),2)
        self.assertTrue(all(0<=r['personal_score']<=1 for r in result))


class ProximityTests(unittest.TestCase):
    def test_home_is_separate_from_desired_location(self):
        text='Backend Developer\nĐịa chỉ: TP.HCM\nNơi muốn làm việc: Hà Nội'
        self.assertEqual(home_locations(text),['ho_chi_minh'])
        self.assertEqual(home_locations('Preferred location: Hanoi'),[])
        self.assertEqual(home_locations('Current location: Da Nang\nDesired location: Nha Trang'),['da_nang'])

    def test_distance_is_symmetric_and_coordinates_have_provenance(self):
        self.assertEqual(set(COORDINATES),set(REGIONS)-{'remote'})
        self.assertAlmostEqual(distance_km('ha_noi','ho_chi_minh'),distance_km('ho_chi_minh','ha_noi'))
        self.assertGreater(distance_km('ha_noi','ho_chi_minh'),1000)
        self.assertIsNone(distance_km('remote','ha_noi'))

    def test_best_fit_can_be_far_but_nearest_retains_its_real_content_score(self):
        jobs=[{'id':'far','score':.9,'regions':['ha_noi']},
              {'id':'near','score':.7,'regions':['ho_chi_minh']}]
        comparison=compare_options(jobs,'ho_chi_minh')
        self.assertEqual(comparison['best_fit'][0]['id'],'far')
        self.assertEqual(comparison['near_home'][0]['id'],'near')
        self.assertEqual(comparison['near_home'][0]['score'],.7)
        self.assertTrue(comparison['near_home'][0]['same_region'])
        self.assertEqual(compare_options(jobs,None)['near_home'],[])

    def test_balanced_choice_can_be_a_compromise_instead_of_either_extreme(self):
        jobs=[{'id':'best','score':.95,'regions':['ha_noi']},
              {'id':'nearest','score':.60,'regions':['ho_chi_minh']},
              {'id':'compromise','score':.90,'regions':['binh_duong']}]
        original=deepcopy(jobs)
        result=compare_options(jobs,'ho_chi_minh')
        self.assertEqual(result['best_fit'][0]['id'],'best')
        self.assertEqual(result['near_home'][0]['id'],'nearest')
        self.assertEqual(result['balanced'][0]['id'],'compromise')
        self.assertEqual(jobs,original)  # Không sửa điểm chuyên môn/đối tượng đầu vào.
        self.assertEqual(result['balanced'][0]['score'],.90)
        scores=[j['balanced_score'] for j in result['balanced']]
        self.assertEqual(scores,sorted(scores,reverse=True))
        self.assertTrue(all(0<=s<=1 for s in scores))
        self.assertEqual(result['balance_policy']['fit_weight'],.7)

    def test_balance_prioritises_fit_and_keeps_nearby_and_demand_scores_separate(self):
        # Việc gần không mặc định thắng khi chuyên môn thấp hơn nhiều.
        jobs=[{'id':'far','score':1.,'personal_score':.1,'regions':['ha_noi']},
              {'id':'near','score':.2,'personal_score':1.,'regions':['ho_chi_minh']}]
        result=compare_options(jobs,'ho_chi_minh')
        self.assertEqual(result['balanced'][0]['id'],'far')
        near=next(j for j in result['balanced'] if j['id']=='near')
        self.assertEqual(near['proximity_score'],1.)
        self.assertAlmostEqual(near['balanced_score'],.44)
        self.assertEqual(near['score'],.2);self.assertEqual(near['personal_score'],1.)

    def test_balance_does_not_fabricate_home_or_remote_distances_and_handles_empty_pool(self):
        jobs=[{'id':'remote','score':.9,'regions':['remote']},
              {'id':'missing','score':.8,'regions':[]},
              {'id':'known','score':.7,'regions':['ha_noi']}]
        self.assertEqual(compare_options(jobs,None)['balanced'],[])
        result=compare_options(jobs,'ho_chi_minh')
        self.assertEqual([j['id'] for j in result['balanced']],['known'])
        self.assertEqual(len(result['best_fit']),3)
        for field in ('balanced','best_fit','near_home'):
            self.assertEqual(compare_options([],'ho_chi_minh')[field],[])

    def test_balance_ties_are_stable_and_multiple_regions_use_nearest_known_area(self):
        jobs=[{'id':'b','score':.8,'regions':['ha_noi','ho_chi_minh']},
              {'id':'a','score':.8,'regions':['ho_chi_minh']}]
        result=compare_options(jobs,'ho_chi_minh',top_n=2)
        self.assertEqual([j['id'] for j in result['balanced']],['a','b'])
        self.assertTrue(all(j['same_region'] for j in result['balanced']))
        self.assertTrue(all(j['proximity_score']==1 for j in result['balanced']))


if __name__=='__main__':unittest.main()
