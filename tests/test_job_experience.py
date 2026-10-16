"""Ca hồi quy từ lỗi 'Không rõ' trong khi nguồn ghi tối thiểu 2 năm."""
from pathlib import Path
import unittest
import pandas as pd
from job_experience import resolve_job_experience


class JobExperienceTests(unittest.TestCase):
    def test_requirement_minimum_ranges_and_months(self):
        cases=[('Kinh nghiệm làm việc: +) Tối thiểu 2 năm kinh nghiệm',2.),
               ('Kinh nghiệm tối thiểu 1 năm trở lên.',1.),
               ('Từ 2 đến 3 năm kinh nghiệm triển khai hệ thống.',2.),
               ('5–8 năm kinh nghiệm DevOps.',5.),
               ('Có ít nhất 1,5 năm kinh nghiệm lập trình Java.',1.5),
               ('Có kinh nghiệm trên 6 tháng React JS/NextJS.',.5),
               ('2+ years of experience in backend engineering.',2.),
               ('Experience: minimum 3 years in a related role.',3.),
               ('Min 3 years of exeperience in similar role.',3.),
               ('Not less than 2 years of experience.',2.),
               ('2–3+ năm kinh nghiệm frontend (ưu tiên React).',2.),
               ('Required: 3+ years of experience in AI. Nice-to-have: Docker.',3.),
               ('Tối thiểu 02 năm kinh làm việc với vai trò Data Analyst và tối thiểu 01 năm kinh nghiệm sử dụng Power BI.',2.)]
        for text,expected in cases:
            with self.subTest(text=text):
                value=resolve_job_experience('Không',text)
                self.assertTrue(value.known)
                self.assertEqual(value.years,expected)
                self.assertEqual(value.source,'requirements')

    def test_do_not_infer_minimum_from_other_numbers_or_preferences(self):
        for text in ['Sinh viên đại học năm 3 trở lên.','Độ tuổi từ 22 đến 30. Thử việc 2 tháng.',
                     'Lương tháng 13, nghỉ phép 12 ngày mỗi năm.','Có 2 năm kinh nghiệm là lợi thế.',
                     'Ưu tiên có 3 năm kinh nghiệm Python.','Preferred qualifications: SQL. 2 years of experience.',
                     'Không yêu cầu kinh nghiệm sử dụng tiếng Hàn.']:
            with self.subTest(text=text):
                self.assertFalse(resolve_job_experience('Không',text).known)
        self.assertFalse(resolve_job_experience('Không','','Our company has 20 years of experience.').known)

    def test_jd_section_fallback_and_unchanged_explicit_metadata(self):
        parsed=resolve_job_experience('Không','','Công ty hoạt động 20 năm. YÊU CẦU: Từ 3-4 năm kinh nghiệm. QUYỀN LỢI: 13 tháng lương.')
        self.assertEqual((parsed.years,parsed.known,parsed.source),(3.,True,'job_description'))
        self.assertEqual(resolve_job_experience('Không','','Required skills & experience: 2+ years experience in DevOps.').years,2.)
        self.assertEqual(resolve_job_experience('5 năm','Kinh nghiệm SQL 2 năm').years,5.)
        self.assertFalse(resolve_job_experience('Không').known)
        self.assertEqual(resolve_job_experience('Dưới 1 năm').years,0.)
        self.assertEqual(resolve_job_experience('Không','Không yêu cầu kinh nghiệm').years,0.)
        self.assertTrue(resolve_job_experience('Không','No experience required.').known)

    def test_catalog_regression_and_bilingual_summary(self):
        from catalog_data import localize_jobs
        from web_support import filter_jobs
        root=Path(__file__).resolve().parents[1]
        jobs=pd.read_csv(root/'data/jobs_catalog.csv').fillna('')
        row=jobs.set_index('Job_ID').loc['VN0002']
        self.assertEqual(row.Experience_Text,'Không')  # Không sửa bằng chứng nguồn.
        self.assertTrue(row.Experience_Known)
        self.assertEqual(row.Experience_Years,2.)
        self.assertEqual(row.Experience_Source,'requirements')
        self.assertIn('VN0002',filter_jobs(jobs,experience=2).Job_ID.tolist())
        self.assertNotIn('VN0002',filter_jobs(jobs,experience=0).Job_ID.tolist())
        english=localize_jobs(jobs,'en').set_index('Job_ID').loc['VN0002']
        self.assertIn('2 years',english.Requirements)
        self.assertIn('2 years',english.Job_Description)
        from hybrid_recommender import HybridJobRecommenderSystem
        engine=HybridJobRecommenderSystem(jobs[jobs.Job_ID=='VN0002'],use_semantic=False)
        cv='Vị trí ứng tuyển: Fullstack Java Developer\nKinh nghiệm: 1 năm\nJava SQL Spring Hibernate React'
        result=engine.match_cv_to_jobs(cv).iloc[0]
        self.assertEqual(result.Experience_Status,'below_minimum')
        self.assertGreater(result.Component_Weights['Experience'],0.)
        self.assertLess(result.Score_Experience,1.)


if __name__=='__main__':unittest.main()
