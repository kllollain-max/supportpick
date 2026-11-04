const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const source = fs.readFileSync(require.resolve('../sw.js'),'utf8');
function worker(network = async()=>new Response('latest')) {
  const events={}, deleted=[], added=[];
  const cache={addAll:async urls=>added.push(...urls),match:async()=>new Response('<h1>offline notice</h1>')};
  const self={registration:{scope:'https://kllollain-max.github.io/supportpick/'},addEventListener:(name,callback)=>events[name]=callback,skipWaiting:async()=>{},clients:{claim:async()=>{}}};
  vm.runInNewContext(source,{self,URL,Response,fetch:network,caches:{open:async()=>cache,keys:async()=>['careerpick-cache','supportpick-shell-old','supportpick-shell-__SHELL_HASH__','another-app'],delete:async key=>deleted.push(key)}});
  async function lifecycle(name) { let pending;events[name]({waitUntil:promise=>pending=promise});await pending; }
  async function request(url,mode='navigate',method='GET') {let response;events.fetch({request:{url,mode,method},respondWith:promise=>response=promise});return response;}
  return {events,deleted,added,lifecycle,request};
}
test('offline pre-cache contains only generic notice and own icons',async()=>{
  const w=worker();await w.lifecycle('install');
  assert.deepEqual(w.added.map(url=>url.split('/').at(-1)),['offline.html','app-icon-192.png','app-icon-512.png']);
});
test('activation cannot delete CareerPick or other applications caches',async()=>{
  const w=worker();await w.lifecycle('activate');assert.deepEqual(w.deleted,['supportpick-shell-old']);
});
test('online navigation preserves live response including HTTP errors',async()=>{
  const w=worker(async()=>new Response('missing',{status:404}));
  const response=await w.request('https://kllollain-max.github.io/supportpick/benefits/123/');
  assert.equal(response.status,404);assert.equal(await response.text(),'missing');
});
test('offline navigation is a non-indexable 503 notice, never cached benefit facts',async()=>{
  const w=worker(async()=>{throw Error('offline');});
  const response=await w.request('https://kllollain-max.github.io/supportpick/benefits/123/');
  assert.equal(response.status,503);assert.equal(response.headers.get('X-Robots-Tag'),'noindex');
  assert.equal(response.headers.get('Cache-Control'),'no-store');assert.match(await response.text(),/offline notice/);
});
test('JSON, foreign projects and mutations bypass the worker',async()=>{
  let requests=0;const w=worker(async()=>{requests++;return new Response('bad');});
  assert.equal(await w.request('https://kllollain-max.github.io/supportpick/data.json','cors'),undefined);
  assert.equal(await w.request('https://kllollain-max.github.io/careerpick/'),undefined);
  assert.equal(await w.request('https://kllollain-max.github.io/supportpick/','navigate','POST'),undefined);
  assert.equal(requests,0);
});
