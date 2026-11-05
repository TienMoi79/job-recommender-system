"""Ca đã biết từ phản ánh UI và lỗi đơn vị/ngắt dòng, không gọi mạng."""
import unittest
from job_presentation import format_job_text, normalize_salary, display_job_field


class JobPresentationTests(unittest.TestCase):
    def test_vnd_units_are_millions_and_periods_are_preserved(self):
        for raw,vi,en in [('1000 - 2000 nghìn/tuần','1–2 triệu/tuần','1–2 million VND/week'),
                          ('50 - 300 nghìn/ngày','0,05–0,3 triệu/ngày','0.05–0.3 million VND/day'),
                          ('28 nghìn/giờ','0,028 triệu/giờ','0.028 million VND/hour'),
                          ('15000000 - 50000000 VND MONTH','15–50 triệu/tháng','15–50 million VND/month'),
                          ('10.000.000 - 15.000.000 VNĐ','10–15 triệu','10–15 million VND'),
                          ('3,5 - 4 triệu','3,5–4 triệu','3.5–4 million VND'),
                          ('15-25tr','15–25 triệu','15–25 million VND'),
                          ('15tr-25tr','15–25 triệu','15–25 million VND')]:
            with self.subTest(raw=raw):
                salary=normalize_salary(raw);self.assertEqual(salary.vi,vi);self.assertEqual(salary.en,en)
        self.assertEqual(normalize_salary('20 triệu').period,'unspecified')

    def test_ambiguous_zero_and_reversed_salary_do_not_become_fake_pay(self):
        for raw in ['105','500','50 - 300','0 VND','50.000.000 - 0 VND','VND MONTH','Đang cập nhật']:
            with self.subTest(raw=raw):self.assertEqual(normalize_salary(raw).vi,'Chưa rõ mức lương')

    def test_allowance_and_insurance_are_not_salary(self):
        raw='50 - 300 nghìn/ngày';context='Lương thỏa thuận theo năng lực. Hỗ trợ ăn trưa 50k/ngày, hỗ trợ gửi xe 300k/tháng.'
        self.assertEqual(normalize_salary(raw,context).status,'allowance_conflict')
        self.assertEqual(normalize_salary(raw,context).vi,'Lương thỏa thuận')
        self.assertEqual(normalize_salary('105','Health insurance coverage up to VND 105 million/year').vi,'Chưa rõ mức lương')
        self.assertEqual(normalize_salary('500','Mức lương cứng: (thỏa thuận theo năng lực). Phụ cấp ăn trưa 500.000đ/tháng').vi,'Lương thỏa thuận')
        # Không xóa lương hợp lệ chỉ vì có chính sách đàm phán/phụ cấp đi kèm.
        self.assertEqual(normalize_salary('15–25 triệu',context).vi,'15–25 triệu')
        self.assertEqual(normalize_salary('10–20 nghìn/giờ',context).vi,'0,01–0,02 triệu/giờ')

    def test_foreign_currency_and_qualifiers_are_not_converted_with_guessed_fx(self):
        self.assertEqual(normalize_salary('2,000 - 4,000 USD').vi,'2000–4000 USD')
        self.assertEqual(normalize_salary('Trên 100 triệu').vi,'Trên 100 triệu')
        self.assertEqual(normalize_salary('Dưới 3 triệu').en,'Below 3 million VND')
        self.assertIn('1800 USD × 14',normalize_salary('Upto $1800 x 14 tháng lương/năm + Thưởng').vi)

    def test_prose_headings_and_bullets_are_readable_without_splitting_ranges(self):
        original='MÔ TẢ CÔNG VIỆC - Phát triển API. - Dùng Node.js và .NET. YÊU CẦU: - Từ 3 - 4 năm kinh nghiệm. QUYỀN LỢI: - Mức lương 15 - 25 triệu.'
        result=format_job_text(original)
        self.assertIn('MÔ TẢ CÔNG VIỆC:\n• Phát triển API.',result)
        self.assertIn('\nYÊU CẦU:\n• Từ 3 - 4 năm',result)
        self.assertIn('15 - 25 triệu',result);self.assertIn('Node.js',result);self.assertIn('.NET',result)
        self.assertEqual(format_job_text('Build based on requirements. Use back-end services.'),'Build based on requirements.\nUse back-end services.')

    def test_html_structure_and_existing_newlines_are_preserved_as_plain_text(self):
        result=format_job_text('<h3>Responsibilities</h3><ul><li>Build APIs</li><li>Use SQL</li></ul><p>Work together.</p><script>bad()</script>')
        self.assertIn('Responsibilities:\n• Build APIs\n• Use SQL',result)
        self.assertNotIn('<li>',result);self.assertNotIn('bad()',result)
        self.assertIn('First line\nSecond line',format_job_text('First line\nSecond line'))

    def test_long_source_without_punctuation_splits_at_task_starts(self):
        text=('Thiết kế kiến trúc để đáp ứng các yêu cầu của khách hàng trong nhiều hệ thống tích hợp '
              'Xây dựng và vận hành CI/CD pipeline cho các dự án quy mô lớn với các môi trường kiểm thử '
              'Phối hợp với các bên liên quan để đảm bảo hệ thống được triển khai thành công '
              'Quản lý hạ tầng AWS theo best practices về bảo mật, hiệu năng và khả năng mở rộng')
        result=format_job_text(text)
        self.assertIn('\nXây dựng',result);self.assertIn('\nPhối hợp',result);self.assertIn('\nQuản lý',result)
        self.assertEqual(' '.join(result.split()),text)

    def test_glued_sentences_middle_dot_and_numbered_source_lists(self):
        result=format_job_text('Work with CSV).Clean data.Build models.Support users.')
        self.assertEqual(result,'Work with CSV).\nClean data.\nBuild models.\nSupport users.')
        self.assertEqual(format_job_text('· Bảo trì máy tính; · Quản lý máy chủ'),'• Bảo trì máy tính;\n• Quản lý máy chủ')
        self.assertEqual(format_job_text('1) Làm API; 2) Kiểm thử API'),'1) Làm API;\n2) Kiểm thử API')
        self.assertEqual(format_job_text('Dùng Node.Js, Vue.js và ASP.NET tại https://Example.Com/ABC.'),'Dùng Node.Js, Vue.js và ASP.NET tại https://Example.Com/ABC.')

    def test_localized_summary_does_not_reveal_wrong_language_source(self):
        row={'Job_Description':'Structured English summary. Experience required.',
             'Original_Job_Description':'Mô tả tiếng Việt','Job_Description_Display':'Mô tả:\n• Tiếng Việt'}
        self.assertNotIn('Tiếng Việt',display_job_field(row,'Job_Description'))
        row['Job_Description']='Mô tả tiếng Việt'
        self.assertEqual(display_job_field(row,'Job_Description'),'Mô tả:\n• Tiếng Việt')


if __name__=='__main__':unittest.main()
