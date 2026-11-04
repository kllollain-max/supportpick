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
  function installContext(nav) {
    const ua = nav.userAgent || '';
    const ios = /iPhone|iPad|iPod/i.test(ua) || (/Macintosh/i.test(ua) && nav.maxTouchPoints > 1);
    const inApp = /KAKAOTALK|NAVER\(|FBAN|FBAV|Instagram|Threads|Barcelona|Line\/|;\s*wv\)/i.test(ua);
    return { ios, android: /Android/i.test(ua), inApp, threads: /Threads|Barcelona/i.test(ua) };
  }
  function installSteps(nav) {
    const { ios, android, inApp } = installContext(nav);
    if (inApp) return ['앱 안의 메뉴(⋯)에서 브라우저로 열기를 선택하세요.', ios ? 'Safari에서 공유(□↑) → 홈 화면에 추가 → 추가를 누르세요.' : 'Chrome 또는 삼성 인터넷에서 메뉴 → 앱 설치 또는 홈 화면에 추가를 선택하세요.'];
    if (ios) return ['Safari에서 이 사이트를 여세요.', '공유 버튼(□↑) → 홈 화면에 추가를 선택하세요.', '이름을 확인하고 추가를 누르세요.'];
    if (android) return ['Chrome의 오른쪽 위 메뉴(⋮) 또는 삼성 인터넷의 메뉴(≡)를 여세요.', '앱 설치 또는 홈 화면에 추가를 선택하고 확인하세요.'];
    return ['Chrome·Edge의 주소창 설치 아이콘 또는 메뉴의 앱 설치를 선택하세요.', '휴대폰에서는 Safari·Chrome·삼성 인터넷으로 열어 홈 화면에 추가할 수 있어요.'];
  }
  function installLinks(canonical) {
    // Send only the public homepage or canonical benefit ID, never personal filters.
    const url = new URL(shareData({ canonical }).url);
    url.searchParams.set('install', '1');
    const address = url.href;
    return { address, chrome: 'intent://' + url.host + url.pathname + url.search
      + '#Intent;scheme=https;package=com.android.chrome;S.browser_fallback_url='
      + encodeURIComponent(address) + ';end;' };
  }
  function createActions(nav, ui, isStandalone = () => false) {
    let promptEvent = null, installed = false, prompting = false;
    const update = () => ui.installState?.({ ready: !!promptEvent, busy: prompting });
    return {
      capture(event) { event.preventDefault(); if (installed || isStandalone()) return; promptEvent = event; update(); },
      installed() { installed = true; promptEvent = null; update(); ui.installed(); },
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
        promptEvent = null; prompting = true; update();
        try {
          await event.prompt();
          const choice = await event.userChoice;
          if (choice && choice.outcome === 'accepted' && !installed) ui.requested();
        } catch (_) { ui.install(installSteps(nav)); }
        finally { prompting = false; update(); }
      }
    };
  }
  function init(win, doc) {
    const scriptUrl = doc.currentScript && doc.currentScript.src;
    const standalone = win.matchMedia('(display-mode: standalone)');
    const isStandalone = () => standalone.matches || win.navigator.standalone === true;
    let dialog, message, input, previousFocus, nativeInstall, installStatus;
    let installState = { ready: false, busy: false };
    function el(tag, text) { const node = doc.createElement(tag); if (text) node.textContent = text; return node; }
    function close() { dialog.close(); }
    function open(title, feature = 'share') {
      if (!dialog) {
        dialog = el('dialog'); dialog.id = 'featureDialog'; dialog.className = 'feature-dialog';
        dialog.setAttribute('aria-labelledby', 'featureTitle');
        dialog.addEventListener('close', () => { if (previousFocus && previousFocus.isConnected) previousFocus.focus(); });
        dialog.addEventListener('click', event => { if (event.target === dialog) close(); });
        doc.body.append(dialog);
      }
      if (!dialog.open) previousFocus = doc.activeElement;
      nativeInstall = null; installStatus = null; dialog.dataset.feature = feature;
      dialog.replaceChildren();
      const header = el('div'); header.className = 'dialog-header';
      const heading = el('h2', title); heading.id = 'featureTitle';
      const dismiss = el('button', '×'); dismiss.type = 'button'; dismiss.className = 'icon-button';
      dismiss.setAttribute('aria-label', '닫기'); dismiss.onclick = close;
      header.append(heading, dismiss); dialog.append(header);
      message = el('p'); message.setAttribute('role', 'status'); message.setAttribute('aria-live', 'polite');
      if (!dialog.open) dialog.showModal();
    }
    function linkField(url, text = '공유할 주소') {
      const label = el('label', text); input = el('input'); input.type = 'url'; input.readOnly = true; input.value = url;
      input.addEventListener('click', () => input.select()); label.append(input); dialog.append(label);
    }
    function hideInstall() { doc.querySelectorAll('[data-install-app]').forEach(button => { button.hidden = true; }); }
    function syncInstall(state) {
      installState = state;
      if (!nativeInstall || !dialog.open || dialog.dataset.feature !== 'install') return;
      nativeInstall.hidden = !state.ready && !state.busy;
      nativeInstall.disabled = state.busy;
      nativeInstall.textContent = state.busy ? '브라우저 설치 창을 여는 중…' : '홈 화면 설치 창 열기';
      installStatus.textContent = state.ready ? '설치 창이 준비됐어요. 아래 버튼을 눌러 주세요.'
        : state.busy ? '열린 브라우저 설치 창에서 계속해 주세요.' : '설치 창이 표시되지 않으면 아래 브라우저 메뉴 방법을 이용하세요.';
    }
    function showInstallHelp(steps) {
      const context = installContext(win.navigator);
      const links = installLinks(doc.querySelector('link[rel="canonical"]')?.href);
      open(context.inApp ? '브라우저에서 이어서 설치하세요' : '휴대폰 홈 화면에 추가', 'install');
      dialog.append(el('p', context.inApp
        ? '앱 안에서 열린 화면에서는 설치 창이 제한될 수 있어요. 휴대폰 브라우저에서 이어서 추가해 주세요.'
        : '설치 창이 준비되면 아래 버튼이 표시돼요. 브라우저 메뉴에서도 홈 화면에 추가할 수 있어요.'));
      installStatus = el('p'); installStatus.className = 'install-status'; installStatus.setAttribute('role', 'status');
      nativeInstall = el('button'); nativeInstall.type = 'button'; nativeInstall.className = 'primary';
      nativeInstall.onclick = () => actions.install();
      const row = el('div'); row.className = 'install-actions'; row.append(nativeInstall);
      // An explicit tap may open Chrome on Android. The host app can still block intents.
      if (context.android) {
        const chrome = el('a', 'Chrome으로 열기'); chrome.className = 'primary'; chrome.href = links.chrome;
        row.append(chrome);
      }
      const copy = el('button', '설치 주소 복사'); copy.type = 'button'; copy.className = 'quiet';
      copy.onclick = () => actions.copy({ url: links.address }); row.append(copy);
      dialog.append(installStatus, row); linkField(links.address, '설치할 주소'); dialog.append(message);
      if (context.android) dialog.append(el('p', 'Chrome이 열리지 않으면 주소를 복사한 뒤 Chrome·삼성 인터넷 주소창에 붙여넣어 주세요. 앱 창 오른쪽 위 ⋯ 메뉴의 브라우저로 열기도 이용할 수 있어요.'));
      const list = el('ol'); steps.forEach(text => list.append(el('li', text))); dialog.append(list);
      if (context.inApp) dialog.append(el('p', '다른 브라우저로 바꾸면 저장·신청 기록은 자동으로 옮겨지지 않아요. 기존 기록이 있다면 원래 화면의 기록 관리에서 먼저 백업하세요.'));
      dialog.append(el('p', '최신 지원정보를 보려면 인터넷 연결이 필요해요.'));
      syncInstall(installState);
    }
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
      install: showInstallHelp,
      installState: syncInstall,
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
    // Continue the user's browser-handoff request without auto-prompting or reopening loops.
    try {
      const current = new URL(win.location.href);
      if (current.searchParams.get('install') === '1') {
        current.searchParams.delete('install');
        win.history.replaceState(win.history.state, '', current.pathname + current.search + current.hash);
        if (!isStandalone()) showInstallHelp(installSteps(win.navigator));
      }
    } catch (_) { /* Installation guidance must not prevent ordinary browsing. */ }
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
  return { HOME, shareData, installContext, installSteps, installLinks, createActions, init };
});
