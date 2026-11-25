"""Child process: virtual-origin browser; no network access or deployment credentials."""
from __future__ import annotations
import hashlib,json,sys,time
from urllib.parse import unquote,urlsplit
from browser_worker_protocol_v1 import VERSION,validate_request,file_hashes,encode
ORIGIN="https://candidate.invalid"
CSP=("sandbox allow-scripts; default-src 'none'; script-src 'unsafe-inline' "+ORIGIN+
     "; style-src 'unsafe-inline' "+ORIGIN+"; img-src data: blob: "+ORIGIN+
     "; font-src data: "+ORIGIN+"; connect-src 'none'; form-action 'none'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
MIME={".html":"text/html; charset=utf-8",".htm":"text/html; charset=utf-8",
      ".js":"text/javascript; charset=utf-8",".mjs":"text/javascript; charset=utf-8",
      ".css":"text/css; charset=utf-8",".json":"application/json",".svg":"image/svg+xml"}
def render(obj):
    from playwright.sync_api import sync_playwright
    files=obj["files"]; base=ORIGIN+"/project/"
    issues=[]; loaded=set(); checked=[]
    def issue(code,detail):
        if len(issues)<20:issues.append({"code":code,"detail":str(detail)[:300]})
    start=time.monotonic()
    with sync_playwright() as pw:
        # Fail closed: never retry with --no-sandbox.
        browser=pw.chromium.launch(headless=True,chromium_sandbox=True,
            proxy={"server":"http://127.0.0.1:9","bypass":""},
            args=["--proxy-bypass-list=<-loopback>","--use-angle=swiftshader","--enable-unsafe-swiftshader",
                  "--disable-background-networking","--disable-sync","--disable-component-update"],
            timeout=15000)
        context=browser.new_context(viewport={"width":960,"height":720},accept_downloads=False)
        context.set_default_timeout(3000)
        def route(r):
            request=r.request; url=request.url; parsed=urlsplit(url)
            if not url.startswith(base) or request.method!="GET" or parsed.query:
                issue("BROWSER_NETWORK_BLOCKED",parsed.scheme+"://"+parsed.netloc)
                r.abort();return
            name=unquote(parsed.path[len("/project/"):])
            if name not in files:
                issue("BROWSER_ASSET_MISSING",name);r.fulfill(status=404,body="Not found");return
            suffix="."+name.rsplit(".",1)[-1].lower()
            loaded.add(name)
            r.fulfill(status=200,body=files[name].encode(),headers={
                "Content-Type":MIME[suffix],"Content-Security-Policy":CSP,
                "X-Content-Type-Options":"nosniff","Access-Control-Allow-Origin":"*",
                "Cross-Origin-Resource-Policy":"cross-origin","Cache-Control":"no-store"})
        context.route("**/*",route)
        context.route_web_socket("**/*",lambda ws:ws.close())
        page=context.new_page()
        page.on("popup",lambda p:p.close())
        page.on("download",lambda d:d.cancel())
        page.on("dialog",lambda d:d.dismiss())
        page.on("pageerror",lambda e:issue("BROWSER_PAGE_ERROR",e))
        page.on("console",lambda m:issue("BROWSER_CONSOLE_ERROR",m.text) if m.type=="error" else None)
        page.on("requestfailed",lambda r:issue("BROWSER_REQUEST_FAILED",r.failure))
        try:
            response=page.goto(base+"index.html",wait_until="load",timeout=15000)
            if not response or response.status!=200:issue("BROWSER_ENTRY_UNAVAILABLE","No successful entry response")
            page.wait_for_timeout(900)
            if page.url!=base+"index.html":issue("BROWSER_NAVIGATION_CHANGED","Unexpected navigation")
            if not page.locator("body").is_visible():issue("BROWSER_BODY_NOT_VISIBLE","Body unavailable")
            canvas_count=page.locator("canvas").count()
            if obj["canvas"]:
                canvas=page.locator("canvas").first
                canvas.wait_for(state="visible",timeout=5000)
                size=canvas.evaluate("(c)=>({width:c.width,height:c.height})")
                if not size["width"] or not size["height"]:issue("BROWSER_CANVAS_EMPTY","Canvas has no pixels")
            for c in obj["checks"]:
                loc=page.locator(c["selector"]); op=c["op"]
                if op=="click":loc.click(timeout=3000)
                elif op=="check":loc.check(timeout=3000)
                elif op=="uncheck":loc.uncheck(timeout=3000)
                elif op=="visible" and not loc.is_visible():raise ValueError("Not visible: "+c["selector"])
                elif op=="text" and c["text"] not in loc.inner_text(timeout=3000):raise ValueError("Text assertion failed: "+c["selector"])
                elif op=="checked" and not loc.is_checked():raise ValueError("Checked assertion failed: "+c["selector"])
                elif op=="unchecked" and loc.is_checked():raise ValueError("Unchecked assertion failed: "+c["selector"])
                checked.append(c)
            page.wait_for_timeout(250)
            shot=page.screenshot(type="jpeg",quality=60,timeout=4000)
            screenshot=hashlib.sha256(shot).hexdigest()
        except Exception as exc:
            issue("BROWSER_EXECUTION_FAILED",str(exc));canvas_count=0;screenshot=None
        finally:
            context.close();browser.close()
    return {"schema":VERSION,"project":obj["project"],"nonce":obj["nonce"],"timestamp":int(time.time()),
            "hashes":file_hashes(files),"browserVerified":not issues,"sandbox":True,"issues":issues,
            "canvasCount":canvas_count,"loadedFiles":sorted(loaded),"checks":checked,
            "screenshotSha256":screenshot,"durationMs":int((time.monotonic()-start)*1000),
            "scope":"isolated render of exact submitted project bytes; listed declarative interactions only"}
if __name__=="__main__":
    obj=validate_request(json.load(sys.stdin))
    try:result=render(obj)
    except Exception as exc:
        # Chromium unavailable is infrastructure failure, not a failed project.
        result={"schema":VERSION,"project":obj["project"],"nonce":obj["nonce"],"timestamp":int(time.time()),
                "hashes":file_hashes(obj["files"]),"browserVerified":False,"sandbox":False,
                "infrastructureError":"CHROMIUM_SANDBOX_OR_WORKER_UNAVAILABLE",
                "issues":[{"code":"BROWSER_INFRASTRUCTURE","detail":str(exc)[:350]}]}
    sys.stdout.buffer.write(encode(result))
