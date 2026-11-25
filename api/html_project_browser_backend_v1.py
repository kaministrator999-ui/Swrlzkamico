"""§C-owned browser execution adapter. Workers never choose or publish patches."""
from __future__ import annotations
import io,json,os,re,secrets,time,zipfile
from urllib.parse import urlsplit
import requests
REPO="kaministrator999-ui/Swrlzkamico"
WORKFLOW="hf-html-project-browser-worker-v16.yml"
WORKFLOW_PATH=".github/workflows/"+WORKFLOW
SCHEMA="swrlz-github-browser-v16"
OWNER="kaministrator999-ui"
SHA=re.compile(r"[0-9a-f]{40}\Z")
NONCE=re.compile(r"[0-9a-f]{32}\Z")
SLUG=re.compile(r"[a-z0-9](?:[a-z0-9-]{0,46}[a-z0-9])?\Z")
MAX_ARCHIVE=512_000
MAX_RECEIPT=64_000
class BrowserWorkerUnavailable(RuntimeError):pass
def title(nonce,project):return "Browser candidate "+nonce+" · "+project
def validate_identity(project,sha,nonce):
    if not (isinstance(project,str) and SLUG.fullmatch(project) and isinstance(sha,str) and SHA.fullmatch(sha)
            and isinstance(nonce,str) and NONCE.fullmatch(nonce)):
        raise BrowserWorkerUnavailable("BROWSER_REQUEST_IDENTITY_INVALID")
def github_api(token):
    """Trusted runner-only API adapter; no arbitrary origins."""
    def call(method,path,*,params=None,data=None):
        r=requests.request(method,"https://api.github.com/repos/"+REPO+"/"+path,
            headers={"Authorization":"Bearer "+token,"Accept":"application/vnd.github+json",
                     "X-GitHub-Api-Version":"2022-11-28"},params=params,json=data,timeout=22,allow_redirects=False)
        if r.status_code==204:return None
        if r.status_code!=200:raise BrowserWorkerUnavailable("GITHUB_BROWSER_API_HTTP_"+str(r.status_code))
        return r.json()
    return call
def download_receipt(token,artifact_id):
    if type(artifact_id) is not int or artifact_id<=0:raise BrowserWorkerUnavailable("INVALID_ARTIFACT_ID")
    url="https://api.github.com/repos/"+REPO+"/actions/artifacts/"+str(artifact_id)+"/zip"
    try:
        with requests.get(url,headers={"Authorization":"Bearer "+token,"Accept":"application/vnd.github+json",
                    "X-GitHub-Api-Version":"2022-11-28"},timeout=22,allow_redirects=False,stream=True) as first:
            if first.status_code not in (301,302,303,307,308):
                raise BrowserWorkerUnavailable("BROWSER_ARTIFACT_DOWNLOAD_HTTP_"+str(first.status_code))
            loc=first.headers.get("Location","")
        dest=urlsplit(loc)
        host=(dest.hostname or "").lower()
        if dest.scheme!="https" or dest.username or dest.password or dest.port not in (None,443) or not any(
                host.endswith(s) for s in (".blob.core.windows.net",".actions.githubusercontent.com",".githubusercontent.com")):
            raise BrowserWorkerUnavailable("BROWSER_ARTIFACT_REDIRECT_REJECTED")
        # Do not forward repository credentials to the storage origin.
        with requests.get(loc,timeout=25,allow_redirects=False,stream=True) as r:
            if r.status_code!=200:raise BrowserWorkerUnavailable("BROWSER_ARCHIVE_HTTP_"+str(r.status_code))
            raw=bytearray()
            for chunk in r.iter_content(16384):
                raw.extend(chunk)
                if len(raw)>MAX_ARCHIVE:raise BrowserWorkerUnavailable("BROWSER_ARCHIVE_TOO_LARGE")
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            members=z.infolist()
            if len(members)!=1 or members[0].filename!="browser-receipt.json" or not 0<members[0].file_size<=MAX_RECEIPT:
                raise BrowserWorkerUnavailable("BROWSER_ARTIFACT_SHAPE_INVALID")
            return json.loads(z.read(members[0]))
    except (requests.RequestException,ValueError,zipfile.BadZipFile,KeyError) as exc:
        raise BrowserWorkerUnavailable("BROWSER_ARTIFACT_UNAVAILABLE:"+type(exc).__name__) from exc
def check_run(run,project,sha,nonce,run_id):
    validate_identity(project,sha,nonce)
    if (not isinstance(run,dict) or type(run_id) is not int or run_id<=0
            or run.get("id")!=run_id or run.get("event")!="workflow_dispatch"
            or run.get("head_sha")!=sha or run.get("head_branch")!="main"
            or run.get("display_title")!=title(nonce,project)
            or str(run.get("path","")).split("@",1)[0]!=WORKFLOW_PATH
            or (run.get("actor") or {}).get("login") not in (OWNER,"github-actions[bot]")):
        raise BrowserWorkerUnavailable("BROWSER_WORKFLOW_RUN_IDENTITY_MISMATCH")
def fetch_verified_receipt(api,token,project,sha,nonce,run_id,hashes,*,download=download_receipt):
    run=api("GET","actions/runs/"+str(run_id))
    check_run(run,project,sha,nonce,run_id)
    if run.get("status")!="completed" or run.get("conclusion")!="success":
        raise BrowserWorkerUnavailable("BROWSER_WORKFLOW_NOT_SUCCESSFUL")
    listing=api("GET","actions/runs/"+str(run_id)+"/artifacts",params={"per_page":"30"})
    matches=[a for a in listing.get("artifacts",[]) if a.get("name")=="swrlz-browser-"+nonce and a.get("expired") is False]
    if len(matches)!=1 or type(matches[0].get("id")) is not int:raise BrowserWorkerUnavailable("BROWSER_RECEIPT_ARTIFACT_MISSING")
    r=download(token,matches[0]["id"])
    if (not isinstance(r,dict) or r.get("schema")!=SCHEMA or r.get("project")!=project
            or r.get("sourceSha")!=sha or r.get("nonce")!=nonce or r.get("runId")!=run_id
            or r.get("hashes")!=hashes or type(r.get("browserVerified")) is not bool
            or not isinstance(r.get("issues"),list) or len(r["issues"])>20
            or any(not isinstance(i,dict) or not isinstance(i.get("code"),str)
                   or not isinstance(i.get("detail"),str) or len(i["detail"])>1600 for i in r["issues"])):
        raise BrowserWorkerUnavailable("BROWSER_RECEIPT_IDENTITY_OR_HASH_MISMATCH")
    if r.get("infrastructureError"):
        raise BrowserWorkerUnavailable("BROWSER_WORKER_INFRASTRUCTURE:"+str(r["infrastructureError"])[:160])
    if r["browserVerified"] and (r["issues"] or r.get("entrySha256")!=hashes.get("index.html")):
        raise BrowserWorkerUnavailable("BROWSER_PASS_RECEIPT_INVALID")
    return r
class GitHubBrowserBackend:
    name="github-actions"
    def __init__(self,api,token,source_sha,*,cancel=None,timeout=300,download=download_receipt,clock=time.monotonic,sleep=time.sleep):
        self.api,self.token,self.source_sha=api,token,source_sha
        self.cancel,self.timeout,self.download,self.clock,self.sleep=cancel,timeout,download,clock,sleep
    def validate_candidate(self,project,files,canvas,proposal):
        try:
            from html_project_agent_v1 import verify_source
        except ImportError:
            from api.html_project_agent_v1 import verify_source
        hashes=verify_source(project,files)
        nonce=secrets.token_hex(16)
        validate_identity(project,self.source_sha,nonce)
        # Only the exact bounded patch for the existing public GitHub project is sent.
        # No chat transcript, private account data, model rationale or OAuth token.
        plan={k:proposal[k] for k in ("schema","project","patches")}
        encoded=json.dumps(plan,separators=(",",":"),ensure_ascii=False)
        if len(encoded.encode())>48000:raise BrowserWorkerUnavailable("BROWSER_PROPOSAL_TOO_LARGE")
        if self.cancel and self.cancel():raise BrowserWorkerUnavailable("CANCELLED")
        self.api("POST","actions/workflows/"+WORKFLOW+"/dispatches",
            data={"ref":"main","inputs":{"source_sha":self.source_sha,"project":project,
                "proposal_json":encoded,"nonce":nonce}})
        deadline=self.clock()+self.timeout
        run_id=None
        while self.clock()<deadline:
            if self.cancel and self.cancel():
                if run_id:
                    try:self.api("POST","actions/runs/"+str(run_id)+"/cancel")
                    except Exception:pass
                raise BrowserWorkerUnavailable("CANCELLED")
            if run_id is None:
                data=self.api("GET","actions/workflows/"+WORKFLOW+"/runs",
                              params={"event":"workflow_dispatch","branch":"main","per_page":"30"})
                matches=[r for r in data.get("workflow_runs",[]) if r.get("display_title")==title(nonce,project)]
                if len(matches)>1:raise BrowserWorkerUnavailable("AMBIGUOUS_BROWSER_RUN")
                if matches:
                    run_id=matches[0].get("id")
                    check_run(matches[0],project,self.source_sha,nonce,run_id)
            if run_id is not None:
                r=self.api("GET","actions/runs/"+str(run_id))
                check_run(r,project,self.source_sha,nonce,run_id)
                if r.get("status")=="completed":
                    receipt=fetch_verified_receipt(self.api,self.token,project,self.source_sha,nonce,run_id,hashes,download=self.download)
                    return {"backend":self.name,"receipt":receipt}
            self.sleep(3)
        if run_id:
            try:self.api("POST","actions/runs/"+str(run_id)+"/cancel")
            except Exception:pass
        raise BrowserWorkerUnavailable("BROWSER_WORKER_TIMEOUT")
class BackendSelector:
    """Stable adapter seam. A new worker implements validate_candidate, not model logic."""
    @property
    def name(self):return os.getenv("SWRLZ_BROWSER_BACKEND","github-actions")
    def for_source(self,owner,source_sha,payload):
        name=self.name
        if name=="github-actions":
            try:import github_html_publish_action_v1 as p
            except ImportError:from api import github_html_publish_action_v1 as p
            auth=p._authorized(owner)
            return GitHubBrowserBackend(lambda method,path,**kw:p._github(auth,method,path,**kw),
                     auth["token"],source_sha,cancel=payload.get("_cancelCheck"))
        if name=="isolated-server":
            # Only an authenticated, independently verified isolated worker may use this lane.
            try:from html_project_browser_client_v1 import validate
            except ImportError:from api.html_project_browser_client_v1 import validate
            return validate
        raise BrowserWorkerUnavailable("UNKNOWN_BROWSER_BACKEND")
backend=BackendSelector()
