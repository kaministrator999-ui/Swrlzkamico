"""Public read-only §wyrlz Chat v294 welcome release acceptance.
Checks served Space source, not authenticated user sessions or physical display.
"""
import json
import re
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

SPACE = "https://kamiloki-swyrlz.hf.space"
HUB_META = "https://huggingface.co/api/spaces/kamiloki/Swyrlz"
SOURCE = "0c34ecf36bc0e8a1c64b03cd036060610cc70c32"
REVISION = "ffc9d264e3ae7f9df8edca5cc878fd2c8587f9fc"
VERSION = "1.1.19"

def get(url, retries=4):
    for n in range(retries):
        try:
            request = Request(url, headers={"User-Agent":"swrlz-v294-welcome-acceptance/1.0",
                                            "Cache-Control":"no-cache"})
            with urlopen(request, timeout=30) as response:
                return response.status, response.read(500_000).decode("utf-8","replace")
        except HTTPError as error:
            if error.code not in (502,503,504) or n+1==retries:
                raise
        except (OSError,URLError):
            if n+1==retries:
                raise
        time.sleep(3*(n+1))
    raise AssertionError("Read retry budget exhausted")

def receipt(label, **details):
    print(json.dumps({"checkpoint":label,"status":"PASS",**details},sort_keys=True),flush=True)

def main():
    status, payload = get(HUB_META)
    assert status==200, ("space-meta-http",status)
    sha=str(json.loads(payload).get("sha") or "")
    assert sha==REVISION, ("wrong-space-revision",sha,REVISION)
    receipt("space-revision",sha=sha,sourceCommit=SOURCE)

    status, html = get(SPACE+"/",retries=6)
    assert status==200,("chat-http",status)
    assert re.search(r'<meta\s+name="swrlz-chat-version"\s+content="1\.1\.19"',html), "Wrong served Chat version"
    assert 'const SWRLZ_CHAT_VERSION = "1.1.19"' in html, "Version constant not updated"
    assert ".first-run-welcome" in html and "width:min(100%,560px);" in html, "Desktop width rule not served"
    assert "@media (min-width:761px)" in html, "Desktop breakpoint not served"
    assert "body.a11y-reduced-transparency .first-run-welcome" in html, "Accessibility CSS not served"
    assert "renderFirstRunWelcome" in html, "First-run greeting renderer not served"
    receipt("hosted-chat-html-and-css",httpStatus=status,chatVersion=VERSION,
            desktopMaxCardPx=560,desktopMinViewportPx=761)

    status, models = get(SPACE+"/api/hf/models")
    count=len(json.loads(models).get("models") or [])
    assert status==200 and count>=1, ("model-catalog",status,count)
    receipt("model-catalog",httpStatus=status,count=count)
    print(json.dumps({"checkpoint":"scope","status":"PARTIAL",
                      "note":"Authenticated session, first-run user rendering, and physical PC acceptance not tested"}),
          flush=True)

if __name__=="__main__":
    main()
