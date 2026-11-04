import sys,json,hashlib,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from publication import wait_manifest,verify_data_release,PublicationError
class PublicationTests(unittest.TestCase):
 def release(self):return {'sourceRevision':'a'*40,'generation':'new','contentFingerprint':'x','files':{'data.json':'one'}}
 def test_previous_generation_cannot_pass_but_bounded_propagation_can(self):
  local=self.release();old={**local,'generation':'old'};values=iter([old,old,local]);pauses=[]
  remote,history=wait_manifest(local,lambda _:json.dumps(next(values)),pauses.append)
  self.assertEqual(remote,local);self.assertEqual([r['generation'] for r in history],['old','old','new']);self.assertEqual(pauses,[5,5])
 def test_persistent_generation_code_and_file_mismatch_never_become_expected(self):
  local=self.release()
  for key,value in [('generation','old'),('sourceRevision','b'*40),('files',{})]:
   with self.assertRaises(PublicationError) as caught:wait_manifest(local,lambda _:json.dumps({**local,key:value}),lambda _:None)
   self.assertEqual(caught.exception.report['expected']['generation'],'new');self.assertEqual(len(caught.exception.report['observations']),3)
 def test_data_and_current_shards_must_have_identical_ids_and_generation(self):
  files={'data.json':{'generation':'g','detailBase':'details/g/','items':[{'id':'1'}]},'details/g/00.json':{'generation':'g','items':{'1':{'id':'1','generation':'g'}}}}
  raw={k:json.dumps(v).encode() for k,v in files.items()};m={'generation':'g','files':{k:hashlib.sha256(v).hexdigest() for k,v in raw.items()}}
  self.assertEqual(verify_data_release(m,raw.__getitem__)['benefits'],1)
  files['details/g/00.json']['generation']='old';raw['details/g/00.json']=json.dumps(files['details/g/00.json']).encode();m['files']['details/g/00.json']=hashlib.sha256(raw['details/g/00.json']).hexdigest()
  with self.assertRaisesRegex(PublicationError,'mixed_detail_generation'):verify_data_release(m,raw.__getitem__)
 def test_wrong_body_hash_is_an_error_not_a_retry_success(self):
  with self.assertRaisesRegex(PublicationError,'hash_mismatch'):verify_data_release({'files':{'data.json':'wrong'}},lambda _:b'{}')
