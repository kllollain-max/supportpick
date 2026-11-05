import io,json,sys,tempfile,unittest,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from r2_backup import config,latest,download,safe_path
class MemoryR2:
 def __init__(self,objects):self.objects=objects
 def get_object(self,**kw):return {'Body':io.BytesIO(self.objects[kw['Key']])}
 def get_paginator(self,_):return self
 def paginate(self,**kw):return [{'Contents':[{'Key':k,'Size':len(v)} for k,v in self.objects.items() if k.startswith(kw.get('Prefix',''))]}]
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
  c=MemoryR2({f'supportpick/v1/verified/{i}.json':json.dumps(r).encode() for i,r in enumerate(rows)})
  self.assertEqual(latest(c,'bucket')['generation'],'5')
 def test_download_corruption_is_not_a_verified_backup(self):
  with tempfile.TemporaryDirectory() as d:
   c=MemoryR2({'x':b'corrupt'})
   with self.assertRaisesRegex(ValueError,'hash'):download(c,'b','x',Path(d)/'out','expected')
 def test_traversal_and_absolute_paths_rejected(self):
  for name in ['/etc/passwd','../bad','runtime/../../bad','a\\b']:
   with self.assertRaises(ValueError):safe_path(name)

class RoundtripTests(unittest.TestCase):
 def test_package_roundtrip_hashes_state_code_and_evidence_and_refuses_tampering(self):
  import tarfile
  from test_collection import Client,rows
  from collect_full import collect
  from refresh import install_candidate,read_current
  from r2_backup import package,restore,upload_verify
  from unittest.mock import patch
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);collect(Client(data=rows(2)),root/'evidence','fixture-generation');install_candidate(root/'evidence',root/'state')
   archive,meta=package(root/'state',root/'evidence',Path(__file__).resolve().parents[1],root/'package')
   self.assertEqual(meta['count'],2);self.assertTrue(any(k.startswith('evidence/') for k in meta['files']))
   out=restore(archive,root/'restored',rebuild=False)
   self.assertEqual(out,meta);self.assertEqual(read_current(root/'restored/runtime')[0]['generation'],'fixture-generation')
   # A valid archive envelope cannot hide a changed source file.
   tampered=root/'tampered.tar.gz'
   with tarfile.open(archive) as src,tarfile.open(tampered,'w:gz') as dst:
    for entry in src.getmembers():
     raw=src.extractfile(entry).read()
     if entry.name=='runtime/current.json':raw+=b' '
     entry.size=len(raw);dst.addfile(entry,io.BytesIO(raw))
   with self.assertRaisesRegex(ValueError,'file_hash'):restore(tampered,root/'bad',False)
   class Store(MemoryR2):
    def put_object(self,**kw):
     body=kw['Body'];self.objects[kw['Key']]=body.read() if hasattr(body,'read') else body
   store=Store({})
   with patch('r2_backup.restore',side_effect=ValueError('restore_failed')):
    with self.assertRaisesRegex(ValueError,'restore_failed'):upload_verify(store,'bucket',archive,meta,root/'failed')
   self.assertFalse(any('/verified/' in key for key in store.objects))
   # Real local code-bundle checkout, site rebuild and HTML verification;
   # this test store is not evidence of an actual R2 connection.
   receipt=upload_verify(store,'bucket',archive,meta,root/'roundtrip',True)
   self.assertTrue(receipt['rebuildVerified']);self.assertEqual(latest(store,'bucket')['generation'],'fixture-generation')
