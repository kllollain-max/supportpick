import io,json,sys,tempfile,unittest,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from r2_backup import config,latest,download,safe_path
class MemoryR2:
 def __init__(self,objects):self.objects=objects
 def get_object(self,**kw):return {'Body':io.BytesIO(self.objects[kw['Key']])}
 def get_paginator(self,_):return self
 def paginate(self,**kw):return [{'Contents':[{'Key':k,'Size':len(v)} for k,v in self.objects.items()]}]
class BackupTests(unittest.TestCase):
 def test_aliases_and_missing_settings(self):
  env={'R2_ACCOUNT_ID':'a'*32,'R2_ACCESS_KEY_ID':'id','R2_SECRET_ACCESS_KEY':'key','R2_BUCKET_NAME':'backups'}
  self.assertEqual(config(env)['bucket'],'backups')
  env['SUPPORTPICK_R2_ACCESS_KEY_ID']='other'
  with self.assertRaisesRegex(ValueError,'ambiguous'):config(env)
  with self.assertRaisesRegex(ValueError,'missing'):config({})
 def test_late_old_receipt_never_overwrites_latest_collection(self):
  rows=[]
  for day in [5,3,4]:rows.append({'version':1,'verified':True,'rebuildVerified':True,'archiveKey':'supportpick/v1/generations/g/'+('a'*64)+'.tar.gz','collectionSucceededAt':f'2026-11-0{day}T10:00:00+09:00','generation':str(day),'sourceRevision':'a'*40})
  c=MemoryR2({f'{i}.json':json.dumps(r).encode() for i,r in enumerate(rows)})
  self.assertEqual(latest(c,'bucket')['generation'],'5')
 def test_download_corruption_is_not_a_verified_backup(self):
  with tempfile.TemporaryDirectory() as d:
   c=MemoryR2({'x':b'corrupt'})
   with self.assertRaisesRegex(ValueError,'hash'):download(c,'b','x',Path(d)/'out','expected')
 def test_traversal_and_absolute_paths_rejected(self):
  for name in ['/etc/passwd','../bad','runtime/../../bad','a\\b']:
   with self.assertRaises(ValueError):safe_path(name)
