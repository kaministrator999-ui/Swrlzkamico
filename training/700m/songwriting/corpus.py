"""Fail-closed quality-review gate for original 700M songwriting SFT data.

No historical chat exports, source lyrics, private profiles, auto-grading,
or unreviewed generated lyrics are authorized as training records.
"""
import hashlib
import json
from pathlib import Path

SCHEMA = "swrlz-700m-songwriting-sft-v1"
DIMENSIONS = ("rhyme", "flow", "coherence", "completion", "originality")
ALLOWED_ORIGINS = {"commissioned-original", "author-original", "reviewed-model-original"}


def load_reviewed_corpus(path):
    items = []
    seen_prompts = set()
    seen_completions = set()
    for line_num, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except ValueError as exc:
            raise ValueError(f"row {line_num}: malformed JSON") from exc
        if row.get("schema") != SCHEMA or row.get("split") not in {"train", "holdout"}:
            raise ValueError(f"row {line_num}: invalid schema/split")
        if row.get("status") != "APPROVED":
            raise ValueError(f"row {line_num}: not approved for weight training")
        if row.get("origin") not in ALLOWED_ORIGINS or row.get("rightsCleared") is not True:
            raise ValueError(f"row {line_num}: provenance/rights not cleared")
        if row.get("privacyReviewed") is not True:
            raise ValueError(f"row {line_num}: privacy review absent")
        prompt, answer = row.get("prompt"), row.get("completion")
        if not isinstance(prompt, str) or not isinstance(answer, str) or len(prompt.strip()) < 20 or len(answer.split()) < 25:
            raise ValueError(f"row {line_num}: missing usable exact prompt/completion")
        reviews = row.get("reviews")
        if not isinstance(reviews, list) or len(reviews) < 2:
            raise ValueError(f"row {line_num}: two documented quality reviews required")
        reviewer_ids = set()
        for review in reviews:
            if not isinstance(review, dict) or not isinstance(review.get("reviewerId"), str) or not review["reviewerId"].strip():
                raise ValueError(f"row {line_num}: review ownership missing")
            rid = review["reviewerId"].strip()
            if rid in reviewer_ids or review.get("approved") is not True or review.get("originalityChecked") is not True:
                raise ValueError(f"row {line_num}: duplicate/failed review")
            reviewer_ids.add(rid)
            scores = review.get("scores")
            if not isinstance(scores, dict) or any(type(scores.get(dim)) is not int or not 4 <= scores[dim] <= 5 for dim in DIMENSIONS):
                raise ValueError(f"row {line_num}: quality threshold not met")
        prompt_hash = hashlib.sha256(" ".join(prompt.lower().split()).encode()).hexdigest()
        lyric_hash = hashlib.sha256(" ".join(answer.lower().split()).encode()).hexdigest()
        if prompt_hash in seen_prompts or lyric_hash in seen_completions:
            raise ValueError(f"row {line_num}: duplicate prompt or target, including across splits")
        seen_prompts.add(prompt_hash)
        seen_completions.add(lyric_hash)
        items.append(row)
    if not items:
        raise ValueError("no approved records")
    return items


def split_corpus(records):
    return ([r for r in records if r["split"] == "train"],
            [r for r in records if r["split"] == "holdout"])


def corpus_receipt(records):
    train, holdout = split_corpus(records)
    return {"schema": SCHEMA, "approvedRecords": len(records),
            "trainRecords": len(train), "holdoutRecords": len(holdout)}
