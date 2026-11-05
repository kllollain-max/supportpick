"""Bounded publication barrier. Never substitutes the expected release with a remote one."""
import hashlib,json,time
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
BASE='https://kllollain-max.github.io/supportpick/'
class PublicationError(ValueError):
    def __init__(self,code,report):super().__init__(code);self.report=report

def read_public(name):
    # One release URL, no alternate host; ask the cache to revalidate.
    with urlopen(Request(BASE+name,headers={'Cache-Control':'no-cache','User-Agent':'SupportPick-Release-Verification/2.0'}),timeout=30) as r:
        return r.read()

def wait_manifest(local,fetch=read_public,pause=time.sleep,attempts=3):
    observed=[]
    for attempt in range(attempts):
        try:
            remote=json.loads(fetch('site-manifest.json'))
            observation={k:remote.get(k) for k in ('sourceRevision','generation','contentFingerprint')}
            observation['attempt']=attempt+1;observed.append(observation)
            if all(remote.get(k)==local.get(k) for k in ('sourceRevision','generation','contentFingerprint','files')):
                return remote,observed
        except (URLError,TimeoutError,json.JSONDecodeError) as error:
            if isinstance(error,HTTPError) and error.code not in (408,429,500,502,503,504):raise
            observed.append({'attempt':attempt+1,'error':type(error).__name__})
        if attempt+1<attempts:pause(5)
    raise PublicationError('publication_not_converged',{'stage':'publication_barrier','expected':{k:local.get(k) for k in ('sourceRevision','generation','contentFingerprint')},'observations':observed,'failed':1})

def verify_data_release(manifest,fetch=read_public):
    def get(name):
        raw=fetch(name)
        if hashlib.sha256(raw).hexdigest()!=manifest['files'].get(name):
            raise PublicationError('public_data_hash_mismatch',{'stage':'data_consistency','file':name,'failed':1})
        return json.loads(raw)
    feed=get('data.json')
    raw=fetch('data.js')
    if hashlib.sha256(raw).hexdigest()!=manifest['files'].get('data.js'):raise PublicationError('public_data_script_hash_mismatch',{'stage':'data_consistency','file':'data.js','failed':1})
    embedded=raw.decode('utf-8').strip().removeprefix('window.SUPPORTPICK_DATA = ').removesuffix(';')
    if json.loads(embedded)!=feed:raise PublicationError('public_data_pair_mismatch',{'stage':'data_consistency','file':'data.js','failed':1})
    if feed.get('generation')!=manifest['generation']:raise PublicationError('public_data_generation_mismatch',{'stage':'data_consistency','file':'data.json','failed':1})
    base=feed.get('detailBase','')
    if not __import__('re').fullmatch(r'details/[A-Za-z0-9_-]+/',base):raise ValueError('unsafe_detail_base')
    shards=[n for n in manifest['files'] if n.startswith(base) and n.endswith('.json')]
    if not shards:raise ValueError('missing_current_detail_shards')
    ids=set()
    for name in shards:
        payload=get(name)
        if payload.get('generation')!=manifest['generation']:raise PublicationError('mixed_detail_generation',{'stage':'data_consistency','file':name,'failed':1})
        for sid,row in payload['items'].items():
            if sid in ids or row.get('id')!=sid or row.get('generation')!=manifest['generation']:raise ValueError('mixed_or_duplicate_detail_row')
            ids.add(sid)
    if ids!={r['id'] for r in feed['items']}:raise ValueError('public_detail_id_set_mismatch')
    return {'generation':feed['generation'],'currentShards':len(shards),'benefits':len(ids)}
