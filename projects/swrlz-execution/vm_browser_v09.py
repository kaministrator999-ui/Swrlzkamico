"""Fixed browser-in-VM diagnostic. No caller-supplied code, paths or URLs."""
import gzip,hashlib,hmac,json,os,re,shutil,signal,subprocess,tempfile,time,threading
from pathlib import Path
from vm_capability_v08 import mac,wire
SCHEMA="swrlz-x-vm-browser-v09"
ROOT=Path(__file__).resolve().parent
LOCK=threading.Lock()
SEEN={}
def digest(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()
def manifest(root):
    data={}
    for line in (root/"SHA256SUMS").read_text().splitlines():
        m=re.fullmatch(r"([a-f0-9]{64})  (vmlinuz|initrd.img|guest.ext4.gz)",line)
        if not m or m[2] in data:raise ValueError("V09_MANIFEST_INVALID")
        data[m[2]]=m[1]
    if set(data)!={"vmlinuz","initrd.img","guest.ext4.gz"}:raise ValueError("V09_MANIFEST_INCOMPLETE")
    for n,h in data.items():
        if digest(root/n)!=h:raise ValueError("V09_IMAGE_HASH_MISMATCH")
    return data
def probe(root=None):
    import secrets,pwd
    root=Path(root) if root else ROOT/"guest-v09"
    result={"schema":SCHEMA,"status":"BLOCKED","candidateExecutionEnabled":False,"isolationVerified":False,
            "browserInGuestVerified":False,"guestBootVerified":False,"domInteractionVerified":False,
            "webglVerified":False,"screenshotVerified":False}
    started=time.monotonic()
    try:
        hashes=manifest(root);result["imageHashes"]=hashes
        qemu=shutil.which("qemu-system-x86_64")
        if not qemu:raise RuntimeError("QEMU_MISSING")
        with tempfile.TemporaryDirectory(prefix="swrlz-v09-") as d:
            work=Path(d);scratch=work/"scratch";scratch.mkdir()
            disk=work/"guest.ext4"
            total=0
            with gzip.open(root/"guest.ext4.gz","rb") as src,disk.open("wb") as dst:
                while True:
                    chunk=src.read(1024*1024)
                    if not chunk:break
                    total+=len(chunk)
                    if total>3*1024**3:raise ValueError("GUEST_DISK_LIMIT")
                    if chunk.count(0)==len(chunk):dst.seek(len(chunk),1)
                    else:dst.write(chunk)
                dst.truncate(total)
            disk.chmod(0o444)
            for n in ("vmlinuz","initrd.img"):
                shutil.copyfile(root/n,work/n);(work/n).chmod(0o444)
            opts={}
            if os.geteuid()==0:
                user=pwd.getpwnam("nobody");work.chmod(0o755);os.chown(scratch,user.pw_uid,user.pw_gid)
                opts={"user":user.pw_uid,"group":user.pw_gid,"extra_groups":[]}
            nonce=secrets.token_hex(16)
            cmd=[qemu,"-no-user-config","-nodefaults","-machine","q35,accel=tcg","-cpu","max",
                 "-m","2048M","-smp","2","-display","none","-serial","stdio","-monitor","none","-nic","none","-no-reboot",
                 "-kernel",str(work/"vmlinuz"),"-initrd",str(work/"initrd.img"),
                 "-drive","file="+str(disk)+",format=raw,if=virtio,snapshot=on",
                 "-append","root=/dev/vda rw console=ttyS0 init=/usr/local/sbin/swrlz-probe panic=-1 quiet swrlz_nonce="+nonce]
            env={"PATH":"/usr/bin:/bin","HOME":str(scratch),"TMPDIR":str(scratch),"LANG":"C.UTF-8"}
            with tempfile.TemporaryFile() as log:
                proc=subprocess.Popen(cmd,cwd=scratch,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=log,
                    close_fds=True,start_new_session=True,**opts)
                timed=False
                try:proc.wait(timeout=300)
                except subprocess.TimeoutExpired:
                    timed=True
                    try:os.killpg(proc.pid,signal.SIGKILL)
                    except ProcessLookupError:pass
                    proc.wait(timeout=10)
                log.seek(0);raw=log.read(1048577)
            result.update(exitCode=proc.returncode,timedOut=timed,logWithinLimit=len(raw)<=1048576)
            for name,marker in (("guestBootVerified","GUEST_READY"),("domInteractionVerified","DOM_PASS"),("webglVerified","DOM_PASS")):
                result[name]=("SWRLZ_V09_"+marker+":"+nonce).encode() in raw
            shot=re.search(rb"SWRLZ_V09_SCREENSHOT:"+nonce.encode()+rb":([a-f0-9]{64})",raw)
            result["screenshotVerified"]=shot is not None
            result["screenshotSha256"]=shot[1].decode() if shot else None
            result["browserInGuestVerified"]=not timed and proc.returncode==0 and len(raw)<=1048576 and all(result[k] for k in ("guestBootVerified","domInteractionVerified","webglVerified","screenshotVerified")) and ("SWRLZ_V09_COMPLETE:"+nonce).encode() in raw
            result["status"]="FIXED_BROWSER_GUEST_PASS" if result["browserInGuestVerified"] else "FIXED_BROWSER_GUEST_BLOCKED"
            result["logCategories"]=[label for label,needle in (("KERNEL_PANIC",b"Kernel panic"),("ROOT_MOUNT_FAILED",b"Unable to mount root"),("BROWSER_FAILED",b"SWRLZ_V09_BROWSER_FAILED"),("DOM_FAILED",b"SWRLZ_V09_DOM_FAILED"),("SCREENSHOT_FAILED",b"SWRLZ_V09_SCREENSHOT_FAILED"),("QEMU_ERROR",b"qemu-system-x86_64:")) if needle in raw]
    except Exception as e:result["blocker"]=type(e).__name__
    result["elapsedSeconds"]=round(time.monotonic()-started,2)
    return result
def remote(raw,signature):
    import gradio as gr
    key=os.environ.get("SWRLZ_X_DIAGNOSTIC_KEY","")
    if len(key)!=64 or not isinstance(raw,str) or len(raw)>512 or not isinstance(signature,str) or len(signature)!=64 or not hmac.compare_digest(mac(key,"vm-v09-request",raw.encode()),signature):raise gr.Error("V09_DENIED")
    try:
        obj=json.loads(raw);now=int(time.time())
        if set(obj)!={"schema","nonce","timestamp"} or obj["schema"]!=SCHEMA or not re.fullmatch(r"[a-f0-9]{32}",obj["nonce"]) or type(obj["timestamp"]) is not int or abs(now-obj["timestamp"])>120:raise ValueError()
    except (ValueError,TypeError,KeyError):raise gr.Error("V09_INVALID")
    if not LOCK.acquire(blocking=False):raise gr.Error("V09_BUSY")
    try:
        for n in list(SEEN):
            if now-SEEN[n]>300:del SEEN[n]
        if obj["nonce"] in SEEN or len(SEEN)>=64:raise gr.Error("V09_REPLAY")
        SEEN[obj["nonce"]]=now
        rec=probe();rec.update(nonce=obj["nonce"],timestamp=int(time.time()),probeSha256=digest(Path(__file__)))
        return {"receipt":rec,"signature":mac(key,"vm-v09-receipt",wire(rec))}
    finally:LOCK.release()
if __name__=="__main__":
    import sys
    result=probe(sys.argv[1]);print(json.dumps(result),flush=True)
    if not result["browserInGuestVerified"]:raise SystemExit(1)
