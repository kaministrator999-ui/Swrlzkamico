"""v0.8: fixed guest boot only; never accepts candidate code, commands or paths."""
import errno,glob,hashlib,hmac,json,os,platform,re,resource,secrets,shutil,signal,stat,struct,subprocess,tempfile,threading,time
from pathlib import Path

SCHEMA="swrlz-x-vm-capability-v08"
LOCK=threading.Lock()
SEEN={}
def wire(x):return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def mac(key,kind,data):return hmac.new(key.encode(),kind.encode()+b"\0"+data,hashlib.sha256).hexdigest()
def newc(entries):
    """Create a small deterministic initramfs; no host directories are packed."""
    out=bytearray()
    def add(name,mode,body,major=0,minor=0):
        n=name.encode()+b"\0"
        fields=(len(out)+1,mode,0,0,1,0,len(body),0,0,major,minor,len(n),0)
        out.extend(b"070701"+b"".join(("%08x"%v).encode() for v in fields)+n)
        out.extend(b"\0"*((-len(out))%4));out.extend(body);out.extend(b"\0"*((-len(out))%4))
    for item in entries:add(*item)
    add("TRAILER!!!",0,b"")
    out.extend(b"\0"*((-len(out))%512))
    return bytes(out)
def guest_init(nonce,canary):
    # Only host-generated hexadecimal nonce and fixed synthetic canary path.
    assert re.fullmatch(r"[a-f0-9]{32}",nonce)
    assert re.fullmatch(r"/tmp/swrlz-v08-[A-Za-z0-9_]+/host-canary",canary)
    return ("""#!/bin/busybox sh
/bin/busybox mount -t proc proc /proc || exec /bin/busybox poweroff -f
/bin/busybox mount -t sysfs sysfs /sys || exec /bin/busybox poweroff -f
/bin/busybox mount -t devtmpfs devtmpfs /dev || exec /bin/busybox poweroff -f
[ ! -e '"""+canary+"""' ] || exec /bin/busybox poweroff -f
[ ! -e /dev/kvm ] || exec /bin/busybox poweroff -f
[ ! -e /dev/sda ] && [ ! -e /dev/vda ] && [ ! -e /dev/nvme0n1 ] || exec /bin/busybox poweroff -f
[ "$(/bin/busybox ls /sys/class/net)" = lo ] || exec /bin/busybox poweroff -f
[ "$(/bin/busybox grep -c '^processor' /proc/cpuinfo)" = 1 ] || exec /bin/busybox poweroff -f
echo guest-private > /tmp/guest-canary
[ "$(/bin/busybox cat /tmp/guest-canary)" = guest-private ] || exec /bin/busybox poweroff -f
echo SWRLZ_V08_GUEST_OK:"""+nonce+"""
exec /bin/busybox poweroff -f
""").encode()
def kernel_path():
    paths=sorted(glob.glob("/boot/vmlinuz-*"),reverse=True)
    return next((Path(p) for p in paths if Path(p).is_file()),None)
def probe_vm():
    started=time.monotonic()
    r={"schema":SCHEMA,"status":"BLOCKED","guestBootVerified":False,"candidateExecutionEnabled":False,
       "isolationVerified":False,"browserInGuestVerified":False,"architecture":platform.machine(),
       "qemuAvailable":False,"kernelAvailable":False,"busyboxAvailable":False,"kvmAccessible":False}
    qemu=shutil.which("qemu-system-x86_64");kernel=kernel_path();busybox=shutil.which("busybox")
    r.update(qemuAvailable=bool(qemu),kernelAvailable=bool(kernel),busyboxAvailable=bool(busybox))
    # A device node alone is not proof of usable KVM; TCG is deliberately used.
    try:
        fd=os.open("/dev/kvm",os.O_RDWR|os.O_CLOEXEC);os.close(fd);r["kvmAccessible"]=True
    except OSError as e:r["kvmOpenErrno"]=e.errno
    if platform.machine()!="x86_64" or not all((qemu,kernel,busybox)):
        r["blocker"]="VM_RUNTIME_PREREQUISITES";return r
    try:
        import pwd
        with tempfile.TemporaryDirectory(prefix="swrlz-v08-",dir="/tmp") as tmp:
            root=Path(tmp);nonce=secrets.token_hex(16)
            canary=root/"host-canary";canary.write_text(nonce)
            image=root/"kernel";shutil.copyfile(kernel,image);image.chmod(0o444)
            initrd=root/"initramfs.cpio"
            dirs=[(p,stat.S_IFDIR|0o755,b"") for p in ("bin","proc","sys","dev","tmp")]
            initrd.write_bytes(newc(dirs+[("dev/console",stat.S_IFCHR|0o600,b"",5,1),("bin/busybox",stat.S_IFREG|0o755,Path(busybox).read_bytes()),("init",stat.S_IFREG|0o755,guest_init(nonce,str(canary)))]));initrd.chmod(0o444)
            runas={}
            if os.geteuid()==0:
                user=pwd.getpwnam("nobody");assert user.pw_uid!=0
                # Keep the synthetic host canary owned by root, inaccessible to QEMU.
                canary.chmod(0o600);root.chmod(0o755)
                runas={"user":user.pw_uid,"group":user.pw_gid,"extra_groups":[]}
            else:root.chmod(0o700)
            r["unprivilegedQemu"]=bool(runas) or os.geteuid()!=0
            # No virtual NIC, disks, host filesystem exports, monitor, or host USB.
            cmd=[qemu,"-no-user-config","-nodefaults","-machine","q35,accel=tcg","-cpu","max",
                 "-m","384M","-smp","1","-display","none","-serial","stdio","-monitor","none","-nic","none",
                 "-no-reboot","-kernel",str(image),"-initrd",str(initrd),"-append","console=ttyS0 rdinit=/init panic=-1 quiet"]
            env={"PATH":"/usr/bin:/bin","HOME":tmp,"LANG":"C.UTF-8"}
            # Bounded log stored outside guest. No shell, no inherited credentials or descriptors.
            with tempfile.TemporaryFile() as log:
                proc=subprocess.Popen(cmd,cwd=tmp,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=log,
                                      close_fds=True,start_new_session=True,**runas)
                timed=False
                try:proc.wait(timeout=90)
                except subprocess.TimeoutExpired:
                    timed=True
                    try:os.killpg(proc.pid,signal.SIGKILL)
                    except ProcessLookupError:pass
                    proc.wait(timeout=10)
                log.seek(0);raw=log.read(262145)
            r["exitCode"]=proc.returncode;r["timedOut"]=timed
            r["logWithinLimit"]=len(raw)<=262144
            r["guestNonceSeen"]=("SWRLZ_V08_GUEST_OK:"+nonce).encode() in raw
            r["hostCanaryUnchanged"]=canary.read_text()==nonce
            r["guestCanaryAbsentOnHost"]=not (root/"guest-canary").exists()
            r["guestBootVerified"]=not timed and proc.returncode==0 and all(r[k] for k in ("unprivilegedQemu","logWithinLimit","guestNonceSeen","hostCanaryUnchanged","guestCanaryAbsentOnHost"))
            r["status"]="FIXED_GUEST_BOOT_PASS" if r["guestBootVerified"] else "FIXED_GUEST_BOOT_BLOCKED"
            r["logCategories"]=[label for label,needle in (("KERNEL_PANIC",b"Kernel panic"),("INIT_FAILURE",b"No working init"),("QEMU_ERROR",b"qemu-system-x86_64:"),("OUT_OF_MEMORY",b"Out of memory")) if needle in raw]
    except Exception as e:r["blocker"]=type(e).__name__
    r["elapsedSeconds"]=round(time.monotonic()-started,2)
    return r
def remote_vm_probe(raw,signature):
    import gradio as gr
    key=os.environ.get("SWRLZ_X_DIAGNOSTIC_KEY","")
    if len(key)!=64 or not isinstance(raw,str) or len(raw)>512 or not isinstance(signature,str) or len(signature)!=64 or not hmac.compare_digest(mac(key,"vm-v08-request",raw.encode()),signature):raise gr.Error("V08_DENIED")
    try:
        obj=json.loads(raw);now=int(time.time())
        if set(obj)!={"schema","nonce","timestamp"} or obj["schema"]!=SCHEMA or not re.fullmatch(r"[a-f0-9]{32}",obj["nonce"]) or type(obj["timestamp"]) is not int or abs(now-obj["timestamp"])>120:raise ValueError()
    except (TypeError,ValueError,KeyError):raise gr.Error("V08_INVALID")
    if not LOCK.acquire(blocking=False):raise gr.Error("V08_BUSY")
    try:
        for n in list(SEEN):
            if now-SEEN[n]>300:del SEEN[n]
        if obj["nonce"] in SEEN or len(SEEN)>=64:raise gr.Error("V08_REPLAY")
        SEEN[obj["nonce"]]=now
        receipt=probe_vm()
        receipt.update(nonce=obj["nonce"],timestamp=int(time.time()),probeSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
        return {"receipt":receipt,"signature":mac(key,"vm-v08-receipt",wire(receipt))}
    finally:LOCK.release()
