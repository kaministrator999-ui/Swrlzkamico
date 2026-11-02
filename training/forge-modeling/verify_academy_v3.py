#!/usr/bin/env python3
"""Offline public teacher-fixture source checker for Academy v3.

No external network, model inference, editor mutation, or hidden benchmark.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
ROUTES = {"explain", "plan", "native-proposal", "context-needed",
          "unsupported-native", "refuse-unapproved", "revision-flow", "diagnose"}
NEEDED = ("id", "domain", "request", "route", "expected", "mustNot", "source", "anchor")

def problems(data, check_sources=True):
    failures = []
    if data.get("schema") != "swrlz-forge-modeling-public-practice-v3-retarget":
        failures.append("wrong v3 schema")
    if data.get("status") != "TEACHER_AUTHORED_NOT_EVALUATED":
        failures.append("only unevaluated teacher data is valid")
    rows = data.get("cases")
    if not isinstance(rows, list) or len(rows) != 16:
        return failures + ["expected exactly 16 source-grounded v3 cases"]
    for index, item in enumerate(rows, 80):
        case_id = f"M{index:03d}"
        if not isinstance(item, dict):
            failures.append(f"{case_id}: row not an object")
            continue
        if item.get("id") != case_id:
            failures.append(f"{case_id}: wrong sequence or duplicate id")
        for key in NEEDED:
            if not isinstance(item.get(key), str) or not item[key].strip():
                failures.append(f"{case_id}: missing {key}")
        if item.get("route") not in ROUTES:
            failures.append(f"{case_id}: invalid route")
        source, anchor = item.get("source"), item.get("anchor")
        if check_sources and isinstance(source, str) and isinstance(anchor, str):
            try:
                path = (ROOT / source).resolve()
                path.relative_to(ROOT.resolve())
                if not path.is_file():
                    failures.append(f"{case_id}: missing source {source}")
                elif anchor not in path.read_text(encoding="utf-8"):
                    failures.append(f"{case_id}: missing anchor {anchor!r}")
            except (OSError, ValueError, UnicodeError):
                failures.append(f"{case_id}: invalid source path")
    if not any(x.get("route") == "unsupported-native" for x in rows if isinstance(x, dict)):
        failures.append("missing unsupported native example")
    if not (HERE / "HAND_RETARGETING_REFERENCE_V3.md").is_file():
        failures.append("missing W3C-to-engine analysis guide")
    if not (HERE / "model_context_v3.txt").is_file():
        failures.append("missing bounded contextual primer")
    return failures

def main():
    data = json.loads((HERE / "academy_v3_delta.json").read_text(encoding="utf-8"))
    errors = problems(data)
    corrupt = json.loads(json.dumps(data))
    corrupt["cases"][1]["id"] = corrupt["cases"][0]["id"]
    if not any("duplicate" in err for err in problems(corrupt, False)):
        errors.append("negative ID corruption test did not fail")
    print(json.dumps({"status": "PASS_SOURCE_FIXTURE" if not errors else "FAIL",
                      "publicCases": len(data.get("cases", [])),
                      "totalPublicAcademyCases": 95,
                      "realModelEvaluated": False,
                      "liveSearchPerformed": False,
                      "deviceTestPerformed": False,
                      "modelWeightsUpdated": False,
                      "errors": errors}, indent=2))
    return bool(errors)

if __name__ == "__main__":
    sys.exit(main())
