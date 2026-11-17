const test=require('node:test');
const assert=require('node:assert/strict');
const C=require('../core.js');
const now=new Date('2026-11-17T18:00:00+09:00');
const s={scope:'2026년 2학기 일반 신청',applicationStart:'2026-07-01T09:00:00+09:00',applicationEnd:'2026-11-17T18:00:00+09:00',followupLabel:'대출 실행',followupEnd:'2026-11-18T17:00:00+09:00',sourceUrl:'https://www.kosaf.go.kr/ko/tuition.do?pg=tuition01',reviewedAt:'2026-11-16T12:00:00+09:00',validUntil:'2026-11-30T12:00:00+09:00'};
const row={id:'GES000000100',periodKind:'fixed',endDate:'2026-11-17',verifiedSchedule:s};
test('same-day cutoff is inclusive and execution deadline does not extend application',()=>{
  assert.equal(C.periodState(row,new Date(+now-1)),'dated');
  assert.equal(C.periodState(row,now),'ended');
  assert.equal(C.status(row,now),'공식 안내상 해당 차수 신청 마감');
  assert.match(C.scheduleText(row,now),/대출 실행 마감 2026-11-18 17:00 KST/);
  assert.equal(C.periodState(row,new Date(+now+3600000)),'ended');
});
test('expired, future-reviewed, malformed and held schedule does not override source dates',()=>{
  for(const patch of [{sourceUrl:'https://www.kosaf.go.kr.evil.example/'},{sourceUrl:'https://x@www.kosaf.go.kr/'},{sourceUrl:'https://www.kosaf.go.kr:8443/'},{applicationEnd:'2026-11-17T18:00:00'},{applicationEnd:'2026-02-30T18:00:00+09:00'},{followupEnd:'2026-11-16T17:00:00+09:00'},{validUntil:'2026-12-31T00:00:00+09:00'}])assert.equal(C.scheduleInfo({...row,verifiedSchedule:{...s,...patch}},now),null);
  assert.equal(C.scheduleInfo(row,new Date(s.validUntil)),null);
  assert.equal(C.scheduleInfo(row,new Date(Date.parse(s.reviewedAt)-1)),null);
  assert.equal(C.scheduleInfo({...row,reviewRequired:true},now),null);
  assert.equal(C.periodState({...row,reviewRequired:true},now),'unknown');
  assert.equal(C.periodState(row,'2026-11-17'),'dated'); // A date alone cannot establish an hour.
});
test('deadline filter retains the instant, never reducing it to a date',()=>{
  const Original=global.Date;
  try{
    global.Date=class extends Original{constructor(...args){super(...(args.length?args:[+now]));}};
    const records=C.blank(),items=[{...row,title:'학자금',organization:'교육부',summary:'설명'}];
    assert.equal(C.filter(items,{periodState:'ended'},records).length,1);
    assert.equal(C.filter(items,{periodState:'dated'},records).length,0);
  }finally{global.Date=Original;}
});
