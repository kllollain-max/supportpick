/* Match published explanations to a specific source edition; no network or storage. */
(function(root){
  'use strict';
  function sourceKey(p){const s=p.sourceUpdatedAt||{};return JSON.stringify([p.id,p.title,p.organization,p.region,p.period,p.summary,typeof s==='object'?s.list||'':s,typeof s==='object'?s.detail||'':'']);}
  function blogURL(value){try{const u=new URL(value);return u.protocol==='https:'&&!u.username&&!u.password&&!u.port&&['blog.naver.com','m.blog.naver.com'].includes(u.hostname)&&/^\/bible_el\/\d+$/.test(u.pathname)&&!u.search&&!u.hash?u.href:'';}catch(e){return '';}}
  function differencesMatch(p,a){
    const actual=p.sourceDifferences||{},review=a.reviewedSourceDifferences||{};
    const keys=[...new Set([...(p.sourceConflicts||[]),...Object.keys(actual)])].sort();
    if(!keys.length)return Object.keys(review).length===0;
    // Only an explicitly reviewed classification-only difference can pass.
    // Eligibility, support amount, application period and other conflicts remain blocked.
    if(keys.length!==1||keys[0]!=='지원유형'||Object.keys(review).length!==1||!review['지원유형'])return false;
    const x=actual['지원유형'],y=review['지원유형'];
    return !!x&&typeof x.list==='string'&&typeof x.detail==='string'&&x.list===y.list&&x.detail===y.detail;
  }
  function find(p,registry,now=new Date()){
    if(!p||p.isSample||registry?.version!==1||!Array.isArray(registry.articles))return null;
    const year=Number(now.toLocaleDateString('sv-SE',{timeZone:'Asia/Seoul'}).slice(0,4));
    const rows=registry.articles.filter(a=>{
      if(!a||typeof a!=='object')return false;
      const verified=Date.parse(a.verifiedAt),published=Date.parse(a.publishedAt||a.publicationObservedAt),until=Date.parse(a.validUntil);
      return differencesMatch(p,a)&&a.status==='published'&&a.publicationVerified===true&&a.benefitId===p.id&&a.sourceKey===sourceKey(p)&&
        a.scope?.year===year&&a.scope?.region===p.region&&typeof a.scope?.round==='string'&&a.scope.round.trim()&&
        typeof a.title==='string'&&a.title.trim()&&a.title.length<=200&&blogURL(a.url)&&
        Number.isFinite(verified)&&Number.isFinite(published)&&Number.isFinite(until)&&published<=verified&&verified<=+now&&
        +now-verified<=30*86400000&&+now<until&&until<=verified+30*86400000;
    });
    // Never choose arbitrarily when multiple editions claim the same benefit.
    return rows.length===1?{...rows[0],url:blogURL(rows[0].url)}:null;
  }
  const api={sourceKey,blogURL,differencesMatch,find};
  if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.SupportPickEditorials=api;
})(typeof window!=='undefined'?window:globalThis);
