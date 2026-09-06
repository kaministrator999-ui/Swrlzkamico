from __future__ import annotations
import gzip, hashlib, os, urllib.request
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

def ensure_r39():
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
        return {"ok":False,"modelReady":False,"code":"R39_NOT_PRESENT","detail":"Upload the repaired R39 gzip into /tmp/swrlz-admin/live through /api/admin or set SWRLZ_R39_URL."}
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
    return {"ok":True,"modelReady":True,"source":"decompressed-r39","rawPath":str(RAW),"rawSha256":rsha}
