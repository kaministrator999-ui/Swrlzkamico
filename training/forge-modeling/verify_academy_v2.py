#!/usr/bin/env python3
"""Verify v2 public rigging curriculum's structure and exact local source anchors.

This checks teacher-authored fixtures only; no model inference, search, or user editing.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = Path(__file__).resolve().parent
ALLOWED_ROUTES = {"explain", "plan", "native-proposal", "context-needed",
                  "unsupported-native", "refuse-unapproved", "revision-flow", "diagnose"}
REQUIRED_DOMAINS = {"hand-rig", "posing", "animation", "persistence", "permission", "source-engineering"}
REQUIRED_FIELDS = ("id", "domain", "request", "route", "expected", "mustNot", "source", "anchor")

def issues_for(data: dict, source_check: bool = True) -> list[str]:
    issues = []
    if data.get("schema") != "swrlz-forge-modeling-public-practice-v2-delta":
        issues.append("incorrect schema")
    if data.get("status") != "TEACHER_AUTHORED_NOT_EVALUATED":
        issues.append("fixture cannot claim model-evaluated")
    rows = data.get("cases")
    if not isinstance(rows, list) or len(rows) != 31:
        return issues + ["expected 31 public follow-up cases"]
    ids = set()
    domains = set()
    for i, item in enumerate(rows, 37):
        if not isinstance(item, dict):
            issues.append(f"row {i} is not an object")
            continue
        rid = item.get("id")
        if rid != f"M{i:03d}" or rid in ids:
            issues.append(f"row {i} unexpected or duplicate ID: {rid}")
        ids.add(rid)
        domains.add(item.get("domain"))
        for field in REQUIRED_FIELDS:
            if not isinstance(item.get(field), str) or not item[field].strip():
                issues.append(f"{rid}: missing {field}")
        if item.get("route") not in ALLOWED_ROUTES:
            issues.append(f"{rid}: invalid route")
        source, anchor = item.get("source"), item.get("anchor")
        if source_check and isinstance(source, str) and isinstance(anchor, str):
            try:
                path = (ROOT / source).resolve()
                path.relative_to(ROOT.resolve())
                if not path.is_file():
                    issues.append(f"{rid}: missing source {source}")
                elif anchor not in path.read_text(encoding="utf-8"):
                    issues.append(f"{rid}: missing source anchor {anchor!r}")
            except (OSError, ValueError, UnicodeError):
                issues.append(f"{rid}: invalid source path")
    if not REQUIRED_DOMAINS.issubset(domains):
        issues.append("missing rigging/animation/reference learning domain")
    if not any(x.get("route") == "unsupported-native" for x in rows if isinstance(x, dict)):
        issues.append("missing unsupported native-operation gate")
    if not any("Quest" in x.get("request", "") for x in rows if isinstance(x, dict)):
        issues.append("missing Quest tracking counterexample")
    if not (BASE / "RIGGING_ANIMATION_RESEARCH_V2.md").is_file():
        issues.append("missing research curriculum")
    return issues

def main() -> int:
    data = json.loads((BASE / "academy_v2_delta.json").read_text(encoding="utf-8"))
    issues = issues_for(data)
    poisoned = json.loads(json.dumps(data))
    poisoned["cases"][1]["id"] = poisoned["cases"][0]["id"]
    if not any("duplicate" in issue for issue in issues_for(poisoned, source_check=False)):
        issues.append("negative duplicate-id test failed to reject corruption")
    report = {"scope": "public teacher fixture and local anchor validation only",
              "cases": len(data.get("cases") or []),
              "modelInferenceExecuted": False, "weightsChanged": False,
              "liveEditorActionsPerformed": False,
              "result": "PASS_SOURCE_FIXTURE" if not issues else "FAIL",
              "errors": issues}
    print(json.dumps(report, indent=2))
    return bool(issues)

if __name__ == "__main__":
    sys.exit(main())
