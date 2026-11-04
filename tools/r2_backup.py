"""Private immutable operational backups. Never contains personal browser records."""
import argparse,hashlib,io,json,os,re,shutil,subprocess,tarfile,tempfile,time
from datetime import datetime,timezone
from pathlib import Path
from zoneinfo import ZoneInfo
from refresh import read_current,verify_snapshot
PREFIX='supportpick/v1/'
LIMIT=600*1024*1024

def digest(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
def config(env=os.environ):
 def pick(*names):
  values={env[n] for n in names if env.get(n)}
  if len(values)>1:raise ValueError('ambiguous_r2_configuration')
  return next(iter(values),'')
 account=pick('R2_ACCOUNT_ID');endpoint=pick('SUPPORTPICK_R2_ENDPOINT') or ('https://'+account+'.r2.cloudflarestorage.com' if account else '')
 values={'endpoint_url':endpoint,'aws_access_key_id':pick('SUPPORTPICK_R2_ACCESS_KEY_ID','R2_ACCESS_KEY_ID'),'aws_secret_access_key':pick('SUPPORTPICK_R2_SECRET_ACCESS_KEY','R2_SECRET_ACCESS_KEY'),'bucket':pick('SUPPORTPICK_R2_BUCKET','R2_BUCKET_NAME')}
 missing=[k for k,v in values.items() if not v]
 if missing:raise ValueError('missing_r2_settings:'+','.join(missing))
 if not re.fullmatch(r'https://[a-f0-9]{32}\.r2\.cloudflarestorage\.com/?',endpoint):raise ValueError('invalid_r2_endpoint')
 if not re.fullmatch(r'[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]',values['bucket']):raise ValueError('invalid_r2_bucket')
 return values

def client_and_bucket():
 import boto3
 from botocore.config import Config
 c=config();bucket=c.pop('bucket')
 return boto3.client('s3',region_name='auto',config=Config(signature_version='s3v4',retries={'total_max_attempts':3,'mode':'standard'},connect_timeout=20,read_timeout=120),**c),bucket

def safe_path(name):
 p=Path(name)
 if not name or p.is_absolute() or '..' in p.parts or '\\' in name:raise ValueError('unsafe_backup_path')
 return p

def package(state,evidence,repo,output):
 state,evidence,repo,output=map(Path,(state,evidence,repo,output))
 if not evidence.is_dir() or not any(p.is_file() for p in evidence.rglob('*')):raise ValueError('backup_evidence_missing')
 pointer,snapshot=read_current(state)
 if not pointer:raise ValueError('missing_valid_state')
 for p in (state/'snapshots').iterdir():verify_snapshot(p)
 sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
 if not re.fullmatch(r'[a-f0-9]{40}',sha):raise ValueError('source_revision_invalid')
 output.mkdir(parents=True,exist_ok=False)
 bundle=output/'code.bundle'
 subprocess.run(['git','bundle','create',str(bundle.resolve()),'HEAD'],cwd=repo,check=True,capture_output=True)
 files={'code.bundle':bundle}
 for prefix,root in [('runtime',state),('evidence',evidence)]:
  for p in root.rglob('*'):
   if p.is_symlink():raise ValueError('backup_symlink')
   if p.is_file():files[prefix+'/'+str(p.relative_to(root))]=p
 if len(files)<3 or sum(p.stat().st_size for p in files.values())>LIMIT:raise ValueError('backup_size_limit')
 secrets=[os.environ.get(k,'').encode() for k in ('SUPPORTPICK_GOV24_SERVICE_KEY','GITHUB_TOKEN','SUPPORTPICK_R2_ACCESS_KEY_ID','SUPPORTPICK_R2_SECRET_ACCESS_KEY','R2_ACCESS_KEY_ID','R2_SECRET_ACCESS_KEY') if len(os.environ.get(k,''))>12]
 entries={}
 for name,p in files.items():
  if name!='code.bundle':
   raw=p.read_bytes()
   if any(v in raw for v in secrets):raise ValueError('backup_secret_detected')
  entries[name]={'sha256':digest(p),'bytes':p.stat().st_size}
 now=datetime.now(timezone.utc)
 meta={'version':1,'schemaVersion':1,'generation':pointer['generation'],'collectionSucceededAt':pointer['lastSuccessAt'],'count':pointer['count'],'sourceRevision':sha,'createdUTC':now.isoformat(),'createdKST':now.astimezone(ZoneInfo('Asia/Seoul')).isoformat(),'files':entries}
 archive=output/'backup.tar.gz'
 with tarfile.open(archive,'w:gz') as tar:
  for name,p in sorted(files.items()):tar.add(p,arcname=name,recursive=False)
  raw=json.dumps(meta,ensure_ascii=False,sort_keys=True).encode();info=tarfile.TarInfo('backup-manifest.json');info.size=len(raw);tar.addfile(info,io.BytesIO(raw))
 if archive.stat().st_size>LIMIT:raise ValueError('compressed_backup_size_limit')
 return archive,meta

def download(client,bucket,key,path,expected):
 body=client.get_object(Bucket=bucket,Key=key)['Body'];size=0
 try:
  with Path(path).open('wb') as out:
   while True:
    block=body.read(1024*1024)
    if not block:break
    size+=len(block)
    if size>LIMIT:raise ValueError('download_size_limit')
    out.write(block)
 finally:body.close()
 if digest(path)!=expected:raise ValueError('download_hash_mismatch')

def restore(archive,destination,rebuild=True):
 dest=Path(destination);dest.mkdir(parents=True,exist_ok=False)
 with tarfile.open(archive,'r:gz') as tar:
  members=tar.getmembers();names=[m.name for m in members]
  if len(names)!=len(set(names)) or sum(m.size for m in members)>LIMIT:raise ValueError('archive_size_or_duplicate')
  for m in members:
   safe_path(m.name)
   if not m.isfile():raise ValueError('backup_links_or_special_files')
  meta=json.load(tar.extractfile('backup-manifest.json'))
  if not re.fullmatch(r'[a-f0-9]{40}',meta.get('sourceRevision','')):raise ValueError('source_revision_invalid')
  if meta.get('version')!=1 or meta.get('schemaVersion')!=1 or set(names)!={*meta['files'],'backup-manifest.json'}:raise ValueError('backup_manifest_set')
  for name,entry in meta['files'].items():
   raw=tar.extractfile(name).read()
   if len(raw)!=entry['bytes'] or hashlib.sha256(raw).hexdigest()!=entry['sha256']:raise ValueError('backup_file_hash_mismatch')
   target=dest/safe_path(name);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
 pointer,_=read_current(dest/'runtime')
 if not pointer or pointer['generation']!=meta['generation'] or pointer['count']!=meta['count']:raise ValueError('restored_state_identity')
 if rebuild:
  code=dest/'code'
  subprocess.run(['git','clone','--no-checkout',str((dest/'code.bundle').resolve()),str(code)],check=True,capture_output=True)
  subprocess.run(['git','checkout','--detach',meta['sourceRevision']],cwd=code,check=True,capture_output=True)
  actual=subprocess.check_output(['git','rev-parse','HEAD'],cwd=code,text=True).strip()
  if actual!=meta['sourceRevision']:raise ValueError('restored_code_identity')
  subprocess.run(['python','tools/build.py','--output',str((dest/'site').resolve()),'--state',str((dest/'runtime').resolve()),'--public-base','https://kllollain-max.github.io/supportpick/'],cwd=code,check=True,stdout=subprocess.DEVNULL)
  subprocess.run(['python','tools/verify_release.py','--output',str((dest/'site').resolve())],cwd=code,check=True,stdout=subprocess.DEVNULL)
 return meta

def upload_verify(client,bucket,archive,meta,work,rebuild=True):
 sha=digest(archive);key=PREFIX+'generations/'+meta['generation']+'/'+sha+'.tar.gz'
 try:
  with Path(archive).open('rb') as body:client.put_object(Bucket=bucket,Key=key,Body=body,IfNoneMatch='*',ContentType='application/gzip',Metadata={'sha256':sha})
 except Exception as e:
  if getattr(e,'response',{}).get('Error',{}).get('Code') not in ('PreconditionFailed','412'):raise
 work=Path(work);work.mkdir(parents=True,exist_ok=False)
 download(client,bucket,key,work/'download.tar.gz',sha)
 recovered=restore(work/'download.tar.gz',work/'restored',rebuild)
 if recovered!=meta:raise ValueError('roundtrip_manifest_mismatch')
 receipt={'version':1,'verified':True,'archiveKey':key,'archiveSha256':sha,'generation':meta['generation'],'collectionSucceededAt':meta['collectionSucceededAt'],'sourceRevision':meta['sourceRevision'],'count':meta['count'],'rebuildVerified':rebuild}
 if rebuild:
  payload=json.dumps(receipt,sort_keys=True).encode();receipt_key=PREFIX+'verified/'+hashlib.sha256(payload).hexdigest()+'.json'
  try:client.put_object(Bucket=bucket,Key=receipt_key,Body=payload,IfNoneMatch='*',ContentType='application/json')
  except Exception as e:
   if getattr(e,'response',{}).get('Error',{}).get('Code') not in ('PreconditionFailed','412'):raise
 return receipt

def latest(client,bucket):
 receipts=[]
 for page in client.get_paginator('list_objects_v2').paginate(Bucket=bucket,Prefix=PREFIX+'verified/'):
  for entry in page.get('Contents',[]):
   if entry['Size']>20000:raise ValueError('receipt_size_limit')
   body=client.get_object(Bucket=bucket,Key=entry['Key'])['Body']
   try:r=json.loads(body.read(20001))
   finally:body.close()
   if r.get('verified') and r.get('rebuildVerified') and r.get('version')==1:
    if not re.fullmatch(r'supportpick/v1/generations/[A-Za-z0-9_-]+/[a-f0-9]{64}\.tar\.gz',r.get('archiveKey','')):raise ValueError('receipt_key_invalid')
    receipts.append(r)
    if len(receipts)>100000:raise ValueError('receipt_count_limit')
 if not receipts:raise ValueError('no_verified_backup')
 # No mutable latest pointer: a late old upload can never roll back this ordering.
 return max(receipts,key=lambda r:(datetime.fromisoformat(r['collectionSucceededAt']),r['generation'],r['sourceRevision']))

def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['backup','restore-latest']);p.add_argument('--state',default='runtime-state');p.add_argument('--evidence',default='output/current-run');p.add_argument('--output',required=True);p.add_argument('--restore-state-to');a=p.parse_args()
 report={'status':'failed'}
 try:
  client,bucket=client_and_bucket()
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp)
   if a.action=='backup':
    archive,meta=package(a.state,a.evidence,Path.cwd(),root/'package');report=upload_verify(client,bucket,archive,meta,root/'roundtrip')
   else:
    receipt=latest(client,bucket);download(client,bucket,receipt['archiveKey'],root/'archive.tar.gz',receipt['archiveSha256']);meta=restore(root/'archive.tar.gz',root/'recovery')
    if a.restore_state_to:shutil.copytree(root/'recovery/runtime',a.restore_state_to)
    report={**receipt,'restoreVerified':True}
  report['status']='passed'
 except Exception as e:
  report['errorCode']=str(e) if isinstance(e,ValueError) and re.fullmatch(r'[a-zA-Z0-9_:,.-]{1,180}',str(e)) else type(e).__name__
  report['serviceError']=getattr(e,'response',{}).get('Error',{}).get('Code','')
 finally:
  out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2));print(json.dumps(report))
 if report['status']!='passed':raise SystemExit(1)
if __name__=='__main__':main()
