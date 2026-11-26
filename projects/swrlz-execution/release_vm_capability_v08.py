"""Deploy a capability-only experiment to existing §X; restore on any failed gate."""
import hashlib,hmac,io,json,os,re,secrets,sys,time
from pathlib import Path
import requests
from x_diagnostic_client import derive_key,diagnose
from vm_capability_v08 import SCHEMA,mac,wire,newc,guest_init
ROOT=Path(__file__).resolve().parent
SPACE="kamiloki/swrlz-execution"
URL="https://kamiloki-swrlz-execution.hf.space/gradio_api/call/swrlz_vm_v08"
FILES=("README.md","packages.txt","launch_v08.py","vm_capability_v08.py")
def sha(raw):return hashlib.sha256(raw).hexdigest()
def patch_readme(raw):
    text=raw.decode()
    m=re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)",text,re.S)
    if not m:raise RuntimeError("V08_README_FRONTMATTER_MISSING")
    front=m.group(1)
    if not re.search(r"(?m)^sdk:\s*gradio\s*$",front):raise RuntimeError("V08_SDK_DRIFT")
    matches=list(re.finditer(r"(?m)^app_file:[ \t]*(.*?)\s*$",front))
    if not matches:front+="\napp_file: launch_v08.py"
    elif len(matches)==1 and matches[0].group(1) in ("app.py","launch_v08.py"):
        front=re.sub(r"(?m)^app_file:[ \t]*[^\r\n]*","app_file: launch_v08.py",front,count=1)
    else:raise RuntimeError("V08_ENTRY_DRIFT")
    return (text[:m.start(1)]+front+text[m.end(1):]).encode()
def call(key):
    obj={"schema":SCHEMA,"nonce":secrets.token_hex(16),"timestamp":int(time.time())}
    raw=wire(obj)
    with requests.Session() as s:
        s.trust_env=False
        with s.post(URL,json={"data":[raw.decode(),mac(key,"vm-v08-request",raw)]},timeout=(10,15),allow_redirects=False,stream=True) as r:
            r.raise_for_status();body=r.raw.read(8193)
        if len(body)>8192:raise RuntimeError("V08_EVENT_LIMIT")
        event=json.loads(body)["event_id"]
        if not re.fullmatch(r"[a-f0-9]{32}",event):raise RuntimeError("V08_EVENT_INVALID")
        with s.get(URL+"/"+event,timeout=(10,120),allow_redirects=False,stream=True) as r:
            r.raise_for_status();kind="";size=0
            for line in r.iter_lines(chunk_size=1024):
                size+=len(line)+1
                if size>65536:raise RuntimeError("V08_STREAM_LIMIT")
                if line.startswith(b"event:"):kind=line[6:].strip().decode()
                if line.startswith(b"data:") and kind=="error":raise RuntimeError("V08_REMOTE_ERROR")
                if line.startswith(b"data:") and kind=="complete":
                    env=json.loads(line[5:].strip())[0];rec=env["receipt"]
                    if not hmac.compare_digest(mac(key,"vm-v08-receipt",wire(rec)),env["signature"]) or rec.get("nonce")!=obj["nonce"] or rec.get("schema")!=SCHEMA or abs(time.time()-rec["timestamp"])>180:raise RuntimeError("V08_RECEIPT_IDENTITY")
                    return rec
    raise RuntimeError("V08_RECEIPT_MISSING")
def selftest():
    import stat
    for name in ("launch_v08.py","vm_capability_v08.py"):compile((ROOT/name).read_bytes(),name,"exec")
    a=patch_readme(b"---\nsdk: gradio\napp_file: app.py\n---\nhello\n")
    assert b"app_file: launch_v08.py" in a and patch_readme(a)==a
    assert b"app_file: launch_v08.py" in patch_readme(b"---\nsdk: gradio\n---\n")
    raw=newc([("init",stat.S_IFREG|0o755,b"test")])
    assert raw.startswith(b"070701") and len(raw)%512==0 and b"TRAILER!!!" in raw
    assert b"SWRLZ_V08_GUEST_OK:" in guest_init("a"*32,"/tmp/swrlz-v08-abcd/host-canary")
    print("V08_FIXED_PROBE_SELFTEST_PASS",flush=True)
def publish():
    from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd,CommitOperationDelete
    token=os.environ["HF_TOKEN"];key=derive_key(token);api=HfApi(token=token)
    def rev():return str(api.repo_info(SPACE,repo_type="space").sha)
    def read(n,r):return Path(hf_hub_download(SPACE,n,repo_type="space",revision=r,token=token)).read_bytes()
    old=rev();names=set(api.list_repo_files(SPACE,repo_type="space",revision=old))
    app_sha=sha((ROOT/"app.py").read_bytes())
    if sha(read("app.py",old))!=app_sha or diagnose(key)["diagnostics"]["source_sha256"]!=app_sha:raise RuntimeError("V08_EXISTING_X_SOURCE_DRIFT")
    orig={n:read(n,old) for n in FILES if n in names}
    if orig.get("packages.txt")!=(ROOT/"packages.txt").read_bytes():raise RuntimeError("V08_EXISTING_PACKAGES_DRIFT")
    desired={"README.md":patch_readme(orig["README.md"]),"packages.txt":orig["packages.txt"].rstrip()+b"\nqemu-system-x86\nlinux-image-amd64\nbusybox-static\n"}
    for n in ("launch_v08.py","vm_capability_v08.py"):
        desired[n]=(ROOT/n).read_bytes()
        if n in orig and orig[n]!=desired[n]:raise RuntimeError("V08_FILE_COLLISION:"+n)
    def add(n,v):return CommitOperationAdd(path_in_repo=n,path_or_fileobj=io.BytesIO(v))
    changed={n:v for n,v in desired.items() if orig.get(n)!=v}
    new=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=old,operations=[add(n,v) for n,v in changed.items()],commit_message="§X v0.8 fixed VM capability experiment").oid
    try:
        for n,v in desired.items():assert read(n,new)==v
        assert sha(read("app.py",new))==app_sha
        deadline=time.monotonic()+900
        while time.monotonic()<deadline:
            if rev()!=new:raise RuntimeError("V08_CONCURRENT_CHANGE")
            stage=str(api.get_space_runtime(SPACE).stage)
            print("V08_STARTUP",stage,flush=True)
            if stage.split(".")[-1] in ("BUILD_ERROR","RUNTIME_ERROR","CONFIG_ERROR"):raise RuntimeError("V08_SPACE_"+stage)
            if stage.split(".")[-1]=="RUNNING":
                try:
                    r=requests.get(URL.replace("/call/swrlz_vm_v08","/info"),timeout=10,allow_redirects=False)
                    if r.status_code==200 and "/swrlz_vm_v08" in r.json().get("named_endpoints",{}):break
                except (requests.RequestException,ValueError):pass
            time.sleep(10)
        else:raise RuntimeError("V08_ENDPOINT_UNVERIFIED")
        rec=call(key)
        Path("swrlz-v08-capability.json").write_text(json.dumps(rec,indent=2)+"\n")
        print("V08_CAPABILITY_RECEIPT",json.dumps(rec),flush=True)
        if rec.get("probeSha256")!=sha(desired["vm_capability_v08.py"]) or rec.get("candidateExecutionEnabled") is not False or rec.get("isolationVerified") is not False or rec.get("browserInGuestVerified") is not False:raise RuntimeError("V08_RECEIPT_SCOPE")
        if rec.get("guestBootVerified") is not True:raise RuntimeError("V08_FIXED_GUEST_BOOT_UNVERIFIED")
        # The existing §C backend pins app.py. Prove that its signed diagnostics still work.
        if diagnose(key)["diagnostics"]["source_sha256"]!=app_sha:raise RuntimeError("V08_V07_REGRESSION")
        print("V08_FIXED_GUEST_BOOT_PASS_V07_PRESERVED",flush=True)
    except Exception:
        if rev()==new:
            restored=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=new,operations=[add(n,orig[n]) if n in orig else CommitOperationDelete(path_in_repo=n) for n in changed],commit_message="Rollback unverified §X v0.8 capability experiment").oid
            print("V08_ROLLBACK",restored,flush=True)
        raise
if __name__=="__main__":
    selftest()
    if sys.argv[1:]==["publish"]:publish()
