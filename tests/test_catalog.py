"""Hợp đồng chất lượng của catalog thật được bàn giao, không gọi mạng khi test."""
from hashlib import sha256
import json
from pathlib import Path
import unittest
import pandas as pd

from catalog_data import localize_jobs
from job_recommender import JobRecommenderSystem
from locations import REGIONS

BASE_DIR = Path(__file__).resolve().parent.parent


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = BASE_DIR / "data/jobs_catalog.csv"
        cls.jobs = pd.read_csv(cls.path, encoding="utf-8-sig")

    def test_500_unique_real_records_with_traceable_source(self):
        self.assertEqual(len(self.jobs), 500)
        self.assertTrue(self.jobs.Job_ID.is_unique)
        self.assertTrue(self.jobs.Source_Row_ID.is_unique)
        self.assertTrue(self.jobs.Content_Fingerprint.is_unique)
        self.assertTrue(self.jobs.Source_Dataset.eq("tinixai/vietnamese-job-descriptions").all())
        self.assertTrue(self.jobs.Source_License.eq("CC-BY-NC-4.0").all())
        self.assertTrue(self.jobs.Source_URL.str.startswith("https://huggingface.co/").all())
        self.assertGreater(self.jobs.Company.nunique(), 100)
        self.assertGreater(self.jobs.Role_Code.nunique(), 10)

    def test_locations_and_manifest_match_catalog(self):
        for codes in self.jobs.Region_Codes:
            self.assertTrue(set(codes.split(";")).issubset(REGIONS))
        self.assertIn("ha_noi", set(self.jobs.Primary_Region))
        self.assertIn("ho_chi_minh", set(self.jobs.Primary_Region))
        self.assertIn("khanh_hoa", set(self.jobs.Primary_Region))
        manifest = json.loads((BASE_DIR / "data/catalog_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["selected_rows"], 500)
        self.assertEqual(manifest["csv_sha256"], sha256(self.path.read_bytes()).hexdigest())

    def test_bilingual_views_share_records_and_regional_matching(self):
        vi, en = localize_jobs(self.jobs, "vi"), localize_jobs(self.jobs, "en")
        self.assertEqual(vi.Job_ID.tolist(), en.Job_ID.tolist())
        self.assertFalse(en.Domain.str.contains(r"[À-ỹ]").any())
        self.assertFalse(en.Job_Description.str.contains(r"[À-ỹ]").any())
        english_originals = ~self.jobs.Job_Description.str.contains(r"[À-ỹ]") & self.jobs.Job_Description.str.contains(r"\b(?:the|with|and|responsibilities|develop)\b", case=False)
        if english_originals.any():
            self.assertTrue(vi.loc[english_originals, "Job_Description"].str.contains("tóm tắt từ mô tả gốc tiếng Anh").all())
        for language, jobs, cv in [("vi", vi, "Vị trí ứng tuyển: Backend Python\nKỹ năng: Python, FastAPI, Django, PostgreSQL, SQL, Docker"),
                                   ("en", en, "Backend Python Developer\nPython, FastAPI, Django, PostgreSQL, SQL, Docker")]:
            with self.subTest(language=language):
                engine = JobRecommenderSystem(jobs, backend="tfidf")
                results = engine.match_cv_to_jobs(cv, location="ha_noi")
                self.assertEqual(len(results), 5)
                self.assertTrue(results.Region_Codes.map(lambda codes: "ha_noi" in codes.split(";")).all())
                self.assertTrue(results.Similarity_Score.is_monotonic_decreasing)


if __name__ == "__main__":
    unittest.main()
