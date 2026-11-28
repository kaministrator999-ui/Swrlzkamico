#!/usr/bin/python3
"""Root-owned, fixed-scope static starter asset publisher for Debian/Linux.
Never executes repository code or accepts a user-supplied path or command."""
import ctypes, fcntl, hashlib, json, os, re, shutil, stat, sys, tempfile, time
from pathlib import Path
LIVE=Path('/var/www/swrlz-engine')
HISTORY=Path('/var/www/.swrlz-engine-releases')
PAYLOAD=Path('/srv/swrlz/source/.deploy/engine-uv/payload')
LIMIT=16*1024*1024
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
    require((LIVE/'SOURCE.json').is_file(),'Missing live SOURCE.json')
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
def read_receipt(root):
    return json.loads(safe_read(root/'SOURCE.json',4*1024*1024))
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
        write_atomic(stage/'SOURCE.json',(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n').encode())
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
    require(len(sys.argv)==2 and sys.argv[1] in ('check','deploy','rollback'),'Command not authorized')
    check_root()
    with open(HISTORY/'lock','a') as f:
        fcntl.flock(f,fcntl.LOCK_EX)
        if sys.argv[1]=='check':print('SWRLZ_ENGINE_GATE_OK')
        elif sys.argv[1]=='deploy':deploy()
        else:rollback()
if __name__=='__main__':main()
