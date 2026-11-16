(function(){
  'use strict';
  const C=window.SupportPick,$=id=>document.getElementById(id),VIEW='supportpick:view:v1';
  const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  function explanation(p,detail=false){
    const a=window.SupportPickEditorials?.find(p,window.SUPPORTPICK_EDITORIALS);if(!a)return '';
    const link=`<a class="editorial-link" href="${esc(a.url)}" target="_blank" rel="noopener noreferrer">${esc(detail?'지원금픽 해설 보기':a.linkLabel||'신청방법 해설')} ↗</a>`;
    return detail?`<section class="detail-block editorial-block"><h3>지원금픽 해설</h3><p>대상 조건·준비 서류·신청 순서를 쉽게 풀어봤어요. 신청 전에는 위의 공식 안내를 확인하세요.</p><p>${esc(a.title)}</p>${a.scopeNote?`<p class="context-note">${esc(a.scopeNote)}</p>`:''}${link}</section>`:`<p class="editorial-note">${link}</p>`;
  }
  const initial={tab:'all',query:'',category:'',region:'',audience:'',supportType:'',age:'',household:'',periodState:'',includeUnknown:true,sort:'updated',scroll:0,limit:30};
  let view={...initial},snapshot={raw:null,data:C.blank()},writable=true,items=[],feedError='',toastTimer,detailFromList=false;
  const drafts=new Map(),comparison=new Set();let searchTimer,feedLoadError='';
  const shardCache=new Map();let detailRequest=0;
  try{snapshot=C.load(localStorage);}catch(e){writable=false;warn(e.message);}
  try{const saved=JSON.parse(sessionStorage.getItem(VIEW)||'null');if(saved&&typeof saved==='object')for(const key of Object.keys(initial))if(typeof saved[key]===typeof initial[key])view[key]=saved[key];}catch(e){}
  if(!['all','matched','saved','apps','guide'].includes(view.tab))view.tab='all';
  try{items=C.parseFeed(window.SUPPORTPICK_DATA);}catch(e){feedError=e.message;}
  const requestedTab=new URLSearchParams(location.search).get('tab');
  if(['all','matched','saved','apps','guide'].includes(requestedTab)){view.tab=requestedTab;remember();const params=new URLSearchParams(location.search);params.delete('tab');history.replaceState(null,'',location.pathname+(params.toString()?'?'+params.toString():'')+location.hash);}
  if(location.hash.startsWith('#benefit=')){try{const oldId=decodeURIComponent(location.hash.slice(9));if(items.some(x=>x.id===oldId)){location.replace('benefits/'+encodeURIComponent(oldId)+'/');return;}}catch(e){}}
  $('audience').innerHTML='<option value="">모든 대상</option>'+[...new Set(items.flatMap(p=>p.audience||[]))].sort().map(s=>`<option>${esc(s)}</option>`).join('');
  $('supportType').innerHTML='<option value="">모든 방식</option>'+[...new Set(items.flatMap(p=>p.supportTypes||[p.supportType]))].sort().map(s=>`<option>${esc(s)}</option>`).join('');
  $('prefCategory').innerHTML='<option value="">모든 분야</option>'+[...new Set([...C.CATEGORIES,...items.map(p=>p.category)])].map(s=>`<option>${esc(s)}</option>`).join('');
  function warn(message){$('storageWarning').textContent=message;$('storageWarning').hidden=false;}
  function toast(message){clearTimeout(toastTimer);$('toast').textContent=message;$('toast').hidden=false;toastTimer=setTimeout(()=>$('toast').hidden=true,4200);}
  function remember(){try{sessionStorage.setItem(VIEW,JSON.stringify(view));}catch(e){}}
  function persist(next){if(!writable)throw Error('기존 기록을 확인할 수 없어 변경을 중단했습니다.');snapshot=C.save(localStorage,snapshot.raw,next);return snapshot.data;}
  function change(update){try{persist(update(structuredClone(snapshot.data)));render();return true;}catch(e){toast(e.message);warn(e.message);return false;}}
  function koreanTime(value){const d=new Date(value);return Number.isFinite(+d)?new Intl.DateTimeFormat('ko-KR',{timeZone:'Asia/Seoul',month:'numeric',day:'numeric',hour:'2-digit',minute:'2-digit',hour12:false}).format(d):'시각 미확인';}
  function setTab(tab){view.tab=tab;view.scroll=0;view.limit=30;remember();if(location.hash.startsWith('#benefit='))history.replaceState(null,'',location.pathname+location.search);render();window.scrollTo({top:0,behavior:'auto'});}
  function categories(){const all=['전체',...new Set([...C.CATEGORIES,...items.map(x=>x.category)])];$('categories').innerHTML=all.map(x=>`<button class="chip" type="button" data-category="${esc(x==='전체'?'':x)}" aria-pressed="${(x==='전체'?'':x)===view.category}">${esc(x)}</button>`).join('');}
  function card(p){
    const saved=snapshot.data.saved.includes(p.id),tracked=C.own(snapshot.data.apps,p.id),reason=view.tab==='matched'?C.matchReasons(p,snapshot.data.prefs):null;
    if(p.reviewRequired===true)return `<article class="benefit-card is-linked"><div class="card-content"><span class="badge">내용 확인 필요</span><h3><a class="title-link card-detail-link" href="benefits/${encodeURIComponent(p.id)}/" data-detail="${esc(p.id)}">${esc(p.title)}</a></h3><p class="organization">${esc(p.organization)}</p><p class="card-summary">공식 최신 안내와 대조 중입니다. 이전 대상·금액을 현재 조건으로 표시하지 않습니다.</p><a href="benefits/${encodeURIComponent(p.id)}/">확인 사유·최신 공식 안내 보기 →</a></div><div class="card-actions"><button data-save="${esc(p.id)}" aria-pressed="${saved}">${saved?'★ 저장됨':'☆ 관심 저장'}</button><button data-track="${esc(p.id)}">${tracked?'신청 기록 보기':'신청 준비하기'}</button></div></article>`;
    return `<article class="benefit-card is-linked"><div class="card-content"><div class="card-top"><span class="category-badge">${esc(p.category)}</span><span class="badge">${esc(C.status(p))}</span></div><h3><a class="title-link card-detail-link" href="benefits/${encodeURIComponent(p.id)}/" data-detail="${esc(p.id)}">${esc(p.title)}</a></h3><p class="organization">${esc(p.organization)} · ${esc(p.regionBasis==='agency_jurisdiction'?'기관 지역 '+p.region:p.region)}</p><p class="card-summary">${esc(p.summary)}</p><dl class="card-meta"><dt>지원</dt><dd>${esc(p.supportType)}</dd><dt>기간</dt><dd>${esc(p.period||'공식 공고 확인')}</dd><dt>출처</dt><dd>${esc(p.source)} · ${esc(koreanTime(p.checkedAt))}</dd></dl><span class="card-open-hint" aria-hidden="true">상세 보기 →</span>${explanation(p)}${reason&&reason.length?`<p class="match-reason">${esc(reason.join(' · '))}</p>`:''}</div><div class="card-actions"><button type="button" data-compare="${esc(p.id)}" aria-pressed="${comparison.has(p.id)}">${comparison.has(p.id)?'✓ 비교 선택됨':'비교 선택'}</button><button data-save="${esc(p.id)}" aria-pressed="${saved}" class="${saved?'saved':''}">${saved?'★ 저장됨':'☆ 관심 저장'}</button><button data-track="${esc(p.id)}">${tracked?'신청 기록 보기':'신청 준비하기'}</button></div></article>`;
  }
  function empty(title,text,action='reset'){return `<div class="empty-state"><span class="empty-mark" aria-hidden="true">◎</span><h3>${esc(title)}</h3><p>${esc(text)}</p>${action==='preferences'?'<button class="primary" data-open-preferences>관심 조건 설정하기</button>':action==='all'?'<button class="quiet" data-show-all>전체 혜택 보기</button>':action==='reset'?'<button class="quiet" data-reset>검색·필터 초기화</button>':''}</div>`;}
  function render(){
    $('savedCount').textContent=snapshot.data.saved.length;$('appCount').textContent=Object.keys(snapshot.data.apps).length;
    document.querySelectorAll('[data-tab]').forEach(b=>{if(b.dataset.tab===view.tab)b.setAttribute('aria-current','page');else b.removeAttribute('aria-current');});
    const isDetail=location.hash.startsWith('#benefit=');
    if($('benefitAnalysis'))$('benefitAnalysis').hidden=isDetail||view.tab!=='all';
    if($('staticDiscovery'))$('staticDiscovery').hidden=isDetail||view.tab!=='all';
    $('detailSection').hidden=!isDetail;$('hero').hidden=isDetail||view.tab!=='all';$('browseSection').hidden=isDetail||view.tab==='guide';$('guideSection').hidden=isDetail||view.tab!=='guide';$('portals').hidden=isDetail;
    if(isDetail){renderDetail();return;}
    $('preferencesButton').hidden=view.tab==='apps';$('searchForm').hidden=view.tab==='apps';$('categories').hidden=view.tab==='apps';$('filterPanel').hidden=view.tab==='apps'||$('filterToggle').getAttribute('aria-expanded')!=='true';$('sort').closest('label').hidden=view.tab==='apps';
    $('query').value=view.query;$('region').value=view.region;$('audience').value=view.audience;$('supportType').value=view.supportType;$('sort').value=view.sort;for(const id of ['age','household','periodState'])$(id).value=view[id];$('includeUnknown').checked=view.includeUnknown;categories();
    const titles={all:'관심 있는 혜택을 찾아보세요',matched:'내 관심 조건에 맞는 혜택',saved:'다시 보고 싶은 혜택',apps:'내가 챙기는 신청 기록'};
    $('sectionTitle').textContent=titles[view.tab]||titles.all;
    $('matchNotice').hidden=view.tab!=='matched';
    const prefs=snapshot.data.prefs;
    $('matchNotice').textContent=`${prefs.region||'모든 지역'} · ${prefs.category||'모든 분야'}. 관심 조건이 비슷한 정보이며 실제 수급 자격을 판정하지 않습니다.`;
    $('dataNote').textContent=feedError||`${window.SUPPORTPICK_DATA.coverage} 수집 완료 ${koreanTime(window.SUPPORTPICK_DATA.collectionSucceededAt||window.SUPPORTPICK_DATA.updatedAt)} KST · 실제 신청 가능 여부는 원문 확인이 필요합니다.`;
    if(view.tab==='apps'){renderApps();return;}
    const rows=C.filter(items,view,snapshot.data);
    if(window.SUPPORTPICK_DATA.partial)$('dataNote').textContent=feedLoadError||'먼저 '+items.length+'건을 표시하고 전체 '+window.SUPPORTPICK_DATA.sourceCount.toLocaleString()+'건을 불러오는 중입니다. 검색 결과는 전체 목록 로딩 후 갱신됩니다.';
    $('resultCount').textContent=`${view.tab==='saved'?'저장한 혜택':'혜택 정보'} ${rows.length}건${window.SUPPORTPICK_DATA.partial?' · 전체 목록 로딩 중':''}`;
    if(feedError){$('list').innerHTML=empty('자료를 확인하지 못했어요',feedError,'none');return;}
    if(view.tab==='matched'&&!prefs.region&&!prefs.category){$('list').innerHTML=empty('어떤 혜택에 관심 있으세요?','관심 지역과 분야를 선택하면 관련 정보를 먼저 볼 수 있어요.','preferences');return;}
    let body=rows.slice(0,view.limit).map(card).join('');
    if(rows.length>view.limit)body+=`<div class="load-more" style="grid-column:1/-1;text-align:center;padding:16px"><button class="quiet" data-more>혜택 더 보기 (${view.limit.toLocaleString()} / ${rows.length.toLocaleString()})</button></div>`;
    if(view.tab==='saved'){
      const missing=window.SUPPORTPICK_DATA.partial?[]:snapshot.data.saved.filter(id=>!items.some(p=>p.id===id));
      body+=missing.map(id=>`<article class="benefit-card"><div class="card-content"><span class="badge">자료 미확인</span><h3>${esc(snapshot.data.apps[id]?.title||id)}</h3><p class="card-summary">현재 목록에서 이 혜택 자료를 찾지 못했습니다. 저장 기록은 보존됩니다.</p></div></article>`).join('');
      $('resultCount').textContent=`저장 ${snapshot.data.saved.length}건 · 현재 검색 결과 ${rows.length}건${missing.length?' · 자료 미확인 '+missing.length+'건':''}`;
    }
    $('list').innerHTML=body||empty(view.tab==='saved'?'저장한 혜택이 없어요':'조건에 맞는 정보가 없어요',view.tab==='saved'?'관심 혜택의 저장 버튼을 눌러 다시 확인하세요.':'검색 조건을 바꾸거나 공식 창구에서 더 많은 정보를 확인해보세요.',view.tab==='saved'?'all':'reset');
  }
  async function renderDetail(){
    const request=++detailRequest;
    let id='';try{id=decodeURIComponent(location.hash.slice(9));}catch(e){}
    let p=items.find(x=>x.id===id);
    if(!p&&window.SUPPORTPICK_DATA.partial&&C.idOK(id)){
      const direct=/^[A-Za-z0-9_-]{1,80}$/.test(id)?`<a class="quiet" href="benefits/${encodeURIComponent(id)}/">공유 상세페이지로 바로 확인 →</a>`:'';
      $('detailSection').innerHTML=(feedLoadError?`<p role="alert">${esc(feedLoadError)}</p><button class="quiet" type="button" data-feed-retry>전체 목록 다시 불러오기</button>`:'<p role="status">전체 목록에서 요청한 지원정보를 확인하고 있습니다.</p>')+direct;
      return;
    }
    if(!p){$('detailSection').innerHTML='<button class="quiet back-button" data-back>← 목록으로</button>'+empty('혜택 자료를 찾지 못했어요','목록으로 돌아가 공식 정보를 다시 확인하세요.','all');return;}
    if(p.reviewRequired===true){
      $('detailSection').innerHTML=`<button class="quiet back-button" data-back>← 목록으로 돌아가기</button><article class="detail-block"><h2 id="detailTitle">${esc(p.title)} · 내용 확인 필요</h2><p>이전 API의 대상·금액을 현재 조건으로 표시하지 않습니다. 확인 사유와 최신 공식 안내·관련 해설을 상세페이지에서 확인하세요.</p><a class="primary" href="benefits/${encodeURIComponent(p.id)}/">최신 확인 안내 보기 →</a></article>`;
      return;
    }
    if(p.detailShard){
      $('detailSection').innerHTML='<button class="quiet back-button" data-back>← 목록으로 돌아가기</button><p role="status">공식 상세자료를 불러오고 있어요.</p>';
      try{
        const base=window.SUPPORTPICK_DATA.detailBase;
        if(!/^details\/[A-Za-z0-9_-]{1,80}\/$/.test(base)||!/^\d{2}$/.test(p.detailShard))throw Error('상세 경로를 확인할 수 없습니다.');
        const url=base+p.detailShard+'.json';
        if(!shardCache.has(url)){
          if(shardCache.size>=3)shardCache.delete(shardCache.keys().next().value);
          shardCache.set(url,fetch(url,{cache:'force-cache'}).then(r=>{if(!r.ok)throw Error('상세 자료 조회에 실패했습니다.');return r.json();}).catch(e=>{shardCache.delete(url);throw e;}));
        }
        const payload=await shardCache.get(url);p=C.parseDetail(payload,p);
        if(request!==detailRequest||location.hash!=='#benefit='+encodeURIComponent(id))return;
      }catch(error){if(request!==detailRequest)return;$('detailSection').innerHTML='<button class="quiet back-button" data-back>← 목록으로 돌아가기</button>'+empty('상세 자료를 불러오지 못했어요',error.message,'none')+'<button class="quiet" data-detail-retry>다시 불러오기</button>';return;}
    }
    document.title=p.title+' | 지원금픽';
    const isSaved=snapshot.data.saved.includes(p.id);
    const fields=[['지원대상',p.target],['지원내용',p.support],['신청방법',p.method],['구비서류',p.documents],['문의처',p.contact]];
    $('detailSection').innerHTML=`<button class="quiet back-button" data-back>← 목록으로 돌아가기</button><article class="detail-header"><span class="category-badge">${esc(p.category)}</span> <span class="badge">${esc(C.status(p))}</span><h2 id="detailTitle" tabindex="-1">${esc(p.title)}</h2><p>${esc(p.organization)} · ${esc(p.regionBasis==='agency_jurisdiction'?'기관 지역 '+p.region:p.region)}</p><dl class="card-meta"><dt>신청기간</dt><dd>${esc(p.period)}</dd><dt>지원방식</dt><dd>${esc(p.supportType)}</dd><dt>자료조회</dt><dd>${esc(koreanTime(p.checkedAt))} KST</dd></dl><p class="context-note">아래 내용은 공식 API에서 조회한 안내입니다. 실제 접수 여부·금액·대상은 최신 공식 공고와 대조해 확인하세요.</p><div class="detail-actions"><a class="primary" href="${esc(p.officialUrl||'https://plus.gov.kr/')}" target="_blank" rel="noopener noreferrer">${p.officialUrl?'정부24 공식 안내 확인 ↗':'정부24에서 서비스명 검색 ↗'}</a><button class="quiet" data-save="${esc(p.id)}" aria-pressed="${isSaved}">${isSaved?'★ 저장됨':'☆ 관심 저장'}</button><button class="quiet" data-track="${esc(p.id)}">내 신청에 기록</button><button class="quiet" type="button" data-share-benefit data-share-id="${esc(p.id)}" data-share-title="${esc(p.title)}">↗ 이 지원금 공유</button></div></article>${explanation(p,true)}${fields.map(([title,value])=>`<section class="detail-block"><h3>${title}</h3><p class="source-text">${esc(value||'공식 안내 확인')}</p></section>`).join('')}${p.sourceDifferences&&Object.keys(p.sourceDifferences).length?'<section class="detail-block"><h3>목록·상세 표기 차이</h3><p class="context-note">공식 API의 목록과 상세 값이 다릅니다. 두 값을 함께 제공하며 실제 적용 기준은 원문에서 확인하세요.</p>'+Object.entries(p.sourceDifferences).map(([key,value])=>'<h4>'+esc(key)+'</h4><p class="source-text">목록: '+esc(value.list)+'\n\n상세: '+esc(value.detail)+'</p>').join('')+'</section>':''}<section class="detail-block"><h3>정보 출처</h3><p class="source-meta">${esc(p.source)} · 서비스 ID ${esc(p.id)}<br>출처 수정일 ${esc(typeof p.sourceUpdatedAt==='object'?'목록 '+(p.sourceUpdatedAt.list||'미제공')+' / 상세 '+(p.sourceUpdatedAt.detail||'미제공'):p.sourceUpdatedAt)} · 조회 ${esc(koreanTime(p.checkedAt))} KST<br>API 조회 성공과 실제 신청 가능 여부는 별개입니다.</p><a href="${esc(p.officialUrl||'https://plus.gov.kr/')}" target="_blank" rel="noopener noreferrer">${p.officialUrl?'공식 원문 다시 확인 ↗':'공식 링크 미제공 · 정부24에서 확인 ↗'}</a></section>`;
  }
  function drawComparison(){
    $('compareBar').hidden=comparison.size===0;
    $('compareCount').textContent='비교할 지원금 '+comparison.size+' / 3개 선택';
    $('compareOpen').disabled=comparison.size<2;
  }
  async function openComparison(){
    $('compareDialog').showModal();$('compareContent').textContent='공식 상세자료를 불러오는 중입니다.';
    try{
      if(window.SUPPORTPICK_DATA.partial)await window.SupportPickFeed.load();
      const selected=await Promise.all([...comparison].map(async id=>{
        const index=items.find(p=>p.id===id);if(!index)throw Error('비교할 자료를 찾지 못했습니다.');
        if(index.reviewRequired)throw Error(index.title+'은 내용 확인 중입니다. 공식 안내에서 확인하세요.');
        const base=window.SUPPORTPICK_DATA.detailBase;
        if(!/^details\/[A-Za-z0-9_-]{1,80}\/$/.test(base)||!/^\d{2}$/.test(index.detailShard))throw Error('상세자료 경로 확인 필요');
        const url=base+index.detailShard+'.json';
        if(!shardCache.has(url))shardCache.set(url,fetch(url,{cache:'force-cache'}).then(r=>{if(!r.ok)throw Error('상세자료 조회 실패');return r.json();}).catch(e=>{shardCache.delete(url);throw e;}));
        return C.parseDetail(await shardCache.get(url),index);
      }));
      const fields=[['운영기관','organization'],['지원대상','target'],['지원내용·금액','support'],['신청기간','period'],['신청방법','method'],['준비서류','documents'],['선정기준','selection'],['API 조회일','checkedAt']];
      let html='<div class="comparison-scroll" tabindex="0" role="region" aria-label="지원금 비교표"><table class="comparison-table"><caption>선택한 지원금의 공식 안내 비교</caption><thead><tr><th scope="col">확인 항목</th>'+selected.map(p=>'<th scope="col"><a href="benefits/'+encodeURIComponent(p.id)+'/">'+esc(p.title)+'</a></th>').join('')+'</tr></thead><tbody>';
      for(const [label,key] of fields)html+='<tr><th scope="row">'+label+'</th>'+selected.map(p=>'<td>'+esc(p[key]||'공식 공고 확인 필요')+'</td>').join('')+'</tr>';
      html+='<tr><th scope="row">중복 수혜</th>'+selected.map(()=>'<td>개별 공고의 중복지원·제외 조항 확인 필요</td>').join('')+'</tr><tr><th scope="row">공식 출처</th>'+selected.map(p=>'<td><a target="_blank" rel="noopener noreferrer" href="'+esc(C.safeURL(p.officialUrl))+'">공식 안내 ↗</a></td>').join('')+'</tr></tbody></table></div>';
      $('compareContent').innerHTML=html;
    }catch(error){$('compareContent').textContent=error.message+' 잠시 후 다시 시도하거나 개별 공식 안내를 확인하세요.';}
  }
  $('compareOpen').onclick=openComparison;
  $('compareClear').onclick=()=>{comparison.clear();drawComparison();render();};
  function retryFeed(){$('feedRetry').hidden=true;feedLoadError='';render();window.SupportPickFeed.load().catch(()=>{});}
  $('feedRetry').onclick=retryFeed;
  window.addEventListener('supportpick:feed',()=>{
    try{items=C.parseFeed(window.SUPPORTPICK_DATA);feedError='';feedLoadError='';$('feedRetry').hidden=true;
      $('audience').innerHTML='<option value="">모든 대상</option>'+[...new Set(items.flatMap(p=>p.audience||[]))].sort().map(x=>'<option>'+esc(x)+'</option>').join('');
      $('supportType').innerHTML='<option value="">모든 방식</option>'+[...new Set(items.flatMap(p=>p.supportTypes||[p.supportType]))].sort().map(x=>'<option>'+esc(x)+'</option>').join('');
      render();
    }catch(error){warn(error.message);}
  });
  window.addEventListener('supportpick:feed-error',e=>{feedLoadError=e.detail+' 현재 일부 목록만 표시합니다. 전체 검색 결과가 아닙니다.';$('dataNote').textContent=feedLoadError;$('feedRetry').hidden=false;if(location.hash.startsWith('#benefit='))renderDetail();});
  function renderApps(){
    const records=Object.entries(snapshot.data.apps).sort((a,b)=>b[1].updatedAt.localeCompare(a[1].updatedAt));
    $('resultCount').textContent=`신청 준비·진행 기록 ${records.length}건`;
    $('dataNote').textContent='직접 입력하는 개인 메모입니다. 공식 접수·선정 결과와 자동으로 연결되지 않습니다.';
    $('list').innerHTML=records.length?records.map(([id,a])=>{
      const d=drafts.get(id)||a,p=items.find(x=>x.id===id);
      return `<article class="tracker-card"><h3>${p?`<a class="title-link" href="benefits/${encodeURIComponent(id)}/" data-detail="${esc(id)}">${esc(a.title)}</a>`:esc(a.title)}</h3><p>마지막 저장 ${esc(koreanTime(a.updatedAt))} KST${p?'':' · 현재 자료 미확인'}</p><form data-app-form="${esc(id)}"><div class="tracker-grid"><label>신청 단계<select name="stage">${C.STAGES.map(s=>`<option${s===d.stage?' selected':''}>${s}</option>`).join('')}</select></label><label>나의 준비 메모<textarea name="note" maxlength="6000" placeholder="준비할 서류, 확인할 내용을 기록하세요">${esc(d.note)}</textarea></label></div><div class="tracker-actions"><button class="primary" type="submit" ${drafts.has(id)?'':'disabled'}>변경사항 저장</button><button class="quiet tracker-delete" type="button" data-delete-app="${esc(id)}" aria-label="${esc(a.title)} 신청 기록 삭제">기록 삭제</button></div><span class="draft-indicator" data-draft="${esc(id)}">${drafts.has(id)?'저장하지 않은 변경이 있어요':''}</span></form></article>`;
    }).join(''):empty('아직 신청 기록이 없어요','혜택의 ‘신청 준비하기’를 눌러 준비할 내용을 챙겨보세요.','all');
  }
  function openPreferences(){const p=snapshot.data.prefs;$('prefRegion').value=p.region;$('prefCategory').value=p.category;$('preferencesError').textContent='';$('preferencesDialog').showModal();}
  function openDetail(id){view.scroll=window.scrollY;remember();detailFromList=true;history.pushState({supportpickDetail:true},'', '#benefit='+encodeURIComponent(id));render();window.scrollTo(0,0);$('detailTitle')?.focus({preventScroll:true});}
  function back(){if(detailFromList){history.back();return;}history.replaceState(null,'',location.pathname+location.search);render();window.scrollTo(0,view.scroll||0);}
  function reset(){view={...view,query:'',category:'',region:'',supportType:'',audience:'',age:'',household:'',periodState:'',includeUnknown:true,sort:'updated',scroll:0,limit:30};remember();render();}
  document.addEventListener('click',e=>{
    const b=e.target.closest('button,a[data-detail]');if(!b)return;
    if(b.dataset.tab){document.title='지원금픽 · 한눈에 보는 생활혜택';setTab(b.dataset.tab);}
    if(b.hasAttribute('data-category')){view.category=b.dataset.category;view.limit=30;remember();render();}
    if(b.dataset.detail){view.scroll=window.scrollY;remember();if(b.tagName!=='A')location.assign('benefits/'+encodeURIComponent(b.dataset.detail)+'/');}
    if(b.hasAttribute('data-back'))back();
    if(b.hasAttribute('data-show-all'))setTab('all');
    if(b.hasAttribute('data-reset'))reset();
    if(b.hasAttribute('data-more')){view.limit+=30;remember();render();}
    if(b.hasAttribute('data-detail-retry'))renderDetail();
    if(b.hasAttribute('data-feed-retry'))retryFeed();
    if(b.hasAttribute('data-open-preferences'))openPreferences();
    if(b.hasAttribute('data-close-dialog'))b.closest('dialog').close();
    if(b.dataset.compare){const id=b.dataset.compare;if(comparison.has(id))comparison.delete(id);else if(comparison.size<3)comparison.add(id);else{toast('지원금은 최대 3개까지 비교할 수 있어요.');return;}drawComparison();render();}
    if(b.dataset.save){const id=b.dataset.save;if(change(s=>{s.saved=s.saved.includes(id)?s.saved.filter(x=>x!==id):[...s.saved,id];return s;}))toast(snapshot.data.saved.includes(id)?'관심 혜택에 저장했어요.':'관심 저장을 해제했어요.');}
    if(b.hasAttribute('data-delete-app')){const id=b.dataset.deleteApp,a=snapshot.data.apps[id];if(!a)return;if(!window.confirm('「'+a.title+'」 신청 기록을 삭제할까요?\n삭제 후에는 이 브라우저에서 복구할 수 없습니다.'))return;const apps={...snapshot.data.apps};delete apps[id];if(change(state=>({...state,apps}))){drafts.delete(id);render();toast('신청 기록을 삭제했어요.');}return;}
    if(b.dataset.track){const id=b.dataset.track,p=items.find(x=>x.id===id);if(!p)return;if(!C.own(snapshot.data.apps,id)&&!change(s=>{s.apps[id]={title:p.title,stage:'관심',note:'',updatedAt:new Date().toISOString()};return s;}))return;setTab('apps');toast('이곳에서 신청 준비 상황을 직접 기록하세요.');}
  });
  $('query').addEventListener('input',e=>{view.query=e.target.value;view.limit=30;remember();clearTimeout(searchTimer);searchTimer=setTimeout(render,160);});
  $('searchForm').addEventListener('submit',e=>{e.preventDefault();render();});
  for(const [id,key] of [['region','region'],['audience','audience'],['supportType','supportType'],['sort','sort'],['age','age'],['household','household'],['periodState','periodState']])$(id).addEventListener('change',e=>{view[key]=e.target.value;view.limit=30;remember();render();});
  $('includeUnknown').addEventListener('change',e=>{view.includeUnknown=e.target.checked;view.limit=30;remember();render();});
  $('filterToggle').onclick=()=>{const expanded=$('filterToggle').getAttribute('aria-expanded')!=='true';$('filterToggle').setAttribute('aria-expanded',String(expanded));$('filterPanel').hidden=!expanded;};
  $('resetFilters').onclick=reset;$('heroMatch').onclick=openPreferences;$('preferencesButton').onclick=openPreferences;
  $('preferencesForm').onsubmit=e=>{e.preventDefault();try{persist({...snapshot.data,prefs:{region:$('prefRegion').value,category:$('prefCategory').value}});$('preferencesDialog').close();setTab('matched');toast('관심 조건을 저장했어요.');}catch(error){$('preferencesError').textContent=error.message;}};
  document.addEventListener('input',e=>{const form=e.target.closest('[data-app-form]');if(!form)return;const id=form.dataset.appForm,a=snapshot.data.apps[id],changed=!!a&&(a.stage!==form.elements.stage.value||a.note!==form.elements.note.value);if(changed)drafts.set(id,{stage:form.elements.stage.value,note:form.elements.note.value});else drafts.delete(id);form.querySelector('[data-draft]').textContent=changed?'저장하지 않은 변경이 있어요':'';form.querySelector('[type=submit]').disabled=!changed;});
  document.addEventListener('submit',e=>{const form=e.target.closest('[data-app-form]');if(!form)return;e.preventDefault();const id=form.dataset.appForm,d={stage:form.elements.stage.value,note:form.elements.note.value};try{persist({...snapshot.data,apps:{...snapshot.data.apps,[id]:{...snapshot.data.apps[id],...d,updatedAt:new Date().toISOString()}}});drafts.delete(id);render();toast('신청 기록을 저장했어요.');}catch(error){toast(error.message);warn(error.message);}});
  $('recordsButton').onclick=()=>{$('recordsError').textContent='';$('recordsDialog').showModal();};
  function backupText(){return C.exportBackup(C.load(localStorage).data);}
  function restoreText(text){persist(C.merge(snapshot.data,C.importBackup(text)));render();$('recordsError').textContent='';toast('기존 기록을 보존하며 백업을 가져왔어요.');}
  $('showBackupText').onclick=()=>{try{$('backupText').value=backupText();$('backupText').focus();$('backupText').select();$('recordsError').textContent='';}catch(e){$('recordsError').textContent=e.message;}};
  $('importTextButton').onclick=()=>{try{restoreText($('backupText').value);}catch(e){$('recordsError').textContent=e.message;}};
  $('exportButton').onclick=()=>{try{const text=backupText();$('backupText').value=text;const blob=new Blob([text],{type:'application/json;charset=utf-8'});const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='supportpick-records-'+new Date().toISOString().slice(0,10)+'.json';document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),30000);toast('백업 다운로드를 요청했어요. 저장한 파일을 확인하세요.');}catch(e){$('recordsError').textContent=e.message;}};
  $('importInput').onchange=async e=>{const file=e.target.files[0];if(!file)return;try{if(file.size>2*1024*1024)throw Error('백업은 2MB 이하의 JSON 파일만 가져올 수 있습니다.');restoreText(await file.text());}catch(error){$('recordsError').textContent=error.message;}finally{e.target.value='';}};
  window.addEventListener('popstate',()=>{render();if(!location.hash.startsWith('#benefit=')){document.title='지원금픽 · 한눈에 보는 생활혜택';requestAnimationFrame(()=>window.scrollTo(0,view.scroll||0));}});
  window.addEventListener('hashchange',()=>render());
  window.addEventListener('storage',e=>{if(e.key!==C.KEY)return;if(drafts.size){warn('다른 탭에서 기록이 변경되었습니다. 입력 중인 메모를 보관한 뒤 새로고침하세요.');return;}try{snapshot=C.load(localStorage);render();toast('다른 탭에서 변경한 기록을 반영했어요.');}catch(error){writable=false;warn(error.message);}});
  window.addEventListener('pagehide',()=>{if(!location.hash){view.scroll=window.scrollY;remember();}});
  window.addEventListener('pageshow',e=>{if(e.persisted&&!drafts.size){try{snapshot=C.load(localStorage);render();}catch(error){writable=false;warn(error.message);}}});
  window.addEventListener('beforeunload',e=>{if(drafts.size){e.preventDefault();e.returnValue='';}});
  render();if(!location.hash)requestAnimationFrame(()=>window.scrollTo(0,view.scroll||0));
  if(!feedError)fetch('status.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('status');return r.json();}).catch(()=>({status:'unavailable'})).then(state=>{const message=C.health(window.SUPPORTPICK_DATA,state);$('feedWarning').textContent=message;$('feedWarning').hidden=!message;});
})();
