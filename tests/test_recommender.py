"""Kiểm thử hành vi phần mềm, KHÔNG phải evaluation chất lượng mô hình ở GĐ3.

Chạy: python -m unittest discover -s tests -v
Các test mặc định dùng TF-IDF nên không yêu cầu mạng/GPU/model tải sẵn.
"""

import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from generate_mock_data import JOB_COLUMNS, MockDataGenerator
from job_recommender import JobRecommenderSystem, TfidfTextVectorizer


class JobRecommenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generator = MockDataGenerator()
        cls.jobs = cls.generator.create_jobs()
        cls.engine = JobRecommenderSystem(cls.jobs, backend="tfidf")

    def test_generated_data_contract(self):
        self.assertGreaterEqual(len(self.jobs), 15)
        self.assertEqual(list(self.jobs.columns), JOB_COLUMNS)
        self.assertEqual(len(self.generator.create_resumes()), 3)
        self.assertTrue(self.jobs["Job_ID"].is_unique)

    def test_csv_round_trip(self):
        with tempfile.TemporaryDirectory() as folder:
            jobs_path, resumes_path = self.generator.save(folder)
            engine = JobRecommenderSystem.from_csv(jobs_path, backend="tfidf")
            self.assertEqual(len(engine.recommend_similar_jobs("J001")), 5)
            self.assertTrue(Path(resumes_path).is_file())

    def test_item_ranking_excludes_query_and_is_descending(self):
        result = self.engine.recommend_similar_jobs("J001")
        self.assertEqual(len(result), 5)
        self.assertNotIn("J001", result["Job_ID"].tolist())
        self.assertTrue(result["Similarity_Score"].is_monotonic_decreasing)
        self.assertTrue(result["Similarity_Score"].between(-1, 1).all())
        self.assertEqual(result["Rank"].tolist(), [1, 2, 3, 4, 5])

    def test_exact_job_description_matches_itself(self):
        # Một đoạn nội dung khớp hoàn toàn phải thắng đoạn khác biệt rõ ràng.
        jobs = pd.DataFrame([
            ["A", "Python", "Pandas", 1, "Analytics", "Python Pandas"],
            ["B", "Flutter", "Dart", 1, "Mobile", "Flutter Dart"],
        ], columns=JOB_COLUMNS)
        engine = JobRecommenderSystem(jobs, backend="tfidf")
        self.assertEqual(engine.match_cv_to_jobs("Python Pandas").iloc[0]["Job_ID"], "A")

    def test_all_three_cvs_have_finite_ranked_results(self):
        for resume in self.generator.create_resumes():
            with self.subTest(resume=resume["Resume_ID"]):
                result = self.engine.match_cv_to_jobs(resume["CV_Text"])
                self.assertEqual(len(result), 5)
                self.assertTrue(np.isfinite(result["Similarity_Score"]).all())
                self.assertTrue(result["Similarity_Score"].is_monotonic_decreasing)

    def test_top_n_is_capped(self):
        self.assertEqual(len(self.engine.recommend_similar_jobs("J001", 100)), len(self.jobs) - 1)
        self.assertEqual(len(self.engine.match_cv_to_jobs("Python", 100)), len(self.jobs))

    def test_invalid_top_n_is_rejected_by_both_methods(self):
        for value in [0, -1, 1.5, True, "5", None]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    self.engine.recommend_similar_jobs("J001", value)
                with self.assertRaises(ValueError):
                    self.engine.match_cv_to_jobs("Python", value)

    def test_unknown_job(self):
        with self.assertRaises(KeyError):
            self.engine.recommend_similar_jobs("J999")

    def test_empty_and_nontext_cv(self):
        for value in ["", " \n ", None, 123]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.engine.match_cv_to_jobs(value)

    def test_out_of_vocabulary_cv_is_not_arbitrarily_ranked(self):
        with self.assertWarns(UserWarning):
            result = self.engine.match_cv_to_jobs("zzzzqqqqxxxx")
        self.assertTrue(result.empty)
        self.assertIn("Similarity_Score", result.columns)

    def test_single_job_has_no_similar_candidates(self):
        engine = JobRecommenderSystem(self.jobs.iloc[:1], backend="tfidf")
        self.assertTrue(engine.recommend_similar_jobs("J001").empty)

    def test_external_dataframe_index_does_not_break_id_mapping(self):
        jobs = self.jobs.iloc[::-1].copy()
        jobs.index = [42] * len(jobs)
        engine = JobRecommenderSystem(jobs, backend="tfidf")
        pd.testing.assert_frame_equal(
            self.engine.recommend_similar_jobs("J001"), engine.recommend_similar_jobs("J001")
        )

    def test_results_and_input_are_isolated(self):
        jobs = self.jobs.copy(deep=True)
        engine = JobRecommenderSystem(jobs, backend="tfidf")
        expected = engine.recommend_similar_jobs("J001")
        jobs.loc[:, "Title"] = "Changed"
        result = engine.recommend_similar_jobs("J001")
        result.loc[:, "Title"] = "Changed again"
        pd.testing.assert_frame_equal(expected, engine.recommend_similar_jobs("J001"))

    def test_cv_queries_do_not_refit_or_change_item_results(self):
        before = self.engine.recommend_similar_jobs("J001")
        self.engine.match_cv_to_jobs("Python Flutter Docker")
        pd.testing.assert_frame_equal(before, self.engine.recommend_similar_jobs("J001"))

    def test_ties_are_resolved_by_job_id(self):
        jobs = pd.concat([self.jobs.iloc[:1]] * 3, ignore_index=True)
        jobs["Job_ID"] = ["Z", "B", "A"]
        result = JobRecommenderSystem(jobs, backend="tfidf").recommend_similar_jobs("Z")
        self.assertEqual(result["Job_ID"].tolist(), ["A", "B"])

    def test_invalid_data_is_rejected(self):
        invalid_cases = [self.jobs.iloc[:0], self.jobs.drop(columns="Skills")]
        duplicate = self.jobs.copy()
        duplicate.loc[1, "Job_ID"] = duplicate.loc[0, "Job_ID"]
        invalid_cases.append(duplicate)
        for column, value in [("Title", None), ("Skills", " "), ("Experience_Years", -1),
                              ("Experience_Years", np.inf), ("Experience_Years", np.nan),
                              ("Experience_Years", "unknown"), ("Experience_Years", True)]:
            jobs = self.jobs.astype({column: object}).copy()
            jobs.loc[0, column] = value
            invalid_cases.append(jobs)
        for index, jobs in enumerate(invalid_cases):
            with self.subTest(case=index), self.assertRaises(ValueError):
                JobRecommenderSystem(jobs, backend="tfidf")

    def test_technology_names_stay_distinct(self):
        encoder = TfidfTextVectorizer()
        encoder.fit_transform(["C++", "C#", ".NET", "Node.js"])
        vectors = encoder.transform(["C++", "C#", ".NET", "Node.js"]).toarray()
        np.testing.assert_allclose(vectors @ vectors.T, np.eye(4))

    def test_unknown_backend(self):
        with self.assertRaises(ValueError):
            JobRecommenderSystem(self.jobs, backend="unknown")


if __name__ == "__main__":
    unittest.main()
