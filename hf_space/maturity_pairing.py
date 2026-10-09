"""Offline comparison of *reported* model trial receipts; no inference or grading.

Only bounded non-sensitive IDs/hashes/scores are accepted. A claimed test receipt
is not cryptographic proof. This is a comparison scaffold, never a deployment,
training or evaluation-acceptance authority.
"""
from __future__ import annotations
import re
from typing import Any

SCHEMA = "swrlz-model-paired-trial-v1"
_SHA = re.compile(r"^[a-f0-9]{64}$")


def _safe_id(value: Any, limit: int = 120) -> str:
    if not isinstance(value, str) or not 1 <= len(value) <= limit:
        raise ValueError("required ID missing or too long")
    if not re.fullmatch(r"[a-zA-Z0-9_./:@+-]+", value):
        raise ValueError("invalid ID characters")
    return value


def _hash(value: Any) -> str:
    if not isinstance(value, str) or not _SHA.fullmatch(value):
        raise ValueError("invalid SHA-256 digest")
    return value


def _candidate(record: Any) -> tuple[str | None, str | None]:
    if not isinstance(record, dict):
        return None, "missing-record"
    output_hash = record.get("outputSha256")
    if not output_hash:
        return None, "unobserved-output"
    _hash(output_hash)
    grader = record.get("grader")
    if not isinstance(grader, dict):
        return None, "missing-external-grader"
    if grader.get("source") != "independent" or not grader.get("receiptRef"):
        return None, "unverified-grader"
    _safe_id(grader.get("receiptRef"), 180)
    technical = grader.get("technicalPass")
    intent = grader.get("intentPass")
    if not isinstance(technical, bool) or not isinstance(intent, bool):
        return None, "incomplete-two-gate-result"
    return "reported-pass" if (technical and intent) else "reported-fail", None


def compare_pairs(doc: dict[str, Any]) -> dict[str, Any]:
    """Summarize self-describing reports, never assert independent ground truth."""
    if not isinstance(doc, dict) or doc.get("schema") != SCHEMA:
        raise ValueError("invalid paired-trial schema")
    items = doc.get("pairs")
    if not isinstance(items, list) or not 1 <= len(items) <= 200:
        raise ValueError("expected 1..200 pairs")
    counts = {"reportedImproved": 0, "reportedRegressed": 0,
              "reportedUnchanged": 0, "unscored": 0}
    rows = []
    seen = set()

    for pair in items:
        if not isinstance(pair, dict):
            raise ValueError("invalid pair record")
        case = _safe_id(pair.get("caseId"))
        if case in seen:
            raise ValueError("duplicate caseId")
        seen.add(case)

        # Identical checkpoint and prompt hash makes the effect attributable to
        # routing/prompt policy, not a silent model-weight or task change.
        identity = {}
        for key in ("modelId", "checkpointSha256", "promptSha256", "evaluatorId"):
            value = pair.get(key)
            identity[key] = _hash(value) if key.endswith("Sha256") else _safe_id(value)
        baseline = pair.get("baseline")
        candidate = pair.get("candidate")
        before, issue_before = _candidate(baseline)
        after, issue_after = _candidate(candidate)

        if before is None or after is None:
            counts["unscored"] += 1
            outcome = "UNSCORED"
            reason = issue_before or issue_after
        elif before != after:
            outcome = "REPORTED_IMPROVED" if after == "reported-pass" else "REPORTED_REGRESSED"
            counts["reportedImproved" if after == "reported-pass" else "reportedRegressed"] += 1
            reason = "both-gates-reported"
        else:
            outcome = "REPORTED_UNCHANGED"
            counts["reportedUnchanged"] += 1
            reason = "both-gates-reported"

        rows.append({"caseId": case, "modelId": identity["modelId"],
                     "outcome": outcome, "reason": reason})
    public = bool(doc.get("publicPractice", True))
    return {
        "schema": "swrlz-model-paired-summary-v1",
        "source": "reported-receipts-only-no-external-audit",
        "canAuthorizeDeployment": False, "provesWeightTraining": False,
        "isSealedHoldout": False if public else "NOT_EXTERNALLY_VERIFIED",
        "pairs": len(items), "counts": counts, "results": rows,
        "warning": "Reported test receipts must be independently audited against exact model outputs. This tool is not the grader.",
    }


def main(argv: list[str] | None = None) -> int:
    """Read local metadata only; never call a model or print raw conversations."""
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Inspect reported Qwen/700M A/B receipts; NOT an independent grader")
    parser.add_argument("--input", required=True, help="Local JSON metadata with the swrlz-model-paired-trial-v1 schema")
    args = parser.parse_args(argv)
    with Path(args.input).open(encoding="utf-8") as stream:
        document = json.load(stream)
    summary = compare_pairs(document)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
