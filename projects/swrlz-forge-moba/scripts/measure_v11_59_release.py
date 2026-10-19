#!/usr/bin/env python3
"""Preflight exact v11.59 source bytes before manifest seal update.

Uses the already SHA-verified v11.20 source manifest and exact cumulative
preview builder, then applies only the v11.59 marker/title production delta.
Does not bypass the final governed build_space.py integrity assertion.
"""
import hashlib, json, runpy, tempfile
from pathlib import Path

PROJECT=Path(__file__).resolve().parents[1]
PREVIEW=PROJECT/"scripts/build_atelier_precision_preview_v11_59.py"
with tempfile.TemporaryDirectory(prefix="atelier_release_measure_") as temp:
    import subprocess
    out=Path(temp)/"candidate"
    subprocess.run(["python",str(PREVIEW),"--output",str(out)],check=True)
    source=(out/"index.html").read_text(encoding="utf-8")
    prev="SWYRL_ENGINE_DEPLOY_MARKER: V11_21_VERTEX_SPHERE_BRUSH_PREVIEW"
    current="SWYRL_ENGINE_DEPLOY_MARKER: V11_59_PRECISION_MODEL_ATELIER"
    assert source.count(prev)==1
    assert source.count("Maker v11.21 preview")>=1
    candidate=source.replace(prev,current,1).replace("Maker v11.21 preview","Maker v11.59")
    assert "<title>§wyrl§ Engine · Maker v11.59</title>" in candidate
    data=candidate.encode("utf-8")
    print("V1159_GOVERNED_RELEASE_DIGEST",json.dumps({"finalSha256":hashlib.sha256(data).hexdigest(),
         "finalBytes":len(data),"releaseMarker":current,"sourcePreviewSha256":hashlib.sha256(source.encode()).hexdigest()}))
