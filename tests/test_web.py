"""Kiểm thử tích hợp thật qua Streamlit AppTest và AI Engine, không giả điểm gợi ý."""
import importlib.util
import re
from pathlib import Path
import unittest
from unittest.mock import patch

import pandas as pd

from generate_mock_data import MockDataGenerator
from job_recommender import JobRecommenderSystem
from web_support import filter_jobs, job_card_html, sample_resumes
from ui_text import TEXT, experience_text

HAS_STREAMLIT = importlib.util.find_spec("streamlit") is not None
BASE_DIR = Path(__file__).resolve().parent.parent
VI_DATA_PATH = BASE_DIR / "data/jobs_vie.csv"
if not VI_DATA_PATH.exists():
    VI_DATA_PATH = BASE_DIR / "data/jobs_vie.cvs"


class WebSupportTests(unittest.TestCase):
    def setUp(self):
        self.jobs = MockDataGenerator().create_vietnamese_jobs()

    def test_literal_search_and_vietnamese_accents(self):
        self.assertEqual(filter_jobs(self.jobs, "[").shape[0], 0)
        self.assertEqual(filter_jobs(self.jobs, "C#")["Job_ID"].tolist(), ["J020"])
        self.assertEqual(filter_jobs(self.jobs, ".NET")["Job_ID"].tolist(), ["J020"])
        self.assertIn("J001", filter_jobs(self.jobs, "PHAN TICH DU LIEU")["Job_ID"].tolist())
        self.assertEqual(filter_jobs(self.jobs, "C++").shape[0], 0)

    def test_combined_filters(self):
        rows = filter_jobs(self.jobs, "Python", "Trí tuệ nhân tạo", "3 năm")
        self.assertEqual(rows["Job_ID"].tolist(), ["J006"])

    def test_filters_use_values_independent_of_translated_labels(self):
        rows = filter_jobs(self.jobs, "Python", "Trí tuệ nhân tạo", 3)
        self.assertEqual(rows["Job_ID"].tolist(), ["J006"])
        self.assertEqual(len(filter_jobs(self.jobs, domain=None, experience=None)), 20)

    def test_english_job_card_and_experience_labels(self):
        row = MockDataGenerator().create_jobs().iloc[0].copy()
        row["Similarity_Score"], row["Rank"] = 0.7, 1
        html = job_card_html(row, language="en", detail=True)
        self.assertIn("Content similarity score", html)
        self.assertIn("1 year of experience", html)
        self.assertNotRegex(html, r"[À-ỹ]")
        self.assertEqual(experience_text("en", 2), "2 years")
        self.assertEqual(experience_text("vi", 2, badge=True), "2 năm kinh nghiệm")

    def test_translation_keys_are_complete_in_both_languages(self):
        self.assertEqual(set(TEXT["vi"]), set(TEXT["en"]))

    def test_job_html_escapes_data_and_has_no_percentage(self):
        row = self.jobs.iloc[0].copy()
        row["Title"] = '<img src=x onerror="alert(1)">'
        row["Skills"] = "<script>alert(1)</script>; C#"
        row["Similarity_Score"], row["Rank"] = -0.2, 1
        html = job_card_html(row)
        self.assertNotIn("<img", html)
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;img", html)
        self.assertIn("-0.2000", html)
        self.assertNotIn("%", html)

    def test_public_jobs_cannot_mutate_engine(self):
        engine = JobRecommenderSystem(self.jobs, backend="tfidf")
        public_jobs = engine.jobs
        public_jobs.loc[0, "Title"] = "Changed"
        self.assertEqual(engine.jobs.loc[0, "Title"], self.jobs.loc[0, "Title"])

    def test_sample_cvs_match_both_languages(self):
        generator = MockDataGenerator()
        for language, jobs in [("vi", self.jobs), ("en", generator.create_jobs())]:
            engine = JobRecommenderSystem(jobs, backend="tfidf")
            for cv_id, expected in [("CV001", {"J001", "J002"}), ("CV002", {"J009"}), ("CV003", {"J005", "J007"})]:
                with self.subTest(language=language, cv=cv_id):
                    results = engine.match_cv_to_jobs(sample_resumes(language)[cv_id]["text"])
                    self.assertIn(results.iloc[0]["Job_ID"], expected)


@unittest.skipUnless(HAS_STREAMLIT, "Cài requirements-web.txt để kiểm thử giao diện")
class StreamlitFlowTests(unittest.TestCase):
    def setUp(self):
        from streamlit.testing.v1 import AppTest
        self.at = AppTest.from_file(str(BASE_DIR / "app.py"), default_timeout=30).run()
        self.assertFalse(self.at.exception)

    def show_cv(self):
        self.at.radio(key="page").set_value("match").run()

    def match_sample(self):
        self.show_cv()
        self.at.button(key="sample_CV001").click().run()
        self.at.button(key="match_cv").click().run()
        self.assertFalse(self.at.exception)

    def test_load_search_and_reset_all_filters(self):
        self.assertEqual(len([b for b in self.at.button if str(b.key).startswith("job_")]), 20)
        self.at.text_input(key="_filter_keyword").input("[").run()
        self.assertFalse(self.at.exception)
        self.assertTrue(any("Không tìm thấy" in v.value for v in self.at.info))
        self.at.selectbox(key="_filter_domain").select("Trí tuệ nhân tạo").run()
        self.at.selectbox(key="_filter_exp").set_value(3).run()
        self.at.button(key="reset_filters").click().run()
        self.assertEqual(self.at.text_input(key="_filter_keyword").value, "")
        self.assertEqual(self.at.selectbox(key="_filter_domain").value, "__all__")
        self.assertEqual(self.at.selectbox(key="_filter_exp").value, "__all__")
        self.assertEqual(len([b for b in self.at.button if str(b.key).startswith("job_")]), 20)

    def test_detail_and_similar_navigation(self):
        self.at.button(key="job_J001").click().run()
        self.assertFalse(self.at.exception)
        self.assertEqual(self.at.session_state["selected_job_id"], "J001")
        self.assertNotIn("similar_J001", [b.key for b in self.at.button])
        self.at.button(key="similar_J002").click().run()
        self.assertEqual(self.at.session_state["selected_job_id"], "J002")
        self.at.button(key="back_detail").click().run()
        self.assertIsNone(self.at.session_state["selected_job_id"])

    def test_cv_real_engine_scores_and_open_detail_return(self):
        self.match_sample()
        expected = JobRecommenderSystem.from_csv(VI_DATA_PATH, backend="tfidf").match_cv_to_jobs(sample_resumes("vi")["CV001"]["text"])
        pd.testing.assert_frame_equal(self.at.session_state["cv_results"], expected)
        self.at.button(key="match_J001").click().run()
        self.assertEqual(self.at.radio(key="page").value, "explore")
        self.assertEqual(self.at.session_state["selected_job_id"], "J001")
        self.at.button(key="back_detail").click().run()
        self.assertEqual(self.at.radio(key="page").value, "match")
        pd.testing.assert_frame_equal(self.at.session_state["cv_results"], expected)
        self.assertIn("match_J001", [b.key for b in self.at.button])
        self.assertEqual(self.at.text_area(key="_cv_text").value, sample_resumes("vi")["CV001"]["text"])

    def test_cv_changes_invalidate_results_and_clear(self):
        self.match_sample()
        self.at.number_input(key="_cv_top_n").set_value(3).run()
        self.assertIsNone(self.at.session_state["cv_results"])
        self.at.button(key="match_cv").click().run()
        self.assertEqual(len(self.at.session_state["cv_results"]), 3)
        self.at.text_area(key="_cv_text").input("Python Backend Django").run()
        self.assertIsNone(self.at.session_state["cv_results"])
        self.at.button(key="clear_cv").click().run()
        self.assertEqual(self.at.text_area(key="_cv_text").value, "")

    def test_empty_and_out_of_vocabulary_cv(self):
        self.show_cv()
        self.at.button(key="match_cv").click().run()
        self.assertTrue(any("Vui lòng nhập" in v.value for v in self.at.warning))
        self.at.text_area(key="_cv_text").input("zzzzqqqqxxxx").run()
        self.at.button(key="match_cv").click().run()
        self.assertTrue(self.at.session_state["cv_results"].empty)
        self.assertTrue(any("Chưa đủ từ khóa" in v.value for v in self.at.info))

    def test_dataset_switch_uses_english_cv_and_clears_old_matches(self):
        self.match_sample()
        self.at.selectbox(key="dataset").set_value("en").run()
        self.assertFalse(self.at.exception)
        self.assertIsNone(self.at.session_state["cv_results"])
        self.assertEqual(self.at.text_area(key="_cv_text").value, "")
        self.at.button(key="sample_CV002").click().run()
        self.assertIn("I am a Python Backend Developer", self.at.text_area(key="_cv_text").value)
        self.at.button(key="match_cv").click().run()
        self.assertEqual(self.at.session_state["cv_results"].iloc[0]["Job_ID"], "J009")

    def test_two_sessions_do_not_share_cv(self):
        from streamlit.testing.v1 import AppTest
        self.match_sample()
        second = AppTest.from_file(str(BASE_DIR / "app.py"), default_timeout=30).run()
        self.assertEqual(second.session_state["cv_text"], "")
        self.assertIsNone(second.session_state["cv_results"])

    def test_single_job_detail_does_not_create_invalid_top_n(self):
        single = MockDataGenerator().create_vietnamese_jobs().iloc[:1].to_csv(index=False).encode("utf-8-sig")
        real_read = Path.read_bytes
        with patch.object(Path, "read_bytes", lambda path: single if path.name in ("jobs_vie.cvs", "jobs_vie.csv") else real_read(path)):
            self.at.run()
            self.at.button(key="job_J001").click().run()
        self.assertFalse(self.at.exception)
        self.assertTrue(any("Chưa có việc làm khác" in v.value for v in self.at.info))

    def test_missing_data_is_visible_error(self):
        real_read = Path.read_bytes
        def read(path):
            if path.name in ("jobs_vie.cvs", "jobs_vie.csv"):
                raise FileNotFoundError()
            return real_read(path)
        with patch.object(Path, "read_bytes", read):
            self.at.run()
        self.assertFalse(self.at.exception)
        self.assertTrue(any("Thiếu dữ liệu" in v.value for v in self.at.error))

    def test_semantic_load_failure_is_recoverable(self):
        with patch("job_recommender.SentenceTransformerVectorizer", side_effect=ImportError("missing model")):
            self.at.radio(key="backend").set_value("sentence-transformers").run()
        self.assertFalse(self.at.exception)
        self.assertTrue(any("Không thể nạp" in v.value for v in self.at.error))
        self.at.radio(key="backend").set_value("tfidf").run()
        self.assertFalse(self.at.exception)
        self.assertTrue(any(b.key == "job_J001" for b in self.at.button))

    def test_cached_engine_refreshes_when_content_changes(self):
        from app import get_recommender_engine
        jobs = MockDataGenerator().create_vietnamese_jobs()
        original = get_recommender_engine(jobs.to_csv(index=False).encode("utf-8"), "tfidf")
        jobs.loc[0, "Title"] = "Chức danh được cập nhật"
        updated = get_recommender_engine(jobs.to_csv(index=False).encode("utf-8"), "tfidf")
        self.assertIsNot(original, updated)
        self.assertEqual(updated.jobs.iloc[0]["Title"], "Chức danh được cập nhật")

    def assert_english_interface(self):
        """Kiểm tra cả nhãn và nội dung hiển thị; bỏ CSS/comment khỏi HTML."""
        displayed = []
        for kind in ("markdown", "caption", "subheader", "info", "warning", "error", "success"):
            for element in getattr(self.at, kind):
                html = re.sub(r"<style>.*?</style>", "", element.value, flags=re.S)
                displayed.append(re.sub(r"<[^>]+>", "", html))
        for kind in ("button", "selectbox", "radio", "text_input", "text_area", "number_input", "expander"):
            for element in getattr(self.at, kind):
                displayed.append(element.label)
                if kind in ("selectbox", "radio"):
                    displayed.extend(element.options)
                if kind in ("text_input", "text_area"):
                    displayed.append(element.placeholder)
        self.assertNotRegex("\n".join(displayed), r"[À-ỹ]")
        self.assertFalse(self.at.exception)

    def test_full_language_switch_and_only_two_navigation_pages(self):
        self.assertEqual(self.at.radio(key="page").options, ["Khám phá việc làm", "Tìm việc theo CV"])
        self.at.selectbox(key="dataset").set_value("en").run()
        self.assertEqual(self.at.radio(key="page").options, ["Explore jobs", "Match your CV"])
        self.assertEqual(self.at.selectbox(key="dataset").label, "Language")
        self.assertEqual(self.at.selectbox(key="dataset").options, ["Vietnamese", "English"])
        self.assertEqual(self.at.selectbox(key="_filter_exp").options, ["All", "1 year", "2 years", "3 years"])
        self.assertEqual(self.at.button(key="job_J001").label, "View details")
        self.assert_english_interface()
        self.at.selectbox(key="_filter_domain").set_value("Artificial Intelligence").run()
        self.at.selectbox(key="_filter_exp").set_value(3).run()
        self.assertEqual([b.key for b in self.at.button if str(b.key).startswith("job_")], ["job_J006"])
        self.assert_english_interface()
        self.at.selectbox(key="dataset").set_value("vi").run()
        self.assertEqual(self.at.selectbox(key="dataset").label, "Ngôn ngữ")
        self.assertEqual(self.at.radio(key="page").options, ["Khám phá việc làm", "Tìm việc theo CV"])
        self.assertEqual(self.at.button(key="job_J001").label, "Xem chi tiết")
        self.assertEqual(self.at.selectbox(key="_filter_exp").value, "__all__")

    def test_english_cv_detail_scores_and_return_navigation(self):
        self.show_cv()
        self.at.selectbox(key="dataset").set_value("en").run()
        self.assertEqual(self.at.radio(key="page").value, "match")
        self.assert_english_interface()
        self.at.button(key="sample_CV002").click().run()
        self.at.button(key="match_cv").click().run()
        self.assert_english_interface()
        expected = JobRecommenderSystem.from_csv(BASE_DIR / "data/jobs.csv", backend="tfidf").match_cv_to_jobs(sample_resumes("en")["CV002"]["text"])
        pd.testing.assert_frame_equal(self.at.session_state["cv_results"], expected)
        self.at.button(key="match_J009").click().run()
        self.assertEqual(self.at.button(key="back_detail").label, "← Back to CV results")
        self.assert_english_interface()
        self.at.button(key="back_detail").click().run()
        self.assertEqual(self.at.radio(key="page").value, "match")
        self.assert_english_interface()

    def test_english_empty_search_cv_and_errors_are_translated(self):
        self.at.selectbox(key="dataset").set_value("en").run()
        self.at.text_input(key="_filter_keyword").input("[").run()
        self.assertTrue(any("No jobs found" in v.value for v in self.at.info))
        self.assert_english_interface()
        self.show_cv()
        self.at.button(key="match_cv").click().run()
        self.assertTrue(any("Please enter" in v.value for v in self.at.warning))
        self.assert_english_interface()
        self.at.text_area(key="_cv_text").input("zzzzqqqqxxxx").run()
        self.at.button(key="match_cv").click().run()
        self.assertTrue(any("Not enough matching" in v.value for v in self.at.info))
        self.assert_english_interface()
        with patch("job_recommender.JobRecommenderSystem.match_cv_to_jobs", side_effect=RuntimeError("failure")):
            self.at.button(key="sample_CV002").click().run()
            self.at.button(key="match_cv").click().run()
        self.assertTrue(any("Unable to process" in v.value for v in self.at.warning))
        self.assert_english_interface()
        with patch("job_recommender.SentenceTransformerVectorizer", side_effect=ImportError("missing model")):
            self.at.radio(key="backend").set_value("sentence-transformers").run()
        self.assertTrue(any("Unable to load" in v.value for v in self.at.error))
        self.assert_english_interface()
        self.at.radio(key="backend").set_value("tfidf").run()
        real_read = Path.read_bytes
        with patch.object(Path, "read_bytes", lambda path: (_ for _ in ()).throw(FileNotFoundError()) if path.name == "jobs.csv" else real_read(path)):
            self.at.run()
        self.assertTrue(any("Job data is missing" in v.value for v in self.at.error))
        self.assert_english_interface()

    def test_data_path_supports_csv_and_legacy_cvs(self):
        from app import dataset_path
        with patch.object(Path, "exists", return_value=True):
            self.assertEqual(dataset_path("vi").name, "jobs_vie.csv")
        with patch.object(Path, "exists", return_value=False):
            self.assertEqual(dataset_path("vi").name, "jobs_vie.cvs")
        self.assertEqual(dataset_path("en").name, "jobs.csv")


if __name__ == "__main__":
    unittest.main()
