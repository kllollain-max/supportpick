"""Download only the same repository's named official collection evidence."""
import io,json,os,tempfile,zipfile
from pathlib import Path
from urllib.request import Request,build_opener
from restore_latest_state import StripCrossOriginAuth,latest_completed_operations_run

def main():
 repo=os.environ['GITHUB_REPOSITORY'];token=os.environ['GITHUB_TOKEN'];opener=build_opener(StripCrossOriginAuth())
 if repo!='kllollain-max/supportpick':raise ValueError('wrong_backup_repository')
 def get(path,binary=False):
  with opener.open(Request('https://api.github.com/repos/'+repo+path,headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json'}),timeout=120) as r:raw=r.read(180*1024*1024+1)
  if len(raw)>180*1024*1024:raise ValueError('evidence_archive_size')
  return raw if binary else json.loads(raw)
 run=latest_completed_operations_run(get,os.environ.get('GITHUB_RUN_ID'))
 if not run:raise ValueError('no_evidence_run')
 artifacts=get('/actions/runs/'+str(run['id'])+'/artifacts')['artifacts']
 choices=[a for a in artifacts if a['name'].startswith('supportpick-collection-evidence-') and not a['expired']]
 if len(choices)!=1:raise ValueError('evidence_artifact_missing_or_ambiguous')
 raw=get('/actions/artifacts/'+str(choices[0]['id'])+'/zip',True)
 destination=Path('output/current-run');destination.mkdir(parents=True,exist_ok=False)
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  if sum(i.file_size for i in z.infolist())>300*1024*1024:raise ValueError('evidence_expanded_size')
  for i in z.infolist():
   p=Path(i.filename)
   if p.is_absolute() or '..' in p.parts or (i.external_attr>>16)&0o170000==0o120000:raise ValueError('unsafe_evidence_member')
  z.extractall(destination)
 print(json.dumps({'evidenceRun':run['id'],'evidenceArtifact':choices[0]['id']}))
if __name__=='__main__':main()
