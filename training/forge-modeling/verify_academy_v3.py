#!/usr/bin/env python3
"""Offline v3 §C→§E teacher-fixture/source-anchor validator, NOT a model benchmark."""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
ROUTES = {"explain", "plan", "native-proposal", "context-needed", "unsupported-native",
          "refuse-unapproved", "revision-flow", "diagnose"}
FIELDS = ("id", "domain", "request", "route", "expected", "mustNot", "source", "anchor")
DOMAINS = {"retargeting", "animation", "research", "privacy", "permission", "evidence"}

def issues_for(data: dict, *, check_sources: bool = True) -> list[str]:
    issues = []
    if data.get("schema") != "swrlz-forge-modeling-public-practice-v3-delta":
        issues.append("wrong v3 schema")
    if data.get("status") != "TEACHER_AUTHORED_NOT_EVALUATED":
        issues.append("cannot claim independent evaluation")
    cases = data.get("cases")
    if not isinstance(cases, list) or len(cases) != 21:
        return issues + ["expected 21 teacher-authored v3 cases"]
    all_ids, domains = set(), set()
    for i, row in enumerate(cases, start=80):
        if not isinstance(row, dict):
            issues.append(f"M{i:03d}: invalid row")
            continue
        id_ = row.get("id")
        if id_ != f"M{i:03d}" or id_ in all_ids:
            issues.append(f"M{i:03d}: out-of-sequence/duplicate ID")
        all_ids.add(id_)
        domains.add(row.get("domain"))
        for field in FIELDS:
            if not isinstance(row.get(field), str) or not row[field].strip():
                issues.append(f"{id_}: missing {field}")
        if row.get("route") not in ROUTES:
            issues.append(f"{id_}: unapproved route")
        source = row.get("source")
        anchor = row.get("anchor")
        if not check_sources or not isinstance(source, str) or not isinstance(anchor, str):
            continue
        try:
            resolved = (ROOT / source).resolve()
            resolved.relative_to(ROOT.resolve())
            if not resolved.is_file():
                issues.append(f"{id_}: source missing {source}")
            elif anchor not in resolved.read_text(encoding="utf-8"):
                issues.append(f"{id_}: source anchor missing {anchor!r}")
        except (OSError, ValueError, UnicodeError):
            issues.append(f"{id_}: source path unsafe")
    if not DOMAINS.issubset(domains):
        issues.append("required teaching domains absent")
    if not any(r.get("route") == "refuse-unapproved" for r in cases):
        issues.append("missing live-capture denial case")
    if not (HERE / "model_context_v3.txt").is_file():
        issues.append("missing bounded v3 teaching reference")
    return issues

def main():
    d = json.loads((HERE / "academy_v3_delta.json").read_text(encoding="utf-8"))
    issues = issues_for(d)
    corrupt = json.loads(json.dumps(d))
    corrupt["cases"][1]["id"] = corrupt["cases"][0]["id"]
    if not any("duplicate" in err for err in issues_for(corrupt, check_sources=False)):
        issues.append("negative duplicate fixture not detected")
    result = {"sourceValidation": "PASS" if not issues else "FAIL",
              "publicTeacherCases": len(d.get("cases") or []),
              "modelInferenceExecuted": False, "onlineResearchExecuted": False,
              "weightTrainingExecuted": False, "nativeEditorActionsExecuted": False,
              "errors": issues}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return int(bool(issues))

if __name__ == "__main__":
    sys.exit(main())
