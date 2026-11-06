import io,json,sys,tempfile,unittest,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from r2_backup import config,latest,download,safe_path,validate_receipt,restore_verified
from unittest.mock import patch

def receipt(generation='fixture-generation',source='a'*40,day=5):
 sha='a'*64
 return {'version':1,'verified':True,'rebuildVerified':True,'archiveKey':'supportpick/v1/generations/'+generation+'/'+sha+'.tar.gz','archiveSha256':sha,'collectionSucceededAt':f'2026-11-0{day}T10:00:00+09:00','generation':generation,'sourceRevision':source,'count':2}
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
  for day in [5,3,4]:rows.append(receipt(str(day),day=day))
  c=MemoryR2({f'supportpick/v1/verified/{i}.json':json.dumps(r).encode() for i,r in enumerate(rows)})
  self.assertEqual(latest(c,'bucket')['generation'],'5')
 def test_same_generation_uses_backup_time_not_arbitrary_commit_sort(self):
  old={**receipt(source='f'*40),'createdUTC':'2026-11-05T02:00:00+00:00'}
  new={**receipt(source='1'*40),'createdUTC':'2026-11-05T03:00:00+00:00'}
  c=MemoryR2({'supportpick/v1/verified/old.json':json.dumps(old).encode(),'supportpick/v1/verified/new.json':json.dumps(new).encode()})
  self.assertEqual(latest(c,'bucket')['sourceRevision'],'1'*40)
 def test_conflicting_endpoint_and_account_cannot_target_another_bucket_account(self):
  env={'R2_ACCOUNT_ID':'a'*32,'R2_ACCESS_KEY_ID':'id','R2_SECRET_ACCESS_KEY':'key','R2_BUCKET_NAME':'backups','SUPPORTPICK_R2_ENDPOINT':'https://'+'b'*32+'.r2.cloudflarestorage.com'}
  with self.assertRaisesRegex(ValueError,'ambiguous'):config(env)
  env['SUPPORTPICK_R2_ENDPOINT']='https://'+'a'*32+'.r2.cloudflarestorage.com/'
  self.assertTrue(config(env)['endpoint_url'].endswith('/'))
 def test_exact_restore_rejects_wrong_source_and_inconsistent_object_before_network(self):
  client=MemoryR2({})
  with tempfile.TemporaryDirectory() as d,patch.object(client,'get_object') as get:
   with self.assertRaisesRegex(ValueError,'source_expectation'):restore_verified(client,'bucket',receipt(),Path(d)/'wrong-source','b'*40)
   with self.assertRaisesRegex(ValueError,'key_invalid'):restore_verified(client,'bucket',{**receipt(),'archiveKey':'supportpick/v1/generations/other/'+'a'*64+'.tar.gz'},Path(d)/'wrong-key','a'*40)
   get.assert_not_called()
 def test_failed_r2_download_never_falls_back_to_local_archive_or_latest(self):
  client=MemoryR2({})
  with tempfile.TemporaryDirectory() as d,patch('r2_backup.restore') as restore,patch('r2_backup.latest') as choose_latest:
   root=Path(d);(root/'backup.tar.gz').write_bytes(b'existing archive is not an R2 download')
   with self.assertRaises(KeyError):restore_verified(client,'bucket',receipt(),root/'new-workspace','a'*40)
   restore.assert_not_called();choose_latest.assert_not_called()
 def test_receipt_with_unverified_status_bad_count_or_naive_time_is_rejected(self):
  for changes in ({'verified':False},{'rebuildVerified':False},{'status':'failed'},{'count':True},{'count':0},{'collectionSucceededAt':'2026-11-05T10:00:00'}):
   with self.subTest(changes=changes),self.assertRaises(ValueError):validate_receipt({**receipt(),**changes})
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
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);collect(Client(data=rows(2)),root/'evidence','fixture-generation');install_candidate(root/'evidence',root/'state')
   archive,meta=package(root/'state',root/'evidence',Path(__file__).resolve().parents[1],root/'package')
   self.assertEqual(meta['count'],2);self.assertTrue(any(k.startswith('evidence/') for k in meta['files']))
   out=restore(archive,root/'restored',rebuild=False)
   self.assertEqual(out,meta);self.assertEqual(read_current(root/'restored/runtime')[0]['generation'],'fixture-generation')
   # Even a valid archive cannot execute a different source than the upload receipt.
   with patch('r2_backup.subprocess.run') as execute:
    with self.assertRaisesRegex(ValueError,'receipt_restored_identity'):
     restore(archive,root/'wrong-source',expected={**meta,'sourceRevision':'b'*40})
    execute.assert_not_called()
   collect(Client(data=rows(2)),root/'other-evidence','other-generation')
   with self.assertRaisesRegex(ValueError,'evidence_identity'):
    package(root/'state',root/'other-evidence',Path(__file__).resolve().parents[1],root/'bad-package')
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
    def head_object(self,**kw):
     raw=self.objects[kw['Key']]
     return {'ContentLength':len(raw),'Metadata':{'sha256':hashlib.sha256(raw).hexdigest()},'ETag':'"fixture-etag"'}
   store=Store({})
   with patch('r2_backup.restore',side_effect=ValueError('restore_failed')):
    with self.assertRaisesRegex(ValueError,'restore_failed'):upload_verify(store,'bucket',archive,meta,root/'failed')
   self.assertFalse(any('/verified/' in key for key in store.objects))
   # Real local code-bundle checkout, site rebuild and HTML verification;
   # this test store is not evidence of an actual R2 connection.
   uploaded=upload_verify(store,'bucket',archive,meta,root/'roundtrip',True)
   self.assertTrue(uploaded['rebuildVerified']);self.assertEqual(latest(store,'bucket')['generation'],'fixture-generation')
   with patch.object(store,'get_object',wraps=store.get_object) as get:
    exact=restore_verified(store,'bucket',uploaded,root/'fresh-r2-only',meta['sourceRevision'])
    get.assert_called_once_with(Bucket='bucket',Key=uploaded['archiveKey'])
   self.assertTrue(exact['restoreVerified']);self.assertEqual(exact['downloadSource'],'r2')
   self.assertEqual(exact['rebuildSummary']['benefits'],2)
   self.assertEqual(exact['rebuildSummary']['sourceRevision'],meta['sourceRevision'])
   self.assertGreater(exact['rebuildSummary']['validatedUrls'],0)
   with patch.object(store,'head_object',return_value={'ContentLength':0,'Metadata':{'sha256':'wrong'}}):
    with self.assertRaisesRegex(ValueError,'uploaded_object_identity'):
     upload_verify(store,'bucket',archive,meta,root/'wrong-remote')
