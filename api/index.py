from __future__ import annotations

import hashlib
import hmac
import json
import mimetypes
import os
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response

from swyrlz.backend import LIVE, PACKED, RAW, ensure_r39, sha

VERSION = "2.1.1"
ROOT = Path("/tmp/swrlz-admin")
UP = ROOT / "uploads"
LOG = ROOT / "full-runtime.log"
for directory in (ROOT, LIVE, UP):
    directory.mkdir(parents=True, exist_ok=True)

INSTANCE = f"{os.getpid()}-{uuid.uuid4().hex[:8]}"
TOKEN = os.environ.get("SWRLZ_ADMIN_TOKEN", "").strip()
MAX_CHUNK = 3 * 1024 * 1024
DOWNLOAD_CHUNK = 3 * 1024 * 1024
DIRECT_DOWNLOAD_MAX = 4 * 1024 * 1024
MAX_TEXT_EDIT = 4 * 1024 * 1024
GATE5 = LIVE / "gate5_live.py"

app = FastAPI(title="§wyrlz Unified Server Workbench", version=VERSION)

# Additive R299-derived web chat surface. Existing admin/LALM routes remain unchanged.
from api.chat import app as swrlz_chat_app

app.mount("/api/chat", swrlz_chat_app, name="swrlz-chat")


def auth(request: Request) -> bool:
    supplied = request.headers.get("x-swrlz-admin-token", "").strip()
    return bool(TOKEN) and hmac.compare_digest(supplied, TOKEN)


def safe_path(value: str | None, default: Path = LIVE) -> Path:
    candidate = Path(value) if value else default
    resolved = candidate.resolve() if candidate.is_absolute() else (ROOT / candidate).resolve()
    root = ROOT.resolve()
    if resolved != root and root not in resolved.parents:
        raise PermissionError("path outside /tmp/swrlz-admin")
    return resolved


def mime_for(path: Path) -> str:
    return mimetypes.guess_type(path.name)[0] or "application/octet-stream"


def text_candidate(path: Path, mime: str | None = None) -> bool:
    mime = mime or mime_for(path)
    if mime.startswith("text/") or mime in {"application/json", "application/javascript", "application/xml", "application/x-sh", "application/sql"}:
        return True
    return path.suffix.lower() in {".py", ".kt", ".kts", ".java", ".js", ".ts", ".tsx", ".jsx", ".html", ".css", ".scss", ".json", ".md", ".txt", ".log", ".xml", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf", ".env", ".sh", ".bat", ".ps1", ".sql", ".csv", ".gradle", ".properties"}


def file_info(path: Path) -> dict:
    stat = path.stat()
    mime = "inode/directory" if path.is_dir() else mime_for(path)
    return {
        "name": path.name,
        "path": str(path),
        "type": "directory" if path.is_dir() else "file",
        "size": stat.st_size,
        "modified": int(stat.st_mtime),
        "mime": mime,
        "editable": path.is_file() and text_candidate(path, mime) and stat.st_size <= MAX_TEXT_EDIT,
    }


def upload_meta_path(upload_id: str) -> Path:
    return UP / f"{upload_id}.json"


def append_log(text: str) -> None:
    with LOG.open("a", encoding="utf-8", errors="replace") as out:
        out.write(text)
        if not text.endswith("\n"):
            out.write("\n")


def lalm_presence() -> dict:
    return {
        "packedPresent": PACKED.is_file(),
        "packedSize": PACKED.stat().st_size if PACKED.is_file() else None,
        "rawPresent": RAW.is_file(),
        "rawSize": RAW.stat().st_size if RAW.is_file() else None,
        "rawPath": str(RAW),
    }


def preview(path: Path) -> dict:
    if not path.is_file():
        raise ValueError("not a file")
    info = file_info(path)
    if text_candidate(path, info["mime"]) and path.stat().st_size <= MAX_TEXT_EDIT:
        raw = path.read_bytes()
        try:
            text = raw.decode("utf-8")
            if "\x00" not in text:
                return {**info, "previewKind": "text", "content": text}
        except UnicodeDecodeError:
            pass
    with path.open("rb") as handle:
        raw = handle.read(4096)
    return {
        **info,
        "previewKind": "binary",
        "hex": raw.hex(" "),
        "previewBytes": len(raw),
        "sha256": sha(path) if path.stat().st_size <= 64 * 1024 * 1024 else None,
    }


def run_gate5() -> dict:
    state = ensure_r39()
    if not state.get("ok") or not state.get("modelReady"):
        return {"ok": False, "code": "R39_NOT_READY", "lalm": state}
    if not GATE5.is_file():
        return {"ok": False, "code": "GATE5_NOT_PRESENT", "detail": str(GATE5), "lalm": state}
    env = os.environ.copy()
    env.update({
        "SWRLZ_R39_PATH": str(RAW),
        "SWRLZ_LALM_PATH": str(RAW),
        "SWRLZ_R39_GZ_PATH": str(PACKED),
        "SWRLZ_LIVE_DIR": str(LIVE),
    })
    started = time.time()
    proc = subprocess.run(
        [sys.executable, str(GATE5)],
        cwd=str(LIVE),
        env=env,
        capture_output=True,
        text=True,
        errors="replace",
        timeout=240,
    )
    elapsed = round(time.time() - started, 3)
    append_log(f"\n=== GATE 5 {time.strftime('%Y-%m-%d %H:%M:%S')} instance={INSTANCE} rc={proc.returncode} elapsed={elapsed}s ===\n{proc.stdout}{proc.stderr}")
    return {
        "ok": proc.returncode == 0,
        "returnCode": proc.returncode,
        "elapsedSeconds": elapsed,
        "stdout": proc.stdout[-20000:],
        "stderr": proc.stderr[-20000:],
        "instanceId": INSTANCE,
        "modelPath": str(RAW),
        "lalm": state,
    }


PAGE = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#080813">
<title>§wyrlz Dragon Jester Workbench</title>
<style>
:root{
 color-scheme:dark;--bg:#070812;--panel:rgba(12,18,35,.86);--panel2:rgba(9,14,28,.96);--line:#28466d;
 --blue:#52c7ff;--cyan:#74f4ff;--violet:#985cff;--purple:#d66cff;--green:#51f49c;--amber:#ffb43c;
 --red:#ff667d;--text:#eff7ff;--muted:#91a9c7;--shadow:0 18px 60px rgba(0,0,0,.42);
}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,sans-serif;color:var(--text);background:
 radial-gradient(circle at 10% -10%,rgba(45,115,255,.22),transparent 33%),
 radial-gradient(circle at 92% 8%,rgba(170,55,255,.19),transparent 34%),
 linear-gradient(180deg,#050711,#090d18 46%,#050810);min-height:100vh;overflow-x:hidden}
body:before{content:"";position:fixed;inset:0;pointer-events:none;opacity:.16;background-image:linear-gradient(rgba(92,182,255,.12) 1px,transparent 1px),linear-gradient(90deg,rgba(92,182,255,.12) 1px,transparent 1px);background-size:36px 36px;mask-image:linear-gradient(to bottom,#000,transparent 84%)}
.shell{width:min(1180px,calc(100% - 24px));margin:auto;padding:18px 0 56px;position:relative}.hero{position:relative;overflow:hidden;border:1px solid rgba(95,117,255,.42);border-radius:26px;background:linear-gradient(135deg,rgba(13,26,51,.96),rgba(18,9,38,.92));box-shadow:var(--shadow),inset 0 0 60px rgba(82,199,255,.04);padding:24px;margin-bottom:14px}
.hero:before,.hero:after{position:absolute;font-size:150px;line-height:1;opacity:.13;filter:drop-shadow(0 0 24px currentColor);pointer-events:none}.hero:before{content:"🐉";left:-22px;top:-15px;color:var(--blue);transform:rotate(-12deg)}.hero:after{content:"🃏";right:-5px;top:-16px;color:var(--purple);transform:rotate(8deg)}
.hero-inner{position:relative;z-index:1;text-align:center}.sigil{font-size:.74rem;letter-spacing:.35em;text-transform:uppercase;color:var(--cyan);font-weight:800}.brand{margin:4px 0 0;font-family:Georgia,'Times New Roman',serif;font-size:clamp(2.3rem,9vw,5.3rem);line-height:.92;letter-spacing:.06em;background:linear-gradient(180deg,#fff 0%,#86cfff 40%,#bb78ff 80%,#fff 100%);-webkit-background-clip:text;background-clip:text;color:transparent;text-shadow:0 0 32px rgba(115,104,255,.24)}
.subtitle{font-size:clamp(1rem,3vw,1.45rem);letter-spacing:.28em;color:#73dfff;font-weight:700;margin-top:9px}.motto{color:var(--muted);letter-spacing:.18em;font-size:.78rem;margin-top:8px}.hero-badges{display:flex;justify-content:center;flex-wrap:wrap;gap:8px;margin-top:18px}.badge{border:1px solid rgba(99,154,255,.38);background:rgba(5,13,28,.7);border-radius:999px;padding:7px 11px;font-size:.76rem;color:#b9d8ff}.badge.online{color:#8fffc2;border-color:rgba(81,244,156,.4)}
.nav{position:sticky;top:7px;z-index:20;display:grid;grid-template-columns:repeat(6,1fr);gap:8px;margin:12px 0 18px;padding:8px;border:1px solid rgba(71,112,176,.36);border-radius:18px;background:rgba(6,11,24,.84);backdrop-filter:blur(18px);box-shadow:0 10px 35px rgba(0,0,0,.3)}
a.navbtn,button.navbtn{text-decoration:none;text-align:center;color:#cfe8ff;padding:10px 8px;border-radius:12px;border:1px solid transparent;background:transparent;font-weight:800;font-size:.75rem;letter-spacing:.05em;cursor:pointer}.navbtn:hover,.navbtn:focus{background:linear-gradient(135deg,rgba(42,120,255,.18),rgba(151,65,255,.17));border-color:#426aa1;color:#fff;outline:none}
.grid{display:grid;grid-template-columns:minmax(250px,340px) minmax(0,1fr);gap:14px}.stack{display:grid;gap:14px}.card{position:relative;border:1px solid rgba(65,103,157,.54);border-radius:20px;background:linear-gradient(145deg,rgba(14,23,42,.91),rgba(8,13,27,.94));box-shadow:0 12px 35px rgba(0,0,0,.26),inset 0 1px rgba(255,255,255,.025);padding:18px;overflow:hidden}.card:before{content:"";position:absolute;inset:0 0 auto;height:1px;background:linear-gradient(90deg,transparent,var(--blue),var(--violet),transparent);opacity:.6}.card h2{font-size:1rem;letter-spacing:.08em;text-transform:uppercase;color:#8edcff;margin:0 0 14px;display:flex;gap:8px;align-items:center}.card h3{margin:0;color:#dcecff}.muted{color:var(--muted)}.tiny{font-size:.75rem}.divider{height:1px;background:#20324b;margin:14px 0}
.statusgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.stat{border:1px solid #294c76;background:rgba(7,17,34,.72);padding:12px;border-radius:14px;min-width:0}.stat .k{font-size:.68rem;color:#8fa8c5;text-transform:uppercase;letter-spacing:.11em}.stat .v{font-weight:850;color:#e9f8ff;margin-top:4px;overflow-wrap:anywhere}.dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--green);box-shadow:0 0 14px var(--green);margin-right:6px}
.row{display:flex;flex-wrap:wrap;gap:9px;align-items:center}input,button,textarea{font:inherit}input{min-width:0;background:#070d1a;color:#fff;border:1px solid #31557d;border-radius:12px;padding:11px 12px;box-shadow:inset 0 0 18px rgba(28,105,188,.04)}input:focus,textarea:focus{outline:none;border-color:#6caeff;box-shadow:0 0 0 3px rgba(75,142,255,.12)}button{background:linear-gradient(145deg,#13243d,#182b46);color:#eaf5ff;border:1px solid #365b87;border-radius:12px;padding:10px 14px;font-weight:800;cursor:pointer;transition:.18s transform,.18s border-color,.18s filter}button:hover{filter:brightness(1.12);border-color:#6aa6ee}button:active{transform:translateY(1px)}button.good{background:linear-gradient(135deg,#0c663f,#124d47);border-color:#25cb79;box-shadow:0 0 18px rgba(50,236,132,.09)}button.hot{background:linear-gradient(135deg,#7d4315,#473321);border-color:#f7a532;box-shadow:0 0 20px rgba(255,153,0,.11)}button.danger{background:linear-gradient(135deg,#622331,#3b1824);border-color:#b63d54}button:disabled{opacity:.42;cursor:not-allowed;filter:none}.wide{width:100%}.token{flex:1;min-width:190px}.action-stack{display:grid;gap:9px}.checkline{display:flex;gap:9px;align-items:center;color:#b9cee5;font-size:.83rem}.check{color:var(--green);font-weight:900}.warn{color:#ffd084}.quote{text-align:center;color:#ad8cff;font-family:Georgia,serif;font-style:italic;letter-spacing:.05em;padding:2px 8px}
pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#050b15;padding:14px;border-radius:14px;border:1px solid #152a45;max-height:440px;overflow:auto;color:#cae6ff;font:12.5px/1.55 ui-monospace,SFMono-Regular,Consolas,monospace;box-shadow:inset 0 0 34px rgba(0,0,0,.32)}#status{min-height:96px;margin:12px 0 0}.console{min-height:310px}.bar{height:10px;background:#131d2d;border:1px solid #1f3350;border-radius:99px;overflow:hidden;margin:9px 0}.fill{height:100%;width:0;background:linear-gradient(90deg,var(--blue),var(--violet),var(--green));box-shadow:0 0 12px rgba(102,213,255,.45)}
#path{flex:1;min-width:210px}#fi{flex:1;min-width:210px}#files{margin-top:12px;border-top:1px solid #20314a}.entry{display:grid;grid-template-columns:1fr auto;gap:10px;padding:11px 6px;border-bottom:1px solid #1d2c43;align-items:center}.entry:hover{background:rgba(52,112,189,.06)}.entry button{padding:7px 10px}.name{overflow-wrap:anywhere}.meta{font-size:.76rem;color:#7f99b9;margin-top:4px}textarea{width:100%;min-height:430px;background:#050b15;color:#eef6ff;border:1px solid #31557d;border-radius:14px;padding:14px;font-family:ui-monospace,SFMono-Regular,Consolas,monospace;white-space:pre;overflow:auto}iframe,img,video,audio{max-width:100%;border-radius:12px}iframe{width:100%;height:520px;background:white}.full{grid-column:1/-1}.toolstrip{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:14px}.tooltile{border:1px solid #29496f;border-radius:14px;background:#0a1424;padding:13px;text-align:center;color:#a9dfff;font-weight:800;font-size:.8rem}.tooltile span{display:block;font-size:1.45rem;margin-bottom:4px}.footer{text-align:center;color:#7189a8;padding:28px 8px 0;font-size:.75rem;letter-spacing:.14em}.footer strong{color:#9cbfff}.infinity{font-size:2rem;color:#8c70ff;line-height:1}
@media(max-width:860px){.grid{grid-template-columns:1fr}.statusgrid{grid-template-columns:repeat(2,1fr)}.nav{grid-template-columns:repeat(3,1fr);position:relative;top:auto}.toolstrip{grid-template-columns:repeat(2,1fr)}}
@media(max-width:520px){.shell{width:min(100% - 14px,1180px);padding-top:8px}.hero{padding:20px 12px}.hero:before,.hero:after{font-size:95px}.nav{gap:5px;padding:6px}.navbtn{font-size:.67rem!important}.card{padding:14px;border-radius:17px}.statusgrid{grid-template-columns:1fr 1fr}.row>*{max-width:100%}.row input{width:100%}.row button{flex:1}.toolstrip{grid-template-columns:1fr 1fr}.brand{letter-spacing:.025em}}
</style>
</head>
<body>
<div class="shell">
<header class="hero" id="top">
 <div class="hero-inner">
  <div class="sigil">Dragon Jester Protocol</div>
  <div class="brand">§WYRLZ</div>
  <div class="subtitle">SERVER WORKBENCH</div>
  <div class="motto">GLITCH · BUILD · RUN · EVOLVE</div>
  <div class="hero-badges"><span class="badge online"><span class="dot"></span>SERVER ONLINE</span><span class="badge">v2.1.1</span><span class="badge">R39 · GATE 5</span><span class="badge">UNIFIED RUNTIME</span></div>
 </div>
</header>
<nav class="nav" aria-label="Workbench navigation">
 <a class="navbtn" href="#status-card">⌁ STATUS</a><a class="navbtn" href="#files-card">▣ FILES</a><a class="navbtn" href="#lalm-card">◈ LALM</a><a class="navbtn" href="#runtime-card">🔥 RUNTIME</a><a class="navbtn" href="#logs-card">≡ LOGS</a><a class="navbtn" href="/api/chat">✦ CHAT</a>
</nav>
<section class="card" id="status-card">
 <h2>⚡ System Status</h2>
 <div class="statusgrid">
  <div class="stat"><div class="k">Server</div><div class="v"><span class="dot"></span>Online</div></div>
  <div class="stat"><div class="k">Version</div><div class="v">2.1.1</div></div>
  <div class="stat"><div class="k">Runtime</div><div class="v">Unified API</div></div>
  <div class="stat"><div class="k">Storage</div><div class="v">/tmp ephemeral</div></div>
 </div>
 <p class="muted tiny">Admin + R39 + Gate 5 + Chat integration. Large transfers remain response-safe and instance-guarded.</p>
</section>
<div class="grid" style="margin-top:14px">
 <div class="stack">
  <section class="card" id="auth-card">
   <h2>🗝 Admin Auth</h2>
   <div class="row"><input class="token" id="tok" type="password" autocomplete="current-password" placeholder="SWRLZ_ADMIN_TOKEN"><button onclick="saveTok()">SET TOKEN</button></div>
   <div class="action-stack" style="margin-top:10px"><button onclick="runtime()">RUNTIME RECEIPT</button><button class="good" onclick="location.href='/api/chat'">✦ OPEN CHAT</button></div>
   <pre id="status">Admin token required. Diagnostics will appear here.</pre>
  </section>
  <section class="card" id="lalm-card">
   <h2>◈ LALM Operations</h2>
   <button class="good wide" onclick="loadLalm()">⬇ LOAD / VERIFY LALM</button>
   <div class="divider"></div>
   <div class="checkline"><span class="check">✓</span> Reconstruct Forge transport</div><div class="checkline"><span class="check">✓</span> Verify R39 integrity</div><div class="checkline"><span class="check">✓</span> Prepare local runtime</div><div class="checkline"><span class="warn">◇</span> Inference wiring tracked separately</div>
  </section>
  <section class="card" id="runtime-card">
   <h2>⚙ Runtime / Gate 5</h2>
   <button class="hot wide" onclick="runGate5()">🔥 RUN HOT GATE 5</button>
   <div class="divider"></div>
   <div class="checkline"><span class="check">✓</span> Same-invocation R39 verification</div><div class="checkline"><span class="check">✓</span> Container structure probe</div><div class="checkline"><span class="check">✓</span> Runtime log capture</div>
  </section>
  <div class="quote">“Chaos creates clarity when the receipts survive.”</div>
 </div>
 <div class="stack">
  <section class="card" id="files-card">
   <h2>▣ Server Files</h2>
   <div class="row"><button onclick="up()">↑ UP ONE DIR</button><input id="path" value="/tmp/swrlz-admin/live"><button onclick="refresh()">GO / REFRESH</button><button onclick="newFolder()">NEW FOLDER</button></div>
   <div class="row" style="margin-top:10px"><input id="fi" type="file" multiple><button onclick="uploadAll()">UPLOAD ANY FILES</button></div>
   <div class="bar"><div id="progress" class="fill"></div></div><div id="summary" class="muted tiny"></div><div id="files"></div>
  </section>
  <section class="card" id="viewer-card">
   <h2>⌕ Viewer / Editor</h2><div id="selected" class="muted tiny">No file selected.</div>
   <div class="row" style="margin:10px 0"><button id="saveBtn" onclick="saveText()" disabled>SAVE TEXT</button><button id="downloadBtn" onclick="downloadSelected()" disabled>DOWNLOAD</button><button id="hashBtn" onclick="hashSelected()" disabled>SHA-256</button><button id="renameBtn" onclick="renameSelected()" disabled>RENAME</button><button id="deleteBtn" class="danger" onclick="deleteSelected()" disabled>DELETE</button></div>
   <div class="bar"><div id="downloadProgress" class="fill"></div></div><div id="viewer"><pre>Select a file to preview it.</pre></div>
  </section>
 </div>
 <section class="card full" id="logs-card">
  <h2>⌁ Runtime Console</h2><div class="row"><button onclick="loadLog()">OPEN FULL LOG</button><button onclick="downloadLog()">DOWNLOAD LOG</button></div><pre id="log" class="console">Log not loaded.</pre>
  <div class="toolstrip"><div class="tooltile"><span>📁</span>Server Files</div><div class="tooltile"><span>◈</span>R39 Inspector</div><div class="tooltile"><span>⚙</span>Runtime State</div><div class="tooltile"><span>🃏</span>Dragon Jester</div></div>
 </section>
</div>
<footer class="footer"><div class="infinity">∞</div><strong>KAMI + §WYRLZ</strong><br>DRAGON JESTER PROTOCOL // R39 // GATE 5 // VERCEL</footer>
</div>
<script>
let token=sessionStorage.getItem('swrlzAdminToken')||'',selected=null,selectedMeta=null;const CHUNK=2*1024*1024;document.getElementById('tok').value=token;
async function saveTok(){token=document.getElementById('tok').value.trim();sessionStorage.setItem('swrlzAdminToken',token);try{let j=await api('auth-check');status(j);await refresh()}catch(e){status('FAILED: '+e.message)}}function status(x){document.getElementById('status').textContent=typeof x==='string'?x:JSON.stringify(x,null,2)}function esc(s){return String(s).replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]))}function fmt(n){if(n==null)return '—';let u=['B','KB','MB','GB'],i=0,v=n;while(v>=1024&&i<u.length-1){v/=1024;i++}return v.toFixed(i?2:0)+' '+u[i]}
async function api(action,q={},body=null,response='json'){const u='/api/admin?'+new URLSearchParams({action,...q});const r=await fetch(u,{method:'POST',headers:{'x-swrlz-admin-token':token},body});if(response==='blob'){if(!r.ok)throw Error(await r.text());return r.blob()}const j=await r.json();if(!r.ok)throw Error(JSON.stringify(j,null,2));return j}
async function chunkRequest(path,instanceId,offset,length){const u='/api/admin?'+new URLSearchParams({action:'download-chunk',path,instanceId,offset,length});const r=await fetch(u,{method:'POST',headers:{'x-swrlz-admin-token':token}});if(!r.ok)throw Error(await r.text());return new Uint8Array(await r.arrayBuffer())}
async function downloadInfo(path){return api('download-info',{path})}
async function downloadBlobChunked(path){const info=await downloadInfo(path),parts=[];let off=0;while(off<info.size){const n=Math.min(info.chunkBytes,info.size-off),part=await chunkRequest(path,info.instanceId,off,n);parts.push(part);off+=part.byteLength;document.getElementById('downloadProgress').style.width=(off/info.size*100)+'%';status('Downloading '+info.name+' '+Math.floor(off/info.size*100)+'%')}document.getElementById('downloadProgress').style.width='0';return {blob:new Blob(parts,{type:info.mime}),info}}
async function saveChunked(path){const name=path.split('/').pop();let handle=null;if('showSaveFilePicker' in window){try{handle=await window.showSaveFilePicker({suggestedName:name})}catch(e){if(e.name==='AbortError')return}}const info=await downloadInfo(path);let off=0,parts=[],writable=handle?await handle.createWritable():null;try{while(off<info.size){const n=Math.min(info.chunkBytes,info.size-off),part=await chunkRequest(path,info.instanceId,off,n);if(writable)await writable.write(part);else parts.push(part);off+=part.byteLength;document.getElementById('downloadProgress').style.width=(off/info.size*100)+'%';status('Downloading '+info.name+' '+fmt(off)+' / '+fmt(info.size)+' ('+Math.floor(off/info.size*100)+'%)')}if(writable)await writable.close();else{const blob=new Blob(parts,{type:info.mime}),a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=info.name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),4000)}status('Download complete: '+info.name+' · '+fmt(info.size))}catch(e){if(writable)try{await writable.abort()}catch(_){ }throw e}finally{document.getElementById('downloadProgress').style.width='0'}}
async function runtime(){try{status(await api('runtime'))}catch(e){status('FAILED: '+e.message)}}function currentPath(){return document.getElementById('path').value.trim()}function up(){let p=currentPath().replace(/\/+$/,''),i=p.lastIndexOf('/');document.getElementById('path').value=i>0?p.slice(0,i):'/tmp/swrlz-admin';refresh()}
async function refresh(){try{let j=await api('list',{path:currentPath()});document.getElementById('path').value=j.path;document.getElementById('summary').textContent=j.entries.length+' entries · '+j.path;document.getElementById('files').innerHTML=j.entries.map(e=>`<div class="entry"><div class="name">${e.type==='directory'?'📁':'📄'} <b>${esc(e.name)}</b><div class="meta">${esc(e.type)} · ${fmt(e.size)} · ${esc(e.mime)}</div></div><button onclick='openEntry(${JSON.stringify(e.path)})'>OPEN</button></div>`).join('');return j}catch(e){status('FAILED: '+e.message);throw e}}
async function openEntry(path){try{let j=await api('preview',{path});if(j.type==='directory'){document.getElementById('path').value=j.path;return refresh()}selected=j.path;selectedMeta=j;document.getElementById('selected').textContent=j.path+' · '+fmt(j.size)+' · '+j.mime;for(const id of ['downloadBtn','hashBtn','renameBtn','deleteBtn'])document.getElementById(id).disabled=false;document.getElementById('saveBtn').disabled=j.previewKind!=='text';let v=document.getElementById('viewer');if(j.previewKind==='text'){v.innerHTML='<textarea id="editor"></textarea>';document.getElementById('editor').value=j.content}else if(j.mime.startsWith('image/'))await mediaPreview('img',j);else if(j.mime.startsWith('video/'))await mediaPreview('video',j);else if(j.mime.startsWith('audio/'))await mediaPreview('audio',j);else if(j.mime==='application/pdf')await mediaPreview('iframe',j);else v.innerHTML='<pre>'+esc('Binary file\n'+(j.sha256?'SHA-256: '+j.sha256+'\n':'')+'First '+j.previewBytes+' bytes:\n'+j.hex)+'</pre>'}catch(e){status('FAILED: '+e.message)}}
async function mediaPreview(tag,j){let d=await downloadBlobChunked(j.path),url=URL.createObjectURL(d.blob),v=document.getElementById('viewer');if(tag==='img')v.innerHTML=`<img src="${url}">`;else if(tag==='video')v.innerHTML=`<video controls src="${url}"></video>`;else if(tag==='audio')v.innerHTML=`<audio controls src="${url}"></audio>`;else v.innerHTML=`<iframe src="${url}"></iframe>`}
async function saveText(){try{let text=document.getElementById('editor').value;status(await api('save-text',{path:selected},new Blob([text],{type:'text/plain;charset=utf-8'})));refresh()}catch(e){status('FAILED: '+e.message)}}async function downloadSelected(){if(!selected)return;try{await saveChunked(selected)}catch(e){status('FAILED: '+e.message)}}async function hashSelected(){try{status(await api('hash',{path:selected}))}catch(e){status('FAILED: '+e.message)}}
async function renameSelected(){let n=prompt('New file name',selectedMeta?.name||'');if(!n)return;try{let j=await api('rename',{path:selected,newName:n});selected=j.path;status(j);refresh();openEntry(j.path)}catch(e){status('FAILED: '+e.message)}}async function deleteSelected(){if(!selected||!confirm('Delete '+selected+' ?'))return;try{status(await api('delete',{path:selected}));selected=null;selectedMeta=null;document.getElementById('viewer').innerHTML='<pre>Select a file to preview it.</pre>';refresh()}catch(e){status('FAILED: '+e.message)}}async function newFolder(){let n=prompt('Folder name');if(!n)return;try{status(await api('mkdir',{path:currentPath(),name:n}));refresh()}catch(e){status('FAILED: '+e.message)}}
async function one(file){let init=await api('upload-init',{path:currentPath(),name:file.name,size:file.size}),off=0;while(off<file.size){let end=Math.min(off+CHUNK,file.size),j=await api('upload-chunk',{uploadId:init.uploadId,offset:off,instanceId:init.instanceId},file.slice(off,end));off=j.received;document.getElementById('progress').style.width=(off/file.size*100)+'%';status(file.name+' '+Math.floor(off/file.size*100)+'%')}return api('upload-finish',{uploadId:init.uploadId,instanceId:init.instanceId})}async function uploadAll(){try{for(const f of document.getElementById('fi').files)status(await one(f));document.getElementById('progress').style.width='0';refresh()}catch(e){status('FAILED: '+e.message)}}
async function loadLalm(){try{status('Loading and verifying R39 in this runtime…');status(await api('lalm-load'));refresh()}catch(e){status('FAILED: '+e.message)}}async function runGate5(){try{status('Preparing R39 and running Gate 5 in the same invocation…');status(await api('gate5-run'));loadLog();refresh()}catch(e){status('FAILED: '+e.message)}}async function loadLog(){try{let j=await api('log-read');document.getElementById('log').textContent=j.content}catch(e){status('FAILED: '+e.message)}}async function downloadLog(){try{await saveChunked('/tmp/swrlz-admin/full-runtime.log')}catch(e){status('FAILED: '+e.message)}}
if(token)refresh();
</script>
</body></html>'''


@app.get("/")
@app.get("/api")
def root():
    return {"ok": True, "service": "§wyrlz Unified Vercel Server", "version": VERSION, "health": "/api/health", "admin": "/api/admin", "lalm": "/api/lalm", "chat": "/api/chat"}


@app.get("/api/health")
def health():
    return {"ok": True, "version": VERSION, "routingReady": True, "runtimeBoundary": "single-api-index", "instanceId": INSTANCE, "adminAuthConfigured": bool(TOKEN), **lalm_presence(), "storage": "Vercel /tmp is ephemeral and instance-local; Gate 5 loads/verifies R39 in the same invocation."}


@app.get("/api/lalm")
def lalm():
    try:
        state = ensure_r39()
        return JSONResponse(status_code=200 if state.get("ok") else 503, content={**state, "instanceId": INSTANCE})
    except Exception as exc:
        return JSONResponse(status_code=500, content={"ok": False, "code": "R39_LOAD_FAILED", "detail": f"{type(exc).__name__}: {exc}", "instanceId": INSTANCE})


@app.get("/api/admin")
def admin_page():
    return HTMLResponse(PAGE)


@app.post("/api/admin")
async def admin_action(
    request: Request,
    action: str = Query(...),
    path: str | None = Query(default=None),
    name: str | None = Query(default=None),
    newName: str | None = Query(default=None),
    size: int | None = Query(default=None),
    uploadId: str | None = Query(default=None),
    offset: int = Query(default=0),
    length: int | None = Query(default=None),
    instanceId: str | None = Query(default=None),
):
    if not auth(request):
        supplied = request.headers.get("x-swrlz-admin-token", "").strip()
        return JSONResponse(status_code=401, content={
            "ok": False,
            "error": "invalid or missing SWRLZ_ADMIN_TOKEN",
            "authConfigured": bool(TOKEN),
            "tokenReceived": bool(supplied),
            "receivedLength": len(supplied),
            "instanceId": INSTANCE,
        })
    try:
        if action == "auth-check":
            return {"ok": True, "authenticated": True, "version": VERSION, "instanceId": INSTANCE, "message": "Admin token accepted."}
        if action == "runtime":
            return {"ok": True, "version": VERSION, "instanceId": INSTANCE, "root": str(ROOT), "live": str(LIVE), "uploadAuthConfigured": bool(TOKEN), "downloadChunkBytes": DOWNLOAD_CHUNK, **lalm_presence()}
        if action == "list":
            base = safe_path(path)
            if not base.exists(): raise FileNotFoundError(base)
            if not base.is_dir(): return {"ok": True, **file_info(base), "entries": []}
            entries = sorted((file_info(p) for p in base.iterdir()), key=lambda x: (x["type"] != "directory", x["name"].lower()))
            return {"ok": True, "path": str(base), "entries": entries, "instanceId": INSTANCE}
        if action == "preview":
            target = safe_path(path)
            if target.is_dir(): return {"ok": True, **file_info(target), "previewKind": "directory"}
            return {"ok": True, **preview(target), "instanceId": INSTANCE}
        if action == "download":
            target = safe_path(path)
            if not target.is_file(): raise FileNotFoundError(target)
            if target.stat().st_size > DIRECT_DOWNLOAD_MAX:
                return JSONResponse(status_code=413, content={"ok": False, "error": "file exceeds direct-download limit; use chunked download", "size": target.stat().st_size, "chunkBytes": DOWNLOAD_CHUNK})
            return FileResponse(target, media_type=mime_for(target), filename=target.name)
        if action == "download-info":
            target = safe_path(path)
            if not target.is_file(): raise FileNotFoundError(target)
            return {"ok": True, "name": target.name, "path": str(target), "size": target.stat().st_size, "mime": mime_for(target), "chunkBytes": DOWNLOAD_CHUNK, "instanceId": INSTANCE}
        if action == "download-chunk":
            if instanceId != INSTANCE:
                return JSONResponse(status_code=409, content={"ok": False, "error": "runtime instance changed; restart download", "instanceId": INSTANCE})
            target = safe_path(path)
            if not target.is_file(): raise FileNotFoundError(target)
            total = target.stat().st_size
            if offset < 0 or offset > total: raise ValueError("invalid download offset")
            wanted = DOWNLOAD_CHUNK if length is None else length
            if wanted <= 0 or wanted > DOWNLOAD_CHUNK: raise ValueError(f"download length must be 1..{DOWNLOAD_CHUNK}")
            wanted = min(wanted, total - offset)
            with target.open("rb") as handle:
                handle.seek(offset)
                body = handle.read(wanted)
            end = offset + len(body)
            headers = {
                "x-swrlz-instance-id": INSTANCE,
                "x-swrlz-offset": str(offset),
                "x-swrlz-next-offset": str(end),
                "x-swrlz-total-size": str(total),
                "content-range": f"bytes {offset}-{max(offset, end - 1)}/{total}",
                "accept-ranges": "bytes",
            }
            return Response(content=body, status_code=206, media_type="application/octet-stream", headers=headers)
        if action == "hash":
            target = safe_path(path)
            if not target.is_file(): raise FileNotFoundError(target)
            return {"ok": True, "path": str(target), "size": target.stat().st_size, "sha256": sha(target)}
        if action == "save-text":
            target = safe_path(path); body = await request.body()
            if len(body) > MAX_TEXT_EDIT: return JSONResponse(status_code=413, content={"ok": False, "error": "text file exceeds editor limit"})
            body.decode("utf-8"); target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(body)
            return {"ok": True, **file_info(target), "sha256": sha(target)}
        if action == "mkdir":
            base = safe_path(path)
            if not name or Path(name).name != name: raise ValueError("simple folder name required")
            target = safe_path(str(base / name)); target.mkdir(parents=False, exist_ok=False)
            return {"ok": True, **file_info(target)}
        if action == "rename":
            target = safe_path(path)
            if not newName or Path(newName).name != newName: raise ValueError("simple newName required")
            renamed = safe_path(str(target.parent / newName)); target.rename(renamed)
            return {"ok": True, **file_info(renamed)}
        if action == "delete":
            target = safe_path(path)
            if target in {ROOT, LIVE, UP}: raise PermissionError("protected runtime directory")
            shutil.rmtree(target) if target.is_dir() else target.unlink()
            return {"ok": True, "deleted": str(target)}
        if action == "upload-init":
            if not name or Path(name).name != name or size is None or size < 0: raise ValueError("simple name and non-negative size required")
            base = safe_path(path); base.mkdir(parents=True, exist_ok=True); target = safe_path(str(base / name)); uid = uuid.uuid4().hex; part = UP / f"{uid}.part"; part.touch()
            metadata = {"uploadId": uid, "instanceId": INSTANCE, "target": str(target), "part": str(part), "expected": size, "received": 0}; upload_meta_path(uid).write_text(json.dumps(metadata), "utf-8")
            return {"ok": True, "uploadId": uid, "instanceId": INSTANCE, "chunkBytes": MAX_CHUNK}
        if action == "upload-chunk":
            if instanceId != INSTANCE: return JSONResponse(status_code=409, content={"ok": False, "error": "runtime instance changed; restart upload"})
            if not uploadId: raise ValueError("uploadId required")
            metadata = json.loads(upload_meta_path(uploadId).read_text("utf-8")); body = await request.body()
            if len(body) > MAX_CHUNK: return JSONResponse(status_code=413, content={"ok": False, "error": "chunk too large"})
            if offset != metadata["received"]: return JSONResponse(status_code=409, content={"ok": False, "error": "offset mismatch", "received": metadata["received"]})
            with Path(metadata["part"]).open("ab") as out: out.write(body)
            metadata["received"] += len(body); upload_meta_path(upload_id=uploadId).write_text(json.dumps(metadata), "utf-8")
            return {"ok": True, "received": metadata["received"], "expected": metadata["expected"], "instanceId": INSTANCE}
        if action == "upload-finish":
            if instanceId != INSTANCE: return JSONResponse(status_code=409, content={"ok": False, "error": "runtime instance changed; restart upload"})
            if not uploadId: raise ValueError("uploadId required")
            metadata = json.loads(upload_meta_path(uploadId).read_text("utf-8")); part = Path(metadata["part"]); target = safe_path(metadata["target"])
            if metadata["received"] != metadata["expected"] or part.stat().st_size != metadata["expected"]: return JSONResponse(status_code=409, content={"ok": False, "error": "upload incomplete"})
            os.replace(part, target); upload_meta_path(uploadId).unlink(missing_ok=True)
            return {"ok": True, **file_info(target), "sha256": sha(target), "instanceId": INSTANCE}
        if action == "lalm-load":
            state = ensure_r39(); return JSONResponse(status_code=200 if state.get("ok") else 503, content={**state, "instanceId": INSTANCE})
        if action == "gate5-run":
            result = run_gate5(); return JSONResponse(status_code=200 if result.get("ok") else 500, content=result)
        if action == "log-read":
            return {"ok": True, "content": LOG.read_text("utf-8", errors="replace") if LOG.exists() else "", "path": str(LOG), "instanceId": INSTANCE}
        return JSONResponse(status_code=400, content={"ok": False, "error": "unknown action"})
    except subprocess.TimeoutExpired as exc:
        append_log(f"\n=== GATE 5 TIMEOUT instance={INSTANCE} ===\n{exc}\n")
        return JSONResponse(status_code=504, content={"ok": False, "error": "Gate 5 exceeded 240 seconds", "instanceId": INSTANCE})
    except Exception as exc:
        return JSONResponse(status_code=500, content={"ok": False, "error": f"{type(exc).__name__}: {exc}", "instanceId": INSTANCE})
