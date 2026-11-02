#!/usr/bin/env python3
"""§C Academy v4: offline public-teacher-fixture and canonical source-anchor checks.

Does NOT call models, the web, the hosted engine, or a live editor.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BASE=Path(__file__).resolve().parent
DOMAINS={"wolf-rig","wolf-animation","sheep-animation","particle","research"}
ROUTES={"explain","plan","diagnose","unsupported-native","context-needed","refuse-unapproved"}
FIELDS=("id","domain","route","request","expected","mustNot","source","anchor")

def validate(doc, *, verify_sources=True):
    errors=[]
    if doc.get("schema")!="swrlz-forge-modeling-public-practice-v4-delta":
        errors.append("wrong schema")
    if doc.get("status")!="TEACHER_AUTHORED_NOT_EVALUATED":
        errors.append("unproven competence status")
    cases=doc.get("cases")
    if not isinstance(cases,list) or len(cases)!=24:
        return errors+["must have 24 v4 teacher cases"]
    seen=set()
    for n,row in enumerate(cases,101):
        if not isinstance(row,dict):
            errors.append(f"row {n} not an object")
            continue
        ident=row.get("id")
        if ident!=f"M{n:03d}" or ident in seen:
            errors.append(f"{ident}: duplicate/out-of-order case")
        seen.add(ident)
        for field in FIELDS:
            if not isinstance(row.get(field),str) or not row[field].strip():
                errors.append(f"{ident}: missing {field}")
        if row.get("route") not in ROUTES or row.get("domain") not in DOMAINS:
            errors.append(f"{ident}: invalid domain/route")
        if verify_sources and isinstance(row.get("source"),str) and isinstance(row.get("anchor"),str):
            try:
                src=(ROOT / row["source"]).resolve()
                src.relative_to(ROOT.resolve())
                if not src.is_file():
                    errors.append(f"{ident}: source absent {row['source']}")
                elif row["anchor"] not in src.read_text(encoding="utf8"):
                    errors.append(f"{ident}: missing source anchor {row['anchor']}")
            except (ValueError,OSError,UnicodeError):
                errors.append(f"{ident}: unsafe/unreadable source")
    if set(row.get("domain") for row in cases if isinstance(row,dict))!=DOMAINS:
        errors.append("missing required wolf/sheep/particle/research domain")
    if not any(row.get("route")=="unsupported-native" for row in cases):
        errors.append("no Chat-native particle limitation case")
    if not (BASE/"WOLF_SHEEP_PARTICLES_V4.md").is_file():
        errors.append("missing v4 teaching guide")
    return errors

def main():
    doc=json.loads((BASE/"academy_v4_delta.json").read_text(encoding="utf8"))
    errs=validate(doc)
    corrupt=json.loads(json.dumps(doc))
    corrupt["cases"][1]["id"]=corrupt["cases"][0]["id"]
    if not any("duplicate" in x for x in validate(corrupt,verify_sources=False)):
        errs.append("negative duplicate-id test failed")
    report={"status":"PASS_SOURCE_FIXTURE" if not errs else "FAIL","cases":len(doc.get("cases") or []),
            "studentInference":False,"trainedWeights":False,"webRetrieval":False,
            "liveEditorOrDeviceTest":False,"errors":errs}
    print(json.dumps(report,indent=2))
    return int(bool(errs))

if __name__=="__main__":
    sys.exit(main())
