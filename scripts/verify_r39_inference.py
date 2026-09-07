#!/usr/bin/env python3
from __future__ import annotations
import ast, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
engine = ROOT / "swyrlz" / "r39_inference.py"
ext = ROOT / "api" / "chat_extensions.py"
gate = ROOT / "swyrlz" / "gate5_live.py"
index = ROOT / "api" / "index.py"
base = ROOT / "api" / "server_v213.py"
patch = ROOT / "swyrlz" / "r39_matvec_patch.py"

for p in (engine, ext, gate, index, base, patch):
    if not p.is_file(): raise SystemExit(f"MISSING:{p.relative_to(ROOT)}")
    ast.parse(p.read_text("utf-8"), filename=str(p))

es = engine.read_text("utf-8")
xs = ext.read_text("utf-8")
gs = gate.read_text("utf-8")
ps = patch.read_text("utf-8")
isrc = index.read_text("utf-8")
checks = {
    "server-version-2.1.4": 'VERSION = "2.1.4"' in isrc,
    "chat-version-1.3.0": 'chat.APP_VERSION = "1.3.0"' in xs,
    "canonical-header-toc-parser": 'struct.unpack_from("<HHIIIQQIIIIII"' in es and 'TOC_ENTRY_BYTES = 128' in es,
    "tensor-data-section-id-routing": 'dataSectionId' in es and 'self.data_sections' in es,
    "reference-lfm2-layer-profile": 'LAYER_KV = [0, 0, 8, 0, 0, 8, 0, 0, 8, 0, 8, 0, 8, 0, 8, 0]' in es,
    "quantizers": all(q in es for q in ('q4_0','q8_0','q4_k','q6_k','bf16')),
    "incremental-utf8": 'IncrementalDecoder' in es and 'getincrementaldecoder("utf-8")' in es,
    "truth-firewall-delta": 'if event_type == "DELTA": event["text"]' in xs,
    "local-route": '"LOCAL_R39"' in es and 'swrlz_r39_python_reference_v1' in es,
    "upstream-preserved": 'chat._proxy_stream(payload) if upstream_ready else _local_stream(payload)' in xs,
    "gate5-payload-locations": 'sectionPayloadLocationsReconstructed' in gs,
    "fail-closed-profile": 'R39_GRAPH_PROFILE_UNSUPPORTED' in es and 'R39_REFERENCE_TENSORS_MISSING' in es,
    "bounded-matvec": 'R39Model.matvec = _bounded_matvec' in ps and '4 * 1024 * 1024' in ps and 'r39_matvec_patch' in xs,
}
failed=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(("PASS" if v else "FAIL")+" | "+k)
if failed: raise SystemExit("FAILED:"+",".join(failed))
print(f"RESULT | {len(checks)}/{len(checks)} PASS")
