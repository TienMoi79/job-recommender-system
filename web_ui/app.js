/* JobVista: giao diện tương tác gọi API Python thật. Không lưu CV vào localStorage.
 * Chỉ danh sách Job_ID đã lưu được giữ trên chính trình duyệt của người dùng. */
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
    savedTitle:'Những cơ hội bạn muốn giữ lại', savedSub:'Được lưu trên trình duyệt này để bạn dễ quay lại.',
    save:'Lưu công việc', unsave:'Bỏ lưu công việc', savedToast:'Đã lưu vào danh sách của bạn', removedToast:'Đã bỏ lưu công việc',
    details:'Chi tiết công việc', description:'Mô tả công việc', requirements:'Yêu cầu ứng viên', skills:'Kỹ năng', source:'Xem tin gốc',
    similar:'Cơ hội tương tự', similarSub:'Gợi ý theo nội dung công việc', selectJob:'Chọn một công việc để xem chi tiết',
    sourceNote:'Dữ liệu tham khảo từ bộ tin công khai. Chưa xác minh tin còn nhận hồ sơ.', sourceLink:'Nguồn dữ liệu',
    noJobs:'Chưa tìm thấy công việc phù hợp', noJobsSub:'Thử thay đổi từ khóa hoặc mở rộng địa điểm và bộ lọc.', noSaved:'Bạn chưa lưu công việc nào', noSavedSub:'Bấm biểu tượng đánh dấu trên công việc bạn quan tâm để lưu lại.',
    previous:'Trước', next:'Sau', page:'Trang', loading:'Đang tải cơ hội mới…', connection:'Chưa kết nối được máy chủ. Kiểm tra terminal và thử lại.', retry:'Thử lại',
    uploadStep:'Tải CV', confirmStep:'Xác nhận thông tin', resultsStep:'Khám phá cơ hội', uploadTitle:'Bắt đầu với CV của bạn',
    uploadSub:'Một tệp CV. Nhiều cơ hội mới.', dropTitle:'Kéo thả CV vào đây', dropSub:'hoặc chọn tệp từ máy tính của bạn', choose:'Chọn tệp CV', formats:'PDF, Word (.docx), JPG, PNG, WEBP, TIFF · Tối đa 15 MB',
    privacy:'CV được xử lý tại máy chủ cục bộ, không gửi sang dịch vụ AI bên ngoài và không lưu thành tệp.', read:'Đọc & phân tích CV', reading:'Đang đọc CV của bạn…', readHint:'CV scan và ảnh cần thêm thời gian để nhận diện chữ.', remove:'Xóa CV',
    sample:'Chưa có CV? Thử một hồ sơ mẫu', sampleData:'Phân tích dữ liệu', sampleBackend:'Lập trình Backend', sampleAI:'Kỹ sư AI',
    how:'Một hành trình, ba bước đơn giản', howSub:'Tập trung vào năng lực. Tìm cơ hội gần với bạn.',
    how1:'Thêm CV của bạn', how1Sub:'Ảnh, PDF hoặc Word — chọn định dạng thuận tiện nhất.', how2:'Chọn nơi bạn muốn làm', how2Sub:'Kiểm tra kỹ năng đã đọc và xác nhận khu vực mong muốn.', how3:'Khám phá công việc phù hợp', how3Sub:'Xem kỹ năng trùng và lý do công việc được gợi ý.',
    analyzed:'CV đã sẵn sàng', detected:'Kỹ năng nhận diện', noSkills:'Chưa nhận diện được kỹ năng cụ thể. Bạn có thể kiểm tra nội dung đã đọc.',
    preferred:'Bạn muốn làm việc ở đâu?', preferredHint:'Địa điểm từ CV chỉ là gợi ý. Hãy chọn nơi bạn thực sự muốn làm.',
    review:'Xem và sửa nội dung đã đọc', textLabel:'Nội dung CV', find:'Tìm công việc phù hợp', matching:'Đang tìm cơ hội cho bạn…',
    ocrNote:'CV được đọc bằng OCR. Hãy kiểm tra lại địa điểm và nội dung nếu ảnh bị mờ hoặc nhiều cột.',
    cvReady:'Đã đọc nội dung CV', matched:'Kết quả từ CV của bạn', matchedSub:'Lọc theo nơi bạn muốn làm, ưu tiên nội dung gần với CV.',
    score:'Điểm phù hợp', why:'Vì sao công việc này phù hợp?', matchedSkills:'Kỹ năng trùng với CV', noSkillMatch:'Chưa tìm thấy kỹ năng trùng trực tiếp.',
    scoreNote:'Điểm tương đồng nội dung, không phải xác suất trúng tuyển. Trọng số hiện tại là cấu hình thử nghiệm.',
    titleScore:'Vị trí', skillScore:'Kỹ năng', domainScore:'Lĩnh vực', descScore:'Nội dung CV', adjust:'Chỉnh sửa CV',
    changed:'Thông tin đã thay đổi. Bấm tìm lại để cập nhật kết quả.', invalidFile:'Vui lòng chọn PDF, Word .docx hoặc ảnh được hỗ trợ, tối đa 15 MB.',
    emptyCv:'Hãy tải CV hoặc chọn một hồ sơ mẫu trước.', publicData:'500 tin IT · Nguồn công khai · Dùng cho đồ án',
    emptyDetail:'Chi tiết sẽ xuất hiện ở đây', close:'Đóng chi tiết', selected:'Đang xem', footer:'Từ kỹ năng đến cơ hội mới.', newFile:'Chọn CV khác',
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
    savedTitle:'Opportunities worth keeping', savedSub:'Saved in this browser so you can come back anytime.',
    save:'Save job', unsave:'Remove saved job', savedToast:'Added to your saved jobs', removedToast:'Removed from saved jobs',
    details:'Job details', description:'Job description', requirements:'Requirements', skills:'Skills', source:'View original listing',
    similar:'Similar opportunities', similarSub:'Recommended by job content', selectJob:'Select a job to see the details',
    sourceNote:'Reference data from public listings. Current availability has not been verified.', sourceLink:'Dataset source',
    noJobs:'No matching opportunities yet', noJobsSub:'Try a different keyword or broaden your location and filters.', noSaved:'No saved jobs yet', noSavedSub:'Use the bookmark on any job that catches your eye.',
    previous:'Previous', next:'Next', page:'Page', loading:'Loading your next opportunity…', connection:'Unable to connect. Check the server terminal and try again.', retry:'Try again',
    uploadStep:'Upload CV', confirmStep:'Check details', resultsStep:'Explore matches', uploadTitle:'Start with your CV',
    uploadSub:'One CV. A world of possibilities.', dropTitle:'Drag your CV here', dropSub:'or choose a file from your computer', choose:'Choose CV file', formats:'PDF, Word (.docx), JPG, PNG, WEBP, TIFF · Up to 15 MB',
    privacy:'Your CV is processed on the local server, never sent to external AI services or saved as a file.', read:'Read & analyze CV', reading:'Reading your CV…', readHint:'Scanned CVs and images take longer to recognize.', remove:'Clear CV',
    sample:'No CV handy? Try a sample profile', sampleData:'Data analyst', sampleBackend:'Backend developer', sampleAI:'AI engineer',
    how:'One journey, three simple steps', howSub:'Focus on your strengths. Find opportunities that fit.',
    how1:'Add your CV', how1Sub:'Image, PDF or Word — use the format that works for you.', how2:'Choose where to work', how2Sub:'Check the extracted skills and confirm your preferred area.', how3:'Explore your matches', how3Sub:'See shared skills and why each job was recommended.',
    analyzed:'Your CV is ready', detected:'Detected skills', noSkills:'No specific skills detected yet. You can review the extracted content.',
    preferred:'Where would you like to work?', preferredHint:'Your CV location is a suggestion. Choose where you actually want to work.',
    review:'Review and edit extracted content', textLabel:'CV content', find:'Find matching opportunities', matching:'Finding opportunities for you…',
    ocrNote:'This CV was read using OCR. Review the location and content if the image is blurry or has multiple columns.',
    cvReady:'CV content extracted', matched:'Matched to your CV', matchedSub:'Filtered by your preferred location, then ranked by CV content.',
    score:'Match score', why:'Why this opportunity?', matchedSkills:'Skills shared with your CV', noSkillMatch:'No direct skill overlap detected.',
    scoreNote:'Content similarity, not a hiring probability. The current weights are an experimental baseline.',
    titleScore:'Position', skillScore:'Skills', domainScore:'Field', descScore:'CV content', adjust:'Edit CV',
    changed:'Your information changed. Find matches again to refresh the results.', invalidFile:'Choose a supported PDF, Word .docx or image file, up to 15 MB.',
    emptyCv:'Upload a CV or choose a sample profile first.', publicData:'500 IT listings · Public data · Academic project',
    emptyDetail:'Job details will appear here', close:'Close details', selected:'Selected', footer:'From your skills to your next opportunity.', newFile:'Choose another CV',
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
const state = {lang:'vi',view:'explore',data:null,jobs:[],saved:new Set(Array.isArray(stored)?stored.filter(x=>typeof x==='string'):[]),
  q:'',region:'',domain:'',exp:'',category:'all',page:1,selected:null,detail:null,detailVersion:0,
  file:null,cvText:'',profile:null,ocr:false,cvRegion:'',matches:null,reading:false,matching:false,cvVersion:0,loading:true,error:''};
const t = key => copy[state.lang][key];
let toastTimer, searchTimer;
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
    <nav aria-label="${t('explore')}">${['explore','cv','saved'].map(view=>`<button class="nav-item ${state.view===view?'active':''}" data-nav="${view}">${view==='saved'?icon('bookmark'):''}${t(view)}${view==='saved'?`<span class="nav-count">${state.saved.size}</span>`:''}</button>`).join('')}</nav>
    <div class="header-actions"><span class="preview-badge"><span></span>${t('preview')}</span><button class="language-btn" id="language" aria-label="${t('language')}" title="${t('language')}">${icon('globe')}<span>${state.lang==='vi'?'VI':'EN'}</span></button></div></div></header>`;
}
function hero() {
  const isCv=state.view==='cv';
  return `<section class="hero ${isCv?'cv-hero':''}"><div class="hero-content"><p class="eyebrow"><span class="eyebrow-line"></span>${t('eyebrow')}</p>
    <h1>${t(isCv?'heroCv':'hero')}</h1><p class="hero-intro">${t(isCv?'cvIntro':'intro')}</p>
    <div class="hero-stats"><span><strong>${state.jobs.length||'500'}</strong>${t('jobs')}</span><i></i><span><strong>${state.data?.companies||'387'}</strong>${t('companies')}</span><i></i><span><strong>${state.data?.regions.length||'10'}</strong>${t('regions')}</span></div></div>
    <div class="hero-art" aria-hidden="true"><div class="orbit orbit-one"></div><div class="orbit orbit-two"></div><span class="art-spark">✳</span>
      <div class="floating-note">${icon('check')} ${t('skillConnection')}</div>
      <div class="opportunity-card"><div class="mini-card-top"><span class="mini-logo">&lt;/&gt;</span><span class="mini-dots">•••</span></div><p>${t('cardRole')}</p><h3>Backend Developer</h3><span class="mini-company">Python · FastAPI · SQL</span><div class="mini-tags"><b>Python</b><b>SQL</b><b>Docker</b></div><div class="mini-card-bottom"><span>${icon('pin')} ${state.lang==='vi'?'Hà Nội':'Hanoi'}</span><span class="art-check">${icon('check')}</span></div></div>
      <div class="floating-match">${icon('spark')}<span><strong>${t('smart')}</strong><small>${t('cardHint')}</small></span></div></div></section>`;
}
function regionOptions(value, all=true, forCv=false) {
  return `${all?`<option value="">${t('regionAll')}</option>`:''}${(forCv?state.data?.all_regions||[]:state.data?.regions||[]).map(r=>`<option value="${r.id}" ${value===r.id?'selected':''}>${escape(r.label)}</option>`).join('')}`;
}
function searchBar() {
  return `<section class="search-area"><form class="search-bar" id="search-form"><label class="keyword-field">${icon('search')}<input id="search" aria-label="${t('keyword')}" placeholder="${t('keyword')}" value="${escape(state.q)}" autocomplete="off"></label>
    <label class="search-location">${icon('pin')}<select id="search-region" aria-label="${t('location')}">${regionOptions(state.region)}</select></label><button class="primary search-button" type="submit">${t('search')}${icon('arrow')}</button></form>
    <div class="suggestions"><span>${t('suggested')}</span>${['Python','Data Analyst','React','UI/UX'].map(x=>`<button data-search="${x}">${x}</button>`).join('')}<span class="search-meta">${icon('spark')}${t('publicData')}</span></div></section>`;
}
function filters() {
  return `<aside class="filters"><div class="filter-heading"><h3>${icon('tune')}${t('filters')}</h3><button class="text-button" id="reset">${t('reset')}</button></div>
    <label class="field-label" for="filter-region">${t('location')}</label><select id="filter-region">${regionOptions(state.region)}</select>
    <label class="field-label" for="filter-domain">${t('domain')}</label><select id="filter-domain"><option value="">${t('allDomains')}</option>${(state.data?.domains||[]).map(d=>`<option ${state.domain===d?'selected':''}>${escape(d)}</option>`).join('')}</select>
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
function saveButton(job, extra='') {const saved=state.saved.has(job.id); return `<button class="save-button ${saved?'is-saved':''} ${extra}" data-save="${job.id}" aria-label="${t(saved?'unsave':'save')}" aria-pressed="${saved}" title="${t(saved?'unsave':'save')}">${icon('bookmark')}</button>`;}
function jobCard(job) {
  return `<article class="job-card ${state.selected===job.id?'selected':''}" data-card="${job.id}"><div class="card-main"><button class="job-open" data-job="${job.id}" aria-label="${escape(job.title)}">${companyLogo(job)}<span><span class="job-company">${escape(job.company)}</span><h3>${escape(job.title)}</h3></span></button>${saveButton(job)}</div>
    <div class="job-meta"><span>${icon('pin')}${escape(job.location)}</span><span>${icon('briefcase')}${experience(job)}</span></div>
    <div class="skill-tags">${job.skills.slice(0,4).map(s=>`<span class="${job.matched_skills?.includes(s)?'matched-skill':''}">${escape(s)}</span>`).join('')}${job.skills.length>4?`<span>+${job.skills.length-4}</span>`:''}</div>
    <div class="job-card-bottom"><strong>${escape(job.salary||t('salaryUnknown'))}</strong>${job.score!==undefined?`<span class="match-score" title="${t('score')}">${icon('spark')}${job.score.toFixed(3)}</span>`:`<button class="card-arrow" data-job="${job.id}" aria-label="${t('details')}: ${escape(job.title)}">${icon('arrow')}</button>`}</div></article>`;
}
function filteredJobs() {
  let jobs=state.view==='cv'?(state.matches||[]):state.jobs;
  if(state.view==='saved') jobs=jobs.filter(j=>state.saved.has(j.id));
  const q=normalized(state.q).trim();
  return jobs.filter(job=>{
    if(q&&!normalized(`${job.title} ${job.company} ${job.skills.join(' ')} ${job.domain}`).includes(q)) return false;
    if(state.region&&!job.regions.includes(state.region)) return false;
    if(state.domain&&job.domain!==state.domain) return false;
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
  return `<div class="results-heading"><div><p class="section-kicker">${state.view==='cv'?t('matched'):t('explore')}</p><h2>${state.view==='saved'?t('savedTitle'):t('resultTitle')}<span>${jobs.length}</span></h2><p>${jobs.length} ${t('resultSuffix')}</p></div><span class="sort-label">${icon('tune')}${t(state.view==='cv'?'relevance':'original')}</span></div>
    ${state.view!=='cv'?`<div class="category-tabs" role="group" aria-label="${t('domain')}">${['all','dev','data','ai'].map(c=>`<button class="${state.category===c?'active':''}" data-category="${c}" aria-pressed="${state.category===c}">${t(c)}</button>`).join('')}</div>`:''}
    <div class="jobs-list">${jobs.slice((state.page-1)*8,state.page*8).map(jobCard).join('')||emptyState()}</div>
    ${pages>1?`<div class="pagination"><button class="page-control" data-page="${state.page-1}" ${state.page===1?'disabled':''} aria-label="${t('previous')}">‹</button><span>${t('page')} <strong>${state.page}</strong> / ${pages}</span><button class="page-control" data-page="${state.page+1}" ${state.page===pages?'disabled':''} aria-label="${t('next')}">›</button></div>`:''}`;
}
function explanation(job) {
  if(job.score===undefined) return '';
  const components=job.components||{};
  const fields=[['Title','titleScore','25%'],['Skills','skillScore','35%'],['Domain','domainScore','15%'],['Job_Description','descScore','25%']];
  return `<section class="explanation"><div class="explanation-title">${icon('spark')}<h3>${t('why')}</h3><strong>${job.score.toFixed(3)}</strong></div><p>${t('matchedSkills')}</p><div class="skill-tags">${job.matched_skills?.length?job.matched_skills.map(s=>`<span class="matched-skill">${escape(s)}</span>`).join(''):`<small>${t('noSkillMatch')}</small>`}</div>
    ${fields.map(([key,label,weight])=>`<div class="score-row"><span>${t(label)} <small>(${weight})</small></span><div><i style="width:${Math.max(0,Math.min(1,components[key]||0))*100}%"></i></div><b>${(components[key]||0).toFixed(3)}</b></div>`).join('')}<small class="score-note">${t('scoreNote')}</small></section>`;
}
function detailPanel() {
  if(!state.selected)return `<div class="detail-placeholder">${icon('briefcase')}<h3>${t('selectJob')}</h3><p>${t('emptyDetail')}</p></div>`;
  if(!state.detail||state.detail.job.id!==state.selected)return `<div class="detail-loading"><span class="loader"></span></div>`;
  if(state.detail.error)return `<div class="empty-state"><p>${t('connection')}</p><button class="secondary" data-job="${state.selected}">${t('retry')}</button></div>`;
  const job={...state.detail.job,...(state.matches?.find(j=>j.id===state.selected)||{})};
  const source=/^https:\/\/huggingface\.co\//.test(job.source||'')?job.source:null;
  return `<div class="detail-topline"><span><i></i>${t('details')}</span><button class="mobile-close icon-button" id="close-detail" aria-label="${t('close')}">${icon('close')}</button>${saveButton(job)}</div>
    <div class="detail-company">${companyLogo(job)}<span>${escape(job.company)}</span></div><h2 class="detail-title">${escape(job.title)}</h2><p class="detail-location">${icon('pin')}${escape(job.location)}</p>
    <div class="detail-facts"><div><small>${state.lang==='vi'?'Mức lương':'Salary'}</small><strong>${escape(job.salary||t('salaryUnknown'))}</strong></div><div><small>${t('experience')}</small><strong>${experience(job)}</strong></div></div>
    <div class="detail-actions">${source?`<a class="primary" href="${escape(source)}" target="_blank" rel="noopener noreferrer">${t('source')}${icon('external')}</a>`:''}<button class="secondary" data-save="${job.id}">${icon('bookmark')}${t(state.saved.has(job.id)?'unsave':'save')}</button></div>
    ${explanation(job)}<section class="detail-section"><h3>${t('skills')}</h3><div class="skill-tags">${job.skills.map(s=>`<span>${escape(s)}</span>`).join('')}</div></section>
    <section class="detail-section"><h3>${t('description')}</h3><p class="description">${escape(job.description)}</p></section>
    ${job.requirements?`<section class="detail-section"><h3>${t('requirements')}</h3><p class="description">${escape(job.requirements)}</p></section>`:''}
    <section class="detail-section similar-section"><h3>${t('similar')}</h3><p class="muted">${t('similarSub')}</p>${state.detail.similar.map(j=>`<button class="similar-job" data-job="${j.id}">${companyLogo(j,true)}<span><strong>${escape(j.title)}</strong><small>${escape(j.location)}</small></span>${icon('chevron')}</button>`).join('')}</section><p class="source-note">${t('sourceNote')}</p>`;
}
function workspace() { return `<section class="workspace" id="workspace">${state.view==='cv'?'':filters()}<div class="results" id="results">${results()}</div><aside class="job-detail" id="job-detail" aria-label="${t('details')}">${detailPanel()}</aside></section>`; }
function cvSteps() {
  const step=state.matches?3:state.profile?2:1;
  return `<ol class="cv-steps">${['uploadStep','confirmStep','resultsStep'].map((key,i)=>`<li class="${step>=i+1?'complete':''}"><span>${step>i+1?icon('check'):String(i+1).padStart(2,'0')}</span>${t(key)}</li>`).join('')}</ol>`;
}
function cvInput() {
  return `<section class="cv-input-panel"><div class="panel-heading"><span class="section-kicker">${t('cv')}</span><h2>${t(state.profile?'analyzed':'uploadTitle')}</h2><p>${t('uploadSub')}</p></div>
    ${state.profile?`<div class="cv-success">${icon('check')}<span><strong>${t('cvReady')}</strong><small>${escape(state.file?.name||t('sample'))}</small></span><button class="icon-button" id="clear-cv" aria-label="${t('remove')}">${icon('close')}</button></div>`:
    `<label class="dropzone ${state.file?'has-file':''} ${state.reading?'is-reading':''}" id="dropzone" tabindex="0"><input type="file" id="cv-file" accept=".pdf,.docx,.png,.jpg,.jpeg,.webp,.tif,.tiff" ${state.reading?'disabled':''}><span class="upload-icon">${state.reading?'<span class="loader"></span>':icon(state.file?'file':'upload')}</span><strong>${state.reading?t('reading'):state.file?escape(state.file.name):t('dropTitle')}</strong><span>${t(state.reading?'readHint':state.file?'newFile':'dropSub')}</span><span class="secondary file-label">${t('choose')}${icon('arrow')}</span><small>${t('formats')}</small></label>
      <button class="primary full-width" id="read-cv" ${!state.file||state.reading?'disabled':''}>${state.reading?'<span class="loader light"></span>':icon('spark')}${t(state.reading?'reading':'read')}</button>`}
    ${state.profile?`<div class="cv-profile"><h3>${t('detected')}<span>${state.profile.skills.length}</span></h3><div class="skill-tags">${state.profile.skills.map(s=>`<span class="matched-skill">${escape(s)}</span>`).join('')||`<p class="muted">${t('noSkills')}</p>`}</div>${state.ocr?`<p class="ocr-note">${t('ocrNote')}</p>`:''}
      <label class="field-label" for="cv-region">${t('preferred')}</label><select id="cv-region">${regionOptions(state.cvRegion,true,true)}</select><p class="field-hint">${t('preferredHint')}</p>
      <details class="cv-text"><summary>${t('review')}</summary><label for="cv-text" class="sr-only">${t('textLabel')}</label><textarea id="cv-text" maxlength="60000">${escape(state.cvText)}</textarea></details><button id="match-cv" class="primary full-width" ${state.matching?'disabled':''}>${state.matching?'<span class="loader light"></span>':icon('spark')}${t(state.matching?'matching':'find')}${icon('arrow')}</button></div>`:''}
    <p class="privacy-note">${icon('lock')}<span>${t('privacy')}</span></p>${!state.reading?`<div class="sample-area"><p>${t('sample')}</p><div>${['sampleData','sampleBackend','sampleAI'].map((key,i)=>`<button data-sample="${i}">${t(key)}${icon('arrow')}</button>`).join('')}</div></div>`:''}</section>`;
}
function cvPage() {
  if(state.matches)return `${cvSteps()}<div class="cv-results-banner"><span class="success-symbol">${icon('check')}</span><div><h2>${t('matched')}</h2><p>${t('matchedSub')}${state.cvRegion?' · '+escape(state.data.all_regions.find(r=>r.id===state.cvRegion)?.label||''):''}</p></div><button class="secondary" id="edit-cv">${t('adjust')}${icon('arrow')}</button></div>${workspace()}`;
  return `${cvSteps()}<div class="cv-layout">${cvInput()}<aside class="cv-guide"><span class="guide-illustration">${icon('file')}<b>${icon('spark')}</b></span><p class="section-kicker">JOBVISTA</p><h2>${t('how')}</h2><p>${t('howSub')}</p><ol>${[1,2,3].map(i=>`<li><span>0${i}</span><div><h3>${t('how'+i)}</h3><p>${t('how'+i+'Sub')}</p></div></li>`).join('')}</ol><div class="guide-note">${icon('check')}<span>${t('scoreNote')}</span></div></aside></div>`;
}
function render() {
  document.documentElement.lang=state.lang;document.title=t('pageTitle');
  $('.skip-link').textContent=state.lang==='vi'?'Đến nội dung':'Skip to content';
  $('#app').innerHTML=`${header()}<main id="main" class="shell">${state.view==='saved'?`<section class="saved-hero"><p class="section-kicker">${t('saved')}</p><h1>${t('savedTitle')}</h1><p>${t('savedSub')}</p></section>`:hero()}
    ${state.loading?`<div class="initial-loading"><span class="loader"></span>${t('loading')}</div>`:state.error?`<div class="empty-state"><p>${t('connection')}</p><button class="primary" id="retry">${t('retry')}</button></div>`:state.view==='cv'?cvPage():searchBar()+workspace()}</main><footer class="footer"><div><strong>JobVista<span> / </span></strong>${t('footer')}</div><a href="https://huggingface.co/datasets/tinixai/vietnamese-job-descriptions" target="_blank" rel="noopener noreferrer">${t('sourceLink')}${icon('external')}</a></footer>`;
  bind();
}
function updateResults() {
  $('#results').innerHTML=results();bindResults();
  const filtered=filteredJobs();
  if(!filtered.some(j=>j.id===state.selected)) {
    state.selected=filtered[0]?.id||null;state.detail=null;
    $('#job-detail').innerHTML=detailPanel();if(state.selected)loadDetail(state.selected);
  }
}
async function loadCatalog() {
  state.loading=true;state.error='';render();const language=state.lang;
  try { const data=await api(`/api/catalog?language=${language}`);if(language!==state.lang)return;
    state.data=data;state.jobs=data.jobs;state.loading=false;render();
    if(state.view!=='cv'){state.selected=filteredJobs()[0]?.id||null;if(state.selected)loadDetail(state.selected);}
  } catch {if(language===state.lang){state.loading=false;state.error='connection';render();}}
}
async function loadDetail(id, openMobile=false) {
  state.selected=id;state.detail=null;const version=++state.detailVersion;
  const panel=$('#job-detail');if(!panel)return;panel.innerHTML=detailPanel();
  document.querySelectorAll('[data-card]').forEach(el=>el.classList.toggle('selected',el.dataset.card===id));
  if(openMobile)panel.classList.add('mobile-open');
  try {const data=await api(`/api/jobs/${encodeURIComponent(id)}?language=${state.lang}${state.view==='cv'&&state.cvRegion?'&location='+encodeURIComponent(state.cvRegion):''}`);
    if(version!==state.detailVersion)return;state.detail=data;panel.innerHTML=detailPanel();bindDetail();panel.scrollTop=0;
  } catch {if(version===state.detailVersion){state.detail={job:{id},error:true};panel.innerHTML=detailPanel();bindDetail();}}
}
function toggleSave(id) {
  if(state.saved.has(id)){state.saved.delete(id);toast(t('removedToast'));}else{state.saved.add(id);toast(t('savedToast'));}
  try{localStorage.setItem('jobvista-saved',JSON.stringify([...state.saved]));}catch{}
  document.querySelector('.nav-count').textContent=state.saved.size;
  if(state.view==='saved')updateResults();else if($('#results')){$('#results').innerHTML=results();bindResults();}
  if($('#job-detail')){$('#job-detail').innerHTML=detailPanel();bindDetail();}
}
function resetFilters() {Object.assign(state,{q:'',region:'',domain:'',exp:'',category:'all',page:1});render();updateResults();}
function navigate(view) {
  state.view=view;state.page=1;state.detailVersion++;state.detail=null;state.selected=null;
  Object.assign(state,{q:'',region:'',domain:'',exp:'',category:'all'});render();
  if(view!=='cv'||state.matches){state.selected=filteredJobs()[0]?.id||null;if(state.selected)loadDetail(state.selected);}
  window.scrollTo({top:0,behavior:'smooth'});
}
function bindDetail() {
  $('#job-detail')?.querySelectorAll('[data-save]').forEach(el=>el.onclick=()=>toggleSave(el.dataset.save));
  $('#job-detail')?.querySelectorAll('[data-job]').forEach(el=>el.onclick=()=>loadDetail(el.dataset.job,true));
  if($('#close-detail'))$('#close-detail').onclick=()=>$('#job-detail').classList.remove('mobile-open');
}
function bindResults() {
  $('#results')?.querySelectorAll('[data-job]').forEach(el=>el.onclick=()=>loadDetail(el.dataset.job,true));
  $('#results')?.querySelectorAll('[data-save]').forEach(el=>el.onclick=()=>toggleSave(el.dataset.save));
  $('#results')?.querySelectorAll('[data-category]').forEach(el=>el.onclick=()=>{state.category=el.dataset.category;state.page=1;updateResults();});
  $('#results')?.querySelectorAll('[data-page]').forEach(el=>el.onclick=()=>{state.page=+el.dataset.page;updateResults();$('#workspace').scrollIntoView({behavior:'smooth',block:'start'});});
  if($('#empty-reset'))$('#empty-reset').onclick=resetFilters;
  $('#results')?.querySelectorAll('[data-nav]').forEach(el=>el.onclick=()=>navigate(el.dataset.nav));
}
function bind() {
  document.querySelectorAll('[data-nav]').forEach(el=>el.onclick=e=>{e.preventDefault();navigate(el.dataset.nav);});
  $('#language').onclick=()=>{state.lang=state.lang==='vi'?'en':'vi';$('#toast').classList.remove('visible');state.domain='';state.cvVersion++;state.reading=false;state.matching=false;state.matches=null;state.selected=null;state.detailVersion++;state.detail=null;loadCatalog();};
  if($('#retry'))$('#retry').onclick=loadCatalog;
  if($('#search-form'))$('#search-form').onsubmit=e=>{e.preventDefault();state.q=$('#search').value;state.page=1;updateResults();$('#workspace').scrollIntoView({behavior:'smooth',block:'start'});};
  if($('#search'))$('#search').oninput=e=>{clearTimeout(searchTimer);const value=e.target.value;searchTimer=setTimeout(()=>{state.q=value;state.page=1;updateResults();},200);};
  document.querySelectorAll('[data-search]').forEach(el=>el.onclick=()=>{state.q=el.dataset.search;state.page=1;$('#search').value=state.q;updateResults();});
  ['search-region','filter-region'].forEach(id=>{if($('#'+id))$('#'+id).onchange=e=>{state.region=e.target.value;state.page=1;['search-region','filter-region'].forEach(other=>{if($('#'+other))$('#'+other).value=state.region;});updateResults();};});
  if($('#filter-domain'))$('#filter-domain').onchange=e=>{state.domain=e.target.value;state.page=1;updateResults();};
  document.querySelectorAll('[name="experience"]').forEach(el=>el.onchange=()=>{state.exp=el.value;state.page=1;updateResults();});
  if($('#reset'))$('#reset').onclick=resetFilters;
  bindResults();bindDetail();bindCv();
}
function chooseFile(file) {
  if(!file)return;
  if(file.size>15*1024*1024||!(/\.(pdf|docx|png|jpe?g|webp|tiff?)$/i.test(file.name))){toast(t('invalidFile'));return;}
  state.cvVersion++;Object.assign(state,{file,cvText:'',profile:null,ocr:false,matches:null,cvRegion:''});render();
}
function clearCv() {state.cvVersion++;Object.assign(state,{file:null,cvText:'',profile:null,ocr:false,matches:null,cvRegion:'',reading:false,matching:false});render();}
async function readCv() {
  if(!state.file||state.reading)return;state.reading=true;const version=++state.cvVersion;const file=state.file;render();
  try {const data=await api(`/api/cv/read?language=${state.lang}`,{method:'POST',headers:{'Content-Type':'application/octet-stream','X-CV-Filename':encodeURIComponent(file.name)},body:file});
    if(version!==state.cvVersion)return;Object.assign(state,{cvText:data.text,profile:data.profile,ocr:data.ocr,cvRegion:data.profile.locations.find(code=>state.data.all_regions.some(r=>r.id===code))||'',reading:false});render();
  }catch(error){if(version===state.cvVersion){state.reading=false;render();toast(error.message);}}
}
async function useSample(index) {
  const version=++state.cvVersion;
  try {const samples=await api('/api/samples');if(version!==state.cvVersion)return;
    const text=samples[index].CV_Text;Object.assign(state,{file:null,cvText:text,ocr:false,profile:{skills:[],locations:[],title:''},matches:null,cvRegion:'',reading:false,matching:false});
    // Phân tích bằng cùng engine thật; hồ sơ mẫu không có thành phố nên không tự gán vùng.
    const result=await api('/api/cv/match',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text,language:state.lang,top_n:1})});
    if(version!==state.cvVersion)return;state.profile=result.profile;render();
  }catch(error){if(version===state.cvVersion)toast(error.message);}
}
async function findMatches() {
  if(!state.cvText.trim()){toast(t('emptyCv'));return;}state.matching=true;const version=++state.cvVersion;render();
  try {const data=await api('/api/cv/match',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:state.cvText,location:state.cvRegion||null,language:state.lang,top_n:24})});
    if(version!==state.cvVersion)return;Object.assign(state,{matches:data.jobs,profile:data.profile,matching:false,page:1,q:'',region:'',domain:'',exp:'',category:'all',selected:data.jobs[0]?.id||null,detail:null});render();if(state.selected)loadDetail(state.selected);$('#workspace').scrollIntoView({behavior:'smooth',block:'start'});
  }catch(error){if(version===state.cvVersion){state.matching=false;render();toast(error.message);}}
}
function bindCv() {
  if($('#cv-file'))$('#cv-file').onchange=e=>chooseFile(e.target.files[0]);
  const drop=$('#dropzone');
  if(drop){drop.ondragover=e=>{e.preventDefault();drop.classList.add('drag-over');};drop.ondragleave=()=>drop.classList.remove('drag-over');drop.ondrop=e=>{e.preventDefault();drop.classList.remove('drag-over');if(!state.reading)chooseFile(e.dataTransfer.files[0]);};drop.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();$('#cv-file').click();}};}
  if($('#read-cv'))$('#read-cv').onclick=readCv;
  if($('#clear-cv'))$('#clear-cv').onclick=clearCv;
  if($('#cv-region'))$('#cv-region').onchange=e=>{state.cvRegion=e.target.value;invalidateCvInputs();};
  if($('#cv-text'))$('#cv-text').oninput=e=>{state.cvText=e.target.value;invalidateCvInputs();};
  if($('#match-cv'))$('#match-cv').onclick=findMatches;
  if($('#edit-cv'))$('#edit-cv').onclick=()=>{state.matches=null;state.detailVersion++;state.selected=null;state.detail=null;render();};
  document.querySelectorAll('[data-sample]').forEach(el=>el.onclick=()=>useSample(+el.dataset.sample));
}
function invalidateCvInputs() {
  // Bỏ kết quả đang tính từ CV/vùng cũ; không cho phản hồi chậm ghi đè dữ liệu mới.
  const wasMatching=state.matching;
  state.cvVersion++;state.matches=null;state.matching=false;
  if(wasMatching&&$('#match-cv')){$('#match-cv').disabled=false;$('#match-cv').innerHTML=`${icon('spark')}${t('find')}${icon('arrow')}`;}
}
document.addEventListener('keydown',event=>{if(event.key==='Escape')$('#job-detail')?.classList.remove('mobile-open');});
loadCatalog();
