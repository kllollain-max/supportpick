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
    const pages = project === 'careerpick' ? ['guides/after-application-checklist.html', 'privacy.html'] : ['', 'benefits/149200000026/', 'privacy.html', 'guides/application-checklist.html', 'guides/compare-benefits.html'];
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
        }
        if (entry.includes('after-application')) {
          assert.equal(await page.locator('#deadline-plan').count(),1);
          await page.locator('summary').first().click();
          assert(await page.locator('details').first().getAttribute('open') !== null);
        }
        if (entry.includes('149200000026')) {
          assert(await page.getByText('카드 발급 전에 훈련과정을 어떻게 비교해 두면 좋을까요?', {exact:true}).count() > 0);
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
