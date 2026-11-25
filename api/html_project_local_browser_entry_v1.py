"""Trusted worker bootstrap. Verify isolation before reading project code."""
import json,os,sys,socket
sys.path[:0]=["/worker","/deps"]
from browser_worker_protocol_v1 import validate_request,encode,file_hashes,VERSION
import time
def main():
    packet=json.load(sys.stdin)
    parent=packet["parentNamespaces"]
    current={n:os.readlink("/proc/self/ns/"+n) for n in ("user","mnt","pid","net","ipc","uts")}
    if set(parent)!=set(current) or any(parent[n]==current[n] for n in current):
        raise RuntimeError("OS_NAMESPACE_ISOLATION_REQUIRED")
    if any(os.path.exists(p) for p in ("/app","/data","/home/user","/root","/run/secrets","/etc/shadow")):
        raise RuntimeError("HOST_FILESYSTEM_VISIBLE")
    if set(os.environ)-{"PATH","HOME","TMPDIR","LANG","SWRLZ_CHROMIUM_EXECUTABLE","LC_CTYPE"}:
        raise RuntimeError("INHERITED_ENVIRONMENT_NOT_EMPTY")
    # Network namespace must have only loopback and no default route.
    if set(os.listdir("/sys/class/net"))-{"lo"} if os.path.isdir("/sys/class/net") else False:
        raise RuntimeError("HOST_NETWORK_VISIBLE")
    routes=open("/proc/net/route",encoding="utf-8").read().splitlines()[1:]
    if any(line.split()[1]=="00000000" for line in routes if len(line.split())>1):
        raise RuntimeError("NETWORK_DEFAULT_ROUTE_PRESENT")
    obj=validate_request(packet["request"])
    from html_project_local_browser_render_v1 import render
    result=render(obj)
    result["isolationVerified"]=True
    sys.stdout.buffer.write(encode(result))
if __name__=="__main__":main()
