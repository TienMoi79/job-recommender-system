/* Chạy độc lập: node --test tests/test_personalization.cjs
 * Không cần cài Node để chạy web; Node chỉ phục vụ kiểm thử JavaScript. */
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const Storage = require('../web_ui/personalization.js');

function memoryStorage() {
  const values = new Map();
  return { getItem: key => values.get(key) ?? null, setItem: (key, value) => values.set(key, value),
    removeItem: key => values.delete(key), values };
}
const profile = (extra={}) => ({version:1,text:'Backend Developer. Python, Django. 2 years experience.',filename:'sample.docx',
  region:'ha_noi',homeRegion:'',experience:'2',experienceEdited:true,ocr:false,updatedAt:123,
  profile:{title:'Backend Developer',skills:['Python','Django'],locations:['ha_noi'],home_locations:[],experience_years:2,experience_status:'confirmed'},...extra});
const search = (extra={}) => ({id:'search-1',q:'Python',region:'ha_noi',domain:'Software Development',exp:'1',category:'dev',updatedAt:123,count:1,...extra});

test('CV persists across adapter instances without the original file or arbitrary fields', () => {
  const memory=memoryStorage(), store=new Storage(memory);
  assert.equal(store.writeProfile(profile({file:Buffer.from('original CV'),password:'never save me'})),true);
  const restored=new Storage(memory).readProfile();
  assert.deepEqual(restored,profile());
  assert.equal(memory.values.get('jobvista-profile-v1').includes('never save me'),false);
  assert.equal(Object.hasOwn(restored,'file'),false);
});
test('zero and unknown experience remain distinct, including an explicit blank override', () => {
  for(const value of ['',0,'0',2.5]){
    const store=new Storage(memoryStorage());store.writeProfile(profile({experience:value}));
    assert.equal(store.readProfile().experience,value===''?'':String(value));
    assert.equal(store.readProfile().experienceEdited,true);
  }
});
test('corrupt storage and unsupported schema fail safely; invalid CV cannot overwrite a good one', () => {
  const memory=memoryStorage(),store=new Storage(memory);
  store.writeProfile(profile());
  for(const bad of [profile({text:''}),profile({text:'x'.repeat(60001)}),profile({experience:-1}),profile({experience:'NaN'}),profile({version:9})])assert.equal(store.writeProfile(bad),false);
  assert.deepEqual(store.readProfile(),profile());
  memory.setItem('jobvista-profile-v1','{broken');assert.equal(store.readProfile(),null);
  assert.equal(store.failed,true);
  memory.setItem('jobvista-searches-v1',JSON.stringify({version:42,items:[search()]}));assert.deepEqual(store.readSearches(),[]);
});
test('quota/security failures do not crash and deletion failure is reported', () => {
  const store=new Storage({getItem(){throw Error('blocked');},setItem(){throw Error('quota');},removeItem(){throw Error('blocked');}});
  assert.equal(store.readProfile(),null);assert.deepEqual(store.readSearches(),[]);
  assert.equal(store.writeProfile(profile()),false);assert.equal(store.writeSearches([search()]),false);
  assert.equal(store.removeProfile(),false);assert.equal(store.failed,true);
});
test('deleting a CV leaves bookmarks and saved searches intact', () => {
  const memory=memoryStorage(),store=new Storage(memory);
  store.writeProfile(profile());store.writeSearches([search()]);memory.setItem('jobvista-saved','["VN0002"]');
  assert.equal(store.removeProfile(),true);assert.equal(new Storage(memory).readProfile(),null);
  assert.deepEqual(new Storage(memory).readSearches(),[search()]);assert.equal(memory.getItem('jobvista-saved'),'["VN0002"]');
});
test('search deduplication keeps all filters and stable domain/region IDs', () => {
  let items=Storage.upsertSearch([],search());const id=items[0].id;
  items=Storage.upsertSearch(items,search({q:'  PYTHON  '}));assert.equal(items.length,1);assert.equal(items[0].id,id);
  items=Storage.upsertSearch(items,search({region:'ho_chi_minh'}));assert.equal(items.length,2);
  const store=new Storage(memoryStorage());store.writeSearches(items);
  assert.deepEqual(new Storage(store.storage).readSearches(),items);
  assert.equal(Storage.cleanSearch(search({q:'',region:'',domain:'',exp:'',category:'all'})),null);
  assert.equal(Storage.cleanSearch(search({exp:'untrusted'})),null);
});
test('saved searches cap at 20 and invalid entries are excluded', () => {
  let items=[];for(let i=0;i<25;i++)items=Storage.upsertSearch(items,search({q:'Query '+i}));
  assert.equal(items.length,20);assert.equal(items[0].q,'Query 24');
  const memory=memoryStorage();memory.setItem('jobvista-searches-v1',JSON.stringify({version:1,items:[null,{},...items,items[0]]}));
  assert.equal(new Storage(memory).readSearches().length,20);
});
test('automatic interests count distinct visits, suppress rapid repeats and expire old entries', () => {
  const old=search({updatedAt:Date.now()-31000,count:3});
  let items=Storage.upsertSearch([old],search());assert.equal(items[0].count,4);
  items=Storage.upsertSearch(items,search());assert.equal(items[0].count,4);
  items=Storage.upsertSearch([search({q:'old',updatedAt:Date.now()-91*86400000})],search());
  assert.equal(items.length,1);assert.equal(items[0].q,'Python');
});

// Kiểm thử điều phối bất đồng bộ bằng các promise chủ động, không mở trình duyệt
// và không sao chép thuật toán Python. Chỉ bỏ entrypoint tải catalog khỏi sandbox.
function appHarness() {
  const memory=memoryStorage(),calls=[];
  const context=vm.createContext({JobVistaStorage:Storage,localStorage:memory,console,Date,Set,JSON,Number,String,
    setTimeout,clearTimeout,document:{addEventListener(){},querySelector(){return null;}},window:{addEventListener(){},scrollTo(){}}});
  const source=fs.readFileSync(path.join(__dirname,'../web_ui/app.js'),'utf8').replace(/loadCatalog\(\);\s*$/,'');
  vm.runInContext(source+`;render=()=>{};toast=()=>{};refreshPersonalPanel=()=>{};
    globalThis.appTest={state,persistCv,clearCv,refreshHome,homePayload,rememberSearch,restoreProfile,chooseFile,readCv,personalPanel,locationComparison,demandExplanation,jobDocument,copy};`,context);
  return {context,memory,calls,app:context.appTest};
}
function deferredApp() {
  const h=appHarness();
  h.context.pendingRequest=(url,options,resolve,reject)=>h.calls.push({url,payload:typeof options.body==='string'?JSON.parse(options.body):options.body,resolve,reject});
  vm.runInContext(`api=(url,options)=>new Promise((resolve,reject)=>pendingRequest(url,options,resolve,reject));`,h.context);
  h.app.state.data={all_regions:[{id:'ha_noi',label:'Hà Nội'}]};
  h.app.restoreProfile(profile());h.app.persistCv();return h;
}
test('homepage uses the saved CV, preferred location and explicit unknown override', async () => {
  const h=deferredApp();h.app.state.cvExperience='';h.app.persistCv();
  const pending=h.app.refreshHome();assert.equal(h.calls.length,1);
  assert.equal(h.calls[0].url,'/api/recommendations');
  assert.equal(h.calls[0].payload.profile.location,'ha_noi');assert.equal(h.calls[0].payload.profile.experience_override,true);
  assert.equal(h.calls[0].payload.profile.experience_years,null);
  h.calls[0].resolve({jobs:[{id:'VN0004',score:0.9}],profile:profile().profile,algorithm:{mode:'hybrid'}});await pending;
  assert.equal(h.app.state.homeMatches[0].id,'VN0004');
  await h.app.refreshHome();assert.equal(h.calls.length,1); // Tái dùng kết quả trong phiên, không tính lại vô ích.
});
test('a late recommendation response cannot resurrect a deleted CV', async () => {
  const h=deferredApp(),pending=h.app.refreshHome();
  h.app.clearCv();h.calls[0].resolve({jobs:[{id:'old'}],profile:profile().profile,algorithm:{}});await pending;
  assert.equal(h.app.state.savedProfile,null);assert.equal(h.app.state.homeMatches,null);
  assert.equal(new Storage(h.memory).readProfile(),null);
});
test('editing CV text refreshes inferred experience without overriding an explicit choice', async () => {
  const h=deferredApp();h.app.state.cvExperienceEdited=false;h.app.state.cvText='Backend Developer. Python, Django.';h.app.persistCv();
  const pending=h.app.refreshHome();h.calls[0].resolve({jobs:[],profile:{...profile().profile,experience_years:null,experience_status:'unknown'},algorithm:{}});await pending;
  assert.equal(h.app.state.savedProfile.experience,'');assert.equal(h.app.state.cvExperience,'');
  assert.equal(new Storage(h.memory).readProfile().experience,'');
  await h.app.refreshHome();assert.equal(h.calls.length,1);
});
test('a late response for an earlier CV or language cannot replace current matches', async () => {
  const h=deferredApp(),first=h.app.refreshHome();
  h.app.state.cvRegion='quang_ninh';h.app.state.lang='en';h.app.persistCv();const second=h.app.refreshHome();
  h.calls[1].resolve({jobs:[],profile:profile().profile,algorithm:{mode:'hybrid-lexical'}});await second;
  h.calls[0].resolve({jobs:[{id:'stale'}],profile:profile().profile,algorithm:{mode:'hybrid'}});await first;
  assert.equal(h.app.state.homeMatches.length,0);assert.equal(h.app.state.homeMethod.mode,'hybrid-lexical');
  assert.equal(h.calls[1].payload.language,'en');assert.equal(h.calls[1].payload.profile.location,'quang_ninh');
});
test('network failures retain the saved CV and allow a successful retry', async () => {
  const h=deferredApp(),first=h.app.refreshHome();h.calls[0].reject(Error('offline'));await first;
  assert.equal(h.app.state.homeError,true);assert.ok(h.app.state.savedProfile);
  const retry=h.app.refreshHome(true);h.calls[1].resolve({jobs:[],profile:profile().profile,algorithm:{}});await retry;
  assert.equal(h.app.state.homeError,false);assert.equal(h.app.state.homeMatches.length,0);
});
test('choosing a replacement CV keeps the saved profile if reading fails', async () => {
  const h=deferredApp();h.app.state.view='cv';
  h.app.chooseFile({name:'replacement.pdf',size:100});
  assert.equal(h.app.state.profile,null);assert.equal(h.app.state.savedProfile.text,profile().text);
  const reading=h.app.readCv();h.calls[0].reject(Error('unreadable PDF'));await reading;
  assert.equal(h.app.state.savedProfile.text,profile().text);
  assert.equal(new Storage(h.memory).readProfile().text,profile().text);
  assert.equal(h.app.state.reading,false);
});
test('successful document reading automatically replaces the saved profile before matching', async () => {
  const h=deferredApp();h.app.state.view='cv';
  h.app.chooseFile({name:'replacement.docx',size:100});
  const reading=h.app.readCv();h.calls[0].resolve({text:'Data Analyst. SQL, Python.',ocr:false,profile:{
    title:'Data Analyst',skills:['SQL','Python'],locations:['ha_noi'],experience_years:null,experience_status:'unknown'}});await reading;
  const restored=new Storage(h.memory).readProfile();assert.equal(restored.filename,'replacement.docx');
  assert.equal(restored.text,'Data Analyst. SQL, Python.');assert.equal(restored.region,'ha_noi');
  assert.equal(restored.experience,'');assert.equal(h.app.state.matches,null);
});
test('failed profile deletion keeps the visible and stored profile consistent', () => {
  const h=deferredApp();h.memory.removeItem=()=>{throw Error('permission denied');};
  h.app.clearCv();assert.ok(h.app.state.savedProfile);assert.ok(h.app.state.cvText);
  assert.ok(new Storage(h.memory).readProfile());assert.equal(h.app.state.storageError,true);
});
test('new UI strings have the same Vietnamese and English keys', () => {
  const {app}=appHarness();assert.deepEqual(Object.keys(app.copy.vi).sort(),Object.keys(app.copy.en).sort());
});
test('home location persists independently from the preferred work region', () => {
  const h=deferredApp();h.app.state.cvHomeRegion='ho_chi_minh';h.app.persistCv();
  const saved=new Storage(h.memory).readProfile();assert.equal(saved.homeRegion,'ho_chi_minh');assert.equal(saved.region,'ha_noi');
  assert.equal(h.app.homePayload().profile.home_region,'ho_chi_minh');
  assert.equal(Object.hasOwn(h.app.homePayload().profile,'record_demand'),false);
  h.app.restoreProfile(saved);assert.equal(h.app.state.cvHomeRegion,'ho_chi_minh');
});
test('comparison keeps content scores and distance labels distinct and escapes job text', () => {
  const h=appHarness();h.app.state.cvHomeRegion='ho_chi_minh';h.app.state.comparison={
    best_fit:[{id:'a',title:'<script>bad</script>',company:'A',location:'Hà Nội',score:.9,distance_km:1135}],
    near_home:[{id:'b',title:'Backend',company:'B',location:'HCM',score:.7,same_region:true}]};
  const html=h.app.locationComparison();assert.ok(html.includes('0.900'));assert.ok(html.includes('0.700'));
  assert.ok(html.includes('1135 km'));assert.ok(html.includes('Cùng khu vực nơi ở'));
  assert.ok(html.includes('&lt;script&gt;'));assert.equal(html.includes('<script>'),false);
  assert.ok(html.includes('không phải đường đi thực tế'));assert.equal(html.includes('0 km'),false);
  const rating=h.app.demandExplanation({demand_rating:2.5,demand_actors:10,demand_weight:.1});
  assert.ok(rating.includes('2.50/5'));assert.ok(rating.includes('10%'));assert.ok(rating.includes('không phải đánh giá chất lượng'));
});
test('job text renders as separate paragraphs, headings and lists without source HTML execution', () => {
  const {app}=appHarness();
  const html=app.jobDocument('MÔ TẢ CÔNG VIỆC:\n• Viết API với Node.js\n• Kinh nghiệm 3 - 4 năm\nQUYỀN LỢI:\nLương 15 - 25 triệu.\n<script>bad()</script>');
  assert.ok(html.includes('<h4>MÔ TẢ CÔNG VIỆC</h4>'));
  assert.ok(html.includes('<ul><li>Viết API với Node.js</li><li>Kinh nghiệm 3 - 4 năm</li></ul>'));
  assert.ok(html.includes('<p>Lương 15 - 25 triệu.</p>'));
  assert.ok(html.includes('&lt;script&gt;bad()&lt;/script&gt;'));assert.equal(html.includes('<script>'),false);
  assert.equal(app.jobDocument(''), '');
  assert.equal(app.jobDocument('MÔ TẢ CÔNG VIỆC:\nNội dung.','description'),'<p>Nội dung.</p>');
  assert.equal(app.jobDocument('1) Làm API\n2) Kiểm thử API'),'<ol><li>Làm API</li><li>Kiểm thử API</li></ol>');
});
test('searches feed recommendations automatically without a saved-search UI', async () => {
  const h=deferredApp();h.app.state.savedProfile=null;h.app.state.profile=null;
  h.app.state.jobs=[{id:'a',title:'Python Developer',company:'A',skills:['Python'],domain:'Software Development',
    domain_id:'Software Development',regions:['ha_noi'],experience_known:true,experience:2,location:'Hà Nội',salary:''}];
  h.app.state.q='Python';h.app.state.region='ha_noi';
  h.app.rememberSearch();assert.equal(h.calls[0].payload.profile,null);
  assert.equal(h.calls[0].payload.searches[0].q,'Python');assert.equal(h.calls[0].payload.searches[0].region,'ha_noi');
  assert.equal(Object.hasOwn(h.calls[0].payload.searches[0],'id'),false);
  const history=new Storage(h.memory).readSearches();assert.equal(history.length,1);
  h.calls[0].resolve({jobs:[{...h.app.state.jobs[0],personal_score:1}],profile:null,
    algorithm:{mode:'interest'},personalization:{mode:'interest',location:'ha_noi'}});
  await new Promise(resolve=>setImmediate(resolve));
  const html=h.app.personalPanel();assert.ok(html.includes('Có thể bạn quan tâm'));
  assert.equal(html.includes('Lưu tìm kiếm'),false);assert.equal(html.includes('saved-search'),false);
  const source=fs.readFileSync(path.join(__dirname,'../web_ui/app.js'),'utf8');
  assert.equal(source.includes('saved-search-panel'),false);assert.equal(source.includes('save-search'),false);
  h.app.state.q='no matching jobs';h.app.rememberSearch();
  assert.equal(new Storage(h.memory).readSearches().length,1); // Không học từ kết quả rỗng.
});
test('late interest suggestions cannot overwrite a newer search', async () => {
  const h=deferredApp();h.app.state.savedProfile=null;
  h.app.state.jobs=[{id:'a',title:'Python React',company:'A',skills:[],domain:'Software Development',regions:['ha_noi']}];
  h.app.state.q='Python';h.app.rememberSearch();h.app.state.q='React';h.app.rememberSearch();
  h.calls[1].resolve({jobs:[{id:'new'}],profile:null,algorithm:{mode:'interest'},personalization:{}});
  await new Promise(resolve=>setImmediate(resolve));
  h.calls[0].resolve({jobs:[{id:'old'}],profile:null,algorithm:{mode:'interest'},personalization:{}});
  await new Promise(resolve=>setImmediate(resolve));assert.equal(h.app.state.homeMatches[0].id,'new');
});
