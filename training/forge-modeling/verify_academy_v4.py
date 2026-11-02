#!/usr/bin/env python3
"""Offline v4 quadruped/Sheep Tag public teaching cases, not model evaluation."""
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
ROUTES={"explain","plan","native-proposal","context-needed","unsupported-native","refuse-unapproved","revision-flow","diagnose"}
DOMAINS={"quadruped-rig","animation","sheep-animation","vfx","permissions","research"}
FIELDS=("id","domain","request","route","expected","mustNot","source","anchor")

def issues_for(data, source_check=True):
    errors=[]
    if data.get("schema")!="swrlz-forge-modeling-public-practice-v4-delta":
        errors.append("invalid schema")
    if data.get("status")!="TEACHER_AUTHORED_NOT_EVALUATED":
        errors.append("cannot claim evaluated status")
    cases=data.get("cases")
    if not isinstance(cases,list) or len(cases)!=20:
        return errors+["requires 20 public cases"]
    ids=set()
    for i,row in enumerate(cases,101):
        if not isinstance(row,dict):
            errors.append(f"M{i:03d}: nonobject");continue
        key=row.get("id")
        if key!=f"M{i:03d}" or key in ids:
            errors.append(f"M{i:03d}: wrong/duplicate case ID")
        ids.add(key)
        if row.get("route") not in ROUTES or row.get("domain") not in DOMAINS:
            errors.append(f"{key}: invalid domain or route")
        for k in FIELDS:
            if not isinstance(row.get(k),str) or not row[k].strip():
                errors.append(f"{key}: missing {k}")
        path=row.get("source");anchor=row.get("anchor")
        if source_check and isinstance(path,str) and isinstance(anchor,str):
            try:
                file=(ROOT/path).resolve()
                file.relative_to(ROOT.resolve())
                if not file.is_file():errors.append(f"{key}: source missing: {path}")
                elif anchor not in file.read_text(encoding="utf-8"):
                    errors.append(f"{key}: source anchor missing: {anchor}")
            except (OSError,ValueError,UnicodeError):
                errors.append(f"{key}: invalid source path")
    if not (HERE/"QUADRUPED_ANIMATION_V4.md").is_file():errors.append("missing teaching guide")
    if not (HERE/"academy_v3_delta.json").is_file():errors.append("missing predecessor")
    return errors

def main():
    d=json.loads((HERE/"academy_v4_delta.json").read_text(encoding="utf-8"))
    errors=issues_for(d)
    damaged=json.loads(json.dumps(d))
    damaged["cases"][1]["id"]=damaged["cases"][0]["id"]
    if not any("duplicate" in e for e in issues_for(damaged,source_check=False)):
        errors.append("corruption guard failed")
    print(json.dumps({"scope":"public fixture and exact source anchor validation ONLY",
                     "cases":len(d.get("cases") or []),
                     "studentInferenceExecuted":False,"weightsChanged":False,
                     "editorOrQuestAcceptance":False,
                     "result":"PASS_SOURCE_FIXTURE" if not errors else "FAIL",
                     "errors":errors},indent=2))
    return int(bool(errors))

if __name__=="__main__":sys.exit(main())
