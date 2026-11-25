'use strict';
// Exercise actual site scripts against local fixture responses; no external traffic.
const {test,before,after}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
let chromium;
try{({chromium}=require('playwright'));}catch(e){
  if(!process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES)throw e;
  ({chromium}=require(path.join(process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES,'playwright')));
}
const DIST=path.resolve(__dirname,'../dist'),ORIGIN='https://kllollain-max.github.io';
const RECORDS='supportpick:records:v1';
const stored=JSON.stringify({version:1,revision:0,saved:['kept'],apps:{},prefs:{region:'',category:''}});
let browser;
before(async()=>{browser=await chromium.launch({headless:true,...(process.env.SP_ANALYTICS_CHROMIUM_EXECUTABLE?{executablePath:process.env.SP_ANALYTICS_CHROMIUM_EXECUTABLE}:{})});});
after(async()=>{await browser?.close();});

async function fixture(width,stale=false){
  const stamp=new Date().toISOString();
  const ids=['different','normal','third','fourth','held'];
  const items=ids.map((id,i)=>({id,title:'비교모의 '+(id==='third'?'different':id),organization:id==='third'?'다른 모의 기관':'모의 기관',category:'생활안정',region:'전국',
    summary:'신청 절차를 대조할 수 있는 모의 공식 안내',target:'모의 대상',targetPreview:'모의 대상',support:id==='normal'?'9,00만원(30만원 x 30개월)':'모의 지원내용',
    method:'공식 창구 확인',documents:'공식 공고 확인',contact:'공식 문의처 확인',selection:'공식 기준 확인',
    supportType:'현금',supportTypes:['현금'],audience:['개인'],period:'공고별 확인',periodKind:'needs_check',
    officialUrl:'https://plus.gov.kr/',checkedAt:stamp,sourceUpdatedAt:stamp,source:'모의 API',
    detailShard:'00',generation:'comparison-fixture',reviewRequired:id==='held',
    sourceConflicts:id==='different'?['지원유형']:[],
    sourceDifferences:id==='different'?{지원유형:{list:'현금||<img src=x onerror=alert(1)>',detail:'서비스(돌봄)'}}:{}}));
  const feed={schemaVersion:1,generation:'comparison-fixture',updatedAt:stamp,collectionSucceededAt:stamp,
    coverage:'비교 기능 모의자료',sourceCount:items.length,isSample:false,partial:false,items,detailBase:'details/comparison-fixture/'};
  const context=await browser.newContext({viewport:{width,height:900},serviceWorkers:'block'});
  await context.addInitScript(({key,value})=>{if(location.origin==='https://kllollain-max.github.io')localStorage.setItem(key,value);},{key:RECORDS,value:stored});
  const errors=[];context.on('page',p=>p.on('pageerror',e=>errors.push(e.message)));
  await context.route('**/*',async route=>{
    const u=new URL(route.request().url());if(u.origin!==ORIGIN)return route.abort();
    const name=u.pathname.replace(/^\/supportpick\//,'')||'index.html';
    if(name==='data.js'||name==='data-bootstrap.js')return route.fulfill({contentType:'text/javascript',body:'window.SUPPORTPICK_DATA='+JSON.stringify(feed)+';'});
    if(name==='status.json')return route.fulfill({json:{status:'success',generation:feed.generation}});
    if(name==='details/comparison-fixture/00.json')return route.fulfill({json:{generation:stale?'other-generation':feed.generation,items:Object.fromEntries(items.map(p=>[p.id,p]))}});
    const file=path.resolve(DIST,name);if(!file.startsWith(DIST+path.sep)||!fs.existsSync(file))return route.fulfill({status:404,body:'missing'});
    const ext=path.extname(file),types={'.js':'text/javascript','.css':'text/css','.html':'text/html','.svg':'image/svg+xml','.png':'image/png'};
    return route.fulfill({contentType:types[ext]||'application/octet-stream',body:fs.readFileSync(file)});
  });
  const page=await context.newPage();await page.goto(ORIGIN+'/supportpick/');await page.waitForSelector('[data-compare="different"]');
  return {context,page,errors};
}

test('comparison shows both classifications at three widths, escapes source HTML and preserves records',async()=>{
  for(const width of [320,390,1440]){
    const {context,page,errors}=await fixture(width);
    try{
      const card=page.locator('article').filter({has:page.locator('[data-compare="different"]')});
      assert.match(await card.innerText(),/목록·상세 분류 차이/);
      assert.equal(await card.locator('img').count(),0);
      assert.equal(await page.locator('[data-compare="held"]').count(),0);
      for(const id of ['different','normal','third'])await page.locator('[data-compare="'+id+'"]').click();
      await page.locator('[data-compare="fourth"]').click();
      assert.match(await page.locator('#compareCount').innerText(),/3 \/ 3/);
      await page.locator('#compareOpen').click();await page.waitForSelector('.comparison-table');
      assert.match(await page.locator('.same-name-notice').innerText(),/기관별 지원 조건/);
      assert.equal(await page.locator('.comparison-table .amount-source-notice').count(),1);
      assert.match(await page.locator('.comparison-table .amount-source-notice').innerText(),/9,00/);
      const headers=page.locator('.comparison-table thead th');
      assert.match(await headers.nth(1).innerText(),/모의 기관/);assert.match(await headers.nth(3).innerText(),/다른 모의 기관/);
      const row=page.locator('.comparison-table tr').filter({has:page.getByRole('rowheader',{name:'지원방식(API 분류)',exact:true})});
      const cells=row.locator('td');assert.equal(await cells.count(),3);
      assert.match(await cells.nth(0).innerText(),/목록: 현금/);assert.match(await cells.nth(0).innerText(),/상세: 서비스\(돌봄\)/);
      assert.equal(await cells.nth(1).innerText(),'현금');assert.equal(await row.locator('img').count(),0);
      assert(await page.locator('.comparison-scroll').evaluate(el=>el.scrollWidth>=el.clientWidth));
      assert.equal(await page.evaluate(key=>localStorage.getItem(key),RECORDS),stored);
      await page.getByRole('button',{name:'비교 닫기',exact:true}).click();await page.locator('#compareClear').click();
      assert.equal(await page.locator('#compareBar').isVisible(),false);assert.deepEqual(errors,[]);
    }finally{await context.close();}
  }
});

test('a mismatched detail generation cannot become a comparison table',async()=>{
  const {context,page,errors}=await fixture(390,true);
  try{
    await page.locator('[data-compare="different"]').click();await page.locator('[data-compare="normal"]').click();await page.locator('#compareOpen').click();
    await page.waitForFunction(()=>document.getElementById('compareContent').textContent.includes('상세 자료 버전이 일치하지 않습니다'));
    assert.equal(await page.locator('.comparison-table').count(),0);
    assert.equal(await page.evaluate(key=>localStorage.getItem(key),RECORDS),stored);assert.deepEqual(errors,[]);
    await page.getByRole('button',{name:'비교 닫기',exact:true}).click();
  }finally{await context.close();}
});

test('home editorial links jump by topic and reopen from a saved tab',async()=>{
  const {context,page,errors}=await fixture(320);
  try{
    const hub=page.locator('#benefitAnalysis');
    await page.locator('#analysisShortcut a').click();
    assert.equal(new URL(page.url()).hash,'#benefitAnalysis');
    const topic=hub.getByRole('link',{name:'주거·전세',exact:true});
    await topic.click();
    assert.equal(new URL(page.url()).hash,'#analysis-housing');
    await page.waitForFunction(()=>document.getElementById('analysis-housing').getBoundingClientRect().top>=0
      && document.getElementById('analysis-housing').getBoundingClientRect().top<innerHeight);
    assert.equal(await hub.getByRole('heading',{level:3}).count(),5);
    assert.equal(await hub.locator('a[href^="guides/"]').count(),34);
    assert.equal(await hub.getByRole('navigation',{name:'제도 해설 분야'}).evaluate(el=>el.scrollWidth),await hub.getByRole('navigation',{name:'제도 해설 분야'}).evaluate(el=>el.clientWidth));
    await page.locator('[data-tab="saved"]').click();
    assert.equal(new URL(page.url()).hash,'');
    assert.equal(await hub.isVisible(),false);
    await page.goto(ORIGIN+'/supportpick/#analysis-housing');
    assert.equal(await hub.isVisible(),true);
    assert.equal(await page.locator('[data-tab="all"]').getAttribute('aria-current'),'page');
    assert.deepEqual(errors,[]);
  }finally{await context.close();}
});
