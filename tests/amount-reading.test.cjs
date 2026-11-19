const {test}=require('node:test');
const assert=require('node:assert/strict');
const C=require('../core.js');
test('amount comma candidates are warnings without numeric conversion or source changes',()=>{
  for(const [support,expected] of [['9,00만원 / 5,00만원 / 1,00만원',['9,00','5,00','1,00']],['19,2500원 / 10,00만원',['19,2500','10,00']],['1,000원 1,500만원 15,000,000원 1.5억원 30만원',[]],['2026,11,19 신청 1,2명',[]],[null,[]]]){
    const p={support},before=JSON.stringify(p);assert.deepEqual(C.malformedAmounts(p),expected);assert.equal(JSON.stringify(p),before);
  }
});
test('held amounts never appear through the warning helper',()=>{
  assert.deepEqual(C.malformedAmounts({support:'9,00만원',reviewRequired:true}),[]);
});
