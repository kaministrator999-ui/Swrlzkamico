#!/usr/bin/env python3
from __future__ import annotations
import ast, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
engine = ROOT / "swyrlz" / "r39_inference.py"
ext = ROOT / "api" / "chat_extensions.py"
gate = ROOT / "swyrlz" / "gate5_live.py"
index = ROOT / "api" / "index.py"
base = ROOT / "api" / "server_v213.py"
matvec = ROOT / "swyrlz" / "r39_matvec_patch.py"
tok = ROOT / "swyrlz" / "r39_tokenizer_patch.py"

for p in (engine, ext, gate, index, base, matvec, tok):
    if not p.is_file(): raise SystemExit(f"MISSING:{p.relative_to(ROOT)}")
    ast.parse(p.read_text("utf-8"), filename=str(p))

es=engine.read_text("utf-8"); xs=ext.read_text("utf-8"); gs=gate.read_text("utf-8"); ms=matvec.read_text("utf-8"); ts=tok.read_text("utf-8"); isrc=index.read_text("utf-8")
checks={
    "server-version-2.1.6": 'VERSION = "2.1.6"' in isrc,
    "chat-version-1.3.2": 'chat.APP_VERSION="1.3.2"' in xs or 'chat.APP_VERSION = "1.3.2"' in xs,
    "canonical-header-toc-parser": 'struct.unpack_from("<HHIIIQQIIIIII"' in es and 'TOC_ENTRY_BYTES = 128' in es,
    "tensor-data-section-id-routing": 'dataSectionId' in es and 'self.data_sections' in es,
    "reference-lfm2-layer-profile": 'LAYER_KV = [0, 0, 8, 0, 0, 8, 0, 0, 8, 0, 8, 0, 8, 0, 8, 0]' in es,
    "quantizers": all(q in es for q in ('q4_0','q8_0','q4_k','q6_k','bf16')),
    "incremental-utf8": 'IncrementalDecoder' in es and 'getincrementaldecoder("utf-8")' in es,
    "truth-firewall-delta": 'event_type=="DELTA"' in xs,
    "local-route": '"LOCAL_R39"' in es and 'swrlz_r39_python_reference_v1' in es,
    "upstream-preserved": 'chat._proxy_stream(payload) if upstream_ready else _local_stream(payload)' in xs,
    "gate5-payload-locations": 'sectionPayloadLocationsReconstructed' in gs,
    "fail-closed-profile": 'R39_GRAPH_PROFILE_UNSUPPORTED' in es and 'R39_REFERENCE_TENSORS_MISSING' in es,
    "bounded-matvec": 'R39Model.matvec = _bounded_matvec' in ms and '4 * 1024 * 1024' in ms and 'r39_matvec_patch' in xs,
    "tokenizer-evidence-patch": 'r39_tokenizer_patch' in xs and 'BpeTokenizer.__init__' in ts,
    "auto-local-init": '_probe_local_once' in xs and 'manualGate5Required' in xs,
    "compute-heartbeat": '_heartbeat_events' in xs and 'COMPUTE_HEARTBEAT' in xs and 'ThreadPoolExecutor' in xs,
}
failed=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(("PASS" if v else "FAIL")+" | "+k)
if failed: raise SystemExit("FAILED:"+",".join(failed))
print(f"RESULT | {len(checks)}/{len(checks)} PASS")
