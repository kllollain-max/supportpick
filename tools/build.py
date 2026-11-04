"""Build an allowlisted site from an integrity-checked immutable generation."""
import argparse,hashlib,json,os,posixpath,re,shutil,subprocess
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote,quote
from refresh import read_current,verify_snapshot
from bootstrap_state import ensure_bootstrap
from search_metadata import public_metadata, read_verifications, write_sitemap, version_local_assets
from detail_pages import write_details
from release_policy import fingerprint
from collect_full import period
ROOT=Path(__file__).resolve().parents[1]
STATIC=('index.html','privacy.html','about.html','terms.html','contact.html','404.html','icon.svg','careerpick-base.css','styles.css','core.js','app.js','detail.js','supportpick-badge.png','supportpick-banner.png','editorials.js','app-features.js','manifest.webmanifest','sw.js','offline.html','app-icon-180.png','app-icon-192.png','app-icon-512.png')
class Links(HTMLParser):
    def __init__(self,output,page,available=None):super().__init__();self.output=output;self.page=page;self.available=available
    def handle_starttag(self,tag,attrs):
        for key,value in attrs:
            if key not in ('href','src') or not value or urlsplit(value).scheme or value.startswith('#'):continue
            path=urlsplit(value).path
            if self.available is not None:
                relative=posixpath.normpath(posixpath.join(str(self.page.parent.relative_to(self.output)),unquote(path)))
                if relative=='.':relative='index.html'
                if relative.startswith('../') or relative.startswith('/') or not (relative in self.available or relative+'/index.html' in self.available):
                    raise ValueError('missing_or_unsafe_local_asset:'+str(self.page.relative_to(self.output))+':'+path)
                continue
            target=(self.page.parent/unquote(path)).resolve() if path else self.page
            if target.is_dir():target=target/'index.html'
            if not target.is_file() or not target.is_relative_to(self.output):raise ValueError('missing_or_unsafe_local_asset:'+str(self.page.relative_to(self.output))+':'+path)
def build(destination,state=None,allow_sample=False,public_base=None):
    output=Path(destination).resolve()
    if output==ROOT or ROOT.is_relative_to(output) or (output.is_relative_to(ROOT) and output!=ROOT/'dist'):raise ValueError('unsafe_output_directory')
    if output.exists() and any(output.iterdir()):raise ValueError('output_not_empty')
    state=Path(state or ROOT/'collection-state')
    if state.resolve()==(ROOT/'collection-state').resolve():ensure_bootstrap(state)
    pointer,snapshot=read_current(state)
    if public_base:
        parsed=urlsplit(public_base)
        if parsed.scheme!='https' or parsed.hostname!='kllollain-max.github.io' or parsed.path!='/supportpick/' or parsed.query or parsed.fragment:raise ValueError('unapproved_public_base')
    if not pointer and not allow_sample:raise ValueError('complete_snapshot_required')
    source=snapshot or ROOT
    feed=verify_snapshot(snapshot) if snapshot else json.loads((ROOT/'data.json').read_text())
    if pointer and (feed.get('isSample') is not False or len(feed['items'])!=pointer['count']):raise ValueError('sample_not_operational')
    verifications=read_verifications(ROOT/'search-verification.json') if public_base else {}
    output.mkdir(parents=True,exist_ok=True)
    for name in STATIC:
        p=ROOT/name
        if p.is_symlink() or not p.is_file():raise ValueError('unsafe_static_source')
        shutil.copyfile(p,output/name)
        if public_base and name.endswith('.html'):
            text=(output/name).read_text().replace('content="noindex,nofollow"','content="index,follow"')
            text=text.replace('<span class="preview-tag">미리보기</span>','').replace(' · 공개 전 미리보기','')
            if name in ('404.html','offline.html'):text=text.replace('content="index,follow"','content="noindex,follow"')
            else:text=public_metadata(text,name,public_base,verifications)
            (output/name).write_text(text)
    registry=json.loads((ROOT/'editorials.json').read_text())
    if registry.get('version')!=1 or not isinstance(registry.get('articles'),list):raise ValueError('invalid_editorial_registry')
    registry_json=json.dumps(registry,ensure_ascii=False,separators=(',',':'))
    (output/'editorial-data.js').write_text('window.SUPPORTPICK_EDITORIALS = '+registry_json.replace('<','\\u003c')+';\n')
    fields={'id','title','organization','category','region','regionBasis','audience','supportType','supportTypes','summary','targetPreview','period','periodKind','startDate','endDate','officialUrl','officialLinkStatus','source','sourceUpdatedAt','checkedAt','detailShard','sourceConflicts'}
    # Keep exact classification conflicts visible and reviewable in both cards and details.
    source_differences={};full_rows={}
    if snapshot:
        for shard_path in (snapshot/'details'/feed['generation']).glob('*.json'):
            shard=json.loads(shard_path.read_text())
            for sid,row in shard['items'].items():
                raw=row.get('rawSource',{})
                source_differences[sid]={key:{'list':raw.get('serviceList',{}).get(key),'detail':raw.get('serviceDetail',{}).get(key)} for key in row.get('sourceConflicts',[])}
                full_rows[sid]={**row,**period(row.get('period','')),'sourceDifferences':source_differences[sid]}
    public_feed={**feed,'items':[{**{k:v for k,v in row.items() if k in fields},**period(row.get('period','')),'sourceDifferences':source_differences.get(row['id'],{})} for row in feed['items']]}
    public_json=json.dumps(public_feed,ensure_ascii=False,separators=(',',':'))
    (output/'data.json').write_text(public_json)
    (output/'data.js').write_text('window.SUPPORTPICK_DATA = '+public_json.replace('<','\\u003c')+';\n')
    generations=[];previous_rows={}
    if snapshot:
        candidates=[snapshot]+sorted((state/'snapshots').iterdir(),key=lambda x:x.name,reverse=True)
        for candidate in candidates:
            if candidate in generations or candidate.name.startswith('.') or not candidate.is_dir():continue
            verify_snapshot(candidate);generations.append(candidate)
            details=candidate/'details'
            if details.exists():
                for shard_path in details.rglob('*.json'):
                    shard=json.loads(shard_path.read_text());public_rows={}
                    for sid,row in shard['items'].items():
                        if candidate!=snapshot:previous_rows[sid]=row
                        public={**{k:v for k,v in row.items() if k!='rawSource'},**period(row.get('period',''))}
                        raw=row.get('rawSource',{})
                        public['sourceDifferences']={key:{'list':raw.get('serviceList',{}).get(key),'detail':raw.get('serviceDetail',{}).get(key)} for key in row.get('sourceConflicts',[])}
                        public_rows[sid]=public
                    target=output/'details'/shard_path.relative_to(details);target.parent.mkdir(parents=True,exist_ok=True)
                    target.write_text(json.dumps({'generation':shard['generation'],'items':public_rows},ensure_ascii=False,separators=(',',':')))
            if len(generations)==2:break
    status=json.loads((state/'status.json').read_text()) if (state/'status.json').exists() else {'status':'preview','generation':feed.get('generation'),'lastSuccessAt':feed.get('updatedAt'),'count':len(feed['items'])}
    (output/'status.json').write_text(json.dumps(status,ensure_ascii=False));(output/'.nojekyll').write_text('')
    guides=json.loads((ROOT/'guides.json').read_text())
    if guides.get('version')!=1 or not isinstance(guides.get('guides'),list):raise ValueError('invalid_own_guide_registry')
    detail=write_details(output,full_rows,previous_rows,public_base,guides,registry,status['status'])
    home=(output/'index.html').read_text()
    home=home.replace('<!-- STATIC_DISCOVERY -->',detail['home'])
    (output/'index.html').write_text(home)
    if public_base:write_sitemap(output,public_base,detail['entries'])
    (output/'search-report.json').write_text(json.dumps(detail['report'],ensure_ascii=False,indent=2))
    # Invalidate only our generic offline shell when its actual assets change.
    shell_hash=hashlib.sha256(b''.join((output/name).read_bytes() for name in ('offline.html','app-icon-192.png','app-icon-512.png'))).hexdigest()[:16]
    worker=output/'sw.js'
    worker.write_text(worker.read_text().replace('__SHELL_HASH__',shell_hash))
    secret=os.environ.get('SUPPORTPICK_GOV24_SERVICE_KEY','')
    secret_variants={secret,unquote(secret),quote(unquote(secret),safe=''),quote(quote(unquote(secret),safe=''),safe='')}-{''}
    forbidden=re.compile(r'gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|(?:servicekey|access_token|authorization)=',re.I)
    files={}
    public_paths=sorted(p for p in output.rglob('*') if p.is_file())
    available={str(p.relative_to(output)) for p in public_paths}
    assets={str(p.relative_to(output)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in public_paths if p.suffix in ('.css','.js','.png','.svg')}
    for p in public_paths:
        if not p.is_file():continue
        if p.is_symlink() or p.stat().st_nlink!=1:raise ValueError('linked_public_file')
        raw=p.read_bytes()
        if p.suffix=='.html':
            versioned=version_local_assets(raw.decode('utf-8'),str(p.relative_to(output)),assets)
            p.write_text(versioned,encoding='utf-8')
            raw=versioned.encode('utf-8')
        # Scan ASCII secret patterns in binary images without treating PNG bytes as UTF-8 documents.
        text=raw.decode('utf-8',errors='ignore')
        if forbidden.search(text) or any(s in text for s in secret_variants):raise ValueError('public_secret_pattern_detected')
        if p.suffix=='.png' and not raw.startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError('invalid_public_png')
        if p.suffix=='.html':
            text=raw.decode('utf-8')
            # GitHub's custom 404 must work from arbitrary missing nested paths.
            if p.name!='404.html':Links(output,p,available).feed(text)
            allowed=('index,follow','noindex,follow') if public_base else ('noindex,nofollow',)
            if not any('<meta name="robots" content="'+expected+'">' in text for expected in allowed):raise ValueError('indexing_policy_mismatch')
        files[str(p.relative_to(output))]=hashlib.sha256(raw).hexdigest()
    size=sum(p.stat().st_size for p in output.rglob('*') if p.is_file())
    if size>300*1024*1024:raise ValueError('public_size_budget')
    revision=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True,check=True).stdout.strip()
    report={'publicFiles':len(files)+1,'bytes':size,'benefits':len(feed['items']),'generation':feed.get('generation'),'sourceRevision':revision,'isSample':not bool(pointer),'published':False,'status':status['status'],**{k:v for k,v in detail['report'].items() if k in ('detailPages','indexableDetails','heldDetails','reviewedGuides','blogLinks','directoryPages','retiredPages')},'files':files}
    report['contentFingerprint']=fingerprint(ROOT,feed,full_rows,previous_rows,status,detail['report'],STATIC)
    (output/'site-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    return {k:v for k,v in report.items() if k!='files'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--state');p.add_argument('--allow-sample',action='store_true');p.add_argument('--public-base');args=p.parse_args()
    print(json.dumps(build(args.output,args.state,args.allow_sample,args.public_base),ensure_ascii=False,indent=2))
