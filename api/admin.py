from __future__ import annotations
import hashlib,hmac,json,os,uuid
from pathlib import Path
from fastapi import FastAPI,Query,Request
from fastapi.responses import HTMLResponse,JSONResponse,PlainTextResponse

app=FastAPI(title="§wyrlz Admin",version="2.0.2")
ROOT=Path("/tmp/swrlz-admin"); LIVE=ROOT/"live"; UP=ROOT/"uploads"; LOG=ROOT/"full-runtime.log"
for d in (ROOT,LIVE,UP): d.mkdir(parents=True,exist_ok=True)
INSTANCE=f"{os.getpid()}-{uuid.uuid4().hex[:8]}"
TOKEN=os.environ.get("SWRLZ_ADMIN_TOKEN","")
MAX_CHUNK=3*1024*1024

PAGE="""<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>§wyrlz SERVER</title>
<style>body{font-family:system-ui;background:#090d13;color:#eef4ff;max-width:900px;margin:auto;padding:16px}input,button{font:inherit;padding:10px;margin:4px}pre{white-space:pre-wrap;background:#121927;padding:12px;border-radius:12px}.bar{height:12px;background:#222;border-radius:8px;overflow:hidden}.fill{height:100%;width:0;background:#7cff9b}</style></head>
<body><h1>§wyrlz SERVER Workbench</h1><p>Upload R39 into <b>/tmp/swrlz-admin/live</b>. /tmp is ephemeral.</p>
<input id='tok' type='password' placeholder='SWRLZ_ADMIN_TOKEN'><button onclick='saveTok()'>SET TOKEN</button><br>
<input id='fi' type='file' multiple><button onclick='uploadAll()'>UPLOAD</button><div class='bar'><div id='f' class='fill'></div></div><pre id='o'>Ready.</pre>
<script>
let token=sessionStorage.getItem('swrlzAdminToken')||'';document.getElementById('tok').value=token;const CHUNK=2*1024*1024;
function saveTok(){token=document.getElementById('tok').value.trim();sessionStorage.setItem('swrlzAdminToken',token)}
async function call(action,q={},body=null){let u='/api/admin?'+new URLSearchParams({action,...q});let r=await fetch(u,{method:'POST',headers:{'x-swrlz-admin-token':token},body});let j=await r.json();if(!r.ok)throw Error(j.error||JSON.stringify(j));return j}
async function one(file){let init=await call('upload-init',{path:'/tmp/swrlz-admin/live',name:file.name,size:file.size});let off=0;while(off<file.size){let end=Math.min(off+CHUNK,file.size);let j=await call('upload-chunk',{uploadId:init.uploadId,offset:off,instanceId:init.instanceId},file.slice(off,end));off=j.received;document.getElementById('f').style.width=(off/file.size*100)+'%';document.getElementById('o').textContent=file.name+' '+Math.floor(off/file.size*100)+'%'}let done=await call('upload-finish',{uploadId:init.uploadId,instanceId:init.instanceId});document.getElementById('o').textContent=JSON.stringify(done,null,2)}
async function uploadAll(){try{for(const f of document.getElementById('fi').files)await one(f)}catch(e){document.getElementById('o').textContent='FAILED: '+e.message}}
</script></body></html>"""

def auth(req):
    supplied=req.headers.get("x-swrlz-admin-token","")
    return bool(TOKEN) and hmac.compare_digest(supplied,TOKEN)

def mp(uid): return UP/f"{uid}.json"
def load(uid): return json.loads(mp(uid).read_text("utf-8"))
def save(uid,m): mp(uid).write_text(json.dumps(m),"utf-8")

@app.get("/")
@app.get("/api/admin")
def get_admin(action:str|None=Query(default=None)):
    if not action: return HTMLResponse(PAGE)
    if action=="log": return PlainTextResponse(LOG.read_text("utf-8","replace") if LOG.exists() else "")
    if action=="runtime": return {"ok":True,"instanceId":INSTANCE,"uploadAuthConfigured":bool(TOKEN),"root":str(ROOT)}
    return JSONResponse(status_code=400,content={"ok":False,"error":"unknown action"})

@app.post("/")
@app.post("/api/admin")
async def post_admin(request:Request,action:str=Query(...),path:str|None=Query(default=None),name:str|None=Query(default=None),size:int|None=Query(default=None),uploadId:str|None=Query(default=None),offset:int=Query(default=0),instanceId:str|None=Query(default=None)):
    if not auth(request): return JSONResponse(status_code=401,content={"ok":False,"error":"invalid or missing SWRLZ_ADMIN_TOKEN"})
    try:
        if action=="upload-init":
            if not name or size is None or size<0: raise ValueError("name and size required")
            base=Path(path or LIVE).resolve(); rr=ROOT.resolve()
            if base!=rr and rr not in base.parents: raise PermissionError("destination outside /tmp/swrlz-admin")
            base.mkdir(parents=True,exist_ok=True); target=base/Path(name).name
            uid=uuid.uuid4().hex; part=UP/f"{uid}.part"; part.touch()
            m={"uploadId":uid,"instanceId":INSTANCE,"target":str(target),"part":str(part),"expected":size,"received":0}; save(uid,m)
            return {"ok":True,"uploadId":uid,"instanceId":INSTANCE,"chunkBytes":MAX_CHUNK}
        if action=="upload-chunk":
            if instanceId!=INSTANCE: return JSONResponse(status_code=409,content={"ok":False,"error":"runtime instance changed"})
            m=load(uploadId); body=await request.body()
            if len(body)>MAX_CHUNK: return JSONResponse(status_code=413,content={"ok":False,"error":"chunk too large"})
            if offset!=m["received"]: return JSONResponse(status_code=409,content={"ok":False,"error":"offset mismatch","received":m["received"]})
            with Path(m["part"]).open("ab") as f: f.write(body)
            m["received"]+=len(body); save(uploadId,m)
            return {"ok":True,"received":m["received"],"expected":m["expected"]}
        if action=="upload-finish":
            if instanceId!=INSTANCE: return JSONResponse(status_code=409,content={"ok":False,"error":"runtime instance changed"})
            m=load(uploadId); part=Path(m["part"]); target=Path(m["target"])
            if m["received"]!=m["expected"] or part.stat().st_size!=m["expected"]: return JSONResponse(status_code=409,content={"ok":False,"error":"upload incomplete"})
            os.replace(part,target); h=hashlib.sha256()
            with target.open("rb") as f:
                for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
            mp(uploadId).unlink(missing_ok=True)
            return {"ok":True,"path":str(target),"size":target.stat().st_size,"sha256":h.hexdigest(),"instanceId":INSTANCE}
        return JSONResponse(status_code=400,content={"ok":False,"error":"unknown action"})
    except Exception as exc:
        return JSONResponse(status_code=500,content={"ok":False,"error":f"{type(exc).__name__}: {exc}"})
