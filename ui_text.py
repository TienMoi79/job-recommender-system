"""Thông báo lỗi đọc CV Việt/Anh cho API JobVista; nhãn web nằm ở web_ui/app.js."""

TEXT = {'vi': {'cv_file_empty': 'Tệp CV đang trống. Hãy chọn một tệp khác.',
        'cv_file_large': 'Tệp CV quá lớn. Vui lòng dùng tệp tối đa 15 MB.',
        'cv_format_unsupported': 'Hãy chọn ảnh, PDF hoặc Word .docx. Với file .doc cũ, hãy lưu lại thành .docx.',
        'cv_file_invalid': 'Không đọc được tệp này. Hãy kiểm tra tệp hoặc lưu lại thành PDF/Word .docx rồi thử '
                           'lại.',
        'cv_too_many_pages': 'CV có quá nhiều trang. Vui lòng dùng tối đa 20 trang.',
        'cv_image_too_large': 'Ảnh quá lớn để đọc. Hãy giảm kích thước ảnh rồi thử lại.',
        'cv_no_text': 'Chưa đọc được nội dung CV. Hãy dùng ảnh rõ nét hơn hoặc tệp PDF/Word có chữ.',
        'cv_text_too_long': 'Nội dung CV quá dài. Vui lòng dùng CV ngắn hơn (tối đa 60.000 ký tự).',
        'cv_pdf_locked': 'PDF có mật khẩu. Hãy tải lên bản PDF không có mật khẩu.',
        'cv_ocr_unavailable': 'Chưa dùng được bộ đọc chữ từ ảnh. Hãy thử lại khi có mạng, hoặc dùng Word '
                              '.docx/PDF có chữ.'},
 'en': {'cv_file_empty': 'The CV file is empty. Choose another file.',
        'cv_file_large': 'The CV file is too large. Please use a file up to 15 MB.',
        'cv_format_unsupported': 'Choose an image, PDF or Word .docx file. Save older .doc files as .docx first.',
        'cv_file_invalid': 'Unable to read this file. Check it or save it as PDF/Word .docx and try again.',
        'cv_too_many_pages': 'The CV has too many pages. Please use no more than 20 pages.',
        'cv_image_too_large': 'The image is too large to read. Reduce its dimensions and try again.',
        'cv_no_text': 'Unable to extract CV content. Use a clearer image or a PDF/Word document with text.',
        'cv_text_too_long': 'The CV content is too long. Use a shorter CV (up to 60,000 characters).',
        'cv_pdf_locked': 'This PDF is password-protected. Upload a PDF without a password.',
        'cv_ocr_unavailable': 'The image text reader is unavailable. Try again with an internet connection, or '
                              'use a Word .docx/text-based PDF.'}}
