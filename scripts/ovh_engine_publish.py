#!/usr/bin/python3
"""Root-owned, fixed-scope static starter asset publisher for Debian/Linux.
Never executes repository code or accepts a user-supplied path or command."""
import ctypes, fcntl, hashlib, json, os, re, shutil, stat, sys, tempfile, time
from pathlib import Path
LIVE=Path('/var/www/swrlz-engine')
HISTORY=Path('/var/www/.swrlz-engine-releases')
PAYLOAD=Path('/srv/swrlz/source/.deploy/engine-uv/payload')
LIMIT=16*1024*1024
RUNTIME_PAYLOAD=Path('/srv/swrlz/source/.deploy/engine-runtime/payload')
SEALED_SOURCE='3fe29516958ea5af2448352fa238eda121cc3031266c61c746380f092d22232e'
SCOPED='.swrlz-starter-receipt.json'
BOOTSTRAP_BASELINE={"scenes/model-atelier-clean-topology-humanoid-v11-554.swyrl.json":"6ef0e683f98c12323129d42cc282983d662939b2","assets/models/clean-topology-humanoid-v11-554-uv-test.png":"e25bf0858a7b9bba9c0fe3d736abe6b9183c7770","assets/models/clean-topology-humanoid-v11-554-uv-guide-2048.png":"d5487d6b3175e3b208d9af6ac07105f74453841f"}
HEX=re.compile(r'^[0-9a-f]{64}$')
GITHEX=re.compile(r'^[0-9a-f]{40}$')
ALLOWED=re.compile(r'^(?:scenes/model-atelier-[A-Za-z0-9_.-]+\.swyrl\.json|assets/models/[A-Za-z0-9_.-]+\.(?:png|jpg|jpeg|webp|json|glb|obj|mtl))$')
def require(cond,msg):
    if not cond: raise RuntimeError(msg)
def digest(data): return hashlib.sha256(data).hexdigest()
def blob(data): return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def safe_read(path,limit=LIMIT):
    # Each component is opened without following symlinks, including parent directories.
    fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY)
    try:
        for part in path.parts[1:-1]:
            child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
            os.close(fd);fd=child
        flags=os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK
        f=os.open(path.name,flags,dir_fd=fd)
        with os.fdopen(f,'rb') as stream:
            st=os.fstat(stream.fileno())
            require(stat.S_ISREG(st.st_mode) and st.st_size<=limit,'Invalid/oversize file: '+path.name)
            data=stream.read(limit+1)
            require(len(data)<=limit,'File exceeds limit')
            return data
    finally: os.close(fd)
def check_root():
    require(os.geteuid()==0,'Root helper required')
    for p in (LIVE,HISTORY):
        s=p.lstat()
        require(stat.S_ISDIR(s.st_mode) and s.st_uid==0 and not s.st_mode&0o022,'Unsafe managed directory: '+str(p))
    require(LIVE.stat().st_dev==HISTORY.stat().st_dev,'Atomic exchange requires same filesystem')
    for root,dirs,files in os.walk(LIVE,followlinks=False):
        for name in dirs+files:
            p=Path(root)/name; s=p.lstat()
            require((stat.S_ISREG(s.st_mode) or stat.S_ISDIR(s.st_mode)) and not s.st_mode&0o022 and s.st_uid==0,'Untrusted live path: '+str(p))
def exchange(a,b):
    libc=ctypes.CDLL(None,use_errno=True)
    fn=libc.renameat2
    fn.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_uint]
    fn.restype=ctypes.c_int
    if fn(-100,os.fsencode(a),-100,os.fsencode(b),2):
        e=ctypes.get_errno();raise OSError(e,os.strerror(e))
def write_atomic(p,data,mode=0o644):
    fd,name=tempfile.mkstemp(prefix='.next-',dir=p.parent)
    try:
        with os.fdopen(fd,'wb') as f:
            f.write(data);f.flush();os.fsync(f.fileno())
        os.chmod(name,mode);os.replace(name,p)
    finally:
        if os.path.exists(name):os.unlink(name)
def receipt_path(root):
    # Preserve a genuine packaged source receipt if present; otherwise use
    # explicitly scoped local provenance. Never invent a sealed engine receipt.
    return root/'SOURCE.json' if os.path.lexists(root/'SOURCE.json') else root/SCOPED
def read_receipt(root):
    return json.loads(safe_read(receipt_path(root),4*1024*1024))
def initialize():
    # Administrator-only bootstrap. The SSH deployment account is NOT
    # authorized to invoke this operation or to bless an unknown baseline.
    if os.path.lexists(receipt_path(LIVE)):
        r=read_receipt(LIVE)
        for rel in BOOTSTRAP_BASELINE:
            data=safe_read(LIVE/rel)
            rec=r['assets'][rel]
            require(rec['bytes']==len(data) and rec['sha256']==digest(data),'Existing receipt differs from live asset: '+rel)
        print('SWRLZ_ENGINE_RECEIPT_PRESENT',flush=True)
        return
    records={}
    for rel,expected in BOOTSTRAP_BASELINE.items():
        data=safe_read(LIVE/rel)
        actual=blob(data)
        require(actual==expected,'Live asset baseline mismatch: '+rel+' expected='+expected+' actual='+actual)
        records[rel]={'sha256':digest(data),'bytes':len(data)}
        print('SWRLZ_ENGINE_BASELINE_OK '+rel,flush=True)
    receipt={'schema':'swrlz-ovh-local-starter-baseline-v1','scope':'Only the three verified starter assets; not an engine build receipt','baselineCommit':'65476cd927d504b8eac8b5cb6d426235a54907b9','assets':records}
    write_atomic(LIVE/SCOPED,(json.dumps(receipt,indent=2)+'\n').encode())
    print('SWRLZ_ENGINE_LOCAL_RECEIPT_CREATED',flush=True)
def verify(root,assets,receipt):
    for rel,meta in assets.items():
        data=safe_read(root/rel)
        require(len(data)==meta['bytes'] and digest(data)==meta['sha256'],'Readback mismatch: '+rel)
        rec=receipt['assets'][rel]
        require(rec['bytes']==len(data) and rec['sha256']==digest(data),'SOURCE.json mismatch: '+rel)
def deploy():
    m=json.loads(safe_read(PAYLOAD/'manifest.json',256*1024))
    require(m.get('schema')=='swrlz-engine-uv-overlay-v1' and m.get('target')==str(LIVE),'Invalid manifest')
    assets=m['assets']
    require(isinstance(assets,dict) and 1<=len(assets)<=32,'Invalid asset count')
    receipt=read_receipt(LIVE)
    staged={};already=0;total=0
    for rel,meta in assets.items():
        require(ALLOWED.fullmatch(rel) is not None and '..' not in rel.split('/'),'Path not authorized: '+rel)
        require(type(meta['bytes']) is int and 0<meta['bytes']<=LIMIT and HEX.fullmatch(meta['sha256']) and GITHEX.fullmatch(meta['baselineGitBlobSha1']),'Invalid integrity record')
        data=safe_read(PAYLOAD/'overlay'/rel)
        require(len(data)==meta['bytes'] and digest(data)==meta['sha256'],'Staged asset mismatch: '+rel)
        total+=len(data);require(total<=64*1024*1024,'Overlay exceeds 64 MiB')
        old=safe_read(LIVE/rel)
        current=receipt['assets'][rel]
        require(current['sha256']==digest(old) and current['bytes']==len(old),'Live SOURCE.json mismatch: '+rel)
        if digest(old)==meta['sha256']:already+=1
        else:require(blob(old)==meta['baselineGitBlobSha1'],'Baseline changed: '+rel)
        staged[rel]=data
    if already==len(assets):
        verify(LIVE,assets,receipt);print('SWRLZ_ENGINE_DEPLOY_OK already-current');return
    require(already==0,'Mixed release state; manual inspection required')
    stage=Path(tempfile.mkdtemp(prefix='candidate-',dir=HISTORY))
    stage.rmdir()
    swapped=False
    try:
        shutil.copytree(LIVE,stage,symlinks=True,copy_function=shutil.copy2)
        for rel,data in staged.items():
            p=stage/rel
            write_atomic(p,data,stat.S_IMODE(p.stat().st_mode))
            receipt['assets'][rel].update(sha256=digest(data),bytes=len(data))
        receipt['ovhStarterOverlay']={'candidateCommit':m.get('candidateCommit'),'browserRun':m.get('browserRun'),'assets':list(staged),'publishedAt':int(time.time())}
        write_atomic(receipt_path(stage),(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n').encode())
        verify(stage,assets,read_receipt(stage))
        exchange(LIVE,stage);swapped=True
        verify(LIVE,assets,read_receipt(LIVE))
        # Old live directory is now the backup. Save pointer before reporting success.
        write_atomic(HISTORY/'previous',(stage.name+'\n').encode(),0o600)
        for rel,meta in assets.items():print('SWRLZ_ENGINE_ASSET_OK '+meta['sha256']+' '+rel,flush=True)
        print('SWRLZ_ENGINE_DEPLOY_OK '+str(m.get('candidateCommit','')),flush=True)
    except BaseException:
        if swapped:exchange(LIVE,stage)
        if stage.exists():shutil.rmtree(stage)
        raise
def deploy_runtime():
    m=json.loads(safe_read(RUNTIME_PAYLOAD/'manifest.json',256*1024))
    require(m.get('schema')=='swrlz-ovh-runtime-overlay-v1' and m.get('target')==str(LIVE),'Invalid runtime manifest')
    require(m.get('sealedSourceSha256')==SEALED_SOURCE,'Unexpected engine source seal')
    evidence=m['browserReceipt']
    require(evidence.get('realStarterCard') is True and evidence.get('errors')==[],'Missing real starter card evidence')
    assets=m['assets']
    fixed={'index.html','modeler.html','swrlz-engine-v11.552.js','assets/uv-unwrapper/uv_atlas_core_v11_555.mjs','assets/uv-unwrapper/uv_lscm_core_v11_555.mjs'}
    require(set(assets)==fixed,'Runtime overlay must contain precisely the five authorized static files')
    receipt=read_receipt(LIVE)
    require(set(m['requiredStarterAssets'])==set(BOOTSTRAP_BASELINE),'Unexpected starter dependency set')
    verify(LIVE,m['requiredStarterAssets'],receipt)
    scene='scenes/model-atelier-clean-topology-humanoid-v11-554.swyrl.json'
    require(evidence.get('hash')==m['requiredStarterAssets'][scene]['sha256'],'Browser-tested starter hash differs')
    staged={};already=0
    for rel,meta in assets.items():
        require(type(meta['bytes']) is int and 0<meta['bytes']<=LIMIT and HEX.fullmatch(meta['sha256']),'Invalid runtime digest')
        data=safe_read(RUNTIME_PAYLOAD/'overlay'/rel)
        require(len(data)==meta['bytes'] and digest(data)==meta['sha256'],'Runtime payload mismatch: '+rel)
        path=LIVE/rel
        if os.path.lexists(path):
            old=safe_read(path)
            if digest(old)==meta['sha256']:already+=1
            else:
                prior=receipt['assets'].get(rel)
                if prior:
                    require(prior['sha256']==digest(old) and prior['bytes']==len(old),'Prior runtime receipt mismatch: '+rel)
                else:
                    require(rel in ('index.html','modeler.html') and digest(old)==SEALED_SOURCE,'Unknown runtime baseline: '+rel+' actual='+digest(old))
        else:
            require(rel not in ('index.html','modeler.html'),'Existing entry page absent: '+rel)
        staged[rel]=data
    require(sum(map(len,staged.values()))<=64*1024*1024,'Runtime overlay exceeds limit')
    require(staged['index.html']==staged['modeler.html'],'Entry pages differ')
    require(b'<script type="module" src="./swrlz-engine-v11.552.js"></script>' in staged['index.html'],'Runtime entry does not reference expected module')
    if already==len(assets):
        verify(LIVE,assets,receipt)
        print('SWRLZ_ENGINE_RUNTIME_DEPLOY_OK already-current',flush=True);return
    stage=Path(tempfile.mkdtemp(prefix='candidate-',dir=HISTORY));stage.rmdir()
    swapped=False
    try:
        shutil.copytree(LIVE,stage,symlinks=True,copy_function=shutil.copy2)
        for rel,data in staged.items():
            path=stage/rel
            path.parent.mkdir(parents=True,exist_ok=True)
            write_atomic(path,data)
            receipt['assets'][rel]={'sha256':digest(data),'bytes':len(data)}
        receipt['ovhRuntimeOverlay']={'sealedSourceSha256':SEALED_SOURCE,'sourceCommit':m.get('sourceCommit'),'browserRun':m.get('browserRun'),'assets':list(staged),'publishedAt':int(time.time())}
        write_atomic(receipt_path(stage),(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n').encode())
        verify(stage,assets,read_receipt(stage))
        verify(stage,m['requiredStarterAssets'],read_receipt(stage))
        exchange(LIVE,stage);swapped=True
        verify(LIVE,assets,read_receipt(LIVE))
        verify(LIVE,m['requiredStarterAssets'],read_receipt(LIVE))
        write_atomic(HISTORY/'previous',(stage.name+'\n').encode(),0o600)
        for rel,meta in assets.items():print('SWRLZ_ENGINE_RUNTIME_ASSET_OK '+meta['sha256']+' '+rel,flush=True)
        print('SWRLZ_ENGINE_RUNTIME_DEPLOY_OK '+str(m.get('sourceCommit','')),flush=True)
    except BaseException:
        if swapped:exchange(LIVE,stage)
        if stage.exists():shutil.rmtree(stage)
        raise
def rollback():
    name=safe_read(HISTORY/'previous',1024).decode().strip()
    require(re.fullmatch(r'candidate-[A-Za-z0-9_-]+',name) is not None,'Invalid rollback pointer')
    old=HISTORY/name
    s=old.lstat();require(stat.S_ISDIR(s.st_mode) and s.st_uid==0,'Unsafe rollback directory')
    read_receipt(old)
    exchange(LIVE,old)
    try:read_receipt(LIVE)
    except BaseException:exchange(LIVE,old);raise
    print('SWRLZ_ENGINE_ROLLBACK_OK',flush=True)
def main():
    require(len(sys.argv)==2 and sys.argv[1] in ('initialize','check','deploy','deploy-runtime','rollback'),'Command not authorized')
    check_root()
    with open(HISTORY/'lock','a') as f:
        fcntl.flock(f,fcntl.LOCK_EX)
        if sys.argv[1]=='initialize':initialize()
        elif sys.argv[1]=='check':
            read_receipt(LIVE)
            print('SWRLZ_ENGINE_GATE_OK')
        elif sys.argv[1]=='deploy':deploy()
        elif sys.argv[1]=='deploy-runtime':deploy_runtime()
        else:rollback()
if __name__=='__main__':main()
