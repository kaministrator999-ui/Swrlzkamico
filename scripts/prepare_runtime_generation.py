#!/usr/bin/env python3
"""Validate/package the accepted runtime generation with local R39 sources."""
from __future__ import annotations
import argparse, hashlib, json, re, shutil
from pathlib import Path

def blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--accepted-root",default="accepted_runtime")
    ap.add_argument("--output-root",required=True)
    a=ap.parse_args()
    root,out=Path(a.accepted_root).resolve(),Path(a.output_root).resolve()
    manifest=json.loads((root/"accepted.json").read_text())
    if manifest.get("contract")!="swrlz-accepted-runtime-v1" or manifest.get("status")!="accepted":
        raise SystemExit("accepted runtime authority is not deployable")
    specs=manifest.get("files") or []
    if not specs: raise SystemExit("accepted runtime contains no promoted files")
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True)
    files=[]
    for spec in specs:
        name=str(spec.get("acceptedTarget") or "")
        src=root/name
        data=src.read_bytes(); data.decode("utf-8")
        expected=str(spec.get("sourceBlobSha") or "")
        if manifest.get("integrity")=="github-blob-sha" and blob_sha(data)!=expected:
            raise SystemExit(f"accepted source blob mismatch: {name}")
        target=out/name; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(data)
        files.append({"owner":spec.get("owner"),"acceptedTarget":name,"runtimeSource":spec.get("runtimeSource"),"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()})

    chain=manifest.get("overlayChain") or []
    if manifest.get("precomposition")!="local-overlay-chain-v1" or not chain:
        raise SystemExit("accepted R39 overlay chain is not registered")
    chain_files=[]
    for spec in chain:
        name=str(spec.get("acceptedTarget") or "")
        data=(root/name).read_bytes(); data.decode("utf-8")
        if blob_sha(data)!=str(spec.get("sourceBlobSha") or ""):
            raise SystemExit(f"accepted overlay blob mismatch: {name}")
        target=out/name; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(data)
        chain_files.append({"name":spec.get("name"),"sourceCommit":spec.get("sourceCommit"),"acceptedTarget":name,"sha256":hashlib.sha256(data).hexdigest()})

    entry=out/"lalm"/"r39_engine.py"
    source=entry.read_text(encoding="utf-8")
    source=source.replace("import json,time,urllib.request","import json,time,urllib.request\nfrom pathlib import Path",1)
    source=source.replace("def _entry(stage,**fields):",'_SWRLZ_CHAIN=Path(__file__).with_name("chain")\n\ndef _entry(stage,**fields):',1)
    local_map={"_source":"v74.py","_overlay":"v75.py","_v76_overlay":"v76.py","_v77_overlay":"v77.py","_v78_overlay":"v78.py","_v79_overlay":"v79.py","_v80_overlay":"v80.py","_v81_overlay":"v81.py","_v82_batch_source":"v82_batch.py","_v84_overlay":"v84.py","_v85_overlay":"v85.py","_v86_overlay":"v86.py","_v87_overlay":"v87.py","_v88_overlay":"v88.py","_v89_overlay":"v89.py","_v90_overlay":"v90.py"}
    for var,filename in local_map.items():
        pattern=re.compile(r'(?m)^\s*with urllib\.request\.urlopen\([^\n]+\) as _response:'+re.escape(var)+r'=_response\.read\([^\n]+\)')
        source,count=pattern.subn(f'    {var}=(_SWRLZ_CHAIN/"{filename}").read_bytes()',source,count=1)
        if count!=1: raise SystemExit(f"R39 localization boundary mismatch for {var}: {count}")
    if "urllib.request.urlopen(" in source:
        raise SystemExit("R39 prepared entrypoint still contains network source fetch")
    compile(source,str(entry),"exec")
    entry.write_text(source,encoding="utf-8")

    prepared={"contract":"swrlz-prepared-runtime-generation-v3","sourceRuntimeCommit":manifest.get("sourceRuntimeCommit"),"acceptedAuthority":"main:accepted_runtime/accepted.json","activation":"bundled-at-production-build","requestPathSyncRequired":False,"r39HistoricalNetworkFetchRequired":False,"r39SourceDelivery":"local-precomposed-chain-v1","files":files,"r39OverlayChain":chain_files}
    (out/"generation.json").write_text(json.dumps(prepared,indent=2,sort_keys=True)+"\n")
    print(json.dumps(prepared,separators=(",",":")))
    return 0
if __name__=="__main__": raise SystemExit(main())
