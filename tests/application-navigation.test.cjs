const {test}=require('node:test');const assert=require('node:assert/strict');const C=require('../core.js');
const now=new Date('2026-11-05T12:00:00+09:00');
const fixed=(id,start,end,extra={})=>({id,title:id,organization:'기관',summary:'청년 지원',category:'생활안정',region:'서울',regionBasis:'agency_jurisdiction',supportType:'현금',applicationPeriodKind:'fixed',applicationPeriods:[{start,end}],...extra});
test('KST deadline, exact time, upcoming and ambiguous remain distinct',()=>{
 const row=fixed('a','2026-11-01','2026-11-05');
 assert.equal(C.applicationState(row,new Date('2026-11-05T14:59:59Z')),'접수 중');
 assert.equal(C.applicationState(row,new Date('2026-11-05T15:00:00Z')),'접수 종료');
 assert.equal(C.applicationState(fixed('b','2026-11-06','2026-11-07'),now),'접수 예정');
 assert.equal(C.applicationState({...row,applicationPeriods:[{start:'2026-11-01',end:'2026-11-05',endAt:'2026-11-05T11:00:00+09:00'}]},now),'접수 종료');
 assert.equal(C.applicationState({endDate:'2026-12-01'},now),'확인 필요');
 assert.equal(C.applicationState({...row,applicationPeriods:[{start:'2026-02-30',end:'2026-03-01'}]},now),'확인 필요');
});
test('seven days inclusive, not eight; multi-round filters compose with query/category and saved',()=>{
 const rows=[fixed('seven','2026-11-01','2026-11-12'),fixed('eight','2026-11-01','2026-11-13'),fixed('closed','2026-10-01','2026-11-04'),{...fixed('unknown','2026-10-01','2026-11-04'),applicationPeriodKind:'needs_check'}];
 const r={...C.blank(),saved:['seven','eight']};
 assert.deepEqual(C.filter(rows,{applicationStatus:'soon',query:'청년',category:'생활안정',tab:'saved',now},r).map(x=>x.id),['seven']);
 assert.deepEqual(C.filter(rows,{applicationStatus:'needs_check',now},r).map(x=>x.id),['unknown']);
 assert.equal(C.filter(rows,{applicationStatus:'not_closed',now},r).length,3);
 const multi={...rows[2],applicationPeriods:[...rows[2].applicationPeriods,{start:'2026-11-05',end:'2026-11-07'}]};
 assert.equal(C.applicationState(multi,now),'접수 중');assert.equal(C.closingSoon(multi,now),true);
});
test('agency mismatch and uncertain conditions cannot reject; explicit residential conditions can narrow exploration',()=>{
 const agency=fixed('a','2026-11-01','2026-12-01');
 assert.ok(C.matchReasons(agency,{region:'강원',category:''}));
 const local={...agency,eligibilityRegionStatus:'explicit',eligibilityRegions:[{scope:'local',regions:['강원'],cities:['춘천시'],basis:'residence',evidence:'강원 춘천 거주'}]};
 assert.equal(C.matchReasons(local,{region:'경기',category:''}),null);
 assert.equal(C.matchReasons(local,{region:'강원',city:'원주시',category:''}),null);
 assert.ok(C.matchReasons(local,{region:'강원',city:'춘천시',category:'',targetGroup:'학생'}).some(x=>x.includes('미확정')));
 assert.ok(C.matchReasons({...local,eligibilityRegionStatus:'needs_check'},{region:'경기',category:''}));
});
test('old backup unchanged; optional city/target survive validation and merging without touching notes',()=>{
 const old=C.blank();assert.deepEqual(C.importBackup(C.exportBackup(old)),old);
 const current={...old,saved:['a'],prefs:{region:'강원',category:'',city:'춘천시',targetGroup:'학생'},apps:{a:{title:'a',note:'준비 메모',stage:'관심',updatedAt:'2026-11-05T00:00:00Z'}}};
 const result=C.merge(current,{...old,saved:['b']});
 assert.deepEqual(result.prefs,current.prefs);assert.equal(result.apps.a.note,'준비 메모');assert.deepEqual(result.saved,['a','b']);
 assert.throws(()=>C.validate({...old,prefs:{...old.prefs,city:'<script>'}}));
});
test('deadline sort uses the next preserved round; matched default favors explicit target evidence',()=>{
 const multi={...fixed('multi','2026-10-01','2026-10-02'),applicationPeriods:[{start:'2026-10-01',end:'2026-10-02'},{start:'2026-11-01',end:'2026-11-06'}],targetGroups:[{label:'학생',evidence:'재학생'}]};
 const later=fixed('later','2026-11-01','2026-11-10',{sourceUpdatedAt:'20261105'});
 assert.deepEqual(C.filter([later,multi],{sort:'deadline',now},C.blank()).map(x=>x.id),['multi','later']);
 const records={...C.blank(),prefs:{region:'',category:'',targetGroup:'학생'}};
 assert.deepEqual(C.filter([later,multi],{sort:'updated',tab:'matched',now},records).map(x=>x.id),['multi','later']);
 assert.equal(C.filter([later,multi],{tab:'matched',now},records).length,2);
});
