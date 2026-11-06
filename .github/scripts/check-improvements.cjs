/* Isolated browser regression; fresh contexts contain synthetic personal records only. */
const {chromium}=require('playwright');
const {createServer}=require('node:http');
const fs=require('node:fs');const path=require('node:path');const assert=require('node:assert/strict');
const root=path.resolve('dist');const outcomes=[];
const liveBase=process.env.SUPPORTPICK_QA_BASE||'';
if(liveBase&&liveBase!=='https://kllollain-max.github.io/supportpick/')throw Error('unexpected QA origin');
const mime={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json','.css':'text/css','.png':'image/png','.svg':'image/svg+xml'};
const server=createServer((req,res)=>{
 let p=path.resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://local').pathname));
 if(!p.startsWith(root+path.sep)&&p!==root){res.writeHead(403).end();return;}
 if(fs.existsSync(p)&&fs.statSync(p).isDirectory())p=path.join(p,'index.html');
 if(!fs.existsSync(p)){res.writeHead(404).end('missing');return;}
 res.setHeader('Content-Type',mime[path.extname(p)]||'application/octet-stream');fs.createReadStream(p).pipe(res);
});
(async()=>{
 if(!liveBase)await new Promise(r=>server.listen(0,'127.0.0.1',r));const base=liveBase||'http://127.0.0.1:'+server.address().port+'/';
 const browser=await chromium.launch({headless:true});fs.mkdirSync('output/browser',{recursive:true});
 try{
  for(const width of [320,390,1440]){
   const context=await browser.newContext({viewport:{width,height:900},timezoneId:'Asia/Seoul',serviceWorkers:'block'});
   await context.route('**/*',route=>new URL(route.request().url()).origin===new URL(base).origin?route.continue():route.abort());
   await context.addInitScript(()=>{if(!['http:','https:'].includes(location.protocol))return;if(!localStorage.getItem('supportpick:records:v1'))localStorage.setItem('supportpick:records:v1',JSON.stringify({version:1,revision:1,saved:['QA_OLD'],apps:{QA_OLD:{title:'검사용 이전 기록',note:'보존할 메모',stage:'서류 준비',updatedAt:'2026-11-04T00:00:00Z'}},prefs:{region:'',category:''}}));localStorage.setItem('careerpick:qa-sentinel','unchanged');});
   const errors=[],consoleErrors=[];
   context.on('page',p=>{p.on('pageerror',e=>errors.push(e.message));p.on('console',m=>{if(m.type()==='error')consoleErrors.push(m.text());});});
   const page=await context.newPage();
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
   const newId=await first.locator('[data-track]').getAttribute('data-track');
   await first.locator('[data-track]').click();assert.ok(await page.locator('[data-app-form]').count()>=2);
   assert.equal(await page.locator('[data-app-form="QA_OLD"] textarea').inputValue(),'보존할 메모');check('saved and application records');
   const form=page.locator('[data-app-form="'+newId+'"]');
   const readRecords=()=>page.evaluate(()=>JSON.parse(localStorage.getItem('supportpick:records:v1')));
   assert.equal(await form.locator('[type=submit]').isEnabled(),false);
   const cleanRevision=(await readRecords()).revision;
   await form.locator('textarea').fill('변경');assert.equal(await form.locator('[type=submit]').isEnabled(),true);
   await form.locator('textarea').fill('');assert.equal(await form.locator('[type=submit]').isEnabled(),false);
   assert.equal((await readRecords()).revision,cleanRevision);check('only changed fields enable saving');
   await form.locator('textarea').fill('새 신청의 검증 메모');await form.locator('select').selectOption('서류 준비');await form.locator('[type=submit]').click();
   await page.reload();await page.locator('[data-tab=apps]').click();assert.equal(await form.locator('textarea').inputValue(),'새 신청의 검증 메모');assert.equal(await form.locator('select').inputValue(),'서류 준비');check('application create edit and reload persistence');
   const preserved=await readRecords();
   const remove=form.locator('[data-delete-app]');await remove.scrollIntoViewIfNeeded();const box=await remove.boundingBox();assert.ok(box&&box.x>=0&&box.x+box.width<=width+1&&box.y>=0&&box.y+box.height<=900,'delete control must be visible');
   await page.screenshot({path:'output/browser/applications-'+width+'.png',fullPage:false});
   page.once('dialog',async d=>{assert.equal(d.type(),'confirm');assert.match(d.message(),/신청 기록을 삭제/);await d.dismiss();});await remove.click();assert.deepEqual(await readRecords(),preserved);check('cancel delete retains exact records');
   page.once('dialog',async d=>{assert.equal(d.type(),'confirm');await d.accept();});await remove.click();assert.equal(await form.count(),0);
   const after=await readRecords();assert.equal(Object.hasOwn(after.apps,newId),false);assert.deepEqual(after.apps.QA_OLD,preserved.apps.QA_OLD);assert.deepEqual(after.saved,preserved.saved);assert.deepEqual(after.prefs,preserved.prefs);
   await page.reload();await page.locator('[data-tab=all]').click();await page.locator('[data-tab=apps]').click();assert.equal(await form.count(),0);
   const reopened=await context.newPage();await reopened.goto(base);await reopened.locator('[data-tab=apps]').click();assert.equal(await reopened.locator('[data-app-form="'+newId+'"]').count(),0);await reopened.close();
   const resumed=await context.newPage();await resumed.goto(base);await resumed.locator('[data-tab=apps]').click();
   const storedBeforeFailure=await resumed.evaluate(()=>localStorage.getItem('supportpick:records:v1'));
   await resumed.evaluate(()=>{const original=Storage.prototype.setItem;Storage.prototype.setItem=function(key,value){if(key==='supportpick:records:v1')throw new DOMException('Synthetic full storage','QuotaExceededError');return original.call(this,key,value);};});
   await resumed.locator('[data-app-form="QA_OLD"] textarea').fill('저장 실패를 검증하는 메모');await resumed.locator('[data-app-form="QA_OLD"] [type=submit]').click();
   assert.equal(await resumed.evaluate(()=>localStorage.getItem('supportpick:records:v1')),storedBeforeFailure);assert.match(await resumed.locator('#storageWarning').innerText(),/저장.*확인하지 못/);assert.doesNotMatch(await resumed.locator('#toast').innerText(),/저장했어요/);
   await resumed.close();check('delete persists across reload navigation and reopening; failures preserve records');
   await page.locator('[data-tab=all]').click();const card=page.locator('.benefit-card').first();const href=await card.locator('h3 a').getAttribute('href');
   // Click the non-title summary, which is covered by the native stretched link.
   await card.locator('.card-summary').evaluate(el=>el.scrollIntoView({block:'center'}));const hit=await card.locator('.card-summary').boundingBox();assert.ok(hit);await page.mouse.click(hit.x+hit.width/2,hit.y+hit.height/2);await page.waitForURL('**/'+href);await page.reload();assert.equal(await page.locator('h1').count(),1);assert.ok((await page.locator('main').innerText()).length>300);await page.goBack();await page.goto(base);check('whole-card detail, direct URL and refresh');
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
   assert.deepEqual(errors,[]);assert.deepEqual(consoleErrors,[]);check('no page or console errors');
   await context.close();
  }
 }finally{await browser.close();server.close();fs.writeFileSync('output/browser/report.json',JSON.stringify(outcomes,null,2));}
 console.log(JSON.stringify({passed:outcomes.length,failed:0,widths:[320,390,1440],base,environment:'Linux Chromium viewport emulation; not actual phone OS installation'}));
})().catch(e=>{console.error(e);server.close();process.exitCode=1;});
