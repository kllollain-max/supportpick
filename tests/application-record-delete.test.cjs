/* Regression: application deletion must preserve other records and existing recovery. */
'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const C=require('../core.js');
const app=fs.readFileSync(require('node:path').join(__dirname,'../app.js'),'utf8');
function memory(){const m=new Map();return {getItem:k=>m.has(k)?m.get(k):null,setItem:(k,v)=>m.set(k,String(v)),removeItem:k=>m.delete(k)};}
const entry=(title,note)=>({title,note,stage:'관심',updatedAt:'2026-11-06T00:00:00Z'});
test('deleting one application preserves other records, favorites, and preferences',()=>{
 const storage=memory();let snapshot=C.load(storage);
 snapshot=C.save(storage,snapshot.raw,{...snapshot.data,saved:['KEEP'],prefs:{region:'강원',category:''},apps:{REMOVE:entry('삭제 대상','메모 A'),KEEP:entry('보존 대상','메모 B')}});
 const apps={...snapshot.data.apps};delete apps.REMOVE;
 const after=C.save(storage,snapshot.raw,{...snapshot.data,apps});
 assert.equal(C.own(after.data.apps,'REMOVE'),false);
 assert.equal(after.data.apps.KEEP.note,'메모 B');
 assert.deepEqual(after.data.saved,['KEEP']);
 assert.equal(after.data.prefs.region,'강원');
 assert.equal(C.load(storage).data.apps.KEEP.title,'보존 대상');
 assert.equal(JSON.parse(storage.getItem(C.RECOVERY)).apps.REMOVE.title,'삭제 대상');
});
test('stale tab cannot overwrite records after deletion',()=>{
 const storage=memory();let old=C.load(storage);
 let current=C.save(storage,old.raw,{...old.data,apps:{REMOVE:entry('삭제 대상','')}});
 assert.throws(()=>C.save(storage,old.raw,{...old.data,apps:{OTHER:entry('오래된 탭','')}}),/다른 탭/);
 const apps={...current.data.apps};delete apps.REMOVE;
 current=C.save(storage,current.raw,{...current.data,apps});
 assert.deepEqual(Object.keys(C.load(storage).data.apps),[]);
});
test('application UI includes a confirmation-gated delete control and dirty-only save',()=>{
 assert.match(app,/data-delete-app/);
 assert.match(app,/window\.confirm\(/);
 assert.match(app,/delete apps\[id\]/);
 assert.match(app,/disabled=!changed/);
 assert.match(app,/drafts\.delete\(id\)/);
});
