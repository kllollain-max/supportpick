(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else api.init(root, document);
})(typeof window === 'object' ? window : null, function () {
  'use strict';
  const HOME = 'https://kllollain-max.github.io/supportpick/';
  const validId = id => /^[A-Za-z0-9:_-]{1,100}$/.test(id || '') && !['__proto__', 'constructor', 'prototype'].includes(id);
  function shareData({ canonical, id, title, site = false } = {}) {
    let url = HOME;
    if (!site && validId(id)) url += 'benefits/' + encodeURIComponent(id) + '/';
    else if (!site && canonical) {
      try {
        const u = new URL(canonical);
        const part = u.pathname.slice('/supportpick/benefits/'.length).replace(/\/$/, '');
        if (u.origin === new URL(HOME).origin && u.pathname.startsWith('/supportpick/benefits/') && validId(decodeURIComponent(part))) {
          url += 'benefits/' + encodeURIComponent(decodeURIComponent(part)) + '/';
        }
      } catch (_) { /* Share the public homepage when a canonical is invalid. */ }
    }
    return { title: site || url === HOME ? '지원금픽 · 한눈에 보는 생활혜택' : String(title || '지원금 안내').slice(0, 300) + ' - 지원금픽',
      text: url === HOME ? '정부지원금과 생활혜택을 공식 출처로 확인하세요.' : '지원대상·신청방법과 최신 공식 안내를 확인하세요.', url };
  }
  function installSteps(nav) {
    const ua = nav.userAgent || '';
    const ios = /iPhone|iPad|iPod/i.test(ua) || (/Macintosh/i.test(ua) && nav.maxTouchPoints > 1);
    const inApp = /KAKAOTALK|NAVER\(|FBAN|FBAV|Instagram|Line\/|; wv\)/i.test(ua);
    if (inApp) return ['앱 안의 메뉴(⋯)에서 브라우저로 열기를 선택하세요.', ios ? 'Safari에서 공유(□↑) → 홈 화면에 추가 → 추가를 누르세요.' : 'Chrome 또는 삼성 인터넷에서 메뉴 → 앱 설치 또는 홈 화면에 추가를 선택하세요.'];
    if (ios) return ['Safari에서 이 사이트를 여세요.', '공유 버튼(□↑) → 홈 화면에 추가를 선택하세요.', '이름을 확인하고 추가를 누르세요.'];
    if (/Android/i.test(ua)) return ['Chrome의 오른쪽 위 메뉴(⋮) 또는 삼성 인터넷의 메뉴(≡)를 여세요.', '앱 설치 또는 홈 화면에 추가를 선택하고 확인하세요.'];
    return ['Chrome·Edge의 주소창 설치 아이콘 또는 메뉴의 앱 설치를 선택하세요.', '휴대폰에서는 Safari·Chrome·삼성 인터넷으로 열어 홈 화면에 추가할 수 있어요.'];
  }
  function createActions(nav, ui, isStandalone = () => false) {
    let promptEvent = null, installed = false, prompting = false;
    return {
      capture(event) { event.preventDefault(); promptEvent = event; },
      installed() { installed = true; promptEvent = null; ui.installed(); },
      async share(data) {
        if (nav.share) {
          try { await nav.share(data); return; }
          catch (error) { if (error && error.name === 'AbortError') return; }
        }
        ui.share(data);
      },
      async copy(data) {
        try {
          if (!nav.clipboard || !nav.clipboard.writeText) throw Error('clipboard_unavailable');
          await nav.clipboard.writeText(data.url);
          ui.copied();
          return true;
        } catch (_) { ui.manualCopy(); return false; }
      },
      async install() {
        if (installed || isStandalone()) { ui.installed(); return; }
        if (prompting) return;
        if (!promptEvent) { ui.install(installSteps(nav)); return; }
        const event = promptEvent;
        promptEvent = null; prompting = true;
        try {
          await event.prompt();
          const choice = await event.userChoice;
          if (choice && choice.outcome === 'accepted' && !installed) ui.requested();
        } catch (_) { ui.install(installSteps(nav)); }
        finally { prompting = false; }
      }
    };
  }
  function init(win, doc) {
    const scriptUrl = doc.currentScript && doc.currentScript.src;
    const standalone = win.matchMedia('(display-mode: standalone)');
    const isStandalone = () => standalone.matches || win.navigator.standalone === true;
    let dialog, message, input, previousFocus;
    function el(tag, text) { const node = doc.createElement(tag); if (text) node.textContent = text; return node; }
    function close() { dialog.close(); }
    function open(title) {
      if (!dialog) {
        dialog = el('dialog'); dialog.id = 'featureDialog'; dialog.className = 'feature-dialog';
        dialog.setAttribute('aria-labelledby', 'featureTitle');
        dialog.addEventListener('close', () => { if (previousFocus && previousFocus.isConnected) previousFocus.focus(); });
        dialog.addEventListener('click', event => { if (event.target === dialog) close(); });
        doc.body.append(dialog);
      }
      previousFocus = doc.activeElement;
      dialog.replaceChildren();
      const header = el('div'); header.className = 'dialog-header';
      const heading = el('h2', title); heading.id = 'featureTitle';
      const dismiss = el('button', '×'); dismiss.type = 'button'; dismiss.className = 'icon-button';
      dismiss.setAttribute('aria-label', '닫기'); dismiss.onclick = close;
      header.append(heading, dismiss); dialog.append(header);
      message = el('p'); message.setAttribute('role', 'status'); message.setAttribute('aria-live', 'polite');
      if (!dialog.open) dialog.showModal();
    }
    function linkField(url) {
      const label = el('label', '공유할 주소'); input = el('input'); input.type = 'url'; input.readOnly = true; input.value = url;
      input.addEventListener('click', () => input.select()); label.append(input); dialog.append(label);
    }
    function hideInstall() { doc.querySelectorAll('[data-install-app]').forEach(button => { button.hidden = true; }); }
    const actions = createActions(win.navigator, {
      share(data) {
        open('지원금픽 공유하기');
        dialog.append(el('p', '링크를 복사해 카카오톡·문자 등 원하는 곳에 붙여넣으세요. 관심 조건과 신청 기록은 공유되지 않아요.'));
        linkField(data.url);
        const copy = el('button', '링크 복사'); copy.type = 'button'; copy.className = 'primary';
        copy.onclick = () => actions.copy(data);
        const row = el('div'); row.className = 'dialog-actions'; row.append(copy); dialog.append(row, message);
      },
      copied() { message.textContent = '주소를 복사했어요. 원하는 곳에 붙여넣어 주세요.'; },
      manualCopy() { message.textContent = '자동 복사를 사용할 수 없어요. 선택된 주소를 길게 누르거나 복사 단축키로 직접 복사하세요.'; input.focus(); input.select(); },
      install(steps) {
        open('휴대폰 홈 화면에 추가');
        dialog.append(el('p', '지원금픽을 홈 화면에서 앱처럼 바로 열 수 있어요. 브라우저에 따라 메뉴 이름이 다를 수 있어요.'));
        const list = el('ol'); steps.forEach(text => list.append(el('li', text))); dialog.append(list);
        dialog.append(el('p', '최신 지원정보를 보려면 인터넷 연결이 필요해요.'));
      },
      requested() {
        open('설치 요청을 전달했어요');
        dialog.append(el('p', '설치가 끝나면 홈 화면이나 앱 목록에서 지원금픽을 열어 주세요.'));
      },
      installed() { hideInstall(); if (dialog && dialog.open) dialog.close(); }
    }, isStandalone);
    win.addEventListener('beforeinstallprompt', event => actions.capture(event));
    win.addEventListener('appinstalled', () => actions.installed());
    if (standalone.addEventListener) standalone.addEventListener('change', () => { if (isStandalone()) hideInstall(); });
    if (isStandalone()) hideInstall();
    doc.addEventListener('click', event => {
      const button = event.target.closest('[data-share-site],[data-share-benefit],[data-install-app]');
      if (!button) return;
      if (button.hasAttribute('data-install-app')) { actions.install(); return; }
      const data = shareData({ site: button.hasAttribute('data-share-site'), id: button.dataset.shareId,
        canonical: doc.querySelector('link[rel="canonical"]')?.href,
        title: button.dataset.shareTitle || doc.querySelector('h1')?.textContent || doc.getElementById('detailTitle')?.textContent });
      actions.share(data);
    });
    // Only this production project may be controlled; no shared-host/root or preview worker.
    if (scriptUrl && win.isSecureContext && 'serviceWorker' in win.navigator) {
      const base = new URL('./', scriptUrl);
      if (base.href === HOME) {
        win.navigator.serviceWorker.register(new URL('sw.js', base).href, { scope: base.pathname, updateViaCache: 'none' }).catch(() => {});
      }
    }
  }
  return { HOME, shareData, installSteps, createActions, init };
});
