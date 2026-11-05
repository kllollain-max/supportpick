/* Isolated CI browser regression; only synthetic personal records on localhost. */
const {chromium}=require('playwright');
const {createServer}=require('node:http');
const fs=require('node:fs');const path=require('node:path');const assert=require('node:assert/strict');
const root=path.resolve('dist');const outcomes=[];
const mime={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json','.css':'text/css','.png':'image/png','.svg':'image/svg+xml'};
const server=createServer((req,res)=>{
 let p=path.resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://local').pathname));
 if(!p.startsWith(root+path.sep)&&p!==root){res.writeHead(403).end();return;}
 if(fs.existsSync(p)&&fs.statSync(p).isDirectory())p=path.join(p,'index.html');
 if(!fs.existsSync(p)){res.writeHead(404).end('missing');return;}
 res.setHeader('Content-Type',mime[path.extname(p)]||'application/octet-stream');fs.createReadStream(p).pipe(res);
});
(async()=>{
 await new Promise(r=>server.listen(0,'127.0.0.1',r));const base='http://127.0.0.1:'+server.address().port+'/';
 const browser=await chromium.launch({headless:true});fs.mkdirSync('output/browser',{recursive:true});
 try{
  for(const width of [320,390,1440]){
   const context=await browser.newContext({viewport:{width,height:900},timezoneId:'Asia/Seoul'});
   await context.route('**/*',route=>new URL(route.request().url()).origin===new URL(base).origin?route.continue():route.abort());
   await context.addInitScript(()=>{if(!localStorage.getItem('supportpick:records:v1'))localStorage.setItem('supportpick:records:v1',JSON.stringify({version:1,revision:1,saved:['QA_OLD'],apps:{QA_OLD:{title:'검사용 이전 기록',note:'보존할 메모',stage:'서류 준비',updatedAt:'2026-11-04T00:00:00Z'}},prefs:{region:'',category:''}}));localStorage.setItem('careerpick:qa-sentinel','unchanged');});
   const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.goto(base);await page.locator('.benefit-card').first().waitFor();
   const check=label=>outcomes.push({width,check:label,status:'passed'});
   const noOverflow=async()=>assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'horizontal overflow '+width);
   await noOverflow();check('home and mobile layout');
   await page.locator('#filterToggle').click();
   await page.locator('#applicationStatus').selectOption('active');
   for(const badge of await page.locator('.benefit-card .badge').allTextContents())assert.match(badge,/접수 중|상시 신청/);
   await page.locator('#applicationStatus').selectOption('needs_check');
   assert.ok(await page.locator('.benefit-card').count()>0);
   for(const badge of await page.locator('.benefit-card .badge').allTextContents())assert.match(badge,/확인 필요/);
   await page.locator('#applicationStatus').selectOption('soon');
   await page.locator('#resetFilters').click();check('status filters and reset');
   const title=await page.locator('.benefit-card h3').first().innerText();
   await page.locator('#query').fill(title);assert.ok(await page.locator('.benefit-card').count()>0);
   await page.locator('#resetFilters').click();check('keyword search');
   await page.locator('#preferencesButton').click();await page.locator('#prefRegion').selectOption('강원');await page.locator('#prefCity').fill('춘천시');await page.locator('#prefTargetGroup').selectOption('학생');await page.locator('#preferencesForm button[type=submit]').click();
   assert.match(await page.locator('#matchNotice').innerText(),/춘천시.*학생/);assert.ok(await page.locator('.match-reason').count()>0);check('matching reasons and uncertainty');
   await page.locator('[data-tab=all]').click();
   const first=page.locator('.benefit-card').first();await first.locator('[data-save]').click();assert.equal(await first.locator('[data-save]').getAttribute('aria-pressed'),'true');
   await first.locator('[data-track]').click();assert.ok(await page.locator('[data-app-form]').count()>=2);
   assert.equal(await page.locator('[data-app-form="QA_OLD"] textarea').inputValue(),'보존할 메모');check('saved and application records');
   await page.locator('[data-tab=all]').click();const card=page.locator('.benefit-card').first();const href=await card.locator('h3 a').getAttribute('href');
   // Click the non-title summary, which is covered by the native stretched link.
   await card.locator('.card-summary').click();await page.waitForURL('**/'+href);await page.reload();assert.equal(await page.locator('h1').count(),1);assert.ok((await page.locator('main').innerText()).length>300);await page.goBack();await page.goBack();await page.goto(base);check('whole-card detail, direct URL and refresh');
   await page.locator('#recordsButton').click();assert.match(await page.locator('#recordsTitle').innerText(),/백업·복원/);await page.locator('#backupFallback summary').click();await page.locator('#showBackupText').click();
   const backup=JSON.parse(await page.locator('#backupText').inputValue());assert.equal(backup.data.apps.QA_OLD.note,'보존할 메모');assert.equal(backup.data.prefs.city,'춘천시');
   const prior=await page.evaluate(()=>localStorage.getItem('supportpick:records:v1'));
   await page.locator('#backupText').fill('{"format":"careerpick-backup","version":1}');await page.locator('#importTextButton').click();assert.ok(await page.locator('#recordsError').innerText());assert.equal(await page.evaluate(()=>localStorage.getItem('supportpick:records:v1')),prior);
   await page.locator('#backupText').fill(JSON.stringify(backup));await page.locator('#importTextButton').click();
   await page.locator('#recordsDialog [data-close-dialog]').click();assert.equal(await page.evaluate(()=>localStorage.getItem('careerpick:qa-sentinel')),'unchanged');check('backup compatibility, invalid rejection and merge');
   await page.locator('[data-share-site]').click();await page.locator('#featureDialog[open]').waitFor();assert.match(await page.locator('#featureTitle').innerText(),/공유/);await page.keyboard.press('Escape');
   await page.locator('[data-install-app]').click();await page.locator('#featureDialog[open]').waitFor();assert.match(await page.locator('#featureTitle').innerText(),/홈 화면|설치/);await page.keyboard.press('Escape');check('share and install guidance retained');
   await noOverflow();assert.deepEqual(errors,[]);await page.screenshot({path:'output/browser/home-'+width+'.png',fullPage:false});
   await page.goto(base+'benefits/149200000026/');assert.equal(await page.locator('.guide-summary tr').count(),4);assert.match(await page.locator('.own-guide').innerText(),/사람 검토.*별도 확인/);await noOverflow();await page.screenshot({path:'output/browser/detail-'+width+'.png',fullPage:false});check('editorial table and mobile paragraphs');
   await context.close();
  }
 }finally{await browser.close();server.close();fs.writeFileSync('output/browser/report.json',JSON.stringify(outcomes,null,2));}
 console.log(JSON.stringify({passed:outcomes.length,failed:0,widths:[320,390,1440]}));
})().catch(e=>{console.error(e);server.close();process.exitCode=1;});
