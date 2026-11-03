#!/usr/bin/env python3
"""Check §C Academy v5 public case format and source anchors offline.

This validator DOES NOT call 700M/Qwen, hosted §E, WebXR or native tools.
Passing means evidence paths/strings are currently present, not model skill.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = Path(__file__).resolve().parent
DOMAINS = {"game-design", "material-texture", "animation-rig", "particle", "cross-studio"}
ROUTES = {"explain", "plan", "diagnose", "unsupported-native", "context-needed", "refuse-unapproved"}
REQUIRED = ("id", "domain", "route", "request", "expected", "mustNot", "source", "anchor")


def validate(doc: dict, *, verify_sources: bool = True) -> list[str]:
    errors: list[str] = []
    if doc.get("schema") != "swrlz-forge-modeling-public-practice-v5-delta":
        errors.append("unexpected schema")
    if doc.get("status") != "TEACHER_AUTHORED_NOT_EVALUATED":
        errors.append("evaluation boundary missing")
    cases = doc.get("cases")
    if not isinstance(cases, list) or len(cases) != 20:
        return errors + ["expected exactly 20 v5 cases"]
    seen: set[str] = set()
    for n, item in enumerate(cases, 125):
        if not isinstance(item, dict):
            errors.append(f"row M{n}: invalid record")
            continue
        ident = item.get("id")
        if ident != f"M{n}" or ident in seen:
            errors.append(f"{ident}: duplicate/out-of-order id")
        seen.add(ident)
        for field in REQUIRED:
            value = item.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{ident}: missing {field}")
            elif len(value) > 1000:
                errors.append(f"{ident}: unreasonable {field}")
        if item.get("domain") not in DOMAINS or item.get("route") not in ROUTES:
            errors.append(f"{ident}: invalid domain/route")
        if verify_sources and isinstance(item.get("source"), str) and isinstance(item.get("anchor"), str):
            try:
                target = (ROOT / item["source"]).resolve()
                target.relative_to(ROOT.resolve())
                if not target.is_file():
                    errors.append(f"{ident}: missing source {item['source']}")
                elif item["anchor"] not in target.read_text(encoding="utf-8"):
                    errors.append(f"{ident}: source anchor absent")
            except (ValueError, OSError, UnicodeError):
                errors.append(f"{ident}: unsafe/unreadable source")
    if {x.get("domain") for x in cases if isinstance(x, dict)} != DOMAINS:
        errors.append("coverage: not all five studio areas represented")
    if not any(x.get("route") == "unsupported-native" for x in cases if isinstance(x, dict)):
        errors.append("coverage: missing denied native operation")
    if not (BASE / "STUDIO_COORDINATION_V5.md").exists():
        errors.append("missing companion teaching guide")
    return errors


def main() -> int:
    doc = json.loads((BASE / "academy_v5_delta.json").read_text(encoding="utf-8"))
    errors = validate(doc)
    bad = json.loads(json.dumps(doc))
    bad["cases"][1]["id"] = bad["cases"][0]["id"]
    if not any("duplicate" in e for e in validate(bad, verify_sources=False)):
        errors.append("negative duplicate-ID control failed")
    bad = json.loads(json.dumps(doc))
    bad["cases"][0]["source"] = "../../etc/passwd"
    if not any("unsafe" in e or "missing source" in e for e in validate(bad)):
        errors.append("negative unsafe source control failed")
    print(json.dumps({
        "status": "PASS_SOURCE_FIXTURE" if not errors else "FAIL",
        "publicCases": len(doc["cases"]),
        "sourceAnchorsChecked": True,
        "trainedWeights": False,
        "measuredStudentAccuracy": False,
        "hostedEngineTest": False,
        "errors": errors
    }, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
