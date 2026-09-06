from __future__ import annotations
import gzip, hashlib, json, os, urllib.request, zipfile
from pathlib import Path

ROOT=Path("/tmp/swrlz-admin")
LIVE=ROOT/"live"
LIVE.mkdir(parents=True,exist_ok=True)
PACKED=LIVE/"SWYRLZ_LALM_R39_PHYSICAL_BASE_REPAIRED.§wyrlzx.gz"
RAW=LIVE/"SWYRLZ_LALM_R39_PHYSICAL_BASE_REPAIRED.§wyrlzx"
PACKED_SIZE=226000615
PACKED_SHA="fd790c873c9f0b43d4862b55491d643a79f8a90da0c9b70ea61b1937b9843e68"
RAW_SIZE=233637480
RAW_SHA="65e4b5d730f66024c44da25aec27730db27aa0019df0df26c0997d17ce58bdee"

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def _repo_root():
    return Path(os.environ.get("SWRLZ_REPO_ROOT",Path.cwd())).resolve()

def _manifest_candidates(root):
    explicit=os.environ.get("SWRLZ_R39_TRANSPORT_MANIFEST","").strip()
    seen=set()
    if explicit:
        p=Path(explicit)
        resolved=(p if p.is_absolute() else root/p).resolve()
        seen.add(resolved)
        yield resolved
    preferred=(root/(PACKED.name+".transport.json")).resolve()
    if preferred not in seen and preferred.exists():
        seen.add(preferred)
        yield preferred
    for p in root.rglob("*.transport.json"):
        resolved=p.resolve()
        if resolved not in seen:
            seen.add(resolved)
            yield resolved

def _copy_verified_chunks(root,data,target):
    chunks=data.get("chunks") or []
    if not chunks:
        raise ValueError("transport manifest has no chunks")
    expected_whole_sha=str(data.get("source_sha256") or data.get("sha256") or "").lower()
    expected_whole_size=int(data.get("source_size_bytes") or data.get("size_bytes") or -1)
    total=0
    whole=hashlib.sha256()
    with target.open("wb") as out:
        for chunk in sorted(chunks,key=lambda c:int(c["index"])):
            rel=Path(str(chunk["path"]))
            chunk_path=(root/rel).resolve()
            if root!=chunk_path and root not in chunk_path.parents:
                raise ValueError("chunk path escapes repository root")
            expected_size=int(chunk["size_bytes"])
            expected_sha=str(chunk["sha256"]).lower()
            actual_size=0
            part_hash=hashlib.sha256()
            with chunk_path.open("rb") as src:
                for block in iter(lambda:src.read(1024*1024),b""):
                    out.write(block)
                    whole.update(block)
                    part_hash.update(block)
                    actual_size+=len(block)
            if actual_size!=expected_size or part_hash.hexdigest()!=expected_sha:
                raise ValueError(f"chunk verification failed: {rel}")
            total+=actual_size
    if total!=expected_whole_size or whole.hexdigest()!=expected_whole_sha:
        target.unlink(missing_ok=True)
        raise ValueError("reconstructed transport verification failed")
    return {"chunks":len(chunks),"size":total,"sha256":whole.hexdigest()}

def _extract_r39_gzip_from_zip(zip_path):
    tmp=PACKED.with_suffix(PACKED.suffix+".part")
    tmp.unlink(missing_ok=True)
    with zipfile.ZipFile(zip_path,"r") as z:
        candidates=[]
        for info in z.infolist():
            if info.is_dir():
                continue
            name=Path(info.filename).name
            if name==PACKED.name:
                candidates=[info]
                break
            if name.endswith(".§wyrlzx.gz") or name.endswith(".gz"):
                candidates.append(info)
        if not candidates:
            raise ValueError("ZIP does not contain an R39 gzip candidate")
        for info in candidates:
            h=hashlib.sha256(); size=0
            with z.open(info,"r") as src,tmp.open("wb") as out:
                for block in iter(lambda:src.read(1024*1024),b""):
                    out.write(block); h.update(block); size+=len(block)
            if size==PACKED_SIZE and h.hexdigest()==PACKED_SHA:
                os.replace(tmp,PACKED)
                return info.filename
            tmp.unlink(missing_ok=True)
    raise ValueError("ZIP contains no gzip matching the exact R39 size/SHA contract")

def _reconstruct_forge_transport():
    root=_repo_root()
    for manifest in _manifest_candidates(root):
        if not manifest.is_file():
            continue
        data=json.loads(manifest.read_text("utf-8"))
        transport=str(data.get("transport",""))
        if not transport.startswith("chunked-git-blobs-v"):
            continue
        source_name=str(data.get("source_zip") or data.get("zip") or "")
        if not source_name:
            continue
        source_tmp=LIVE/(Path(source_name).name+".transport.part")
        try:
            meta=_copy_verified_chunks(root,data,source_tmp)
            if source_name==PACKED.name:
                if meta["size"]!=PACKED_SIZE or meta["sha256"]!=PACKED_SHA:
                    raise ValueError("transported gzip does not match R39 contract")
                os.replace(source_tmp,PACKED)
                return {"manifest":str(manifest),"transport":transport,"chunks":meta["chunks"],"wrapper":"none"}
            if source_name.lower().endswith(".zip"):
                nested=_extract_r39_gzip_from_zip(source_tmp)
                source_tmp.unlink(missing_ok=True)
                return {"manifest":str(manifest),"transport":transport,"chunks":meta["chunks"],"wrapper":"zip","archive":source_name,"nested":nested}
        finally:
            source_tmp.unlink(missing_ok=True)
    return None

def ensure_r39():
    transport=None
    if not PACKED.exists():
        transport=_reconstruct_forge_transport()
    url=os.environ.get("SWRLZ_R39_URL","").strip()
    if not PACKED.exists() and url:
        tmp=PACKED.with_suffix(PACKED.suffix+".part")
        with urllib.request.urlopen(url,timeout=90) as r,tmp.open("wb") as o:
            while True:
                b=r.read(1024*1024)
                if not b: break
                o.write(b)
        os.replace(tmp,PACKED)
    if RAW.exists() and RAW.stat().st_size==RAW_SIZE and sha(RAW)==RAW_SHA:
        return {"ok":True,"modelReady":True,"source":"cached-raw","rawPath":str(RAW),"rawSha256":RAW_SHA}
    if not PACKED.exists():
        return {"ok":False,"modelReady":False,"code":"R39_NOT_PRESENT","detail":"Upload R39 with Forge chunked Git transport (direct gzip or ZIP wrapper), upload the gzip through /api/admin, or set SWRLZ_R39_URL."}
    if PACKED.stat().st_size!=PACKED_SIZE:
        return {"ok":False,"modelReady":False,"code":"R39_PACKED_SIZE_MISMATCH","actual":PACKED.stat().st_size,"expected":PACKED_SIZE}
    psha=sha(PACKED)
    if psha!=PACKED_SHA:
        return {"ok":False,"modelReady":False,"code":"R39_PACKED_SHA_MISMATCH","actual":psha,"expected":PACKED_SHA}
    tmp=RAW.with_suffix(RAW.suffix+".part")
    with gzip.open(PACKED,"rb") as src,tmp.open("wb") as dst:
        while True:
            b=src.read(1024*1024)
            if not b: break
            dst.write(b)
    os.replace(tmp,RAW)
    rsha=sha(RAW)
    ok=RAW.stat().st_size==RAW_SIZE and rsha==RAW_SHA
    if not ok:
        return {"ok":False,"modelReady":False,"code":"R39_RAW_VERIFY_FAILED","actualSize":RAW.stat().st_size,"actualSha256":rsha}
    result={"ok":True,"modelReady":True,"source":"decompressed-r39","rawPath":str(RAW),"rawSha256":rsha}
    if transport:
        result["packedSource"]="forge-chunked-repository"
        result["transportManifest"]=transport["manifest"]
        result["transport"]=transport["transport"]
        result["transportChunks"]=transport["chunks"]
        result["transportWrapper"]=transport["wrapper"]
        if transport.get("archive"): result["transportArchive"]=transport["archive"]
        if transport.get("nested"): result["transportNestedR39"]=transport["nested"]
    return result
