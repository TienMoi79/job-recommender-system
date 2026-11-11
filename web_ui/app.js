/* JobVista: API Python tính điểm thật; tìm kiếm và CV đã đọc được lưu cục bộ
 * trong trình duyệt. Không lưu tệp CV gốc, không có đồng bộ tài khoản. */
'use strict';

const copy = {
  vi: {
    pageTitle:'JobVista — Tìm cơ hội của bạn', tagline:'MỞ LỐI SỰ NGHIỆP', explore:'Khám phá việc làm', cv:'Tìm việc với CV', saved:'Việc đã lưu',
    preview:'Bản xem thử', language:'Switch to English', eyebrow:'MỘT BƯỚC GẦN HƠN VỚI CÔNG VIỆC BẠN YÊU',
    hero:'Không chỉ tìm việc.<br>Tìm <em>đúng cơ hội.</em>', intro:'Khám phá việc làm IT và kết nối kỹ năng của bạn với những cơ hội phù hợp. Hành trình mới bắt đầu từ đây.',
    heroCv:'Để kỹ năng của bạn<br><em>tìm thấy đúng nơi.</em>', cvIntro:'Tải CV lên. Chúng tôi giúp bạn khám phá công việc phù hợp với năng lực và nơi bạn muốn làm việc.',
    jobs:'việc làm IT', companies:'công ty', regions:'khu vực', smart:'Tìm việc từ CV', smartSub:'Kỹ năng của bạn là điểm bắt đầu',
    cardRole:'CƠ HỘI DÀNH CHO BẠN', cardHint:'Từ kỹ năng đến công việc phù hợp', skillConnection:'Kết nối kỹ năng',
    keyword:'Chức danh, kỹ năng hoặc công ty', regionAll:'Tất cả địa điểm', search:'Tìm việc', suggested:'Thử tìm:', all:'Tất cả',
    data:'Dữ liệu', dev:'Lập trình', ai:'Trí tuệ nhân tạo', filters:'Bộ lọc', reset:'Đặt lại', domain:'Lĩnh vực', allDomains:'Tất cả lĩnh vực',
    location:'Địa điểm làm việc', experience:'Kinh nghiệm', expAny:'Tất cả kinh nghiệm', exp0:'Dưới 1 năm', exp1:'1–3 năm', exp3:'Trên 3 năm',
    years:'năm', expUnknown:'Kinh nghiệm chưa rõ', salaryUnknown:'Lương thỏa thuận / chưa rõ', minExp:'Từ',
    cvNudge:'Công việc nào hợp với bạn?', cvNudgeSub:'Để CV giúp bạn tìm câu trả lời.', tryCv:'Thử tìm việc với CV',
    resultTitle:'Cơ hội dành cho bạn', resultSuffix:'việc làm phù hợp bộ lọc', relevance:'Theo độ phù hợp', original:'Thứ tự trong dữ liệu',
    cvResultTitle:'Việc làm phù hợp với CV tại khu vực bạn chọn', cvResultAllTitle:'Việc làm phù hợp với CV trên tất cả khu vực',
    cvResultSuffix:'việc làm được đề xuất theo CV và khu vực đã chọn', cvResultAllSuffix:'việc làm được đề xuất theo CV trên tất cả khu vực',
    savedTitle:'Những cơ hội bạn muốn giữ lại', savedSub:'Được lưu trên trình duyệt này để bạn dễ quay lại.',
    save:'Lưu công việc', unsave:'Bỏ lưu công việc', savedToast:'Đã lưu vào danh sách của bạn', removedToast:'Đã bỏ lưu công việc',
    details:'Chi tiết công việc', description:'Mô tả công việc', requirements:'Yêu cầu ứng viên', skills:'Kỹ năng',
    similar:'Cơ hội tương tự', similarSub:'Gợi ý theo nội dung công việc', selectJob:'Chọn một công việc để xem chi tiết',
    sourceNote:'Dữ liệu tham khảo từ bộ tin công khai. Chưa xác minh tin còn nhận hồ sơ.',
    noJobs:'Chưa tìm thấy công việc phù hợp', noJobsSub:'Thử thay đổi từ khóa hoặc mở rộng địa điểm và bộ lọc.', noSaved:'Bạn chưa lưu công việc nào', noSavedSub:'Bấm biểu tượng đánh dấu trên công việc bạn quan tâm để lưu lại.',
    previous:'Trước', next:'Sau', page:'Trang', loading:'Đang tải cơ hội mới…', connection:'Chưa kết nối được máy chủ. Kiểm tra terminal và thử lại.', retry:'Thử lại',
    uploadStep:'Tải CV', confirmStep:'Xác nhận thông tin', resultsStep:'Khám phá cơ hội', uploadTitle:'Bắt đầu với CV của bạn',
    uploadSub:'Một tệp CV. Nhiều cơ hội mới.', dropTitle:'Kéo thả CV vào đây', dropSub:'hoặc chọn tệp từ máy tính của bạn', choose:'Chọn tệp CV', formats:'PDF, Word (.docx), JPG, PNG, WEBP, TIFF · Tối đa 15 MB',
    privacy:'Nội dung CV đã đọc và lựa chọn của bạn được tự lưu trên trình duyệt này để gợi ý lần sau. Không lưu tệp gốc, không gửi tới AI bên ngoài. Có thể xóa hồ sơ bất cứ lúc nào; tránh dùng trên máy dùng chung.', read:'Đọc & phân tích CV', reading:'Đang đọc CV của bạn…', readHint:'CV scan và ảnh cần thêm thời gian để nhận diện chữ.', remove:'Xóa hồ sơ CV',
    sample:'Chưa có CV? Thử một hồ sơ mẫu', sampleData:'Phân tích dữ liệu', sampleBackend:'Lập trình Backend', sampleAI:'Kỹ sư AI',
    how:'Một hành trình, ba bước đơn giản', howSub:'Tập trung vào năng lực. Tìm cơ hội gần với bạn.',
    how1:'Thêm CV của bạn', how1Sub:'Ảnh, PDF hoặc Word — chọn định dạng thuận tiện nhất.', how2:'Chọn nơi bạn muốn làm', how2Sub:'Kiểm tra kỹ năng đã đọc và xác nhận khu vực mong muốn.', how3:'Khám phá công việc phù hợp', how3Sub:'Xem kỹ năng trùng và lý do công việc được gợi ý.',
    analyzed:'CV đã sẵn sàng', detected:'Kỹ năng nhận diện', noSkills:'Chưa nhận diện được kỹ năng cụ thể. Bạn có thể kiểm tra nội dung đã đọc.',
    preferred:'Bạn muốn làm việc ở đâu?', preferredHint:'Địa điểm từ CV chỉ là gợi ý. Hãy chọn nơi bạn thực sự muốn làm.',
    review:'Xem và sửa nội dung đã đọc', textLabel:'Nội dung CV', find:'Tìm công việc phù hợp', matching:'Đang tìm cơ hội cho bạn…',
    ocrNote:'CV được đọc bằng OCR. Hãy kiểm tra lại địa điểm và nội dung nếu ảnh bị mờ hoặc nhiều cột.',
    cvReady:'Đã đọc nội dung CV', matched:'Kết quả từ CV của bạn', matchedSub:'Lọc theo nơi bạn muốn làm, ưu tiên nội dung gần với CV.',
    score:'Điểm phù hợp', why:'Vì sao công việc này phù hợp?', matchedSkills:'Kỹ năng trùng với CV', noSkillMatch:'Chưa tìm thấy kỹ năng trùng trực tiếp.',
    scoreNote:'Điểm kết hợp nội dung, kỹ năng, vị trí và kinh nghiệm; không phải xác suất trúng tuyển. Thành phần chưa rõ được bỏ qua và các trọng số còn lại được chuẩn hóa lại.',
    titleScore:'Vị trí', skillScore:'Kỹ năng', domainScore:'Lĩnh vực', descScore:'Nội dung CV', adjust:'Chỉnh sửa CV',
    changed:'Thông tin đã thay đổi. Bấm tìm lại để cập nhật kết quả.', invalidFile:'Vui lòng chọn PDF, Word .docx hoặc ảnh được hỗ trợ, tối đa 15 MB.',
    emptyCv:'Hãy tải CV hoặc chọn một hồ sơ mẫu trước.', publicData:'tin IT · Nguồn công khai · Dùng cho đồ án',
    homeRegion:'Bạn hiện đang ở đâu?', homeHint:'Nơi ở khác với nơi muốn làm việc. Chọn lại nếu CV được đọc chưa đúng; dùng để đối chiếu việc gần bạn.',
    homeUnknown:'Chưa xác định nơi ở', comparisonTitle:'Cân nhắc chuyên môn và khoảng cách',
    comparisonSub:'Đối chiếu toàn quốc; danh sách bên dưới vẫn theo nơi muốn làm việc bạn đã chọn.',
    bestFit:'Phù hợp chuyên môn nhất', nearest:'Gần nơi ở nhất trong các việc đạt ngưỡng',
    balancedTitle:'Cân bằng chuyên môn và khoảng cách', balancedBadge:'GỢI Ý KẾT HỢP',
    balancedIntro:'Ưu tiên công việc phù hợp với năng lực, đồng thời cân nhắc độ gần nơi bạn ở.',
    balancedScore:'Điểm cân bằng', proximityScore:'Điểm gần nơi ở', balanceHow:'Cách sắp xếp gợi ý kết hợp',
    balanceRule:'Ưu tiên chuyên môn {fit}%, kết hợp độ gần nơi ở {proximity}%. Càng xa, điểm gần càng giảm. Chỉ xét công việc đã đạt ngưỡng phù hợp với CV và có khoảng cách xác định.',
    balanceNote:'Điểm xếp hạng tham khảo, không phải xác suất trúng tuyển. Hai nhóm bên dưới giúp bạn đối chiếu riêng từng yếu tố.',
    distanceNote:'Khoảng cách ước tính đường chim bay giữa các điểm đại diện thành phố; không phải đường đi thực tế hay địa chỉ công ty. Cùng khu vực vẫn có thể cách xa nhau.',
    sameRegion:'Cùng khu vực nơi ở', approxDistance:'Cách khu vực của bạn khoảng', unknownDistance:'Chưa xác định khoảng cách',
    setHome:'Cần xác nhận nơi ở để so sánh khoảng cách.', noNear:'Chưa có việc đủ phù hợp và đủ thông tin vị trí để đối chiếu.',
    cvOnlyScore:'Điểm chuyên môn CV', demandLabel:'Điểm quan tâm ngành', demandHint:'Điểm nhu cầu từ lượt ghép CV ẩn danh trong 30 ngày, không phải đánh giá chất lượng công việc.',
    demandSample:'trình duyệt tham gia', demandWaiting:'Chưa đủ 5 trình duyệt để tính vào xếp hạng.', demandActive:'Góp tối đa 10% vào điểm gợi ý; nội dung phù hợp vẫn là căn cứ chính.',
    demandPrivacy:'Khi bấm tìm việc, web ghi nhận nhóm nghề và mã trình duyệt ẩn danh để tính nhu cầu; không đưa nội dung CV vào thống kê.',
    emptyDetail:'Chi tiết sẽ xuất hiện ở đây', close:'Đóng chi tiết', selected:'Đang xem', footer:'Từ kỹ năng đến cơ hội mới.', newFile:'Chọn CV khác',
    lexicalScore:'Từ khóa', semanticScore:'Ý nghĩa nội dung', expScore:'Kinh nghiệm', notUsed:'Chưa sử dụng',
    cvExperience:'Tổng số năm kinh nghiệm', cvExperienceHint:'Kiểm tra số năm đã đọc. Có thể sửa hoặc để trống nếu chưa xác định; không rõ sẽ không bị coi là 0 năm.',
    experienceUnknown:'Chưa xác định', notMentioned:'Chưa thấy trong CV', missingRequired:'Kỹ năng bắt buộc chưa thấy trong CV',
    matchedCount:'kỹ năng trong tin đã thấy trong CV', expMeets:'Kinh nghiệm đạt mức tối thiểu được ghi trong tin.',
    expBelow:'Kinh nghiệm thấp hơn mức tối thiểu trong tin; hệ thống giảm điểm mềm, không tự loại.',
    expFitUnknown:'Chưa đủ thông tin kinh nghiệm; thành phần này không được tính điểm.',
    semanticFallback:'Lượt tìm này dùng từ khóa, kỹ năng, vị trí và kinh nghiệm; chưa dùng điểm tương đồng ngữ nghĩa.',
    invalidExperience:'Số năm kinh nghiệm phải từ 0 đến 60, hoặc để trống nếu chưa xác định.',
    forYou:'Phù hợp với bạn', forYouSub:'Ưu tiên CV và nơi bạn muốn làm, kết hợp những công việc bạn quan tâm gần đây.',
    interestTitle:'Có thể bạn quan tâm', interestSub:'Gợi ý từ mối quan tâm gần đây. Thêm CV để đối chiếu với kỹ năng và kinh nghiệm của bạn.',
    interestEyebrow:'CƠ HỘI DÀNH RIÊNG CHO BẠN', interestSummary:'Từ những công việc bạn quan tâm', interestLocal:'Mối quan tâm được ghi nhớ tự động trên trình duyệt này.',
    personalScore:'Điểm gợi ý', interestWhy:'Gợi ý này dựa trên mối quan tâm khi tìm việc, chưa phải đánh giá độ phù hợp với CV.',
    combinedWhy:'Gợi ý kết hợp hồ sơ CV và mối quan tâm khi tìm việc. Phần điểm ghép CV bên dưới được tính riêng.',
    personalEyebrow:'GỢI Ý TỪ HỒ SƠ CỦA BẠN', profileEmpty:'Cơ hội phù hợp bắt đầu từ CV của bạn',
    profileEmptySub:'Đọc CV một lần để nhận gợi ý riêng mỗi khi quay lại trang chủ.', addCv:'Thêm CV của bạn',
    profileSaved:'Hồ sơ đã tự lưu', profileSession:'Hồ sơ chỉ dùng trong phiên này', savedCv:'CV đã lưu',
    editProfile:'Cập nhật hồ sơ', deleteProfile:'Xóa hồ sơ', profileDeleted:'Đã xóa hồ sơ CV đã lưu',
    allMatches:'Xem tất cả gợi ý', personalLoading:'Đang tìm cơ hội dành cho bạn…',
    personalEmpty:'Chưa có việc đủ phù hợp với hồ sơ và khu vực này.', personalEmptySub:'Bạn có thể cập nhật kỹ năng hoặc mở rộng nơi muốn làm. Chúng tôi không thêm việc ngoài vùng để lấp danh sách.',
    personalError:'Chưa tải được gợi ý cá nhân. Hồ sơ đã lưu vẫn được giữ lại.',
    storageError:'Trình duyệt không cho phép lưu hoặc bộ nhớ đã đầy. Thay đổi mới chỉ dùng trong phiên này; bản đã lưu trước đó có thể vẫn còn. Hãy kiểm tra quyền lưu trữ của trình duyệt.',
    deleteFailed:'Chưa xóa được hồ sơ khỏi bộ nhớ trình duyệt. Hãy kiểm tra quyền lưu trữ hoặc xóa dữ liệu trang web trong cài đặt trình duyệt.',
    autoSaveHint:'Tự lưu nội dung đã đọc, khu vực và kinh nghiệm khi bạn chỉnh sửa. Chọn CV khác để thay hồ sơ; Xóa hồ sơ để bỏ dữ liệu đã lưu.',
    personalScope:'Khu vực trong hồ sơ CV được ưu tiên. Web tự ghi nhớ mối quan tâm để điều chỉnh gợi ý cho những lần sau.',
  },
  en: {
    pageTitle:'JobVista — Find your next opportunity', tagline:'MAKE YOUR NEXT MOVE', explore:'Explore jobs', cv:'Match your CV', saved:'Saved jobs',
    preview:'Preview', language:'Chuyển sang tiếng Việt', eyebrow:'ONE STEP CLOSER TO WORK YOU LOVE',
    hero:'More than a job.<br>Your <em>next opportunity.</em>', intro:'Explore IT jobs and connect your skills with opportunities that fit. Your next chapter starts here.',
    heroCv:'Let your skills<br><em>find their place.</em>', cvIntro:'Upload your CV. Discover opportunities that fit your experience and where you want to work.',
    jobs:'IT opportunities', companies:'companies', regions:'regions', smart:'Find jobs with your CV', smartSub:'Your skills are the starting point',
    cardRole:'YOUR NEXT OPPORTUNITY', cardHint:'From your skills to the right opportunity', skillConnection:'Connect your skills',
    keyword:'Job title, skill or company', regionAll:'All locations', search:'Find jobs', suggested:'Try:', all:'All jobs',
    data:'Data', dev:'Development', ai:'Artificial intelligence', filters:'Filters', reset:'Reset', domain:'Field', allDomains:'All fields',
    location:'Work location', experience:'Experience', expAny:'Any experience', exp0:'Under 1 year', exp1:'1–3 years', exp3:'Over 3 years',
    years:'years', expUnknown:'Experience not specified', salaryUnknown:'Salary negotiable / unspecified', minExp:'From',
    cvNudge:'Which job fits your skills?', cvNudgeSub:'Let your CV help you find the answer.', tryCv:'Try CV matching',
    resultTitle:'Your next opportunity', resultSuffix:'jobs match your filters', relevance:'Best match first', original:'Dataset order',
    cvResultTitle:'Jobs matching your CV in your selected area', cvResultAllTitle:'Jobs matching your CV across all areas',
    cvResultSuffix:'jobs recommended for your CV and selected area', cvResultAllSuffix:'jobs recommended for your CV across all areas',
    savedTitle:'Opportunities worth keeping', savedSub:'Saved in this browser so you can come back anytime.',
    save:'Save job', unsave:'Remove saved job', savedToast:'Added to your saved jobs', removedToast:'Removed from saved jobs',
    details:'Job details', description:'Job description', requirements:'Requirements', skills:'Skills',
    similar:'Similar opportunities', similarSub:'Recommended by job content', selectJob:'Select a job to see the details',
    sourceNote:'Reference data from public listings. Current availability has not been verified.',
    noJobs:'No matching opportunities yet', noJobsSub:'Try a different keyword or broaden your location and filters.', noSaved:'No saved jobs yet', noSavedSub:'Use the bookmark on any job that catches your eye.',
    previous:'Previous', next:'Next', page:'Page', loading:'Loading your next opportunity…', connection:'Unable to connect. Check the server terminal and try again.', retry:'Try again',
    uploadStep:'Upload CV', confirmStep:'Check details', resultsStep:'Explore matches', uploadTitle:'Start with your CV',
    uploadSub:'One CV. A world of possibilities.', dropTitle:'Drag your CV here', dropSub:'or choose a file from your computer', choose:'Choose CV file', formats:'PDF, Word (.docx), JPG, PNG, WEBP, TIFF · Up to 15 MB',
    privacy:'Extracted CV content and your preferences are automatically saved in this browser for future suggestions. The original file is not saved or sent to external AI. Delete your profile anytime; avoid shared devices.', read:'Read & analyze CV', reading:'Reading your CV…', readHint:'Scanned CVs and images take longer to recognize.', remove:'Delete CV profile',
    sample:'No CV handy? Try a sample profile', sampleData:'Data analyst', sampleBackend:'Backend developer', sampleAI:'AI engineer',
    how:'One journey, three simple steps', howSub:'Focus on your strengths. Find opportunities that fit.',
    how1:'Add your CV', how1Sub:'Image, PDF or Word — use the format that works for you.', how2:'Choose where to work', how2Sub:'Check the extracted skills and confirm your preferred area.', how3:'Explore your matches', how3Sub:'See shared skills and why each job was recommended.',
    analyzed:'Your CV is ready', detected:'Detected skills', noSkills:'No specific skills detected yet. You can review the extracted content.',
    preferred:'Where would you like to work?', preferredHint:'Your CV location is a suggestion. Choose where you actually want to work.',
    review:'Review and edit extracted content', textLabel:'CV content', find:'Find matching opportunities', matching:'Finding opportunities for you…',
    ocrNote:'This CV was read using OCR. Review the location and content if the image is blurry or has multiple columns.',
    cvReady:'CV content extracted', matched:'Matched to your CV', matchedSub:'Filtered by your preferred location, then ranked by CV content.',
    score:'Match score', why:'Why this opportunity?', matchedSkills:'Skills shared with your CV', noSkillMatch:'No direct skill overlap detected.',
    scoreNote:'A combined content, skills, role and experience score, not a hiring probability. Unknown components are omitted and the remaining weights are renormalized.',
    titleScore:'Position', skillScore:'Skills', domainScore:'Field', descScore:'CV content', adjust:'Edit CV',
    changed:'Your information changed. Find matches again to refresh the results.', invalidFile:'Choose a supported PDF, Word .docx or image file, up to 15 MB.',
    emptyCv:'Upload a CV or choose a sample profile first.', publicData:'IT listings · Public data · Academic project',
    homeRegion:'Where do you currently live?', homeHint:'Your home area can differ from your preferred work location. Check the extracted area to compare nearby opportunities.',
    homeUnknown:'Home area not identified', comparisonTitle:'Compare career fit and distance',
    comparisonSub:'Nationwide comparison; the main list below still follows your preferred work location.',
    bestFit:'Best professional fit', nearest:'Closest to home among qualifying jobs',
    balancedTitle:'Balance career fit and distance', balancedBadge:'COMBINED PICKS',
    balancedIntro:'Prioritise jobs that match your skills while considering how close they are to your home area.',
    balancedScore:'Balanced score', proximityScore:'Proximity score', balanceHow:'How combined picks are ranked',
    balanceRule:'Professional fit contributes {fit}% and proximity contributes {proximity}%. Proximity decreases with distance. Only jobs meeting the CV relevance threshold and with a known distance are considered.',
    balanceNote:'An indicative ranking score, not a hiring probability. The two groups below let you compare each factor separately.',
    distanceNote:'Approximate straight-line distance between representative city points, not travel distance or the company address. Jobs in the same area may still be far apart.',
    sameRegion:'In your home area', approxDistance:'Approximately this far from your area:', unknownDistance:'Distance not identified',
    setHome:'Confirm your home area to compare distance.', noNear:'No sufficiently relevant jobs with known locations to compare yet.',
    cvOnlyScore:'CV content score', demandLabel:'Career interest rating', demandHint:'Demand from anonymous CV matching over 30 days, not an employer or job quality rating.',
    demandSample:'participating browsers', demandWaiting:'At least 5 browsers are needed before demand affects ranking.', demandActive:'Contributes up to 10% to recommendation scores; content fit remains the main signal.',
    demandPrivacy:'Finding jobs records the career group and an anonymous browser identifier for demand statistics; CV content is not stored in these statistics.',
    emptyDetail:'Job details will appear here', close:'Close details', selected:'Selected', footer:'From your skills to your next opportunity.', newFile:'Choose another CV',
    lexicalScore:'Keywords', semanticScore:'Meaning', expScore:'Experience', notUsed:'Not used',
    cvExperience:'Total years of experience', cvExperienceHint:'Check the extracted years. Correct them or leave blank if unknown; unknown is not treated as zero.',
    experienceUnknown:'Not identified', notMentioned:'Not mentioned in your CV', missingRequired:'Required skills not mentioned in your CV',
    matchedCount:'skills in the listing found in your CV', expMeets:'Your experience meets the stated minimum.',
    expBelow:'Your experience is below the stated minimum; a soft score reduction applies, without automatic rejection.',
    expFitUnknown:'Not enough experience information; this component is not scored.',
    semanticFallback:'These results use keywords, skills, role and experience; semantic similarity was not used for this search.',
    invalidExperience:'Experience must be between 0 and 60 years, or left blank if unknown.',
    forYou:'Recommended for you', forYouSub:'Your CV and preferred location come first, with recent job interests helping personalize the order.',
    interestTitle:'You might be interested', interestSub:'Based on your recent interests. Add a CV to check your skills and experience against these opportunities.',
    interestEyebrow:'OPPORTUNITIES FOR YOU', interestSummary:'Based on the opportunities you explore', interestLocal:'Your interests are remembered automatically in this browser.',
    personalScore:'Recommendation score', interestWhy:'This suggestion reflects your job-search interests, rather than a CV fit assessment.',
    combinedWhy:'This suggestion combines CV fit and job-search interests. The CV matching score below is calculated separately.',
    personalEyebrow:'BASED ON YOUR PROFILE', profileEmpty:'Your next opportunity starts with your CV',
    profileEmptySub:'Read your CV once to get personal suggestions whenever you return to the homepage.', addCv:'Add your CV',
    profileSaved:'Profile saved automatically', profileSession:'Profile available in this session only', savedCv:'Saved CV',
    editProfile:'Update profile', deleteProfile:'Delete profile', profileDeleted:'Saved CV profile deleted',
    allMatches:'See all matches', personalLoading:'Finding opportunities for you…',
    personalEmpty:'No sufficiently relevant jobs in this location yet.', personalEmptySub:'Update your skills or broaden your preferred location. We do not fill the list with jobs outside your chosen area.',
    personalError:'Personal suggestions are unavailable right now. Your saved profile is still here.',
    storageError:'Browser storage is blocked or full. New changes last for this session only; an older saved copy may remain. Check your browser storage permissions.',
    deleteFailed:'Unable to remove the profile from browser storage. Check storage permissions or clear this site’s data in your browser settings.',
    autoSaveHint:'Extracted content, location and experience save automatically as you edit. Choose another CV to replace the profile, or delete it to remove saved data.',
    personalScope:'Your CV location takes priority. Interests are remembered automatically to personalize future suggestions.',
  }
};
const icons = {
  search:'<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 4 4"/>',
  pin:'<path d="M19 10c0 5-7 11-7 11S5 15 5 10a7 7 0 1 1 14 0Z"/><circle cx="12" cy="10" r="2.3"/>',
  bookmark:'<path d="M6 4h12v17l-6-4-6 4Z"/>', arrow:'<path d="M5 12h14m-6-6 6 6-6 6"/>',
  spark:'<path d="m12 3 2.7 6.3L21 12l-6.3 2.7L12 21l-2.7-6.3L3 12l6.3-2.7Z"/>',
  briefcase:'<rect x="3" y="7" width="18" height="14" rx="2"/><path d="M8 7V4h8v3M3 12c5 3 13 3 18 0m-9 0v4"/>',
  chevron:'<path d="m9 5 7 7-7 7"/>', check:'<path d="m5 12 4 4L19 6"/>',
  upload:'<path d="M12 16V3m-5 5 5-5 5 5M4 15v6h16v-6"/>',
  file:'<path d="M14 3H5v18h14V8Zm0 0v5h5M8 12h8m-8 4h6"/>',
  lock:'<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>',
  close:'<path d="m6 6 12 12M6 18 18 6"/>', tune:'<path d="M3 7h18M3 17h18"/><circle cx="8" cy="7" r="3"/><circle cx="16" cy="17" r="3"/>',
  clock:'<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  external:'<path d="M14 3h7v7m0-7L10 14M10 3H3v18h18v-7"/>',
  globe:'<circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="4" ry="9"/><path d="M3 12h18"/>',
};
const icon = (name, cls='') => `<svg class="icon ${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${icons[name]||icons.briefcase}</svg>`;
const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const normalized = value => String(value).toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/đ/g,'d');
const $ = selector => document.querySelector(selector);
let stored = [];
try { stored = JSON.parse(localStorage.getItem('jobvista-saved') || '[]'); } catch {}
// Lấy localStorage cũng có thể bị SecurityError, nên trì hoãn bên trong adapter.
const personalStore = new JobVistaStorage({getItem:key=>localStorage.getItem(key),setItem:(key,value)=>localStorage.setItem(key,value),removeItem:key=>localStorage.removeItem(key)});
const restoredProfile = personalStore.readProfile();
const state = {lang:'vi',view:'explore',data:null,jobs:[],saved:new Set(Array.isArray(stored)?stored.filter(x=>typeof x==='string'):[]),
  q:'',region:'',domain:'',exp:'',category:'all',page:1,selected:null,detail:null,detailVersion:0,
  file:null,cvFilename:'',cvText:'',profile:null,ocr:false,cvRegion:'',cvHomeRegion:'',cvExperience:'',cvExperienceEdited:false,matchMethod:null,matches:null,comparison:null,reading:false,matching:false,cvVersion:0,loading:true,error:'',
  searchHistory:personalStore.readSearches(),savedProfile:restoredProfile,profileStored:!!restoredProfile,
  storageError:personalStore.failed,homeMatches:null,homeMethod:null,homePreference:null,homeLoading:false,homeError:false,homeVersion:0,homeKey:''};
function restoreProfile(record) {
  if(!record)return;
  Object.assign(state,{file:null,cvFilename:record.filename,cvText:record.text,profile:record.profile,ocr:record.ocr,
    cvRegion:record.region,cvHomeRegion:record.homeRegion||record.profile.home_locations?.[0]||'',cvExperience:record.experience,cvExperienceEdited:record.experienceEdited});
}
restoreProfile(restoredProfile);
const t = key => copy[state.lang][key];
let toastTimer, searchTimer, profileTimer, interestTimer;
function toast(message) { const el=$('#toast'); el.textContent=message; el.classList.add('visible'); clearTimeout(toastTimer); toastTimer=setTimeout(()=>el.classList.remove('visible'),3400); }
async function api(path, options={}) {
  const response = await fetch(path, options);
  if (!response.ok) {
    let error; try { error=await response.json(); } catch {}
    throw new Error(typeof error?.detail==='string' && !['invalid_location','empty_cv','job_not_found'].includes(error.detail) ? error.detail : t('connection'));
  }
  return response.json();
}
function logo() { return '<img src="/assets/favicon.svg" alt="" width="36" height="36"><span>Job<span class="brand-light">Vista</span><small>'+t('tagline')+'</small></span>'; }
function header() {
  return `<header class="header"><div class="header-inner"><a href="#" class="brand" data-nav="explore" aria-label="JobVista">${logo()}</a>
    <nav aria-label="${t('explore')}">${['explore','cv','saved'].map(view=>`<button class="nav-item ${state.view===view||(view==='explore'&&state.view==='personal')?'active':''}" data-nav="${view}">${view==='saved'?icon('bookmark'):''}${t(view)}${view==='saved'?`<span class="nav-count">${state.saved.size}</span>`:''}</button>`).join('')}</nav>
    <div class="header-actions"><span class="preview-badge"><span></span>${t('preview')}</span><button class="language-btn" id="language" aria-label="${t('language')}" title="${t('language')}">${icon('globe')}<span>${state.lang==='vi'?'VI':'EN'}</span></button></div></div></header>`;
}
function hero() {
  const isCv=state.view==='cv';
  return `<section class="hero ${isCv?'cv-hero':''}"><div class="hero-content"><p class="eyebrow"><span class="eyebrow-line"></span>${t('eyebrow')}</p>
    <h1>${t(isCv?'heroCv':'hero')}</h1><p class="hero-intro">${t(isCv?'cvIntro':'intro')}</p>
    <div class="hero-stats"><span><strong>${state.jobs.length||'—'}</strong>${t('jobs')}</span><i></i><span><strong>${state.data?.companies||'—'}</strong>${t('companies')}</span><i></i><span><strong>${state.data?.regions.length||'—'}</strong>${t('regions')}</span></div></div>
    <div class="hero-art" aria-hidden="true"><div class="orbit orbit-one"></div><div class="orbit orbit-two"></div><span class="art-spark">✳</span>
      <div class="floating-note">${icon('check')} ${t('skillConnection')}</div>
      <div class="opportunity-card"><div class="mini-card-top"><span class="mini-logo">&lt;/&gt;</span><span class="mini-dots">•••</span></div><p>${t('cardRole')}</p><h3>Backend Developer</h3><span class="mini-company">Python · FastAPI · SQL</span><div class="mini-tags"><b>Python</b><b>SQL</b><b>Docker</b></div><div class="mini-card-bottom"><span>${icon('pin')} ${state.lang==='vi'?'Hà Nội':'Hanoi'}</span><span class="art-check">${icon('check')}</span></div></div>
      <div class="floating-match">${icon('spark')}<span><strong>${t('smart')}</strong><small>${t('cardHint')}</small></span></div></div></section>`;
}
function regionOptions(value, all=true, forCv=false) {
  return `${all?`<option value="">${t('regionAll')}</option>`:''}${(forCv?state.data?.all_regions||[]:state.data?.regions||[]).map(r=>`<option value="${r.id}" ${value===r.id?'selected':''}>${escape(r.label)}</option>`).join('')}`;
}
function searchBar() {
  return `<section class="search-area"><form class="search-bar" id="search-form"><label class="keyword-field">${icon('search')}<input id="search" aria-label="${t('keyword')}" placeholder="${t('keyword')}" value="${escape(state.q)}" autocomplete="off" maxlength="200"></label>
    <label class="search-location">${icon('pin')}<select id="search-region" aria-label="${t('location')}">${regionOptions(state.region)}</select></label><button class="primary search-button" type="submit">${t('search')}${icon('arrow')}</button></form>
    <div class="suggestions"><span>${t('suggested')}</span>${['Python','Data Analyst','React','UI/UX'].map(x=>`<button data-search="${x}">${x}</button>`).join('')}<span class="search-meta">${icon('spark')}${state.jobs.length} ${t('publicData')}</span></div></section>`;
}
function storageNotice() {return state.storageError?`<p class="storage-notice" role="status">${icon('lock')}${t('storageError')}</p>`:'';}
function personalPanel() {
  const record=state.savedProfile;
  if(!record&&!state.searchHistory.length)return `<section class="personal-empty"><span class="personal-symbol">${icon('spark')}</span><div><h2>${t('profileEmpty')}</h2><p>${t('profileEmptySub')}</p></div><button class="secondary" data-nav="cv">${t('addCv')}${icon('arrow')}</button></section>`;
  // Chưa có CV và không có tín hiệu đủ phù hợp: không dựng gợi ý giả cho đầy trang.
  if(!record&&!state.homeLoading&&!state.homeError&&!state.homeMatches?.length)return '';
  const location=state.data.all_regions.find(r=>r.id===record?.region)?.label||t('regionAll');
  return `<section class="personal-panel" aria-labelledby="personal-title"><div class="personal-heading"><div><p class="section-kicker">${t(record?'personalEyebrow':'interestEyebrow')}</p><h2 id="personal-title">${t(record?'forYou':'interestTitle')}</h2><p>${t(record?'forYouSub':'interestSub')}</p></div><button class="secondary" id="all-personal" ${!state.homeMatches?.length?'disabled':''}>${t('allMatches')}${icon('arrow')}</button></div>
    ${record?`<div class="saved-profile-summary"><span class="personal-symbol">${icon('file')}</span><div><strong>${t(state.profileStored?'profileSaved':'profileSession')}</strong><span>${escape(record.profile.title||record.profile.skills.slice(0,4).join(' · ')||t('savedCv'))}</span><small>${icon('pin')}${escape(location)} · ${record.experience===''?t('expUnknown'):escape(record.experience)+' '+t('years')}${record.updatedAt?' · '+new Date(record.updatedAt).toLocaleDateString(state.lang==='vi'?'vi-VN':'en-GB'):''}</small></div><div class="profile-actions"><button class="text-button" id="edit-profile">${t('editProfile')}</button><button class="text-button danger-text" id="delete-profile">${t('deleteProfile')}</button></div></div>`:`<div class="interest-summary">${icon('spark')}<span>${t('interestSummary')}</span><button class="text-button" data-nav="cv">${t('addCv')}${icon('arrow')}</button></div>`}
    ${state.homeLoading?`<div class="personal-status" role="status"><span class="loader"></span>${t('personalLoading')}</div>`:state.homeError?`<div class="personal-status"><p>${t('personalError')}</p><button class="secondary" id="retry-personal">${t('retry')}</button></div>`:state.homeMatches?.length?`${state.homeMethod?.mode==='hybrid-lexical'?`<p class="personal-fallback">${t('semanticFallback')}</p>`:''}<div class="personal-jobs">${state.homeMatches.slice(0,4).map(jobCard).join('')}</div>`:`<div class="personal-status personal-no-match"><h3>${t('personalEmpty')}</h3><p>${t('personalEmptySub')}</p><button class="secondary" id="broaden-profile">${t('editProfile')}${icon('arrow')}</button></div>`}
    <p class="personal-scope">${t(record?'personalScope':'interestLocal')}</p></section>`;
}
function refreshPersonalPanel() {
  if($('#personal-home')){$('#personal-home').innerHTML=storageNotice()+personalPanel();bindPersonal();}
}
function savedMatchPayload(record) {
  return {text:record.text,location:record.region||null,language:state.lang,top_n:24,
    home_region:record.homeRegion||null,experience_override:record.experienceEdited,experience_years:record.experience===''?null:Number(record.experience)};
}
function homePayload() {
  return {language:state.lang,profile:state.savedProfile?savedMatchPayload(state.savedProfile):null,
    searches:state.searchHistory.map(({id,...signal})=>signal),top_n:24};
}
async function refreshHome(force=false) {
  if((!state.savedProfile&&!state.searchHistory.length)||!state.data)return;
  const payload=homePayload(),key=JSON.stringify(payload);
  if(!force&&state.homeKey===key&&(state.homeLoading||state.homeMatches!==null))return;
  const version=++state.homeVersion;
  Object.assign(state,{homeKey:key,homeLoading:true,homeError:false,homeMatches:null,homeMethod:null});refreshPersonalPanel();
  try {
    const result=await api('/api/recommendations',{method:'POST',headers:{'Content-Type':'application/json'},body:key});
    // Xóa/thay CV, đổi ngôn ngữ hoặc sửa khu vực phải vô hiệu hóa kết quả cũ.
    if(version!==state.homeVersion||JSON.stringify(homePayload())!==key)return;
    Object.assign(state,{homeMatches:result.jobs,homeMethod:result.algorithm,homePreference:result.personalization,homeLoading:false});
    // Văn bản có thể đã được người dùng sửa; dùng phân tích mới cho tóm tắt hồ sơ.
    if(state.savedProfile&&result.profile){
      state.savedProfile.profile=result.profile;
      if(!state.savedProfile.experienceEdited)state.savedProfile.experience=result.profile.experience_years??'';
      state.profileStored=personalStore.writeProfile(state.savedProfile);
      if(!state.profileStored)state.storageError=true;
      if(state.cvText===payload.profile.text){state.profile=result.profile;if(!state.cvExperienceEdited)state.cvExperience=result.profile.experience_years??'';}
    }
    state.homeKey=JSON.stringify(homePayload());
    refreshPersonalPanel();
  }catch{if(version===state.homeVersion){state.homeLoading=false;state.homeError=true;refreshPersonalPanel();}}
}
function persistCv() {
  clearTimeout(profileTimer);profileTimer=null;
  if(!state.profile||!state.cvText.trim()||
    (state.cvExperience!==''&&(!Number.isFinite(Number(state.cvExperience))||Number(state.cvExperience)<0||Number(state.cvExperience)>60)))return false;
  const record=JobVistaStorage.cleanProfile({version:1,text:state.cvText,filename:state.cvFilename,ocr:state.ocr,profile:state.profile,
    region:state.cvRegion,homeRegion:state.cvHomeRegion,experience:state.cvExperience,experienceEdited:state.cvExperienceEdited,updatedAt:Date.now()});
  if(!record)return false;
  state.savedProfile=record;state.profileStored=personalStore.writeProfile(record);
  if(!state.profileStored)state.storageError=true;
  if(state.homeKey!==JSON.stringify(homePayload())){state.homeVersion++;state.homeKey='';state.homeMatches=null;state.homeLoading=false;state.homeError=false;}
  return true;
}
function rememberSearch() {
  clearTimeout(interestTimer);interestTimer=null;
  if(state.view!=='explore'||!state.data)return;
  state.q=($('#search')?.value??state.q).trim().slice(0,200);
  const item={q:state.q,region:state.region,domain:state.domain,exp:state.exp,category:state.category};
  if(!JobVistaStorage.cleanSearch(item)||!filteredJobs().length)return;
  state.searchHistory=JobVistaStorage.upsertSearch(state.searchHistory,item);
  if(!personalStore.writeSearches(state.searchHistory))state.storageError=true;
  state.homeVersion++;state.homeKey='';state.homeMatches=null;state.homeLoading=false;refreshHome();
}
function queueSearchInterest(){clearTimeout(interestTimer);interestTimer=setTimeout(rememberSearch,1000);}
function editSavedProfile() {
  clearTimeout(profileTimer);state.cvVersion++;state.reading=false;state.matching=false;state.matches=null;
  restoreProfile(state.savedProfile);navigate('cv');
}
function showPersonalMatches(id=null) {
  if(!state.homeMatches)return;
  const jobs=state.homeMatches,method=state.homeMethod;
  clearTimeout(profileTimer);profileTimer=null;state.cvVersion++;state.reading=false;state.matching=false;
  if(interestTimer)rememberSearch();
  restoreProfile(state.savedProfile);state.matches=jobs;state.matchMethod=method;
  navigate('personal');if(id)toggleJobDetails(id);$('#workspace')?.scrollIntoView({behavior:'smooth',block:'start'});
}
function bindPersonal() {
  if($('#all-personal'))$('#all-personal').onclick=()=>showPersonalMatches();
  ['edit-profile','broaden-profile'].forEach(id=>{if($('#'+id))$('#'+id).onclick=editSavedProfile;});
  if($('#delete-profile'))$('#delete-profile').onclick=clearCv;
  if($('#retry-personal'))$('#retry-personal').onclick=()=>refreshHome(true);
  $('#personal-home')?.querySelectorAll('[data-nav]').forEach(el=>el.onclick=()=>navigate(el.dataset.nav));
  $('#personal-home')?.querySelectorAll('[data-card]').forEach(el=>el.onclick=event=>{if(!event.target.closest('button,a'))showPersonalMatches(el.dataset.card);});
  $('#personal-home')?.querySelectorAll('[data-job]').forEach(el=>el.onclick=()=>showPersonalMatches(el.dataset.job));
  $('#personal-home')?.querySelectorAll('[data-save]').forEach(el=>el.onclick=()=>toggleSave(el.dataset.save));
}
function filters() {
  return `<aside class="filters"><div class="filter-heading"><h3>${icon('tune')}${t('filters')}</h3><button class="text-button" id="reset">${t('reset')}</button></div>
    <label class="field-label" for="filter-region">${t('location')}</label><select id="filter-region">${regionOptions(state.region)}</select>
    <label class="field-label" for="filter-domain">${t('domain')}</label><select id="filter-domain"><option value="">${t('allDomains')}</option>${(state.data?.domain_options||[]).map(([id,label])=>`<option value="${escape(id)}" ${state.domain===id?'selected':''}>${escape(label)}</option>`).join('')}</select>
    <fieldset class="experience"><legend>${t('experience')}</legend>${[['','expAny'],['0','exp0'],['1','exp1'],['3','exp3']].map(([value,label])=>`<label><input type="radio" name="experience" value="${value}" ${state.exp===value?'checked':''}>${t(label)}</label>`).join('')}</fieldset>
    <div class="cv-nudge"><span class="nudge-icon">${icon('spark')}</span><h3>${t('cvNudge')}</h3><p>${t('cvNudgeSub')}</p><button data-nav="cv">${t('tryCv')}${icon('arrow')}</button></div>
    <p class="filter-note">${t('sourceNote')}</p></aside>`;
}
function companyLogo(job, small=false) {
  const hash=[...job.company].reduce((sum,c)=>sum+c.charCodeAt(0),0)%5;
  const words=job.company.replace(/CÔNG TY|CỔ PHẦN|TNHH|COMPANY|LIMITED|CORPORATION|TECHNOLOGIES/gi,'').trim().split(/\s+/).filter(Boolean);
  const initials=words.slice(0,2).map(w=>w[0]).join('').toUpperCase()||'IT';
  return `<span class="company-logo logo-${hash} ${small?'small':''}" aria-hidden="true">${escape(initials)}</span>`;
}
function experience(job) { return job.experience_known?`${t('minExp')} ${job.experience} ${state.lang==='en'&&job.experience===1?'year':t('years')}`:t('expUnknown'); }
function distanceLabel(job){return job.same_region?t('sameRegion'):job.distance_km!==null&&job.distance_km!==undefined?`${t('approxDistance')} ${job.distance_km} km`:t('unknownDistance');}
function demandExplanation(job) {
  if(job.demand_rating===undefined)return '';
  return `<section class="demand-explanation"><h3>${t('demandLabel')}: ${job.demand_rating.toFixed(2)}/5</h3>${job.personal_score!==undefined?`<p><strong>${t('personalScore')}: ${job.personal_score.toFixed(3)}</strong></p>`:''}<p>${t('demandHint')}</p><small>${job.demand_actors} ${t('demandSample')} · ${t(job.demand_weight>0?'demandActive':'demandWaiting')}</small></section>`;
}
function locationComparison() {
  const comparison=state.comparison;if(!comparison)return '';
  const policy=comparison.balance_policy||{fit_weight:.7,proximity_weight:.3};
  const rule=t('balanceRule').replace('{fit}',Math.round(policy.fit_weight*100)).replace('{proximity}',Math.round(policy.proximity_weight*100));
  const empty=`<p class="field-hint">${t(comparison.home_region||state.cvHomeRegion?'noNear':'setHome')}</p>`;
  const card=(job,balanced=false)=>`<article class="comparison-card${balanced?' balanced-card':''}"><button data-compare-job="${escape(job.id)}"><strong>${escape(job.title)}</strong><small>${escape(job.company)}</small><span>${escape(job.location)}</span><span class="comparison-distance">${escape(distanceLabel(job))}</span>${balanced?`<span class="balance-components"><span>${t('cvOnlyScore')}: ${job.score.toFixed(3)}</span><span>${t('proximityScore')}: ${job.proximity_score.toFixed(3)}</span></span><b class="balanced-score">${t('balancedScore')}: ${job.balanced_score.toFixed(3)}</b>`:`<b>${t('cvOnlyScore')}: ${job.score.toFixed(3)}</b>`}</button></article>`;
  return `<section class="location-comparison"><div class="personal-heading"><div><p class="section-kicker">${t('comparisonTitle')}</p><h2>${t('comparisonTitle')}</h2><p>${t('comparisonSub')}</p></div></div>
    <section class="balanced-recommendations" aria-labelledby="balanced-heading"><p class="balanced-badge">${icon('spark')}${t('balancedBadge')}</p><h3 id="balanced-heading">${t('balancedTitle')}</h3><p class="balanced-intro">${t('balancedIntro')}</p><div class="balanced-jobs">${(comparison.balanced||[]).map(job=>card(job,true)).join('')||empty}</div><details class="balance-method"><summary>${t('balanceHow')}</summary><p>${escape(rule)}</p><p>${t('balanceNote')}</p></details></section>
    <div class="comparison-columns">${[['best_fit','bestFit'],['near_home','nearest']].map(([key,label])=>`<div><h3>${icon(key==='best_fit'?'spark':'pin')}${t(label)}</h3><div class="comparison-jobs">${(comparison[key]||[]).map(job=>card(job)).join('')||empty}</div></div>`).join('')}</div><p class="field-hint">${t('distanceNote')}</p></section>`;
}
function saveButton(job, extra='') {const saved=state.saved.has(job.id); return `<button class="save-button ${saved?'is-saved':''} ${extra}" data-save="${job.id}" aria-label="${t(saved?'unsave':'save')}" aria-pressed="${saved}" title="${t(saved?'unsave':'save')}">${icon('bookmark')}</button>`;}
function jobCard(job) {
  return `<article class="job-card ${state.selected===job.id?'selected':''}" data-card="${job.id}"><div class="card-main"><button class="job-open" data-job="${job.id}" aria-label="${escape(job.title)}" aria-controls="job-detail" aria-expanded="${state.selected===job.id}">${companyLogo(job)}<span><span class="job-company">${escape(job.company)}</span><h3>${escape(job.title)}</h3></span></button>${saveButton(job)}</div>
    <div class="job-meta"><span>${icon('pin')}${escape(job.location)}</span><span>${icon('briefcase')}${experience(job)}</span></div>${job.home_region?`<p class="job-distance">${icon('pin')}${escape(distanceLabel(job))}</p>`:''}
    <div class="skill-tags">${job.skills.slice(0,4).map(s=>`<span class="${job.matched_skills?.includes(s)?'matched-skill':''}">${escape(s)}</span>`).join('')}${job.skills.length>4?`<span>+${job.skills.length-4}</span>`:''}</div>
    <div class="job-card-bottom"><strong>${escape(job.salary||t('salaryUnknown'))}</strong>${job.personal_score!==undefined||job.score!==undefined?`<span class="match-score" title="${t(job.personal_score!==undefined?'personalScore':'score')}">${icon('spark')}${(job.personal_score??job.score).toFixed(3)}</span>`:`<button class="card-arrow" data-job="${job.id}" aria-controls="job-detail" aria-expanded="${state.selected===job.id}" aria-label="${t('details')}: ${escape(job.title)}">${icon('arrow')}</button>`}</div></article>`;
}
function filteredJobs() {
  let jobs=['cv','personal'].includes(state.view)?(state.matches||[]):state.jobs;
  if(state.view==='saved') jobs=jobs.filter(j=>state.saved.has(j.id));
  const q=normalized(state.q).trim();
  return jobs.filter(job=>{
    if(q&&!normalized(`${job.title} ${job.company} ${job.skills.join(' ')} ${job.domain}`).includes(q)) return false;
    if(state.region&&!job.regions.includes(state.region)) return false;
    if(state.domain&&job.domain_id!==state.domain) return false;
    if(state.exp){ if(!job.experience_known) return false; if(state.exp==='0'&&job.experience>=1) return false; if(state.exp==='1'&&(job.experience<1||job.experience>3)) return false; if(state.exp==='3'&&job.experience<=3)return false; }
    const category=normalized(job.domain);
    if(state.category==='data'&&!/du lieu|data/.test(category))return false;
    if(state.category==='dev'&&!/phat trien|development|software/.test(category))return false;
    if(state.category==='ai'&&!/tri tue|intelligence/.test(category))return false;
    return true;
  });
}
function emptyState() {
  const saved=state.view==='saved';
  return `<div class="empty-state">${icon(saved?'bookmark':'search')}<h3>${t(saved?'noSaved':'noJobs')}</h3><p>${t(saved?'noSavedSub':'noJobsSub')}</p><button class="secondary" ${saved?'data-nav="explore"':'id="empty-reset"'}>${t(saved?'explore':'reset')}${icon('arrow')}</button></div>`;
}
function results() {
  const jobs=filteredJobs();const pages=Math.max(1,Math.ceil(jobs.length/8));state.page=Math.min(state.page,pages);
  return `<div class="results-heading"><div><p class="section-kicker">${state.view==='cv'?t('matched'):state.view==='personal'?t('interestEyebrow'):t('explore')}</p><h2>${state.view==='saved'?t('savedTitle'):state.view==='cv'?t(state.cvRegion?'cvResultTitle':'cvResultAllTitle'):state.view==='personal'?t(state.savedProfile?'forYou':'interestTitle'):t('resultTitle')}<span>${jobs.length}</span></h2><p>${jobs.length} ${t(state.view==='cv'?(state.cvRegion?'cvResultSuffix':'cvResultAllSuffix'):'resultSuffix')}</p></div><span class="sort-label">${icon('tune')}${t(['cv','personal'].includes(state.view)?'relevance':'original')}</span></div>
    ${!['cv','personal'].includes(state.view)?`<div class="category-tabs" role="group" aria-label="${t('domain')}">${['all','dev','data','ai'].map(c=>`<button class="${state.category===c?'active':''}" data-category="${c}" aria-pressed="${state.category===c}">${t(c)}</button>`).join('')}</div>`:''}
    <div class="jobs-list">${jobs.slice((state.page-1)*8,state.page*8).map(jobCard).join('')||emptyState()}</div>
    ${pages>1?`<div class="pagination"><button class="page-control" data-page="${state.page-1}" ${state.page===1?'disabled':''} aria-label="${t('previous')}">‹</button><span>${t('page')} <strong>${state.page}</strong> / ${pages}</span><button class="page-control" data-page="${state.page+1}" ${state.page===pages?'disabled':''} aria-label="${t('next')}">›</button></div>`:''}`;
}
function explanation(job) {
  if(job.score===undefined) return '';
  const components=job.components||{};
  const weights=job.component_weights||{};
  const fields=[['Lexical','lexicalScore'],['Semantic','semanticScore'],['Title','titleScore'],['Skills','skillScore'],['Domain','domainScore'],['Experience','expScore']];
  return `<section class="explanation"><div class="explanation-title">${icon('spark')}<h3>${t('why')}</h3><strong>${job.score.toFixed(3)}</strong></div><p>${t('matchedSkills')}</p><div class="skill-tags">${job.matched_skills?.length?job.matched_skills.map(s=>`<span class="matched-skill">${escape(s)}</span>`).join(''):`<small>${t('noSkillMatch')}</small>`}</div>
    <p class="skill-coverage">${job.matched_skills?.length||0}/${job.job_skills_count||job.skills.length} ${t('matchedCount')}</p>
    ${job.not_mentioned_skills?.length?`<p>${t('notMentioned')}</p><div class="skill-tags missing-tags">${job.not_mentioned_skills.map(skill=>`<span>${escape(skill)}</span>`).join('')}</div>`:''}
    ${job.missing_required_skills?.length?`<p class="required-note">${t('missingRequired')}: ${job.missing_required_skills.map(escape).join(', ')}</p>`:''}
    <p class="experience-note">${t(job.experience_status==='meets_minimum'?'expMeets':job.experience_status==='below_minimum'?'expBelow':'expFitUnknown')}${job.candidate_experience!==null&&job.candidate_experience!==undefined?` (${job.candidate_experience} ${t('years')})`:''}</p>
    ${fields.map(([key,label])=>`<div class="score-row"><span>${t(label)} <small>(${Math.round((weights[key]||0)*100)}%)</small></span><div><i style="width:${Math.max(0,Math.min(1,components[key]||0))*100}%"></i></div><b title="${weights[key]>0?'':t('notUsed')}">${weights[key]>0?(components[key]||0).toFixed(3):'—'}</b></div>`).join('')}<small class="score-note">${t('scoreNote')}</small></section>`;
}
function detailTopline(job=null) {
  return `<div class="detail-topline"><span><i></i>${t('details')}</span><button class="detail-close icon-button" id="close-detail" aria-label="${t('close')}">${icon('close')}</button>${job?saveButton(job):''}</div>`;
}
function jobDocument(value,kind='') {
  // API cung cấp text xuống dòng; HTML luôn được escape, không chèn source HTML.
  const lines=String(value||'').split(/\r?\n/).map(line=>line.trim()).filter(Boolean);
  const repeated={description:['mo ta cong viec','job description'],requirements:['yeu cau','yeu cau ung vien','yeu cau cong viec','requirements']};
  if(repeated[kind]?.includes(normalized(lines[0]||'').replace(/[:：]$/,'').trim()))lines.shift();
  let html='',items=[],listType='ul';
  const flush=()=>{if(items.length){html+=`<${listType}>${items.map(item=>`<li>${escape(item)}</li>`).join('')}</${listType}>`;items=[];}};
  for(const line of lines){
    const numbered=/^\d{1,2}[.)]\s+/.test(line),bullet=/^[•▪●·∙*+]\s+|^[-–—]\s+/.test(line);
    if(numbered||bullet){const type=numbered?'ol':'ul';if(items.length&&type!==listType)flush();listType=type;items.push(line.replace(/^(?:[•▪●·∙*+\-–—]|\d{1,2}[.)])\s+/,''));continue;}
    flush();
    if(line.length<=85&&/[:：]$/.test(line))html+=`<h4>${escape(line.replace(/[:：]$/,''))}</h4>`;
    else html+=`<p>${escape(line)}</p>`;
  }
  flush();return html;
}
function detailPanel() {
  if(!state.selected)return '';
  if(!state.detail||state.detail.job.id!==state.selected)return `${detailTopline()}<div class="detail-loading"><span class="loader"></span></div>`;
  if(state.detail.error)return `${detailTopline()}<div class="empty-state"><p>${t('connection')}</p><button class="secondary" data-retry-job="${state.selected}">${t('retry')}</button></div>`;
  const comparisonJobs=state.comparison?[...(state.comparison.balanced||[]),...state.comparison.best_fit,...state.comparison.near_home]:[];
  const job={...state.detail.job,...(['cv','personal'].includes(state.view)?state.matches?.find(j=>j.id===state.selected)||comparisonJobs.find(j=>j.id===state.selected)||{}:{})};
  return `${detailTopline(job)}
    <div class="detail-company">${companyLogo(job)}<span>${escape(job.company)}</span></div><h2 class="detail-title">${escape(job.title)}</h2><p class="detail-location">${icon('pin')}${escape(job.location)}</p>
    <div class="detail-facts"><div><small>${state.lang==='vi'?'Mức lương':'Salary'}</small><strong>${escape(job.salary||t('salaryUnknown'))}</strong></div><div><small>${t('experience')}</small><strong>${experience(job)}</strong></div></div>
    <div class="detail-actions"><button class="secondary" data-save="${job.id}">${icon('bookmark')}${t(state.saved.has(job.id)?'unsave':'save')}</button></div>
    ${job.home_region?`<p class="detail-distance">${icon('pin')}${escape(distanceLabel(job))}</p><p class="field-hint">${t('distanceNote')}</p>`:''}${job.personalization_mode&&job.personalization_mode!=='cv'?`<div class="interest-explanation">${icon('spark')}<div><strong>${t('personalScore')}: ${job.personal_score.toFixed(3)}</strong><p>${t(job.personalization_mode==='cv+interest'?'combinedWhy':'interestWhy')}</p></div></div>`:''}${explanation(job)}${demandExplanation(job)}<section class="detail-section"><h3>${t('skills')}</h3><div class="skill-tags">${job.skills.map(s=>`<span>${escape(s)}</span>`).join('')}</div></section>
    <section class="detail-section"><h3>${t('description')}</h3><div class="description job-document">${jobDocument(job.description,'description')}</div></section>
    ${job.requirements?`<section class="detail-section"><h3>${t('requirements')}</h3><div class="description job-document">${jobDocument(job.requirements,'requirements')}</div></section>`:''}
    <section class="detail-section similar-section"><h3>${t('similar')}</h3><p class="muted">${t('similarSub')}</p>${state.detail.similar.map(j=>`<button class="similar-job" data-job="${j.id}">${companyLogo(j,true)}<span><strong>${escape(j.title)}</strong><small>${escape(j.location)}</small></span>${icon('chevron')}</button>`).join('')}</section><p class="source-note">${t('sourceNote')}</p>`;
}
function workspace() { return `<section class="workspace ${state.selected?'has-detail':''} ${state.view==='personal'?'personal-results':''}" id="workspace">${['cv','personal'].includes(state.view)?'':filters()}<div class="results" id="results">${results()}</div><aside class="job-detail ${state.selected?'mobile-open':''}" id="job-detail" aria-label="${t('details')}" ${state.selected?'':'hidden'}>${detailPanel()}</aside></section>`; }
function cvSteps() {
  const step=state.matches?3:state.profile?2:1;
  return `<ol class="cv-steps">${['uploadStep','confirmStep','resultsStep'].map((key,i)=>`<li class="${step>=i+1?'complete':''}"><span>${step>i+1?icon('check'):String(i+1).padStart(2,'0')}</span>${t(key)}</li>`).join('')}</ol>`;
}
function cvInput() {
  return `<section class="cv-input-panel"><div class="panel-heading"><span class="section-kicker">${t('cv')}</span><h2>${t(state.profile?'analyzed':'uploadTitle')}</h2><p>${t('uploadSub')}</p></div>
    ${state.profile?`<div class="cv-success">${icon('check')}<span><strong>${t('cvReady')}</strong><small>${escape(state.cvFilename||t('savedCv'))}</small></span><button class="icon-button" id="clear-cv" aria-label="${t('remove')}">${icon('close')}</button></div><div class="cv-saved-tools"><span>${icon('check')}${t(state.profileStored?'profileSaved':'profileSession')}</span><button class="text-button" id="replace-cv">${t('newFile')}</button></div><p class="field-hint">${t('autoSaveHint')}</p>`:
    `<label class="dropzone ${state.file?'has-file':''} ${state.reading?'is-reading':''}" id="dropzone" tabindex="0"><input type="file" id="cv-file" accept=".pdf,.docx,.png,.jpg,.jpeg,.webp,.tif,.tiff" ${state.reading?'disabled':''}><span class="upload-icon">${state.reading?'<span class="loader"></span>':icon(state.file?'file':'upload')}</span><strong>${state.reading?t('reading'):state.file?escape(state.file.name):t('dropTitle')}</strong><span>${t(state.reading?'readHint':state.file?'newFile':'dropSub')}</span><span class="secondary file-label">${t('choose')}${icon('arrow')}</span><small>${t('formats')}</small></label>
      <button class="primary full-width" id="read-cv" ${!state.file||state.reading?'disabled':''}>${state.reading?'<span class="loader light"></span>':icon('spark')}${t(state.reading?'reading':'read')}</button>`}
    ${state.profile?`<div class="cv-profile"><h3>${t('detected')}<span>${state.profile.skills.length}</span></h3><div class="skill-tags">${state.profile.skills.map(s=>`<span class="matched-skill">${escape(s)}</span>`).join('')||`<p class="muted">${t('noSkills')}</p>`}</div>${state.ocr?`<p class="ocr-note">${t('ocrNote')}</p>`:''}
      <label class="field-label" for="cv-region">${t('preferred')}</label><select id="cv-region">${regionOptions(state.cvRegion,true,true)}</select><p class="field-hint">${t('preferredHint')}</p>
      <label class="field-label" for="cv-home-region">${t('homeRegion')}</label><select id="cv-home-region"><option value="">${t('homeUnknown')}</option>${state.data.all_regions.filter(r=>r.id!=='remote').map(r=>`<option value="${r.id}" ${state.cvHomeRegion===r.id?'selected':''}>${escape(r.label)}</option>`).join('')}</select><p class="field-hint">${t('homeHint')}</p>
      <label class="field-label" for="cv-experience">${t('cvExperience')}</label><input id="cv-experience" class="experience-input" type="number" min="0" max="60" step="0.5" value="${escape(state.cvExperience)}" placeholder="${t('experienceUnknown')}"><p class="field-hint">${t('cvExperienceHint')}</p>
      <details class="cv-text"><summary>${t('review')}</summary><label for="cv-text" class="sr-only">${t('textLabel')}</label><textarea id="cv-text" maxlength="60000">${escape(state.cvText)}</textarea></details><button id="match-cv" class="primary full-width" ${state.matching?'disabled':''}>${state.matching?'<span class="loader light"></span>':icon('spark')}${t(state.matching?'matching':'find')}${icon('arrow')}</button></div>`:''}
    ${storageNotice()}<p class="privacy-note">${icon('lock')}<span>${t('privacy')} ${t('demandPrivacy')}</span></p>${!state.reading?`<div class="sample-area"><p>${t('sample')}</p><div>${['sampleData','sampleBackend','sampleAI'].map((key,i)=>`<button data-sample="${i}">${t(key)}${icon('arrow')}</button>`).join('')}</div></div>`:''}</section>`;
}
function cvPage() {
  if(state.matches)return `${cvSteps()}<div class="cv-results-banner"><span class="success-symbol">${icon('check')}</span><div><h2>${t('matched')}</h2><p>${t('matchedSub')}${state.cvRegion?' · '+escape(state.data.all_regions.find(r=>r.id===state.cvRegion)?.label||''):''}</p></div><button class="secondary" id="edit-cv">${t('adjust')}${icon('arrow')}</button></div>${locationComparison()}${state.matchMethod?.mode==='hybrid-lexical'?`<p class="algorithm-notice">${t('semanticFallback')}</p>`:''}${workspace()}`;
  return `${cvSteps()}<div class="cv-layout">${cvInput()}<aside class="cv-guide"><span class="guide-illustration">${icon('file')}<b>${icon('spark')}</b></span><p class="section-kicker">JOBVISTA</p><h2>${t('how')}</h2><p>${t('howSub')}</p><ol>${[1,2,3].map(i=>`<li><span>0${i}</span><div><h3>${t('how'+i)}</h3><p>${t('how'+i+'Sub')}</p></div></li>`).join('')}</ol><div class="guide-note">${icon('check')}<span>${t('scoreNote')}</span></div></aside></div>`;
}
function render() {
  document.documentElement.lang=state.lang;document.title=t('pageTitle');
  $('.skip-link').textContent=state.lang==='vi'?'Đến nội dung':'Skip to content';
  $('#app').innerHTML=`${header()}<main id="main" class="shell">${state.view==='saved'?`<section class="saved-hero"><p class="section-kicker">${t('saved')}</p><h1>${t('savedTitle')}</h1><p>${t('savedSub')}</p></section>`:hero()}
    ${state.loading?`<div class="initial-loading"><span class="loader"></span>${t('loading')}</div>`:state.error?`<div class="empty-state"><p>${t('connection')}</p><button class="primary" id="retry">${t('retry')}</button></div>`:state.view==='cv'?cvPage():state.view==='personal'?workspace():searchBar()+(state.view==='explore'?`<div id="personal-home">${storageNotice()}${personalPanel()}</div>`:'')+workspace()}</main><footer class="footer"><div><strong>JobVista<span> / </span></strong>${t('footer')}</div></footer>`;
  bind();
}
function updateResults() {
  const filtered=filteredJobs();
  const pages=Math.max(1,Math.ceil(filtered.length/8));state.page=Math.min(state.page,pages);
  // Lọc hoặc chuyển trang có thể loại tin đang xem. Đóng bảng thay vì tự mở tin khác.
  if(state.selected&&!filtered.slice((state.page-1)*8,state.page*8).some(j=>j.id===state.selected))closeJobDetails();
  $('#results').innerHTML=results();bindResults();
}
async function loadCatalog() {
  state.loading=true;state.error='';render();const language=state.lang;
  try { const data=await api(`/api/catalog?language=${language}`);if(language!==state.lang)return;
    state.data=data;state.jobs=data.jobs;state.loading=false;
    if(state.savedProfile&&!data.all_regions.some(r=>r.id===state.savedProfile.region)&&state.savedProfile.region){
      // Không âm thầm mở rộng sang mọi vùng khi mã vùng đã lưu không còn hợp lệ.
      state.homeError=true;state.homeMatches=null;render();return;
    }
    render();refreshHome();
  } catch {if(language===state.lang){state.loading=false;state.error='connection';render();}}
}
async function loadDetail(id) {
  state.selected=id;state.detail=null;const version=++state.detailVersion;
  const panel=$('#job-detail');if(!panel)return;panel.innerHTML=detailPanel();
  syncDetailVisibility();bindDetail();
  const location=['cv','personal'].includes(state.view)?state.savedProfile?state.cvRegion:state.homePreference?.location:'';
  try {const data=await api(`/api/jobs/${encodeURIComponent(id)}?language=${state.lang}${location?'&location='+encodeURIComponent(location):''}`);
    if(version!==state.detailVersion)return;state.detail=data;panel.innerHTML=detailPanel();bindDetail();panel.scrollTop=0;
  } catch {if(version===state.detailVersion){state.detail={job:{id},error:true};panel.innerHTML=detailPanel();bindDetail();}}
}
function syncDetailVisibility() {
  const open=state.selected!==null;
  const panel=$('#job-detail');if(panel){panel.hidden=!open;panel.classList.toggle('mobile-open',open);}
  $('#workspace')?.classList.toggle('has-detail',open);
  document.querySelectorAll('[data-card]').forEach(el=>el.classList.toggle('selected',el.dataset.card===state.selected));
  document.querySelectorAll('#results [data-job]').forEach(el=>el.setAttribute('aria-expanded',String(el.dataset.job===state.selected)));
}
function closeJobDetails(restoreFocus=false) {
  const previous=state.selected;
  // Tăng version để phản hồi đến chậm không thể mở lại bảng vừa đóng.
  state.detailVersion++;state.selected=null;state.detail=null;
  const panel=$('#job-detail');if(panel)panel.innerHTML='';syncDetailVisibility();
  if(restoreFocus&&previous)document.querySelector(`#results [data-job="${previous}"]`)?.focus({preventScroll:true});
}
function toggleJobDetails(id) {
  if(state.selected===id){closeJobDetails();return;}
  loadDetail(id);
}
function toggleSave(id) {
  if(state.saved.has(id)){state.saved.delete(id);toast(t('removedToast'));}else{state.saved.add(id);toast(t('savedToast'));}
  try{localStorage.setItem('jobvista-saved',JSON.stringify([...state.saved]));}catch{}
  document.querySelector('.nav-count').textContent=state.saved.size;
  if(state.view==='saved')updateResults();else if($('#results')){$('#results').innerHTML=results();bindResults();}
  if($('#job-detail')){$('#job-detail').innerHTML=detailPanel();bindDetail();}
  refreshPersonalPanel();
}
function resetFilters() {clearTimeout(searchTimer);clearTimeout(interestTimer);interestTimer=null;Object.assign(state,{q:'',region:'',domain:'',exp:'',category:'all',page:1});render();updateResults();}
function navigate(view) {
  clearTimeout(searchTimer);
  if(interestTimer)rememberSearch();
  if(profileTimer)persistCv();
  state.view=view;state.page=1;state.detailVersion++;state.detail=null;state.selected=null;
  Object.assign(state,{q:'',region:'',domain:'',exp:'',category:'all'});render();
  window.scrollTo({top:0,behavior:'smooth'});
  if(view==='explore')refreshHome();
}
function bindDetail() {
  $('#job-detail')?.querySelectorAll('[data-save]').forEach(el=>el.onclick=()=>toggleSave(el.dataset.save));
  $('#job-detail')?.querySelectorAll('[data-job]').forEach(el=>el.onclick=()=>toggleJobDetails(el.dataset.job));
  $('#job-detail')?.querySelectorAll('[data-retry-job]').forEach(el=>el.onclick=()=>loadDetail(el.dataset.retryJob));
  if($('#close-detail'))$('#close-detail').onclick=()=>closeJobDetails(true);
}
function bindResults() {
  // Nhấp bất kỳ vùng nào trên thẻ cũng bật/tắt; nút lưu hoạt động độc lập.
  $('#results')?.querySelectorAll('[data-card]').forEach(el=>el.onclick=event=>{if(!event.target.closest('button,a,input,select,textarea'))toggleJobDetails(el.dataset.card);});
  $('#results')?.querySelectorAll('[data-job]').forEach(el=>el.onclick=()=>toggleJobDetails(el.dataset.job));
  $('#results')?.querySelectorAll('[data-save]').forEach(el=>el.onclick=()=>toggleSave(el.dataset.save));
  $('#results')?.querySelectorAll('[data-category]').forEach(el=>el.onclick=()=>{state.category=el.dataset.category;state.page=1;updateResults();queueSearchInterest();});
  $('#results')?.querySelectorAll('[data-page]').forEach(el=>el.onclick=()=>{state.page=+el.dataset.page;updateResults();$('#workspace').scrollIntoView({behavior:'smooth',block:'start'});});
  if($('#empty-reset'))$('#empty-reset').onclick=resetFilters;
  $('#results')?.querySelectorAll('[data-nav]').forEach(el=>el.onclick=()=>navigate(el.dataset.nav));
}
function bind() {
  document.querySelectorAll('[data-nav]').forEach(el=>el.onclick=e=>{e.preventDefault();navigate(el.dataset.nav);});
  $('#language').onclick=()=>{clearTimeout(searchTimer);if(interestTimer)rememberSearch();if(profileTimer)persistCv();if(state.view==='personal')state.view='explore';state.lang=state.lang==='vi'?'en':'vi';$('#toast').classList.remove('visible');state.cvVersion++;state.homeVersion++;state.homeKey='';state.homeMatches=null;state.homeLoading=false;state.reading=false;state.matching=false;state.matches=null;state.selected=null;state.detailVersion++;state.detail=null;loadCatalog();};
  if($('#retry'))$('#retry').onclick=loadCatalog;
  if($('#search-form'))$('#search-form').onsubmit=e=>{e.preventDefault();clearTimeout(searchTimer);state.q=$('#search').value;state.page=1;updateResults();rememberSearch();$('#workspace').scrollIntoView({behavior:'smooth',block:'start'});};
  if($('#search'))$('#search').oninput=e=>{clearTimeout(searchTimer);clearTimeout(interestTimer);const value=e.target.value;searchTimer=setTimeout(()=>{state.q=value;state.page=1;updateResults();queueSearchInterest();},200);};
  document.querySelectorAll('[data-search]').forEach(el=>el.onclick=()=>{clearTimeout(searchTimer);state.q=el.dataset.search;state.page=1;$('#search').value=state.q;updateResults();rememberSearch();});
  ['search-region','filter-region'].forEach(id=>{if($('#'+id))$('#'+id).onchange=e=>{state.region=e.target.value;state.page=1;['search-region','filter-region'].forEach(other=>{if($('#'+other))$('#'+other).value=state.region;});updateResults();queueSearchInterest();};});
  if($('#filter-domain'))$('#filter-domain').onchange=e=>{state.domain=e.target.value;state.page=1;updateResults();queueSearchInterest();};
  document.querySelectorAll('[name="experience"]').forEach(el=>el.onchange=()=>{state.exp=el.value;state.page=1;updateResults();queueSearchInterest();});
  if($('#reset'))$('#reset').onclick=resetFilters;
  bindResults();bindDetail();bindCv();bindPersonal();
}
function chooseFile(file) {
  if(!file)return;
  if(file.size>15*1024*1024||!(/\.(pdf|docx|png|jpe?g|webp|tiff?)$/i.test(file.name))){toast(t('invalidFile'));return;}
  clearTimeout(profileTimer);profileTimer=null;
  state.cvVersion++;Object.assign(state,{file,cvFilename:file.name,cvText:'',profile:null,ocr:false,matches:null,comparison:null,cvRegion:'',cvHomeRegion:'',cvExperience:'',cvExperienceEdited:false,matchMethod:null,reading:false,matching:false});render();
}
function clearCv() {
  // Nếu trình duyệt từ chối xóa, không báo thành công hoặc làm như dữ liệu đã mất.
  if(!personalStore.removeProfile()){state.storageError=true;toast(t('deleteFailed'));return;}
  clearTimeout(profileTimer);profileTimer=null;state.cvVersion++;state.homeVersion++;state.detailVersion++;
  Object.assign(state,{file:null,cvFilename:'',cvText:'',profile:null,ocr:false,matches:null,comparison:null,cvRegion:'',cvHomeRegion:'',cvExperience:'',cvExperienceEdited:false,matchMethod:null,reading:false,matching:false,
    savedProfile:null,profileStored:false,homeMatches:null,homeMethod:null,homePreference:null,homeLoading:false,homeError:false,homeKey:'',selected:null,detail:null});render();toast(t('profileDeleted'));if(state.view==='explore')refreshHome();
}
async function readCv() {
  if(!state.file||state.reading)return;state.reading=true;const version=++state.cvVersion;const file=state.file;render();
  try {const data=await api(`/api/cv/read?language=${state.lang}`,{method:'POST',headers:{'Content-Type':'application/octet-stream','X-CV-Filename':encodeURIComponent(file.name)},body:file});
    if(version!==state.cvVersion)return;Object.assign(state,{cvText:data.text,profile:data.profile,ocr:data.ocr,cvRegion:data.profile.locations.find(code=>state.data.all_regions.some(r=>r.id===code))||'',cvHomeRegion:data.profile.home_locations?.[0]||'',cvExperience:data.profile.experience_years??'',cvExperienceEdited:false,reading:false});persistCv();render();if(state.view==='explore')refreshHome();
  }catch(error){if(version===state.cvVersion){state.reading=false;render();toast(error.message);}}
}
async function useSample(index) {
  clearTimeout(profileTimer);profileTimer=null;
  const version=++state.cvVersion;
  try {const samples=await api('/api/samples');if(version!==state.cvVersion)return;
    const text=samples[index].CV_Text;Object.assign(state,{file:null,cvFilename:'',cvText:text,ocr:false,profile:{skills:[],locations:[],home_locations:[],title:''},matches:null,comparison:null,cvRegion:'',cvHomeRegion:'',reading:false,matching:false});
    // Phân tích bằng cùng engine thật; hồ sơ mẫu không có thành phố nên không tự gán vùng.
    const result=await api('/api/cv/match',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text,language:state.lang,top_n:1})});
    if(version!==state.cvVersion)return;state.profile=result.profile;state.cvExperience=result.profile.experience_years??'';state.cvExperienceEdited=false;persistCv();render();if(state.view==='explore')refreshHome();
  }catch(error){if(version===state.cvVersion)toast(error.message);}
}
async function findMatches() {
  if(!state.cvText.trim()){toast(t('emptyCv'));return;}
  if(state.cvExperience!==''&&(!Number.isFinite(Number(state.cvExperience))||Number(state.cvExperience)<0||Number(state.cvExperience)>60)){toast(t('invalidExperience'));return;}
  state.matching=true;const version=++state.cvVersion;render();
  try {const data=await api('/api/cv/match',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:state.cvText,location:state.cvRegion||null,home_region:state.cvHomeRegion||null,compare_locations:true,actor_id:anonymousActor(),record_demand:true,language:state.lang,top_n:24,experience_override:state.cvExperienceEdited,experience_years:state.cvExperience===''?null:Number(state.cvExperience)})});
    if(version!==state.cvVersion)return;state.detailVersion++;Object.assign(state,{matches:data.jobs,comparison:data.comparison,profile:data.profile,matchMethod:data.algorithm,matching:false,page:1,q:'',region:'',domain:'',exp:'',category:'all',selected:null,detail:null});if(!state.cvExperienceEdited)state.cvExperience=data.profile.experience_years??'';
    persistCv();state.homeVersion++;Object.assign(state,{homeMatches:null,homeMethod:null,homeLoading:false,homeError:false,homeKey:''});render();$('#workspace').scrollIntoView({behavior:'smooth',block:'start'});
  }catch(error){if(version===state.cvVersion){state.matching=false;render();toast(error.message);}}
}
function bindCv() {
  if($('#cv-file'))$('#cv-file').onchange=e=>chooseFile(e.target.files[0]);
  const drop=$('#dropzone');
  if(drop){drop.ondragover=e=>{e.preventDefault();drop.classList.add('drag-over');};drop.ondragleave=()=>drop.classList.remove('drag-over');drop.ondrop=e=>{e.preventDefault();drop.classList.remove('drag-over');if(!state.reading)chooseFile(e.dataTransfer.files[0]);};drop.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();$('#cv-file').click();}};}
  if($('#read-cv'))$('#read-cv').onclick=readCv;
  if($('#clear-cv'))$('#clear-cv').onclick=clearCv;
  if($('#replace-cv'))$('#replace-cv').onclick=()=>{clearTimeout(profileTimer);profileTimer=null;state.cvVersion++;Object.assign(state,{file:null,cvFilename:'',profile:null,cvText:'',reading:false,matching:false,matches:null});render();};
  if($('#cv-region'))$('#cv-region').onchange=e=>{state.cvRegion=e.target.value;invalidateCvInputs();};
  if($('#cv-home-region'))$('#cv-home-region').onchange=e=>{state.cvHomeRegion=e.target.value;invalidateCvInputs();};
  document.querySelectorAll('[data-compare-job]').forEach(el=>el.onclick=()=>{toggleJobDetails(el.dataset.compareJob);$('#workspace')?.scrollIntoView({behavior:'smooth',block:'start'});});
  if($('#cv-experience'))$('#cv-experience').oninput=e=>{state.cvExperience=e.target.value;state.cvExperienceEdited=true;invalidateCvInputs();};
  if($('#cv-text'))$('#cv-text').oninput=e=>{state.cvText=e.target.value;invalidateCvInputs();};
  if($('#match-cv'))$('#match-cv').onclick=findMatches;
  if($('#edit-cv'))$('#edit-cv').onclick=()=>{state.matches=null;state.detailVersion++;state.selected=null;state.detail=null;render();};
  document.querySelectorAll('[data-sample]').forEach(el=>el.onclick=()=>useSample(+el.dataset.sample));
}
function invalidateCvInputs() {
  // Bỏ kết quả đang tính từ CV/vùng cũ; không cho phản hồi chậm ghi đè dữ liệu mới.
  const wasMatching=state.matching;
  state.cvVersion++;state.matches=null;state.comparison=null;state.matching=false;
  state.homeVersion++;state.homeKey='';state.homeMatches=null;state.homeLoading=false;
  clearTimeout(profileTimer);profileTimer=setTimeout(()=>{persistCv();if(state.view==='explore')refreshHome();},500);
  if(wasMatching&&$('#match-cv')){$('#match-cv').disabled=false;$('#match-cv').innerHTML=`${icon('spark')}${t('find')}${icon('arrow')}`;}
}

function anonymousActor(){
  try{let id=localStorage.getItem('jobvista-demand-actor');if(!/^[a-f0-9-]{36}$/i.test(id||'')){id=crypto.randomUUID();localStorage.setItem('jobvista-demand-actor',id);}return id;}catch{return null;}
}
document.addEventListener('keydown',event=>{if(event.key==='Escape'&&state.selected)closeJobDetails(true);});
// Lưu nốt sửa đổi chưa hết debounce trước khi đóng/tải lại tab.
window.addEventListener('pagehide',()=>{if(profileTimer)persistCv();if(interestTimer)rememberSearch();});
loadCatalog();
