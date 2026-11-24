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
    const pages = project === 'careerpick' ? ['guides/after-application-checklist.html', 'privacy.html'] : ['', 'benefits/149200000026/', 'benefits/142100000062/', 'benefits/611000000127/', 'benefits/398000000296/', 'benefits/O00388400004/', 'benefits/628000000155/', 'benefits/626000000633/', 'benefits/611000019611/', 'privacy.html', 'guides/application-checklist.html', 'guides/compare-benefits.html', 'guides/energy-voucher-2026.html', 'guides/emergency-vs-livelihood-2026.html', 'guides/child-allowance-2026.html', 'guides/housing-benefit-2026.html', 'benefits/135200000120/', 'guides/earned-income-credit-late-2026.html', 'guides/women-farmer-voucher-records-2026.html', 'guides/youth-savings-contribution-2026.html', 'benefits/646000000145/', 'benefits/135200005013/', 'benefits/SD0000015525/', 'guides/first-meeting-vs-parent-benefit-2026.html', 'benefits/305000000113/', 'guides/culture-card-deadlines-2026.html', 'guides/basic-pension-amounts-2026.html', 'benefits/137100000236/', 'benefits/648000001107/', 'benefits/B55151000066/', 'benefits/SSE000000170/', 'guides/forest-voucher-application-vs-use-2026.html', 'guides/gyeonggi-child-transport-cap-2026.html', 'benefits/140000000176/', 'benefits/641000000139/', 'guides/winter-bills-vs-home-improvement-2026.html', 'benefits/424000000006/', 'benefits/B55353000001/', 'benefits/135200005003/', 'benefits/WII000001410/', 'guides/long-term-lease-notice-checklist-2026.html', 'guides/local-social-service-application-vs-use-2026.html', 'benefits/999000000024/', 'benefits/SD0000016138/', 'benefits/WII000000310/', 'benefits/132000000006/', 'guides/leave-benefit-claim-checklist-2026.html', 'guides/unemployment-benefit-vs-pension-credit-2026.html', 'benefits/149200005007/', 'benefits/SD0000015536/', 'benefits/999000000008/', 'benefits/135200000115/', 'benefits/171000000005/', 'benefits/B55201500004/', 'benefits/WII000001460/', 'guides/scholarships-vs-student-loan-steps-2026.html', 'guides/small-business-loan-vs-guarantee-2026.html', 'benefits/SD0000004508/', 'benefits/999000000090/', 'benefits/134200005002/', 'benefits/GES000000110/', 'benefits/GES000000100/', 'benefits/SD0000007429/', 'benefits/SD0000018904/', 'guides/incheon-pregnancy-transport-vs-postpartum-2026.html', 'benefits/628000000735/', 'benefits/628000000744/', 'guides/incheon-child-dream-birth-year-2026.html', 'benefits/628000000739/', 'guides/maternal-service-application-use-refund-2026.html', 'benefits/PTR000050390/', 'benefits/628000000111/', 'guides/rental-guarantee-fee-cap-and-dates-2026.html', 'benefits/161300000103/', 'guides/youth-mutual-aid-closed-enrollment-maturity-2026.html', 'benefits/SD0000011848/', 'guides/youth-housing-account-announcement-tax-conversion-2026.html', 'benefits/161300000088/', 'guides/didimdol-cap-collateral-and-closing-2026.html', 'benefits/B55140800003/', 'guides/school-welfare-vs-education-benefit-2026.html', 'guides/sunchang-birth-total-vs-installments-2026.html', 'benefits/477000000110/', 'guides/busan-child-care-fee-vs-copayment-2026.html', 'guides/jeungpyeong-insurance-contract-vs-claim-2026.html', 'benefits/626000000649/', 'benefits/557000000250/', 'benefits/875000000016/', 'guides/influenza-season-vs-dose-history-2026.html', 'guides/veterans-vehicle-inspection-discount-2026.html', 'guides/training-card-vs-employment-support-2026.html'];
    await fs.mkdir('mobile-evidence', {recursive:true});
    for (const width of [320,390,1440]) {
      const context = await browser.newContext({viewport:{width,height:900},serviceWorkers:'block'});
      await context.route('**/*', route => route.request().url().startsWith(origin + '/') ? route.continue() : route.abort());
      for (const entry of pages) {
        const page = await context.newPage();
        const response = await page.goto(origin + '/' + project + '/' + entry, {waitUntil:'networkidle'});
        assert.equal(response.status(),200);
        await page.locator('h1').waitFor({state:'visible'});
        if(['benefits/626000000649/','benefits/557000000250/','benefits/875000000016/'].includes(entry)){
          assert.equal(await page.locator('.reviewed-amount-advisory').count(),1);
          assert.equal(await page.locator('.amount-source-notice').count(),1);
        }
        if (['benefits/142100000062/', 'benefits/611000000127/', 'benefits/135200005013/', 'benefits/GES000000110/', 'benefits/611000019611/', 'benefits/626000000633/', 'benefits/628000000155/', 'benefits/O00388400004/'].includes(entry)) {
          await page.getByRole('heading', {name: '신청 마감 후 확인할 일', exact: true}).waitFor();
          assert.equal(await page.getByRole('link', {name: '공식 신청 창구 ↗', exact: true}).count(), 0);
        }
        if (entry === 'benefits/398000000296/') {
          assert.equal(await page.getByRole('link', {name: '공식 신청 창구 ↗', exact: true}).count(), 0);
          await page.getByRole('link', {name: '기존 신청 링크 · 현재 접수 여부 확인 ↗', exact: true}).waitFor();
        }
        if (entry === 'guides/training-card-vs-employment-support-2026.html') {
          assert.equal(await page.locator('.guide-table').count(), 1);
          for (const id of ['149200000026', '149200005007']) {
            assert.equal(await page.locator('a[href="../benefits/' + id + '/"]').count(), 1);
          }
        }
        if (['benefits/149200000026/', 'benefits/149200005007/'].includes(entry)) {
          assert.equal(await page.locator('a[href="../../guides/training-card-vs-employment-support-2026.html"]').count(), 1);
        }
        if(entry==='guides/veterans-vehicle-inspection-discount-2026.html'){
          assert.equal(await page.locator('.guide-table').count(),1);
          assert(await page.getByText('수검 후 60일 이내이며 환불 요청 시점에 전산조회가 가능할 것',{exact:true}).isVisible());
        }
        if(entry==='guides/influenza-season-vs-dose-history-2026.html'){
          assert.equal(await page.locator('.guide-table').count(),2);
          assert.equal(await page.locator('a[href="../benefits/135200000115/"]').count(),1);
          assert(await page.getByRole('heading',{name:'‘1회 지원’ 요약보다 접종 이력과 절기를 먼저 확인하세요',exact:true}).count());
        }
        if(entry==='benefits/135200000115/'){
          assert.equal(await page.locator('.influenza-source-advisory').count(),1);
          assert.equal(await page.locator('a[href="../../guides/influenza-season-vs-dose-history-2026.html"]').count(),1);
        }
        if(entry==='guides/busan-child-care-fee-vs-copayment-2026.html'){
          assert(await page.getByText('16,000 × 4 = 64,000원',{exact:false}).count());
          assert.equal(await page.locator('a[href="../benefits/626000000649/"]').count(),1);
        }
        if(entry==='guides/jeungpyeong-insurance-contract-vs-claim-2026.html'){
          assert.equal(await page.locator('.guide-table').count(),2);
          assert.equal(await page.locator('a[href="../benefits/557000000250/"]').count(),1);
        }
        if(entry==='guides/sunchang-birth-total-vs-installments-2026.html'){
          assert.equal(await page.locator('.guide-table').count(),1);
          assert.equal(await page.locator('a[href="../benefits/477000000110/"]').count(),1);
          assert(await page.getByRole('heading',{name:'1,500만원을 한 달 생활비에 모두 넣으면 안 되는 이유',exact:true}).count());
        }
        if(entry==='benefits/477000000110/'){
          assert.equal(await page.locator('.amount-source-notice').count(),1);
          assert.equal(await page.locator('a[href="../../guides/sunchang-birth-total-vs-installments-2026.html"]').count(),1);
        }
        if(entry==='guides/school-welfare-vs-education-benefit-2026.html'){
          assert.equal(await page.locator('.guide-table').count(),2);
          assert.equal(await page.locator('a[href="../benefits/SD0000015525/"]').count(),1);
          assert(await page.getByRole('heading',{name:'학교 선정 기준을 학생 개인의 자격으로 읽지 마세요',exact:true}).count());
        }
        if(entry==='benefits/SD0000015525/'){
          assert.equal(await page.locator('a[href="../../guides/school-welfare-vs-education-benefit-2026.html"]').count(),1);
        }
        if(entry==='guides/didimdol-cap-collateral-and-closing-2026.html'){
          assert.equal(await page.locator('.guide-table').count(),2);
          assert(await page.getByRole('heading',{name:'상품 한도와 집값에 대한 비율은 서로 다른 제한입니다',exact:true}).count());
          assert.equal(await page.locator('a[href="../benefits/B55140800003/"]').count(),1);
        }
        if(entry==='benefits/B55140800003/'){
          assert(await page.getByText('내용 확인 필요',{exact:true}).count()>0);
          assert.equal(await page.locator('a[href="../../guides/didimdol-cap-collateral-and-closing-2026.html"]').count(),1);
          assert.equal(await page.getByRole('heading',{name:'선정기준·세부 자격',exact:true}).count(),0);
        }
        if(entry==='guides/youth-housing-account-announcement-tax-conversion-2026.html'){
          assert.equal(await page.locator('.guide-table').count(),2);
          assert(await page.getByRole('heading',{name:'발표일이 곧 내 계좌의 적용일은 아닙니다',exact:true}).count());
          assert.equal(await page.locator('a[href="../benefits/161300000088/"]').count(),1);
        }
        if(entry==='benefits/161300000088/'){
          assert(await page.getByText('내용 확인 필요',{exact:true}).count()>0);
          assert.equal(await page.locator('a[href="../../guides/youth-housing-account-announcement-tax-conversion-2026.html"]').count(),1);
          assert.equal(await page.getByRole('heading',{name:'선정기준·세부 자격',exact:true}).count(),0);
        }
        if(entry==='guides/youth-mutual-aid-closed-enrollment-maturity-2026.html'){
          assert.equal(await page.locator('.guide-table').count(),2);
          assert(await page.getByRole('heading',{name:'먼저 기존 계약이 있는지 확인하세요',exact:true}).count());
          assert.equal(await page.locator('a[href="../benefits/SD0000011848/"]').count(),1);
        }
        if(entry==='benefits/SD0000011848/'){
          assert(await page.getByText('내용 확인 필요',{exact:true}).count()>0);
          assert.equal(await page.locator('a[href="../../guides/youth-mutual-aid-closed-enrollment-maturity-2026.html"]').count(),1);
          assert.equal(await page.getByRole('heading',{name:'선정기준·세부 자격',exact:true}).count(),0);
        }
        if(entry==='guides/rental-guarantee-fee-cap-and-dates-2026.html'){
          assert.equal(await page.locator('.guide-table').count(),2);
          assert(await page.getByRole('heading',{name:'가입일과 지원 신청일을 모두 적어 두세요',exact:true}).count());
          assert.equal(await page.locator('a[href="../benefits/161300000103/"]').count(),1);
        }
        if(entry==='benefits/161300000103/'){
          assert(await page.getByText('내용 확인 필요',{exact:true}).count()>0);
          assert.equal(await page.locator('a[href="../../guides/rental-guarantee-fee-cap-and-dates-2026.html"]').count(),1);
          assert.equal(await page.getByRole('heading',{name:'선정기준·세부 자격',exact:true}).count(),0);
        }
        if(entry==='guides/maternal-service-application-use-refund-2026.html'){
          assert.equal(await page.locator('.guide-table').count(),2);
          assert(await page.getByRole('heading',{name:'같은 ‘60일’이어도 기준일이 다릅니다',exact:true}).count());
          assert.equal(await page.locator('a[href="../benefits/PTR000050390/"]').count(),1);
          assert.equal(await page.locator('a[href="../benefits/628000000111/"]').count(),1);
        }
        if(entry==='benefits/PTR000050390/'){
          assert(await page.getByText('내용 확인 필요',{exact:true}).count()>0);
          assert.equal(await page.locator('a[href="../../guides/maternal-service-application-use-refund-2026.html"]').count(),1);
          assert.equal(await page.getByRole('heading',{name:'선정기준·세부 자격',exact:true}).count(),0);
        }
        if(entry==='guides/incheon-child-dream-birth-year-2026.html'){
          assert.equal(await page.locator('.guide-table').count(),2);
          assert(await page.getByRole('heading',{name:'과거의 확대 계획을 올해 대상자로 읽지 마세요',exact:true}).count());
          assert.equal(await page.locator('a[href="../benefits/628000000739/"]').count(),1);
        }
        if(entry==='guides/incheon-pregnancy-transport-vs-postpartum-2026.html'){
          assert.equal(await page.locator('.guide-table').count(),2);
          assert(await page.getByRole('heading',{name:'신청 마감일과 포인트 만료일은 다른 일정입니다',exact:true}).count());
          assert.equal(await page.locator('a[href="../benefits/628000000735/"]').count(),1);
          assert.equal(await page.locator('a[href="../benefits/628000000744/"]').count(),1);
        }
        if(entry==='guides/leave-benefit-claim-checklist-2026.html'){
          assert(await page.getByRole('heading',{name:'임신 중 배우자 돌봄과 급여 신청을 나누어 확인하세요',exact:true}).count());
          assert.equal(await page.locator('a[href="https://www.moel.go.kr/news/enews/report/enewsView.do?news_seq=19964"]').count(),2);
          assert.equal(await page.locator('.guide-table').count(),2);
          assert(await page.getByText('근로자 신청인지, 회사가 실제 지급 후 대위 신청하는지 확인',{exact:true}).count());
          assert.equal(await page.locator('a[href="../benefits/999000000008/"]').count(),1);
          assert.equal(await page.locator('a[href="../benefits/WII000001460/"]').count(),1);
        }
        if(entry==='guides/unemployment-benefit-vs-pension-credit-2026.html'){
          assert.equal(await page.locator('.guide-table').count(),2);
          assert(await page.getByRole('heading',{name:'마지막 입금일보다 소정급여일수의 마지막 날을 먼저 확인하세요',exact:true}).count());
          assert.equal(await page.locator('a[href="../benefits/B55201500004/"]').count(),1);
          assert.equal(await page.locator('a[href="../benefits/SD0000015536/"]').count(),1);
        }
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
          await page.locator('#query').fill('문화누리카드');
          await page.locator('[data-detail="648000001107"]').click();
          await page.locator('.source-advisory').getByText('신청 주소 확인:',{exact:true}).waitFor();
          await page.goto(origin + '/' + project + '/#benefit=648000001107', {waitUntil:'networkidle'});
          await page.locator('#detailSection').getByRole('link',{name:'출처·확인 안내 상세페이지 →',exact:true}).click();
          await page.locator('.source-advisory').getByText('신청 주소 확인:',{exact:true}).waitFor();
          await page.goto(origin + '/' + project + '/', {waitUntil:'networkidle'});
          await page.waitForFunction(() => window.SUPPORTPICK_DATA && !window.SUPPORTPICK_DATA.partial,{timeout:60000});
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
        if(entry==='guides/culture-card-deadlines-2026.html'){
          assert.equal(await page.locator('a[href^="../benefits/"]').count(),3);
          assert(await page.getByText('2026.12.31.까지',{exact:true}).count()>0);
          assert(await page.getByText('2025년 기간과 14만원',{exact:false}).count()>0);
        }
        if(entry==='guides/basic-pension-amounts-2026.html'){
          assert.equal(await page.locator('a[href="../benefits/SSE000000170/"]').count(),1);
          assert(await page.getByText('349,700원 × 80% = 279,760원',{exact:true}).count()>0);
        }
        if(entry==='benefits/648000001107/'){
          assert(await page.locator('.source-advisory').getByText('신청 주소 확인:',{exact:true}).count()>0);
          assert.equal(await page.locator('.source-advisory a').getAttribute('href'),'https://www.mnuri.kr/munhwa/cardIssueGuide.do');
        }
        if(entry==='benefits/B55151000066/'){
          assert(await page.locator('.source-advisory').getByText('지난 연도 자료:',{exact:true}).count()>0);
          assert.equal(await page.locator('meta[name="robots"]').getAttribute('content'),'index,follow');
          assert(await page.getByText('2025년 기준 14만 원',{exact:false}).count()>0);
        }
        if(entry==='guides/forest-voucher-application-vs-use-2026.html'){
          assert.equal(await page.locator('a[href="../benefits/140000000176/"]').count(),1);
          assert(await page.getByText('1월 30일 18시 도착분까지',{exact:true}).count()>0);
          assert(await page.getByText('강원숲체험장(춘천)',{exact:false}).count()>0);
        }
        if(entry==='guides/gyeonggi-child-transport-cap-2026.html'){
          assert.equal(await page.locator('a[href="../benefits/641000000139/"]').count(),1);
          assert(await page.getByText('82,000원',{exact:true}).count()>0);
          assert(await page.getByText('60,000원',{exact:true}).count()>0);
        }
        if(entry==='benefits/140000000176/'){
          assert(await page.locator('.source-advisory').getByText('신청과 사용기한 구분:',{exact:true}).count()>0);
          assert.equal(await page.locator('meta[name="robots"]').getAttribute('content'),'index,follow');
          assert(await page.getByText('11월 30일까지 새로 신청할 수 있나요?',{exact:true}).count()>0);
        }
        if(entry==='guides/winter-bills-vs-home-improvement-2026.html'){
          assert(await page.getByText('9월 11일 18시',{exact:false}).count()>0);
          assert.equal(await page.locator('a[href="../benefits/424000000006/"]').count(),1);
          assert(await page.getByText('소유주 동의 가능 여부',{exact:true}).count()>0);
        }
        if(entry==='benefits/424000000006/'){
          assert.equal(await page.locator('a[href="../../guides/winter-bills-vs-home-improvement-2026.html"]').count(),1);
          assert(await page.getByText('전국 안내에 연말 날짜가 있으면 지금 신청할 수 있나요?',{exact:true}).count()>0);
        }
        if(entry==='benefits/B55353000001/'){
          assert(await page.getByText('긴급복지 생계지원과 동절기 연료비는 같은 제한인가요?',{exact:true}).count()>0);
        }
        if(entry==='benefits/135200005003/'){
          assert(await page.getByText('먼저 지원한다는 말은 이후 조사가 없다는 뜻인가요?',{exact:true}).count()>0);
        }
        if(entry==='benefits/WII000001410/'){
          assert(await page.getByText('통장에 찍힌 월급을 기준액에서 바로 빼도 되나요?',{exact:true}).count()>0);
        }
        if(entry==='guides/long-term-lease-notice-checklist-2026.html'){
          assert.equal(await page.locator('a[href="../benefits/999000000024/"]').count(),1);
          assert(await page.getByText('서울시민·면적별 기준',{exact:false}).count()>0);
        }
        if(entry==='guides/local-social-service-application-vs-use-2026.html'){
          assert.equal(await page.locator('a[href="../benefits/SD0000016138/"]').count(),1);
          assert(await page.getByText('이용기관 선택·계약',{exact:true}).count()>0);
        }
        const revisedQuestions={
          'benefits/999000000024/':'최장 20년이면 처음 계약할 때 20년 거주가 확정되나요?',
          'benefits/SD0000016138/':'신청 전에 진단서와 건강보험 관련 서류를 모두 발급해야 하나요?',
          'benefits/WII000000310/':'상담 뒤 추가 확인이나 기관 연계도 받을 수 있나요?',
          'benefits/132000000006/':'건강검진을 어제 받았으면 오늘 바로 자료를 불러올 수 있나요?'};
        if(revisedQuestions[entry]){
          const question=page.getByText(revisedQuestions[entry],{exact:true});
          await question.click();
          assert(await page.locator('details[open]').count()>0);
        }
        const dimensions = await page.evaluate(() => ({width:innerWidth, content:document.documentElement.scrollWidth}));
        assert(dimensions.content <= dimensions.width + 1, JSON.stringify({entry,...dimensions}));
        await page.screenshot({path:'mobile-evidence/' + width + '-' + entry.replace(/[^a-z0-9]/gi,'_') + '.png',fullPage:true});
        if(entry==='guides/scholarships-vs-student-loan-steps-2026.html'){
          assert.equal(await page.locator('table').count(),2);
          assert.equal(await page.locator('a[href="../benefits/GES000000100/"]').count(),1);
          assert((await page.locator('main').innerText()).includes('전환대출'));
        }
        if(entry==='guides/small-business-loan-vs-guarantee-2026.html'){
          assert.equal(await page.locator('table').count(),2);
          assert((await page.locator('main').innerText()).includes('은행 대출이자는 별도'));
          assert.equal(await page.locator('a[href="../benefits/SD0000018904/"]').count(),1);
        }
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
