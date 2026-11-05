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

    def test_expanded_unique_real_records_with_traceable_source(self):
        self.assertEqual(len(self.jobs), 7050)
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
        self.assertEqual(manifest["selected_rows"], len(self.jobs))
        self.assertEqual(manifest["csv_sha256"], sha256(self.path.read_bytes()).hexdigest())

    def test_first_500_ids_and_source_text_are_preserved(self):
        frozen=pd.read_csv(BASE_DIR/'data/evaluation/jobs_catalog_500.csv').fillna('')
        for column in frozen.columns:
            if column in ('Salary','Salary_EN'):continue  # Sửa hiển thị lương có lưu Salary_Original.
            self.assertEqual(self.jobs.head(500)[column].fillna('').tolist(),frozen[column].tolist(),column)

    def test_presentation_has_no_currencyless_numbers_or_thousand_vnd_labels(self):
        jobs=self.jobs.set_index('Job_ID')
        self.assertEqual(jobs.loc['VN0005','Salary'],'1–2 triệu/tuần')
        self.assertEqual(jobs.loc['VN0059','Salary'],'Chưa rõ mức lương')
        self.assertEqual(jobs.loc['VN0059','Salary_Original'],'105')
        self.assertEqual(jobs.loc['VN0142','Salary'],'Lương thỏa thuận')
        self.assertFalse(self.jobs.Salary.str.contains('nghìn|ngàn|VND MONTH',regex=True).any())
        self.assertFalse(self.jobs.Salary.str.fullmatch(r'[\d\s.,–-]+').any())
        self.assertGreater(len(jobs.loc['VN0010','Job_Description_Display'].splitlines()),10)
        self.assertIn('\nQUYỀN LỢI:',jobs.loc['VN0014','Job_Description_Display'])

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
