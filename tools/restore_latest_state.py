"""Restore a trusted main-branch operations artifact, validate before install."""
import io,json,os,re,shutil,tempfile,zipfile
from pathlib import Path
from urllib.request import Request,build_opener,HTTPRedirectHandler
from urllib.parse import urlsplit
from refresh import read_current
from bootstrap_state import ensure_bootstrap
class StripCrossOriginAuth(HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        if urlsplit(newurl).scheme!='https':raise ValueError('unsafe_redirect')
        new=super().redirect_request(req,fp,code,msg,headers,newurl)
        if urlsplit(req.full_url).netloc!=urlsplit(newurl).netloc:new.remove_header('Authorization')
        return new
def latest_completed_operations_run(get,current_run_id):
    # Server-side workflow/branch/status indexes can lag behind the repository history.
    # Read unfiltered history, then enforce all trust conditions locally.
    for page in range(1,11):
        runs=get('/actions/runs?per_page=100&page='+str(page))['workflow_runs']
        eligible=[r for r in runs if r.get('path')=='.github/workflows/supportpick-operations.yml'
            and r.get('head_branch')=='main' and r.get('status')=='completed'
            and r.get('event') in ('schedule','workflow_dispatch') and str(r.get('id'))!=current_run_id]
        if eligible:return max(eligible,key=lambda r:(r.get('created_at',''),r['id']))
        if len(runs)<100:return None
    raise ValueError('operations_history_window_exceeded')
def main():
    ensure_bootstrap('collection-state')
    repo=os.environ.get('GITHUB_REPOSITORY','');token=os.environ.get('GITHUB_TOKEN','')
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',repo) or not token:raise ValueError('missing_runtime_context')
    opener=build_opener(StripCrossOriginAuth())
    def get(path,binary=False):
        req=Request('https://api.github.com/repos/'+repo+path,headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','Cache-Control':'no-cache'})
        with opener.open(req,timeout=60) as r:data=r.read(180*1024*1024+1)
        if len(data)>180*1024*1024:raise ValueError('artifact_size_limit')
        return data if binary else json.loads(data)
    try:run=latest_completed_operations_run(get,os.environ.get('GITHUB_RUN_ID'))
    except Exception:
        raise ValueError('latest_state_lookup_failed') from None
    if run:
        artifacts=get('/actions/runs/'+str(run['id'])+'/artifacts')['artifacts']
        selected=next((a for a in artifacts if a['name']=='supportpick-runtime-state' and not a['expired']),None)
        if not selected:raise ValueError('latest_runtime_state_unavailable')
        raw=get('/actions/artifacts/'+str(selected['id'])+'/zip',binary=True)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            with zipfile.ZipFile(io.BytesIO(raw)) as z:
                if sum(i.file_size for i in z.infolist())>300*1024*1024:raise ValueError('expanded_size_limit')
                for info in z.infolist():
                    p=Path(info.filename)
                    if p.is_absolute() or '..' in p.parts or (info.external_attr>>16)&0o170000==0o120000:raise ValueError('unsafe_artifact_member')
                z.extractall(root)
            pointer,_=read_current(root)
            if not pointer:raise ValueError('artifact_has_no_complete_snapshot')
            if run.get('conclusion')=='success' and pointer['generation']!='gov24-'+str(run['id'])+'-'+str(run.get('run_attempt',1)):
                raise ValueError('successful_run_generation_mismatch')
            destination=Path('collection-state')
            if destination.exists():shutil.rmtree(destination)
            shutil.copytree(root,destination)
            print('Restored validated operations state for generation '+pointer['generation']);return
    print('No earlier trusted operations run; using the validated initial baseline.')
if __name__=='__main__':main()
