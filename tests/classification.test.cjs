const {test}=require('node:test');
const assert=require('node:assert/strict');
const C=require('../core.js');

test('classification differences retain both attributed values without changing source or filters',()=>{
  const p={supportType:'현금',supportTypes:['현금'],sourceConflicts:['지원유형'],sourceDifferences:{지원유형:{list:'현금||서비스(돌봄)',detail:'현금'}}};
  const before=JSON.stringify(p),c=C.supportClassification(p);
  assert.equal(c.different,true);assert.equal(c.list,'현금 · 서비스(돌봄)');assert.equal(c.detail,'현금');
  assert.match(c.text,/분류 차이/);assert.equal(JSON.stringify(p),before);
});
test('a flagged missing pair stays qualified, while held rows never expose old classifications',()=>{
  assert.deepEqual(C.supportClassification({supportType:'현금',sourceConflicts:['지원유형']}),{text:'목록·상세 분류 차이 · 원문 확인',different:true,list:'미제공',detail:'미제공'});
  const p={supportType:'과거 현금 분류',reviewRequired:true,sourceDifferences:{지원유형:{list:'이전 목록',detail:'이전 상세'}}};
  assert.deepEqual(C.supportClassification(p),{text:'내용 확인 필요',different:false,list:'',detail:''});
});
test('unflagged normal classifications are unchanged and malformed pair values are not coerced to text',()=>{
  assert.equal(C.supportClassification({supportType:'이용권'}).text,'이용권');
  const c=C.supportClassification({sourceDifferences:{지원유형:{list:{bad:'value'},detail:null}}});
  assert.equal(c.list,'미제공');assert.equal(c.detail,'미제공');
});
