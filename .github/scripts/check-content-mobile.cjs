const http = require('node:http');
const fs = require('node:fs/promises');
const path = require('node:path');
const assert = require('node:assert/strict');
const { chromium } = require('playwright');

(async () => {
  const project = process.argv[2];
  assert(['careerpick', 'supportpick'].includes(project));
  const root = path.resolve('dist');
  const server = http.createServer(async (req, res) => {
    try {
      const url = new URL(req.url, 'http://localhost');
      const prefix = '/' + project + '/';
      if (!url.pathname.startsWith(prefix)) { res.writeHead(404).end(); return; }
      let relative = decodeURIComponent(url.pathname.slice(prefix.length));
      if (!relative || relative.endsWith('/')) relative += 'index.html';
      const filename = path.resolve(root, relative);
      if (!filename.startsWith(root + path.sep)) { res.writeHead(403).end(); return; }
      const data = await fs.readFile(filename);
      const ext = path.extname(filename);
      const mime = {'.html':'text/html; charset=utf-8', '.css':'text/css', '.js':'application/javascript', '.png':'image/png', '.svg':'image/svg+xml'};
      res.writeHead(200, {'Content-Type':mime[ext] || 'application/octet-stream'}).end(data);
    } catch { res.writeHead(404).end(); }
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const origin = 'http://127.0.0.1:' + server.address().port;
  const browser = await chromium.launch({headless:true});
  const results = [];
  try {
    const pages = project === 'careerpick' ? ['guides/after-application-checklist.html', 'privacy.html'] : ['', 'benefits/149200000026/', 'privacy.html', 'guides/application-checklist.html', 'guides/compare-benefits.html', 'guides/energy-voucher-2026.html', 'guides/emergency-vs-livelihood-2026.html', 'guides/child-allowance-2026.html', 'guides/housing-benefit-2026.html', 'benefits/135200000120/', 'guides/earned-income-credit-late-2026.html', 'guides/women-farmer-voucher-records-2026.html', 'guides/youth-savings-contribution-2026.html', 'benefits/646000000145/', 'benefits/135200005013/', 'benefits/SD0000015525/', 'guides/first-meeting-vs-parent-benefit-2026.html', 'benefits/305000000113/'];
    await fs.mkdir('mobile-evidence', {recursive:true});
    for (const width of [320,390,1440]) {
      const context = await browser.newContext({viewport:{width,height:900},serviceWorkers:'block'});
      await context.route('**/*', route => route.request().url().startsWith(origin + '/') ? route.continue() : route.abort());
      for (const entry of pages) {
        const page = await context.newPage();
        const response = await page.goto(origin + '/' + project + '/' + entry, {waitUntil:'networkidle'});
        assert.equal(response.status(),200);
        await page.locator('h1').waitFor({state:'visible'});
        if (project === 'supportpick' && entry === '') {
          await page.waitForFunction(() => window.SUPPORTPICK_DATA && !window.SUPPORTPICK_DATA.partial,{timeout:60000});
          const total=await page.evaluate(() => window.SUPPORTPICK_DATA.items.length);
          assert(total>10000);
          assert.equal(await page.locator('.benefit-card').count(),30);
          await page.locator('#filterToggle').click();
          await page.locator('#age').fill('35');
          await page.locator('#age').dispatchEvent('change');
          await page.locator('#household').selectOption('1인가구');
          assert(await page.locator('#resultCount').innerText());
          await page.locator('#resetFilters').click();
          if(width===320){
            const legacy=await context.newPage();
            let catalogAttempts=0;
            await legacy.route('**/catalog/*.json',async route=>{
              await new Promise(resolve=>setTimeout(resolve,1800));
              if(++catalogAttempts===1){await route.abort('failed');return;}
              await route.continue();
            });
            await legacy.goto(origin+'/'+project+'/#benefit=135200000120',{waitUntil:'domcontentloaded'});
            await legacy.getByText('전체 목록에서 요청한 지원정보를 확인하고 있습니다.',{exact:true}).waitFor();
            assert.equal(await legacy.getByText('혜택 자료를 찾지 못했어요',{exact:true}).count(),0);
            await legacy.getByRole('button',{name:'전체 목록 다시 불러오기',exact:true}).click();
            assert.equal(await legacy.getByRole('link',{name:'공유 상세페이지로 바로 확인 →',exact:true}).getAttribute('href'),'benefits/135200000120/');
            await legacy.getByText('아동수당 · 내용 확인 필요',{exact:true}).waitFor();
            await legacy.close();
          }
          await page.locator('[data-compare]').nth(0).click();
          await page.locator('[data-compare]').nth(1).click();
          await page.locator('#compareOpen').click();
          await page.locator('.comparison-table').waitFor({state:'visible'});
          assert.equal(await page.locator('.comparison-table thead th').count(),3);
          assert(await page.getByText('개별 공고의 중복지원·제외 조항 확인 필요').count()>0);
          await page.getByRole('button',{name:'비교 닫기',exact:true}).click();
          await page.locator('#compareClear').click();
          await page.locator('#query').fill('없는정보검사문자열');
          await page.getByText('조건에 맞는 정보가 없어요',{exact:true}).waitFor();
          await page.locator('#resetFilters').click();
          assert.equal(await page.locator('.benefit-card').count(),30);
          for(const [query,id] of [['청년내일저축계좌','135200005013'],['교육복지 우선 지원','SD0000015525']]){
            await page.locator('#query').fill(query);
            const card=page.locator('.benefit-card').filter({has:page.locator('[data-detail="'+id+'"]')});
            await card.getByText('지원대상 원문 일부:',{exact:false}).waitFor();
            assert(!['상동','-'].includes((await card.locator('.card-summary').innerText()).trim()));
          }
          await page.locator('#query').fill('아동수당');
          const heldCard=page.locator('.benefit-card').filter({has:page.locator('[data-detail="135200000120"]')});
          await heldCard.getByText('내용 확인 필요',{exact:true}).waitFor();
          assert(!(await heldCard.innerText()).includes('만 8세 미만'));
          assert.equal(await heldCard.locator('[data-compare]').count(),0);
          await page.goto(origin + '/' + project + '/#benefit=135200000120',{waitUntil:'networkidle'});
          await page.locator('#detailSection').getByText('아동수당 · 내용 확인 필요',{exact:true}).waitFor();
          assert(!(await page.locator('#detailSection').innerText()).includes('매달 25일'));
          await page.goto(origin + '/' + project + '/', {waitUntil:'networkidle'});
          await page.locator('#filterToggle').click();
          await page.locator('#resetFilters').click();
        }
        if (entry.includes('after-application')) {
          assert.equal(await page.locator('#deadline-plan').count(),1);
          await page.locator('summary').first().click();
          assert(await page.locator('details').first().getAttribute('open') !== null);
        }
        if (entry.includes('149200000026')) {
          assert(await page.getByText('카드 발급 전에 훈련과정을 어떻게 비교해 두면 좋을까요?', {exact:true}).count() > 0);
        }
        if (entry === 'benefits/135200000120/') {
          assert.equal(await page.locator('meta[name="robots"]').getAttribute('content'),'noindex,follow');
          assert.equal(await page.locator('a[href="../../guides/child-allowance-2026.html"]').count(),1);
          assert(!(await page.locator('main').innerText()).includes('90일(출국일 포함)'));
        }
        if (entry === 'benefits/646000000145/') {
          assert.equal(await page.locator('meta[name="robots"]').getAttribute('content'),'noindex,follow');
          assert.equal(await page.locator('a[href="../../guides/women-farmer-voucher-records-2026.html"]').count(),1);
          assert(!(await page.locator('main').innerText()).includes('2024년 현재'));
        }
        if (entry === 'guides/women-farmer-voucher-records-2026.html') {
          assert.equal(await page.locator('a[href="../benefits/646000000145/"]').count(),1);
          assert.equal(await page.locator('a[href="../benefits/629000000182/"]').count(),1);
          assert(await page.getByText('현행 자격 확정표 아님',{exact:false}).count()>0);
          const sourceLinks=await page.locator('a[href^="../benefits/"]').allTextContents();
          assert.equal(new Set(sourceLinks).size,2);
          assert(sourceLinks.some(text=>text.includes('전남도청 농업정책과')));
          assert(sourceLinks.some(text=>text.includes('동구청')));
        }
        if (entry === 'guides/youth-savings-contribution-2026.html') {
          assert(await page.getByText('1,800만원',{exact:true}).count()>0);
          assert.equal(await page.locator('a[href="../benefits/135200005013/"]').count(),1);
        }
        if(['benefits/135200005013/','benefits/SD0000015525/'].includes(entry)){
          assert((await page.locator('.benefit-summary').innerText()).startsWith('지원대상 원문 일부:'));
        }
        if(entry==='benefits/305000000113/'){
          assert.equal(await page.locator('meta[name="robots"]').getAttribute('content'),'noindex,follow');
          assert.equal(await page.locator('a[href="https://www.ddm.go.kr/www/contents.do?key=756"]').count(),1);
          assert.equal(await page.locator('a[href="../../guides/first-meeting-vs-parent-benefit-2026.html"]').count(),1);
          assert(!(await page.locator('main').innerText()).includes('출생아1인당 1회 200만원의 이용권 지원'));
        }
        if(entry==='guides/first-meeting-vs-parent-benefit-2026.html'){
          assert.equal(await page.locator('a[href^="../benefits/"]').count(),4);
          assert(await page.getByText('100만원 − 58만4천원 = 현금 차액 41만6천원',{exact:true}).count()>0);
        }
        const dimensions = await page.evaluate(() => ({width:innerWidth, content:document.documentElement.scrollWidth}));
        assert(dimensions.content <= dimensions.width + 1, JSON.stringify({entry,...dimensions}));
        await page.screenshot({path:'mobile-evidence/' + width + '-' + entry.replace(/[^a-z0-9]/gi,'_') + '.png',fullPage:true});
        results.push({entry,width,http:200,overflow:0});
        await page.close();
      }
      await context.close();
    }
    await fs.writeFile('mobile-evidence/results.json',JSON.stringify({project,environment:'Linux Chromium; viewport emulation, not real Android',results},null,2));
    console.log(JSON.stringify({passed:results.length,failed:0}));
  } finally {
    await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => {console.error(error);process.exitCode=1;});
