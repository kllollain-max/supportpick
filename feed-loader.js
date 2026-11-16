/* Paint a small verified first page, then load the immutable complete edition. */
(function(){
  'use strict';
  let pending;
  function load(){
    if(!window.SUPPORTPICK_DATA.partial)return Promise.resolve();
    if(pending)return pending;
    const before=window.SUPPORTPICK_DATA;
    if(!/^catalog\/[a-f0-9]{64}\.json$/.test(before.catalogUrl||''))return Promise.reject(Error('전체 목록 경로를 확인할 수 없습니다.'));
    pending=fetch(before.catalogUrl,{cache:'force-cache'}).then(r=>{
      if(!r.ok)throw Error('전체 목록을 불러오지 못했습니다.');
      return r.json();
    }).then(feed=>{
      if(feed.generation!==before.generation||feed.items?.length!==before.sourceCount)throw Error('목록 버전이 다릅니다. 새로고침 후 다시 확인하세요.');
      window.SupportPick.parseFeed(feed);
      window.SUPPORTPICK_DATA=feed;
      window.dispatchEvent(new CustomEvent('supportpick:feed'));
    }).catch(error=>{
      pending=null;
      window.dispatchEvent(new CustomEvent('supportpick:feed-error',{detail:error.message}));
      throw error;
    });
    return pending;
  }
  window.SupportPickFeed={load};
  window.addEventListener('DOMContentLoaded',()=>setTimeout(()=>load().catch(()=>{}),0),{once:true});
})();
