"""Deploy a capability-only experiment to existing §X; restore on any failed gate."""
import hashlib,hmac,io,json,os,re,secrets,sys,time
from pathlib import Path
import requests
from x_diagnostic_client import derive_key,diagnose
from vm_browser_v09 import SCHEMA,mac,wire,manifest,digest
ROOT=Path(__file__).resolve().parent
SPACE="kamiloki/swrlz-execution"
URL="https://kamiloki-swrlz-execution.hf.space/gradio_api/call/swrlz_vm_browser_v09"
FILES=("README.md","launch_v09.py","vm_browser_v09.py","guest-v09/vmlinuz","guest-v09/initrd.img","guest-v09/guest.ext4.gz","guest-v09/SHA256SUMS")
def sha(raw):return hashlib.sha256(raw).hexdigest()
def patch_readme(raw):
    text=raw.decode()
    m=re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)",text,re.S)
    if not m:raise RuntimeError("V09_README_FRONTMATTER_MISSING")
    front=m.group(1)
    if not re.search(r"(?m)^sdk:\s*gradio\s*$",front):raise RuntimeError("V09_SDK_DRIFT")
    matches=list(re.finditer(r"(?m)^app_file:[ \t]*(.*?)\s*$",front))
    if not matches:front+="\napp_file: launch_v09.py"
    elif len(matches)==1 and matches[0].group(1) in ("launch_v08.py","launch_v09.py"):
        front=re.sub(r"(?m)^app_file:[ \t]*[^\r\n]*","app_file: launch_v09.py",front,count=1)
    else:raise RuntimeError("V09_ENTRY_DRIFT")
    return (text[:m.start(1)]+front+text[m.end(1):]).encode()
def call(key):
    obj={"schema":SCHEMA,"nonce":secrets.token_hex(16),"timestamp":int(time.time())}
    raw=wire(obj)
    with requests.Session() as s:
        s.trust_env=False
        with s.post(URL,json={"data":[raw.decode(),mac(key,"vm-v09-request",raw)]},timeout=(10,15),allow_redirects=False,stream=True) as r:
            r.raise_for_status();body=r.raw.read(8193)
        if len(body)>8192:raise RuntimeError("V09_EVENT_LIMIT")
        event=json.loads(body)["event_id"]
        if not re.fullmatch(r"[a-f0-9]{32}",event):raise RuntimeError("V09_EVENT_INVALID")
        with s.get(URL+"/"+event,timeout=(10,360),allow_redirects=False,stream=True) as r:
            r.raise_for_status();kind="";size=0
            for line in r.iter_lines(chunk_size=1024):
                size+=len(line)+1
                if size>65536:raise RuntimeError("V09_STREAM_LIMIT")
                if line.startswith(b"event:"):kind=line[6:].strip().decode()
                if line.startswith(b"data:") and kind=="error":raise RuntimeError("V09_REMOTE_ERROR")
                if line.startswith(b"data:") and kind=="complete":
                    env=json.loads(line[5:].strip())[0];rec=env["receipt"]
                    if not hmac.compare_digest(mac(key,"vm-v09-receipt",wire(rec)),env["signature"]) or rec.get("nonce")!=obj["nonce"] or rec.get("schema")!=SCHEMA or abs(time.time()-rec["timestamp"])>180:raise RuntimeError("V09_RECEIPT_IDENTITY")
                    return rec
    raise RuntimeError("V09_RECEIPT_MISSING")
def publish():
    from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd,CommitOperationDelete
    image=Path(sys.argv[2]).resolve();hashes=manifest(image)
    token=os.environ["HF_TOKEN"];key=derive_key(token);api=HfApi(token=token)
    def rev():return str(api.repo_info(SPACE,repo_type="space").sha)
    def fetch(n,r):return Path(hf_hub_download(SPACE,n,repo_type="space",revision=r,token=token))
    old=rev();names=set(api.list_repo_files(SPACE,repo_type="space",revision=old))
    app_sha=sha((ROOT/"app.py").read_bytes())
    if digest(fetch("app.py",old))!=app_sha or diagnose(key)["diagnostics"]["source_sha256"]!=app_sha:raise RuntimeError("V09_EXISTING_X_SOURCE_DRIFT")
    for n in ("launch_v08.py","vm_capability_v08.py"):
        if digest(fetch(n,old))!=digest(ROOT/n):raise RuntimeError("V09_V08_SOURCE_DRIFT:"+n)
    orig={n:fetch(n,old) for n in FILES if n in names}
    if any(n in orig for n in FILES[1:]):raise RuntimeError("V09_EXISTING_FILE_COLLISION")
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        readme=Path(tmp)/"README.md";readme.write_bytes(patch_readme(orig["README.md"].read_bytes()))
        desired={"README.md":readme,"launch_v09.py":ROOT/"launch_v09.py","vm_browser_v09.py":ROOT/"vm_browser_v09.py"}
        for n in ("vmlinuz","initrd.img","guest.ext4.gz","SHA256SUMS"):desired["guest-v09/"+n]=image/n
        def add(n,p):return CommitOperationAdd(path_in_repo=n,path_or_fileobj=str(p))
        new=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=old,operations=[add(n,p) for n,p in desired.items()],commit_message="§X v0.9 fixed guest browser experiment").oid
        try:
            for n,p in desired.items():
                if digest(fetch(n,new))!=digest(p):raise RuntimeError("V09_READBACK:"+n)
            deadline=time.monotonic()+900
            while time.monotonic()<deadline:
                if rev()!=new:raise RuntimeError("V09_CONCURRENT_CHANGE")
                stage=str(api.get_space_runtime(SPACE).stage);print("V09_STARTUP",stage,flush=True)
                if stage.split(".")[-1] in ("BUILD_ERROR","RUNTIME_ERROR","CONFIG_ERROR"):raise RuntimeError("V09_SPACE_"+stage)
                if stage.split(".")[-1]=="RUNNING":
                    try:
                        r=requests.get(URL.replace("/call/swrlz_vm_browser_v09","/info"),timeout=10,allow_redirects=False)
                        if r.status_code==200 and "/swrlz_vm_browser_v09" in r.json().get("named_endpoints",{}):break
                    except (requests.RequestException,ValueError):pass
                time.sleep(10)
            else:raise RuntimeError("V09_ENDPOINT_UNVERIFIED")
            rec=call(key)
            Path("swrlz-v09-live.json").write_text(json.dumps(rec,indent=2)+"\n")
            print("V09_LIVE_RECEIPT",json.dumps(rec),flush=True)
            if rec.get("probeSha256")!=digest(ROOT/"vm_browser_v09.py") or rec.get("imageHashes")!=hashes or rec.get("candidateExecutionEnabled") is not False or rec.get("isolationVerified") is not False or rec.get("browserInGuestVerified") is not True:raise RuntimeError("V09_LIVE_BROWSER_UNVERIFIED")
            if diagnose(key)["diagnostics"]["source_sha256"]!=app_sha:raise RuntimeError("V09_V07_REGRESSION")
            print("V09_FIXED_GUEST_BROWSER_PASS",flush=True)
        except Exception:
            if rev()==new:
                restored=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=new,operations=[add(n,orig[n]) if n in orig else CommitOperationDelete(path_in_repo=n) for n in desired],commit_message="Rollback unverified §X v0.9").oid
                print("V09_ROLLBACK",restored,flush=True)
            raise
if __name__=="__main__":
    if len(sys.argv)==3 and sys.argv[1]=="publish":publish()
    else:raise SystemExit("usage: publish IMAGE_DIR")
