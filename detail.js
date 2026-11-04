/* Individual static documents share the existing isolated, verified record store. */
(function(){
  'use strict';
  const C=window.SupportPick, node=document.getElementById('benefit-record');
  if(!C||!node)return;
  let row;try{row=JSON.parse(node.textContent);}catch(e){return;}
  if(!C.idOK(row.id)||typeof row.title!=='string'||row.base!=='../../')return;
  const saveButton=document.querySelector('[data-save]'),trackButton=document.querySelector('[data-track]');
  const warning=document.getElementById('record-warning');
  let snapshot,writable=false;
  function fail(error){warning.textContent=error.message||'기록 저장을 확인하지 못했습니다.';warning.hidden=false;}
  function draw(){saveButton.setAttribute('aria-pressed',String(snapshot.data.saved.includes(row.id)));saveButton.textContent=snapshot.data.saved.includes(row.id)?'★ 저장됨':'☆ 관심 저장';}
  try{snapshot=C.load(localStorage);writable=true;saveButton.disabled=false;trackButton.disabled=false;draw();}catch(error){fail(error);}
  function change(mutator){
    if(!writable)return false;
    try{const next=mutator(structuredClone(snapshot.data));snapshot=C.save(localStorage,snapshot.raw,next);draw();warning.hidden=true;return true;}catch(error){fail(error);return false;}
  }
  saveButton.addEventListener('click',()=>{if(change(s=>{s.saved=s.saved.includes(row.id)?s.saved.filter(x=>x!==row.id):[...s.saved,row.id];return s;}))document.getElementById('record-message').textContent=snapshot.data.saved.includes(row.id)?'관심 혜택에 저장했습니다.':'관심 저장을 해제했습니다.';});
  trackButton.addEventListener('click',()=>{
    // Verify the current store even when this item was already tracked.
    try{const latest=C.load(localStorage);if(latest.raw!==snapshot.raw)throw Error('다른 탭에서 기록이 변경되었습니다. 새로고침 후 다시 시도하세요.');}catch(error){fail(error);return;}
    if(!C.own(snapshot.data.apps,row.id)&&!change(s=>{s.apps[row.id]={title:row.title.slice(0,300),stage:'관심',note:'',updatedAt:new Date().toISOString()};return s;}))return;
    location.assign(row.base+'?tab=apps');
  });
  window.addEventListener('storage',e=>{if(e.key!==C.KEY)return;try{snapshot=C.load(localStorage);draw();}catch(error){writable=false;saveButton.disabled=true;trackButton.disabled=true;fail(error);}});
  const message=document.createElement('p');message.id='record-message';message.setAttribute('role','status');message.className='context-note';saveButton.parentElement.after(message);
  if(row.periodKind)document.getElementById('period-status').textContent=C.status(row);
  const age=Date.now()-Date.parse(row.checkedAt);
  if(!Number.isFinite(age)||age>30*3600000){const banner=document.getElementById('freshness-warning');banner.textContent='자료 조회 후 시간이 지났습니다. 현재 접수·변경 사항은 공식 안내에서 확인하세요.';banner.hidden=false;}
  for(const block of document.querySelectorAll('[data-blog-until]'))if(!(Date.now()<Date.parse(block.dataset.blogUntil)))block.hidden=true;
})();
