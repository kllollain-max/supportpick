const test=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
const C=require('../core.js');
const a={id:'A',title:'주택바우처 안내',organization:'기관',summary:'지원',category:'주거',region:'강원',audience:[],supportType:'현금',ageMin:19,ageMax:39,households:['1인가구'],periodKind:'ongoing'};
test('age and household filters retain unknowns only by explicit option',()=>{
 const rows=[a,{...a,id:'B',ageMin:null,ageMax:null,households:[]}];
 assert.equal(C.filter(rows,{age:'39',household:'1인가구'},C.blank()).length,2);
 assert.equal(C.filter(rows,{age:'39',household:'1인가구',includeUnknown:false},C.blank()).length,1);
 assert.equal(C.filter(rows,{age:'40',includeUnknown:false},C.blank()).length,0);
 assert.equal(C.filter(rows,{household:'다자녀가구',includeUnknown:false},C.blank()).length,0);
});
test('period state uses KST and never means verified open',()=>{
 assert.equal(C.periodState({...a,endDate:'2026-11-16'},new Date('2026-11-16T15:00:00Z')),'ended');
 assert.equal(C.periodState({...a,periodKind:'fixed',endDate:'2026-11-17'},new Date('2026-11-16T15:00:00Z')),'dated');
 assert.equal(C.periodState({...a,periodKind:'fixed',endDate:'2026-02-31'}),'unknown');
});
test('indexed filtering has the same AND semantics without modifying source order',()=>{
 const rows=[{...a,id:'B',title:'다른 안내'},a],before=JSON.stringify(rows);
 assert.equal(C.filter(rows,{query:'주택바우처 기관',sort:'title'},C.blank())[0].id,'A');
 assert.equal(C.filter(rows,{query:'주거 없는말',sort:'title'},C.blank()).length,0);
 assert.doesNotThrow(()=>C.filter(rows,{sort:'__proto__'},C.blank()));
 assert.equal(JSON.stringify(rows),before);
});
function loader(fetch){
 const before={schemaVersion:1,generation:'g1',partial:true,catalogUrl:'catalog/'+'a'.repeat(64)+'.json',sourceCount:2,items:[]};
 const events=[],window={SUPPORTPICK_DATA:before,SupportPick:{parseFeed(feed){if(feed.invalid)throw Error('invalid');return feed.items;}},dispatchEvent(e){events.push(e)},addEventListener(){}};
 const context={window,fetch,CustomEvent:class {constructor(type,options={}){this.type=type;this.detail=options.detail;}},setTimeout};
 vm.runInNewContext(fs.readFileSync('feed-loader.js','utf8'),context);return {window,events,before};
}
test('progressive loader coalesces loads and checks generation before replacing bootstrap',async()=>{
 let calls=0;const l=loader(async()=>{calls++;return {ok:true,json:async()=>({generation:'g1',items:[{},{}]})}});
 await Promise.all([l.window.SupportPickFeed.load(),l.window.SupportPickFeed.load()]);
 assert.equal(calls,1);assert.equal(l.window.SUPPORTPICK_DATA.partial,undefined);assert.equal(l.events[0].type,'supportpick:feed');
});
test('a failed load preserves bootstrap and retry can recover',async()=>{
 let calls=0;const l=loader(async()=>({ok:true,json:async()=>({generation:++calls===1?'wrong':'g1',items:[{},{}]})}));
 await assert.rejects(l.window.SupportPickFeed.load());assert.equal(l.window.SUPPORTPICK_DATA,l.before);
 assert.equal(l.events[0].type,'supportpick:feed-error');
 await l.window.SupportPickFeed.load();assert.equal(l.window.SUPPORTPICK_DATA.generation,'g1');
});
