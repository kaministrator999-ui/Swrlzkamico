#!/usr/bin/env python3
"""Credential-free Chromium smoke check, preserving the production sandbox."""
from __future__ import annotations
import argparse, hashlib, json, mimetypes, re, sys, threading
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote,urlsplit
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from api.html_project_safe_route_v1 import HEADERS,ORIGIN,resolve_asset
from api.lightweight_webpage_inspector_v1 import inspect_files
from playwright.sync_api import sync_playwright

@contextmanager
def preview(root,slug):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            prefix="/api/html-projects/"+slug+"/"
            path=urlsplit(self.path).path
            if not path.startswith(prefix):
                self.send_error(404);return
            try:
                target=resolve_asset(root.parent,slug,unquote(path[len(prefix):]))
                raw=target.read_bytes()
                if len(raw)>1_000_000:raise ValueError("asset too large")
            except Exception:
                self.send_error(404);return
            mime=mimetypes.guess_type(target.name)[0] or "application/octet-stream"
            if target.suffix in (".js",".mjs"):mime="text/javascript; charset=utf-8"
            if target.suffix in (".html",".htm"):mime="text/html; charset=utf-8"
            self.send_response(200)
            self.send_header("Content-Type",mime)
            self.send_header("Content-Length",str(len(raw)))
            for k,v in HEADERS.items():
                self.send_header(k,v.replace(ORIGIN,"http://127.0.0.1:"+str(self.server.server_port)))
            self.end_headers()
            self.wfile.write(raw)
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(("127.0.0.1",0),Handler)
    t=threading.Thread(target=server.serve_forever,daemon=True);t.start()
    try:
        yield "http://127.0.0.1:"+str(server.server_port)+"/api/html-projects/"+slug+"/index.html"
    finally:
        server.shutdown();server.server_close();t.join(timeout=5)

def smoke(root,url,viewer_fixture=False):
    files={p.relative_to(root).as_posix():p.read_bytes() for p in root.rglob("*") if p.is_file()}
    expected={name:hashlib.sha256(raw).hexdigest() for name,raw in files.items()}
    static=inspect_files(files)
    if not static["staticPass"]:raise RuntimeError("BROWSER_SOURCE_STATIC_INVALID: "+repr(static["issues"]))
    base=url.rsplit("/",1)[0]+"/"
    errors=[];blocked=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,args=["--use-angle=swiftshader","--enable-unsafe-swiftshader"])
        # The opaque-origin CSP already forbids service workers. Playwright
        # service_workers="block" injects a navigator.serviceWorker access
        # that itself throws inside this sandbox. Preserve the real policy.
        context=browser.new_context(viewport={"width":960,"height":720})
        def route(r):
            target=r.request.url
            if target.startswith(base) and r.request.method in ("GET","HEAD"):
                r.continue_()
            else:
                blocked.append(urlsplit(target).scheme+":/"+urlsplit(target).netloc)
                r.abort()
        context.route("**/*",route)
        page=context.new_page()
        page.on("pageerror",lambda err:errors.append("pageerror: "+str(err)[:200]))
        page.on("requestfailed",lambda req:errors.append("requestfailed: "+str(req.failure)[:120]))
        page.on("console",lambda msg:errors.append("console: "+msg.text[:200]) if msg.type=="error" else None)
        try:
            response=page.goto(url,wait_until="load",timeout=45000)
            if not response or response.status!=200:raise RuntimeError("BROWSER_ENTRY_UNAVAILABLE")
            csp=response.headers.get("content-security-policy","")
            if "sandbox allow-scripts" not in csp or "allow-same-origin" in csp or "connect-src 'none'" not in csp:
                raise RuntimeError("BROWSER_SANDBOX_POLICY_MISMATCH")
            if hashlib.sha256(response.body()).hexdigest()!=expected["index.html"]:
                raise RuntimeError("BROWSER_ENTRY_HASH_MISMATCH")
            page.wait_for_timeout(1600)
            if not page.locator("body").is_visible():raise RuntimeError("BROWSER_BODY_NOT_VISIBLE")
            if static["renderingRequiredForFullVerification"]:
                canvas=page.locator("canvas").first
                canvas.wait_for(state="visible",timeout=12000)
                size=canvas.evaluate("(c)=>({width:c.width,height:c.height})")
                if not size["width"] or not size["height"]:raise RuntimeError("BROWSER_CANVAS_EMPTY")
            interactions=[]
            if viewer_fixture:
                page.locator("#loading").wait_for(state="hidden",timeout=12000)
                canvas=page.locator("canvas").first
                before=page.screenshot(clip={"x":200,"y":160,"width":560,"height":400})
                page.locator("#light-toggle").uncheck()
                page.wait_for_timeout(700)
                after=page.screenshot(clip={"x":200,"y":160,"width":560,"height":400})
                if before==after:raise RuntimeError("VIEWER_LIGHT_CONTROL_NO_RENDER_CHANGE")
                page.locator("#wireframe-toggle").check()
                page.locator("#reset-btn").click()
                if page.locator("#wireframe-toggle").is_checked() or not page.locator("#light-toggle").is_checked():
                    raise RuntimeError("VIEWER_RESET_CONTROL_FAILED")
                interactions=["lighting changed rendered pixels","wireframe toggle","reset controls"]
            if blocked or errors:raise RuntimeError("BROWSER_EXECUTION_FAILED: "+repr({"errors":errors[:12],"blocked":blocked[:12]}))
            receipt={"browserVerified":True,"entrySha256":expected["index.html"],
                     "canvasCount":page.locator("canvas").count(),"interactions":interactions,
                     "scope":"browser load/render smoke; task-specific interactions only when listed"}
            print("BROWSER_PROJECT_SMOKE_PASS",json.dumps(receipt),flush=True)
            return receipt
        finally:
            context.close();browser.close()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--project",required=True)
    p.add_argument("--root",required=True)
    p.add_argument("--live",action="store_true")
    p.add_argument("--viewer-fixture",action="store_true")
    p.add_argument("--receipt")
    args=p.parse_args()
    if not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,46}[a-z0-9])?",args.project):raise ValueError("INVALID_PROJECT")
    root=Path(args.root).resolve()
    if root.name!=args.project or not root.is_dir():raise ValueError("INVALID_PROJECT_ROOT")
    if args.live:
        result=smoke(root,ORIGIN+"/api/html-projects/"+args.project+"/index.html",args.viewer_fixture)
    else:
        with preview(root,args.project) as url:result=smoke(root,url,args.viewer_fixture)
    if args.receipt:Path(args.receipt).write_text(json.dumps(result,indent=2))
if __name__=="__main__":main()
