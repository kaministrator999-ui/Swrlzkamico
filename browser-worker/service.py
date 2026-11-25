"""Single-flight browser worker; request bodies never persisted or logged."""
from __future__ import annotations
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import hmac,json,os,signal,subprocess,sys,threading,time,tempfile
from browser_worker_protocol_v1 import *
KEY=os.environ.get("SWRLZ_BROWSER_WORKER_KEY","")
if len(KEY)!=64:raise RuntimeError("BROWSER_WORKER_AUTH_REQUIRED")
ROOT=Path(__file__).resolve().parent
BUSY=threading.Lock()
SEEN={}
class Handler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup();self.connection.settimeout(12)
    def log_message(self,*args):pass
    def reply(self,status,obj):
        raw=encode(obj);self.send_response(status)
        self.send_header("Content-Type","application/json")
        self.send_header("Cache-Control","no-store")
        self.send_header("Content-Length",str(len(raw)));self.end_headers()
        self.wfile.write(raw)
    def do_GET(self):
        if self.path=="/health":self.reply(200,{"schema":VERSION,"service":"browser-worker","authenticatedRender":True})
        else:self.reply(404,{"error":"NOT_FOUND"})
    def do_POST(self):
        if self.path!="/v1/render":self.reply(404,{"error":"NOT_FOUND"});return
        if not self.headers.get("X-Swrlz-Signature"):self.reply(401,{"error":"AUTH_REQUIRED"});return
        if not BUSY.acquire(blocking=False):self.reply(429,{"error":"BROWSER_BUSY"});return
        try:
            try:length=int(self.headers.get("Content-Length","0"))
            except ValueError:length=0
            if not 0<length<=MAX_BODY:self.reply(413,{"error":"BODY_LIMIT"});return
            raw=self.rfile.read(length)
            if len(raw)!=length or not hmac.compare_digest(mac(KEY,"request",raw),self.headers.get("X-Swrlz-Signature","")):
                self.reply(401,{"error":"BAD_SIGNATURE"});return
            try:obj=validate_request(json.loads(raw))
            except (ValueError,TypeError,KeyError):self.reply(400,{"error":"INVALID_REQUEST"});return
            now=time.time()
            for k,v in list(SEEN.items()):
                if v<now-180:del SEEN[k]
            if obj["nonce"] in SEEN:self.reply(409,{"error":"REPLAY"});return
            if len(SEEN)>=256:self.reply(429,{"error":"REPLAY_CACHE_LIMIT"});return
            SEEN[obj["nonce"]]=now
            with tempfile.TemporaryDirectory(prefix="browser-job-") as home:
                # Child receives no HF/GitHub token, HMAC key or service environment.
                env={"PATH":os.defpath+":/usr/local/bin","HOME":home,"TMPDIR":home,
                     "LANG":"C.UTF-8","PLAYWRIGHT_BROWSERS_PATH":"/opt/pw-browsers","PYTHONDONTWRITEBYTECODE":"1"}
                proc=subprocess.Popen([sys.executable,"-I",str(ROOT/"render_entry.py")],
                    stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,
                    cwd=home,env=env,start_new_session=True)
                try:out,_=proc.communicate(raw,timeout=48)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid,signal.SIGKILL);proc.communicate()
                    self.reply(503,{"error":"BROWSER_EXECUTION_TIMEOUT"});return
                if proc.returncode or len(out)>80_000:
                    self.reply(503,{"error":"BROWSER_CHILD_FAILED"});return
                result=json.loads(out)
                self.reply(200,{"receipt":result,"signature":mac(KEY,"receipt",encode(result))})
        except (OSError,ValueError,TypeError,KeyError):
            try:self.reply(503,{"error":"BROWSER_WORKER_ERROR"})
            except OSError:pass
        finally:BUSY.release()
if __name__=="__main__":
    ThreadingHTTPServer(("0.0.0.0",7860),Handler).serve_forever()
