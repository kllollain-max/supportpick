const { test } = require('node:test');
const assert = require('node:assert/strict');
const { HOME, shareData, installSteps, createActions } = require('../app-features.js');
function fixture(nav = {}, standalone) {
  const calls = [];
  const ui = Object.fromEntries(['share','copied','manualCopy','install','requested','installed'].map(name => [name, value => calls.push({ name, value })]));
  return { calls, actions: createActions(nav, ui, standalone) };
}
test('site sharing excludes personal query/hash and benefit identity', () => {
  assert.equal(shareData({site:true,id:'test',canonical:HOME+'?tab=apps#private'}).url, HOME);
});
test('detail sharing uses safe stable URL and strips query/hash', () => {
  assert.deepEqual(shareData({id:'gov24:123',title:'월세지원'}), {
    title:'월세지원 - 지원금픽',text:'지원대상·신청방법과 최신 공식 안내를 확인하세요.',url:HOME+'benefits/gov24%3A123/'
  });
  assert.equal(shareData({canonical:HOME+'benefits/gov24%3A123/?private=1#note'}).url,HOME+'benefits/gov24%3A123/');
});
test('invalid or unrelated canonical cannot become a shared link', () => {
  for(const canonical of ['javascript:alert(1)','https://evil.test/supportpick/benefits/123/',HOME+'benefits/123/extra/',HOME+'benefits/%2F/',HOME+'benefits/__proto__/','%bad']) {
    assert.equal(shareData({canonical}).url,HOME,canonical);
  }
  assert.equal(shareData({id:'../careerpick'}).url,HOME);
});
test('native share runs in initiating call and does not open fallback on success', async () => {
  let called = false;
  const {actions,calls}=fixture({share:data=>{called=true;assert.equal(data.url,HOME);return Promise.resolve();}});
  const pending=actions.share(shareData()); assert.equal(called,true); await pending; assert.deepEqual(calls,[]);
});
test('cancelled native sharing has no copy or fallback side effect', async () => {
  const {actions,calls}=fixture({share:async()=>{throw {name:'AbortError'};}});
  await actions.share(shareData()); assert.deepEqual(calls,[]);
});
test('unsupported/blocked share opens manual options', async () => {
  for(const nav of [{},{share:async()=>{throw {name:'NotAllowedError'};}}]) {
    const {actions,calls}=fixture(nav); await actions.share(shareData()); assert.equal(calls[0].name,'share');
  }
});
test('copy reports success only after the clipboard write succeeds', async () => {
  const {actions,calls}=fixture({clipboard:{writeText:async text=>assert.equal(text,HOME)}});
  assert.equal(await actions.copy(shareData()),true); assert.equal(calls[0].name,'copied');
});
test('denied/unavailable clipboard selects manual copying, never false success', async () => {
  for(const nav of [{},{clipboard:{writeText:async()=>{throw Error('denied');}}}]) {
    const {actions,calls}=fixture(nav); assert.equal(await actions.copy(shareData()),false); assert.equal(calls[0].name,'manualCopy');
  }
});
test('installation guidance covers iPhone, iPad desktop UA, Android and in-app browsers', () => {
  assert.match(installSteps({userAgent:'iPhone Safari'}).join(' '),/Safari.*공유/);
  assert.match(installSteps({userAgent:'Macintosh Safari',maxTouchPoints:5}).join(' '),/Safari.*공유/);
  assert.match(installSteps({userAgent:'Android Chrome'}).join(' '),/앱 설치/);
  assert.match(installSteps({userAgent:'iPhone KAKAOTALK'}).join(' '),/브라우저로 열기.*Safari/);
  assert.match(installSteps({userAgent:'Android NAVER(inapp)'}).join(' '),/브라우저로 열기/);
});
test('retained install prompt is invoked once and acceptance is not reported as installed', async () => {
  const {actions,calls}=fixture(); let prompted=0, prevented=0;
  actions.capture({preventDefault(){prevented++;},prompt(){prompted++;return Promise.resolve();},userChoice:Promise.resolve({outcome:'accepted'})});
  const pending=actions.install(); assert.equal(prompted,1); await pending;
  assert.equal(prevented,1); assert.deepEqual(calls.map(x=>x.name),['requested']);
  await actions.install(); assert.equal(prompted,1); assert.equal(calls.at(-1).name,'install');
});
test('dismissal is quiet and failed install gives manual guidance', async () => {
  for(const fails of [false,true]) {
    const {actions,calls}=fixture();
    actions.capture({preventDefault(){},prompt(){if(fails)throw Error('blocked');},userChoice:Promise.resolve({outcome:'dismissed'})});
    await actions.install(); assert.deepEqual(calls.map(x=>x.name),fails?['install']:[]);
  }
});
test('installed or standalone app never prompts again', async () => {
  const {actions,calls}=fixture();actions.installed();await actions.install();assert.deepEqual(calls.map(x=>x.name),['installed','installed']);
  const f=fixture({},()=>true);await f.actions.install();assert.equal(f.calls[0].name,'installed');
});
