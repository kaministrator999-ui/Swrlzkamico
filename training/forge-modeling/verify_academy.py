#!/usr/bin/env python3
"""Offline §C⇄§E modeling teacher-fixture validator. Never grades models."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
ROUTES = {
    "explain", "plan", "native-proposal", "context-needed",
    "unsupported-native", "refuse-unapproved", "revision-flow", "diagnose",
}
DOMAINS = {"intent", "context", "native", "edit", "anatomy", "state", "release", "evidence"}

def issues_for(doc, check_sources=True):
    errors = []
    if doc.get("schema") != "swrlz-forge-modeling-public-practice-v1":
        errors.append("bad schema")
    if doc.get("status") != "TEACHER_AUTHORED_NOT_EVALUATED":
        errors.append("corpus must remain unevaluated without real model receipts")
    if not isinstance(doc.get("cases"), list) or len(doc["cases"]) < 30:
        errors.append("need >=30 teacher examples")
        return errors
    seen = set()
    for i, row in enumerate(doc["cases"]):
        if not isinstance(row, dict):
            errors.append(f"{i}: case is not object")
            continue
        label = row.get("id", f"row_{i}")
        if not re.fullmatch(r"M\d{3}", str(label)) or label in seen:
            errors.append(f"{label}: invalid/duplicate id")
        seen.add(label)
        if row.get("route") not in ROUTES or row.get("domain") not in DOMAINS:
            errors.append(f"{label}: unknown route/domain")
        for key in ("request", "expected", "mustNot", "source", "anchor"):
            if not isinstance(row.get(key), str) or not row[key].strip():
                errors.append(f"{label}: missing {key}")
        src = row.get("source")
        anchor = row.get("anchor")
        if check_sources and isinstance(src, str) and isinstance(anchor, str):
            try:
                path = (ROOT / src).resolve()
                path.relative_to(ROOT.resolve())
                if not path.is_file():
                    errors.append(f"{label}: source missing {src}")
                elif anchor not in path.read_text(encoding="utf-8"):
                    errors.append(f"{label}: source anchor missing: {anchor!r} in {src}")
            except (OSError, ValueError, UnicodeError):
                errors.append(f"{label}: invalid source path")
    if not any(r.get("route") == "native-proposal" for r in doc["cases"] if isinstance(r, dict)):
        errors.append("no bounded native proposal example")
    if not any(r.get("route") == "unsupported-native" for r in doc["cases"] if isinstance(r, dict)):
        errors.append("no unsupported-capability examples")
    return errors

def main():
    data = json.loads((HERE / "academy_v1.json").read_text(encoding="utf-8"))
    failures = issues_for(data)
    # Negative structural self-test: deliberately duplicated ID must be rejected.
    poisoned = json.loads(json.dumps(data))
    poisoned["cases"][1]["id"] = poisoned["cases"][0]["id"]
    if not any("duplicate" in e for e in issues_for(poisoned, check_sources=False)):
        failures.append("negative duplicate test did not fail")
    output = {
        "scope": "local teaching schema + verified repository source anchors only",
        "modelInferenceExecuted": False,
        "weightsChanged": False,
        "liveChatActivated": False,
        "cases": len(data["cases"]),
        "result": "PASS_TEACHER_SOURCE_FIXTURE" if not failures else "FAIL",
        "errors": failures,
    }
    print(json.dumps(output, indent=2))
    return int(bool(failures))

if __name__ == "__main__":
    sys.exit(main())
