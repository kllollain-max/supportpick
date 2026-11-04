const test=require('node:test'),assert=require('node:assert/strict');
const E=require('../editorials.js');
const now=new Date('2026-11-04T08:00:00+09:00');
const item={id:'TEST1',title:'청년 지원',organization:'기관',region:'경기',period:'2026-11-01 ~ 2026-11-30',summary:'생활지원',sourceUpdatedAt:{list:'2026-11-01',detail:'2026-11-01'}};
const article={benefitId:'TEST1',title:'대상 조건과 신청 준비',url:'https://blog.naver.com/bible_el/123456789',sourceKey:E.sourceKey(item),status:'published',publicationVerified:true,scope:{year:2026,region:'경기',round:'4분기'},publishedAt:'2026-11-03T12:00:00+09:00',verifiedAt:'2026-11-04T07:00:00+09:00',validUntil:'2026-11-20T00:00:00+09:00'};
const registry=(a=article)=>({version:1,articles:[a]});
test('confirmed article attaches to exact benefit/source edition',()=>assert.equal(E.find(item,registry(),now).url,article.url));
test('unpublished draft or missing publication evidence never appears',()=>{for(const a of [{...article,status:'draft'},{...article,publicationVerified:false},{...article,url:''}])assert.equal(E.find(item,registry(a),now),null);});
test('different ID, region, year and changed source invalidate association',()=>{for(const row of [{...item,id:'OTHER'},{...item,region:'서울'},{...item,period:'2027 연간'},{...item,summary:'수정된 지원 조건'},{...item,sourceUpdatedAt:{list:'2026-11-02',detail:'2026-11-01'}}])assert.equal(E.find(row,registry(),now),null);assert.equal(E.find(item,registry({...article,scope:{...article.scope,year:2025}}),now),null);});
test('conflicting source, missing round and sample benefits stay unlinked',()=>{for(const row of [{...item,sourceConflicts:['지원대상']},{...item,sourceDifferences:{기간:{}}},{...item,isSample:true}])assert.equal(E.find(row,registry(),now),null);assert.equal(E.find(item,registry({...article,scope:{year:2026,region:'경기',round:''}}),now),null);});
test('stale or future confirmations and expired links are withheld',()=>{for(const a of [{...article,verifiedAt:'2026-09-01T00:00:00+09:00'},{...article,verifiedAt:'2026-11-05T00:00:00+09:00'},{...article,validUntil:'2026-11-04T07:00:00+09:00'},{...article,validUntil:'2027-01-01T00:00:00+09:00'}])assert.equal(E.find(item,registry(a),now),null);});
test('another blog, unsafe schemes and deceptive hosts are rejected',()=>{for(const url of ['javascript:alert(1)','https://blog.naver.com.evil.test/bible_el/123','https://blog.naver.com/other/123','https://user@blog.naver.com/bible_el/123','https://blog.naver.com/bible_el/123?redirect=other'])assert.equal(E.find(item,registry({...article,url}),now),null);});
test('ambiguous duplicate articles are hidden instead of guessed',()=>assert.equal(E.find(item,{version:1,articles:[article,{...article,url:'https://blog.naver.com/bible_el/222'}]},now),null));
test('static site has no Threads navigation or blog channel banner',()=>{const fs=require('node:fs');const html=fs.readFileSync(require('node:path').join(__dirname,'../index.html'),'utf8');assert.doesNotMatch(html,/threads\.com|supportpick-channels|href="https:\/\/blog.naver.com\/bible_el"/);assert.match(html,/지원금픽 — 정부지원금/);});
test('malformed registry entry cannot break the list',()=>assert.equal(E.find(item,{version:1,articles:[null,4,'bad']},now),null));
test('registration CLI preserves history and refuses an unconfirmed draft',()=>{
 const fs=require('node:fs'),os=require('node:os'),path=require('node:path'),cp=require('node:child_process');
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'sp-editorial-'));
 try{
  const current=new Date(),verifiedAt=new Date(+current-20000).toISOString(),publishedAt=new Date(+current-60000).toISOString();
  const a={...article,scope:{...article.scope,year:Number(current.toLocaleDateString('sv-SE',{timeZone:'Asia/Seoul'}).slice(0,4))},publishedAt,verifiedAt,validUntil:new Date(+current+86400000).toISOString()};
  const output=path.join(dir,'registry.json'),input=path.join(dir,'input.json'),feed=path.join(dir,'feed.json');
  fs.writeFileSync(output,JSON.stringify(registry({...a,url:'https://blog.naver.com/bible_el/111'})));
  fs.writeFileSync(input,JSON.stringify(a));fs.writeFileSync(feed,JSON.stringify({isSample:false,items:[item]}));
  const args=[path.join(__dirname,'../tools/register-editorial.cjs'),'--input',input,'--feed',feed,'--output',output];
  cp.execFileSync(process.execPath,args);
  const saved=JSON.parse(fs.readFileSync(output,'utf8'));assert.equal(saved.articles.length,2);assert.equal(saved.articles[0].status,'superseded');assert.equal(saved.articles[1].url,a.url);
  const before=fs.readFileSync(output,'utf8');fs.writeFileSync(input,JSON.stringify({...a,publicationVerified:false}));
  assert.throws(()=>cp.execFileSync(process.execPath,args,{stdio:'pipe'}));assert.equal(fs.readFileSync(output,'utf8'),before);
 }finally{fs.rmSync(dir,{recursive:true,force:true});}
});
