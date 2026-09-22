#!/usr/bin/env python3
"""Validate/package the accepted runtime generation with local R39 sources."""
from __future__ import annotations
import argparse, base64, hashlib, json, re, shutil, urllib.parse, urllib.request
from pathlib import Path

# Historical R39 ancestry is acquired only during pre-deploy preparation. Every
# source is pinned. The v61 historical SHA embedded by v65 is no longer resolvable,
# so its byte-identical surviving source is pinned to the accepted rehearsal commit.
_DEEP_R39 = [
("v73.py","023ac7efdabbe8c317490bc23f410e3a370b5eaf","r39_engine_v73.py",None),
("v72.py","3c41765183650793ad6c4c552c2d2a2cc5db6056","r39_engine_v72.py",None),
("v71.py","b1bfa7eaec5eec7b21b020a7f8d7ec423416d5ab","r39_engine_v71.py",None),
("v70.py","d35c55aed8a1d83550e6639af70759fe0b310554","r39_engine_v70.py",None),
("v69.py","a47edea4867c8082baddf27b04182430dc92fb31","r39_engine_v69.py",None),
("v68.py","9420c0e02b63821c1271ad38c6f826b00c3b013c","r39_engine_v68.py",None),
("v67.py","d080434b426ece68b92e14af8f5fb9e1a34daffd","r39_engine_v67.py",None),
("v66.py","a3bbf9b12d370c16c69f255dde3bf2f3c56ab3a8","r39_engine_v66.py",None),
("v65.py","0103eaa9162f8e6cf7c396f9e5238c2d05abc773","r39_engine_v65.py",None),
("v61.py","b7076a6fbd2a8028a13326f32511316f18de07ba","r39_engine_v61.py","ae27745d9a4d988b28e2351f793d9c568a24ef26"),
("v60e.py","bc870515340d28588f8bf9c93455d69ececc0311","r39_engine_v60e.py",None),
("v59.py","4cc51edaab602e0f72f20ac85bcaa23996621cf5","r39_engine_v59.py",None),
("v58e.py","0abf95d24084eed41a7a5240c1ee9438c6dc4d28","r39_engine_v58e.py",None),
("v57.py","e5f17eedf60c22bf92aa296125aed91535f16a18","r39_engine_v57.py",None),
("v56.py","55d494b28c97d973fb217944498416a5ef7f8de8","r39_engine_v56.py",None),
("v55.py","ab0b368d871f168c4cf8ae906572d4d4fe2beac8","r39_engine_v55.py",None),
("v54.py","3d9559c642f3ff72743607a98a55a1ae3c5821c8","r39_engine_v54.py",None),
("v53.py","651a3c620a114bb6d75857ae8f9fb9ab2e224f31","r39_engine_v53.py",None),
("v52.py","3670f9c777b7425e7033bcedcbf7539b19b8965c","r39_engine_v52.py",None),
("v51.py","a30e2f53df0cbe421ee67e9de40d24a999f9bb17","r39_engine_v51.py",None),
("v50.py","21b3ee32fa89f6f54917818802b92c8858f13913","r39_engine_v50.py",None),
("v49.py","930f6305cb65e55070214a046c400da6234fc387","r39_engine_v49.py",None),
("v48.py","aa17d773acc5a679f74fdabdd08c613cac7d30be","r39_engine_v48.py",None),
("v47.py","137fc1761b5284e7d4e03bf68073ac316734858d","r39_engine_v47.py",None),
("v46.py","4bc9eda49bd5953345467ab6174e54b4faed79fa","r39_engine_v46.py",None),
("v45.py","991a3bae34ad0cfb8eac6d5b77e007a1239558cd","r39_engine_v45.py",None),
("v44.py","2031e2dfcd998a24671796b948adadadd3f803ac","r39_engine_v44.py",None),
("v43.py","ecfc9d1001822bc5eeefb7501574e1cb4d49a3c8","r39_engine_v43.py",None),
("v42.py","bc2842b6f57564305ba917665a02333130ecf848","r39_engine_v42.py",None),
("v41.py","1b75ca5c46c1f67f19fb4a4f145722aa13718840","r39_engine_v41.py",None),
("v37.py","337aa9838a867432073b4c814298b6bfb266072f","r39_engine_v37.py",None),
("v36.py","494997652994b36b2351edfec51cee1c8b8c3651","r39_engine_v36.py",None),
("v35.py","2d6c942da0166bb752a7f3e3d8ae62f92602dec1","r39_engine_v35.py",None),
("v34.py","0c0b0e2033ca848768a38207fd104eefacc0d0be","r39_engine_v34.py",None),
("v33.py","97962919586e3b96a33099b745df225282984f60","r39_engine_v33.py",None),
("v32.py","f8fa75f3afcf0b829e5bfae75688c58cd1b6e2ca","r39_engine_v32.py",None),
("v31.py","12f6f99660382607e8ccd99c63f07b4a7890031e","r39_engine_v31.py",None),
("v30.py","c2a014016ec6755b2652a081407109f0ca38d128","r39_engine_v30.py",None),
("v29.py","49a59dce9cd908d21178626d53f228ec14e8c70d","r39_engine_v29.py",None),
("v28.py","f7ffe36332349a5745b122de71d4880340aa66ee","r39_engine_v28.py",None),
("v27.py","a5250b6ae2daeaada0dc4434272799ef00bb026b","r39_engine_v27.py",None),
("v26.py","6d2bd7424cf047265fb85bcecf85c13c66ed1116","r39_engine_v26.py",None),
("v25.py","64d66949d0c1af42a31a93d2f5a59b02e8bca038","r39_engine_v25.py",None),
("v24.py","602ca6168173e93f8e50ccb7c6e486a5a58e888a","r39_engine_v24.py",None),
("v23.py","c35b08a162112ed29552d408123fdb5ebddc7434","r39_engine_v23.py",None),
("v22.py","5c59eac61256bc76b9eca6e33843ff7d4911877e","r39_engine.py",None),
("r39_engine_v17_base.py","5c59eac61256bc76b9eca6e33843ff7d4911877e","r39_engine_v17_base.py","runtime"),
("r39_batch_prefill_v22.py","569332d9573ffb1c05cce229a56d3adee6c0c704","r39_batch_prefill.py",None),
]

def _raw(commit: str, filename: str) -> str:
    return f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{commit}/runtime_hot/{filename}"

def _fetch_pinned(commit: str, filename: str) -> bytes:
    req=urllib.request.Request(_raw(commit,filename),headers={"User-Agent":"swrlz-predeploy-r39-ancestry"})
    with urllib.request.urlopen(req,timeout=20) as response:
        data=response.read(4_000_001)
    if len(data)>4_000_000: raise SystemExit(f"historical R39 source too large: {filename}")
    data.decode("utf-8")
    return data


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

    # Materialize the recursive pre-v74 ancestry during preparation, never at
    # audience/runtime boot. A local URL shim preserves the historical exec lineage
    # byte-for-byte while making every recognized source acquisition filesystem-only.
    ancestry_dir=out/"lalm"/"ancestry"; ancestry_dir.mkdir(parents=True,exist_ok=True)
    ancestry=[]
    url_map={}
    for local_name,commit,filename,requested_alias in _DEEP_R39:
        data=_fetch_pinned(commit,filename)
        target=ancestry_dir/local_name; target.write_bytes(data)
        fetch_url=_raw(commit,filename)
        url_map[fetch_url]=f"ancestry/{local_name}"
        if requested_alias and requested_alias!="runtime":
            url_map[_raw(requested_alias,filename)]=f"ancestry/{local_name}"
        ancestry.append({"name":local_name,"sourceCommit":commit,"sourcePath":"runtime_hot/"+filename,"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()})
    # v22 historically names v17 through the runtime branch; bind that mutable-looking
    # URL to the pinned v22-era archive packaged above.
    url_map["https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/runtime/runtime_hot/r39_engine_v17_base.py"]="ancestry/r39_engine_v17_base.py"

    entry=out/"lalm"/"r39_engine.py"
    source=entry.read_text(encoding="utf-8")
    source=source.replace("import json,time,urllib.request","import json,time,urllib.request\nfrom pathlib import Path",1)
    source=source.replace("def _entry(stage,**fields):",'_SWRLZ_CHAIN=Path(__file__).with_name("chain")\n_SWRLZ_ANCESTRY=Path(__file__).with_name("ancestry")\n\ndef _entry(stage,**fields):',1)
    local_map={"_source":"v74.py","_overlay":"v75.py","_v76_overlay":"v76.py","_v77_overlay":"v77.py","_v78_overlay":"v78.py","_v79_overlay":"v79.py","_v80_overlay":"v80.py","_v81_overlay":"v81.py","_v82_batch_source":"v82_batch.py","_v85_overlay":"v85.py","_v86_overlay":"v86.py","_v87_overlay":"v87.py","_v88_overlay":"v88.py","_v89_overlay":"v89.py","_v90_overlay":"v90.py"}
    for var,filename in local_map.items():
        pattern=re.compile(r'(?m)^\s*with urllib\.request\.urlopen\([^\n]+\) as _response:'+re.escape(var)+r'=_response\.read\([^\n]+\)')
        source,count=pattern.subn(f'    {var}=(_SWRLZ_CHAIN/"{filename}").read_bytes()',source,count=1)
        if count!=1: raise SystemExit(f"R39 localization boundary mismatch for {var}: {count}")
    # Install a fail-closed local source transport before v74 executes. Historical
    # wrappers may keep their original urllib calls, but recognized R39 source URLs
    # are served only from this immutable prepared generation; unknown URLs fail.
    shim='''\nclass _SwrlzLocalResponse:\n    def __init__(self,data): self._data=data\n    def __enter__(self): return self\n    def __exit__(self,*args): return False\n    def read(self,limit=-1): return self._data if limit is None or limit<0 else self._data[:limit]\n\n_SWRLZ_SOURCE_URLS='''+repr(url_map)+'''\n_SWRLZ_ORIGINAL_URLOPEN=urllib.request.urlopen\ndef _swrlz_local_urlopen(request,*args,**kwargs):\n    url=getattr(request,"full_url",request)\n    url_text=str(url)\n    rel=_SWRLZ_SOURCE_URLS.get(url_text)\n    if rel is not None:\n        return _SwrlzLocalResponse((Path(__file__).parent/rel).read_bytes())\n    parsed=urllib.parse.urlparse(url_text)\n    transport_prefix="/kaministrator999-ui/Swrlzkamico/"\n    transport_marker="/.transport/lalm%C2%A7wyrlz/lalm%C2%A7wyrlz.zip.part"\n    if parsed.scheme=="https" and parsed.netloc=="raw.githubusercontent.com" and parsed.path.startswith(transport_prefix) and transport_marker in parsed.path:\n        return _SWRLZ_ORIGINAL_URLOPEN(request,*args,**kwargs)\n    raise RuntimeError("R39_PREPARED_UNKNOWN_NETWORK_SOURCE:"+url_text)\nurllib.request.urlopen=_swrlz_local_urlopen\n'''
    anchor='_SWRLZ_ANCESTRY=Path(__file__).with_name("ancestry")\n'
    source=source.replace(anchor,anchor+shim,1)
    if "urllib.request.urlopen(" in source:
        raise SystemExit("R39 prepared entrypoint still contains network source fetch")
    compile(source,str(entry),"exec")
    entry.write_text(source,encoding="utf-8")

    prepared={"contract":"swrlz-prepared-runtime-generation-v3","sourceRuntimeCommit":manifest.get("sourceRuntimeCommit"),"acceptedAuthority":"main:accepted_runtime/accepted.json","activation":"bundled-at-production-build","requestPathSyncRequired":False,"r39HistoricalNetworkFetchRequired":False,"r39SourceDelivery":"local-precomposed-full-lineage-v2","files":files,"r39OverlayChain":chain_files,"r39HistoricalAncestry":ancestry}
    (out/"generation.json").write_text(json.dumps(prepared,indent=2,sort_keys=True)+"\n")
    print(json.dumps(prepared,separators=(",",":")))
    return 0
if __name__=="__main__": raise SystemExit(main())
