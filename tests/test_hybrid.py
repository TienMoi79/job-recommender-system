from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import json
import math
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd

from experience_matching import extract_experience, experience_fit
from hybrid_recommender import HybridJobRecommenderSystem, JobDiversifier, skill_evidence, skill_fit
from evaluation import ranking_metrics, load_benchmark
from resume_profile import ResumeAnalyzer


def jobs_fixture():
    return pd.DataFrame([
      dict(Job_ID='P1',Title='Backend Developer Python',Skills='Python; SQL; Django',Experience_Years=1,Experience_Known=True,Domain='Software Development',Job_Description='Build REST services with Python and Django. Maintain SQL databases.',Company='Acme',Region_Codes='ha_noi',Requirements='Must-have: Python; SQL. Preferred: Docker.'),
      dict(Job_ID='P2',Title='Senior Backend Developer Python',Skills='Python; SQL; Django',Experience_Years=5,Experience_Known=True,Domain='Software Development',Job_Description='Build REST services with Python and Django. Maintain SQL databases.',Company='Acme',Region_Codes='ha_noi',Requirements=''),
      dict(Job_ID='J1',Title='Backend Developer Java',Skills='Java; Spring; SQL',Experience_Years=1,Experience_Known=True,Domain='Software Development',Job_Description='Build web services using Java Spring and SQL for enterprise applications.',Company='Beta',Region_Codes='ha_noi',Requirements=''),
      dict(Job_ID='F1',Title='Frontend Developer',Skills='JavaScript; React; HTML',Experience_Years=1,Experience_Known=True,Domain='Software Development',Job_Description='Build interactive web interfaces in React and JavaScript with HTML.',Company='Gamma',Region_Codes='ho_chi_minh',Requirements=''),
    ])


class ExperienceTests(unittest.TestCase):
    def test_explicit_bilingual_and_unknown(self):
        for text,years in [('Kinh nghiệm: 2 năm',2),('3 years of work experience in Python',3),('Tổng kinh nghiệm: 4 năm. Python 2 năm kinh nghiệm',4),('Kinh nghiệm: 1,5 năm',1.5),('Chưa có kinh nghiệm',0)]:
            self.assertEqual(extract_experience(text).years,years)
        for text in ['Tốt nghiệp năm 2024. Địa chỉ 10 đường A.','Python 3 năm kinh nghiệm. Java 1 năm kinh nghiệm.','Có 2-3 năm kinh nghiệm']:
            self.assertIsNone(extract_experience(text).years)

    def test_unknown_not_zero_and_soft_gap(self):
        self.assertEqual(experience_fit(None,4),(0.,'unknown'))
        self.assertEqual(experience_fit(0,0),(1.,'meets_minimum'))
        self.assertGreater(experience_fit(2,3)[0],experience_fit(2,6)[0])
        self.assertEqual(experience_fit(6,2)[0],1.)
        with self.assertRaises(ValueError):experience_fit(-1,2)


class HybridTests(unittest.TestCase):
    def setUp(self):
        self.jobs=jobs_fixture()
        self.engine=HybridJobRecommenderSystem(self.jobs,use_semantic=False)
        self.cv='Vị trí ứng tuyển: Backend Developer Python\nKinh nghiệm: 1 năm\nPython SQL Django'

    def test_stack_and_experience_beat_wrong_stack_or_seniority(self):
        result=self.engine.match_cv_to_jobs(self.cv,10,location='ha_noi')
        self.assertEqual(result.iloc[0].Job_ID,'P1')
        self.assertTrue(result.Region_Codes.eq('ha_noi').all())
        self.assertLess(result.loc[result.Job_ID=='P2','Score_Experience'].iloc[0],1.)
        self.assertNotIn('J1',result.Job_ID.tolist())
        self.assertTrue(result.Similarity_Score.is_monotonic_decreasing)

    def test_six_scores_and_active_weights_reconstruct_exact_total(self):
        for _,row in self.engine.match_cv_to_jobs(self.cv,10).iterrows():
            self.assertAlmostEqual(sum(row.Component_Weights.values()),1.)
            self.assertEqual(row.Component_Weights['Semantic'],0.)
            expected=sum(row.Component_Weights[field]*row['Score_'+field] for field in row.Component_Weights)
            self.assertAlmostEqual(expected,row.Similarity_Score)
        unknown=self.engine.match_cv_to_jobs('Backend Developer Python\nPython SQL Django',5)
        self.assertTrue(all(weights['Experience']==0 for weights in unknown.Component_Weights))
        self.assertTrue(unknown.Experience_Status.eq('unknown').all())

    def test_skill_evidence_does_not_assume_all_are_required(self):
        row={'Skills':'Python; SQL; Docker; Git','Requirements':'Must-have: Python and SQL. Preferred: Docker. We use Git.'}
        evidence=skill_evidence(row)
        self.assertEqual(evidence.required,frozenset({'Python','SQL'}))
        self.assertEqual(evidence.preferred,frozenset({'Docker'}))
        score,matched,missing=skill_fit(('Python','Git'),evidence)
        self.assertAlmostEqual(score,3/5.5)
        self.assertEqual(matched,['Git','Python'])
        self.assertEqual(missing,['Docker','SQL'])

    def test_semantic_signal_is_used_and_not_cached_as_cv(self):
        with patch.object(self.engine,'_semantic_scores',return_value=(np.array([.95,.1,.1,.1]),True)):
            result=self.engine.match_cv_to_jobs('Business reporting narrative without known technology',1,location='ha_noi')
        self.assertEqual(result.iloc[0].Job_ID,'P1')
        self.assertGreater(result.iloc[0].Component_Weights['Semantic'],0.)
        self.assertEqual(result.iloc[0].Ranking_Method,'hybrid')

    def test_empty_region_and_unrelated_text_do_not_pad(self):
        self.assertTrue(self.engine.match_cv_to_jobs(self.cv,location='quang_ninh').empty)
        self.assertTrue(self.engine.match_cv_to_jobs('zzzzqqqqxxxx').empty)
        with self.assertRaises(ValueError):self.engine.match_cv_to_jobs(self.cv,location='wrong')

    def test_profile_must_match_text_and_candidate_can_confirm_years(self):
        profile=ResumeAnalyzer().analyze(self.cv)
        with self.assertRaises(ValueError):self.engine.match_cv_to_jobs('different',profile=profile)
        confirmed=replace(profile,experience_years=6,experience_status='confirmed')
        result=self.engine.match_cv_to_jobs(self.cv,profile=confirmed)
        self.assertTrue(result.Score_Experience.eq(1.).all())

    def test_queries_and_results_do_not_mutate_input_or_index(self):
        before=self.engine.jobs
        result=self.engine.match_cv_to_jobs(self.cv)
        result.loc[0,'Title']='changed'
        pd.testing.assert_frame_equal(before,self.engine.jobs)
        pd.testing.assert_frame_equal(self.jobs,jobs_fixture())

    def test_missing_model_is_explicit_and_has_no_semantic_weight(self):
        engine=HybridJobRecommenderSystem(self.jobs)
        with patch('semantic_index.PublicSemanticIndex',side_effect=OSError('model unavailable')):
            result=engine.match_cv_to_jobs(self.cv)
        self.assertEqual(engine.semantic_status,'unavailable')
        self.assertTrue(result.Ranking_Method.eq('hybrid-lexical').all())
        self.assertTrue(result.Score_Semantic.eq(0.).all())
        self.assertTrue(all(weights['Semantic']==0. and math.isclose(sum(weights.values()),1.)
                            for weights in result.Component_Weights))

    def test_language_switch_preserves_matching_and_duplicate_groups(self):
        from catalog_data import localize_jobs
        root=Path(__file__).resolve().parents[1]
        source=pd.read_csv(root/'data/jobs_catalog.csv').fillna('').head(30)
        vi=HybridJobRecommenderSystem(localize_jobs(source,'vi'),use_semantic=False)
        en=HybridJobRecommenderSystem(localize_jobs(source,'en'),use_semantic=False)
        left=vi.match_cv_to_jobs(self.cv,10,location='ha_noi')
        right=en.match_cv_to_jobs(self.cv,10,location='ha_noi')
        self.assertGreater(len(left),0)
        self.assertEqual(left.Job_ID.tolist(),right.Job_ID.tolist())
        np.testing.assert_allclose(left.Similarity_Score,right.Similarity_Score)
        self.assertEqual(vi.diversifier.group,en.diversifier.group)

    def test_duplicate_suppression_and_company_diversity(self):
        original=self.jobs.iloc[[0]].copy()
        duplicate=original.copy();duplicate.Job_ID='P3';duplicate.Job_Description=duplicate.Job_Description+' '
        jobs=pd.concat([self.jobs,duplicate],ignore_index=True)
        engine=HybridJobRecommenderSystem(jobs,use_semantic=False)
        result=engine.match_cv_to_jobs(self.cv,10,location='ha_noi')
        self.assertFalse({'P1','P3'}.issubset(set(result.Job_ID)))
        self.assertIn('P2',set(result.Job_ID)) # Senior is a different vacancy.
        self.assertNotIn('P3',set(engine.recommend_similar_jobs('P1',10).Job_ID))

    def test_company_limit_only_replaces_with_comparable_candidate(self):
        jobs=pd.concat([self.jobs.iloc[[0]]]*5,ignore_index=True)
        jobs.Job_ID=['A','B','C','D','E'];jobs.Company=['Acme']*4+['Beta']
        for i in jobs.index:jobs.loc[i,'Job_Description']=f'Completely distinct description number {i} to avoid grouping.'
        diversifier=JobDiversifier(jobs);diversifier.group={key:key for key in jobs.Job_ID}
        ranked=jobs.copy();ranked['Similarity_Score']=[1,.95,.9,.85,.84]
        result=diversifier.select(ranked,3)
        self.assertIn('E',result.Job_ID.tolist())
        ranked.loc[4,'Similarity_Score']=.1
        self.assertNotIn('E',diversifier.select(ranked,3).Job_ID.tolist())


class EvaluationTests(unittest.TestCase):
    def test_metrics_known_answer_underfill_and_duplicates(self):
        metrics=ranking_metrics(['A','X','B'],{'A':2,'B':1},5)
        self.assertEqual(metrics['Precision@5'],.4)
        self.assertEqual(metrics['StrictPrecision@5'],.2)
        self.assertEqual(metrics['Recall@5'],1.)
        self.assertAlmostEqual(metrics['NDCG@5'],3.5/(3+1/math.log2(3)))
        self.assertEqual(metrics['MRR@5'],1.)
        self.assertEqual(ranking_metrics([],{},5)['NDCG@5'],0.)
        with self.assertRaises(ValueError):ranking_metrics(['A','A'],{'A':2})

    def test_benchmark_groups_and_catalog_hash_are_frozen(self):
        root=Path(__file__).resolve().parents[1]
        data,queries=load_benchmark(root/'data/evaluation/benchmark.json',pd.read_csv(root/'data/jobs_catalog.csv'))
        self.assertEqual(len(queries),30)
        self.assertEqual(sum(query.split=='dev' for query in queries),10)
        self.assertTrue(data['frozen_before_model_comparison'])

    def test_public_embedding_cache_contains_only_catalog(self):
        from semantic_index import PublicSemanticIndex
        class Dummy:
            _model=SimpleNamespace(get_sentence_embedding_dimension=lambda:2)
            calls=0
            def fit_transform(self,documents):self.calls+=1;return np.array([[1.,0.],[0.,1.]])
            def transform(self,texts):return np.array([[1.,0.]])
        dummy=Dummy()
        with TemporaryDirectory() as folder,patch('semantic_index.encoder',return_value=dummy):
            index=PublicSemanticIndex(['Public job A','Public job B'],cache_dir=Path(folder))
            before={p.name:p.read_bytes() for p in Path(folder).iterdir()}
            index.similarity('PRIVATE-CV-SENTINEL')
            self.assertEqual(before,{p.name:p.read_bytes() for p in Path(folder).iterdir()})
            PublicSemanticIndex(['Public job A','Public job B'],cache_dir=Path(folder))
            self.assertEqual(dummy.calls,1)


if __name__=='__main__':unittest.main()
