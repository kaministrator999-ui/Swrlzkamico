#!/usr/bin/env python3
"""Prepare verified image+answer pairs for Qwen3-VL multimodal LoRA training.

Input is PRIVATE source annotation JSONL, never Qwen-generated reports.
Outputs are ms-swift JSONL files and a non-sensitive aggregate manifest.
No network calls, image copies, training, or model weights are involved.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from collections import defaultdict

SPLITS = ("train", "val", "test")
DEFAULT_PROMPT = "What do you see in this image?"
MAX_IMAGE_BYTES = 20 * 1024 * 1024


def _row_source(path: Path):
    with path.open("r", encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except ValueError as exc:
                raise ValueError(f"Invalid JSON line {number}") from exc
            if not isinstance(item, dict):
                raise ValueError(f"Line {number}: expected a JSON object")
            yield number, item


def _image(image_root: Path, raw: str) -> tuple[str, str]:
    if not isinstance(raw, str) or not raw.strip() or Path(raw).is_absolute():
        raise ValueError("image must be a relative path within --image-root")
    full = (image_root / raw).resolve()
    if not full.is_relative_to(image_root):
        raise ValueError("image escapes --image-root")
    if full.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp"):
        raise ValueError("Unsupported image type")
    if not full.is_file() or full.stat().st_size > MAX_IMAGE_BYTES:
        raise ValueError("image missing or too large (max 20 MiB)")
    hash_obj = hashlib.sha256()
    with full.open("rb") as stream:
        magic = stream.read(12)
        if not (magic.startswith(b"\xff\xd8\xff")
                or magic.startswith(b"\x89PNG\r\n\x1a\n")
                or (magic[:4] == b"RIFF" and magic[8:12] == b"WEBP")):
            raise ValueError("image content doesn't match JPEG/PNG/WebP")
        stream.seek(0)
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hash_obj.update(chunk)
    return str(full), hash_obj.hexdigest()


def prepare(source: Path, root: Path, output: Path, *, min_train_characters: int = 3) -> dict:
    if min_train_characters < 2:
        raise ValueError("At least two training characters are required")
    root = root.resolve(strict=True)
    source = source.resolve(strict=True)
    rows = {split: [] for split in SPLITS}
    groups = defaultdict(set)
    seen_ids = set()
    image_splits = defaultdict(set)
    image_answers = defaultdict(set)
    for line, item in _row_source(source):
        identifier = item.get("id")
        group = item.get("character_id")
        split = item.get("split")
        verified = item.get("human_verified")
        answer = item.get("gold_answer")
        prompt = item.get("question", DEFAULT_PROMPT)
        if not isinstance(identifier, str) or not identifier.strip() or identifier in seen_ids:
            raise ValueError(f"Line {line}: missing or duplicated sample id")
        seen_ids.add(identifier)
        if not isinstance(group, str) or not group.strip():
            raise ValueError(f"Line {line}: character_id required")
        if split not in SPLITS:
            raise ValueError(f"Line {line}: split must be train, val, or test")
        if verified is not True:
            raise ValueError(f"Line {line}: human_verified must be true; model guesses are not gold labels")
        if not isinstance(answer, str) or not (40 <= len(answer.strip()) <= 6000):
            raise ValueError(f"Line {line}: gold_answer must be 40–6000 chars")
        if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 400:
            raise ValueError(f"Line {line}: invalid question")
        if "<image>" in prompt or "<video>" in prompt:
            raise ValueError(f"Line {line}: question must not contain manual image placeholders")
        if "Local image analyzer's description" in answer or "Focused image details (unverified" in answer:
            raise ValueError(f"Line {line}: raw Qwen analyzer output cannot serve as a verified gold answer")
        try:
            image_path, image_hash = _image(root, item.get("image"))
        except (ValueError, OSError) as exc:
            raise ValueError(f"Line {line}: {exc}") from exc
        groups[group].add(split)
        image_splits[image_hash].add(split)
        image_answers[image_hash].add(answer.strip())
        rows[split].append({
            "messages": [
                {"role": "user", "content": "<image>" + prompt.strip()},
                {"role": "assistant", "content": answer.strip()},
            ],
            "images": [image_path],
        })

    leaking_groups = [group for group, splits in groups.items() if len(splits) > 1]
    leaking_images = [digest for digest, splits in image_splits.items() if len(splits) > 1]
    contradictory_labels = [digest for digest, labels in image_answers.items() if len(labels) > 1]
    if leaking_groups or leaking_images:
        raise ValueError("Train/validation/test leakage: an image or character appears in multiple splits")
    if contradictory_labels:
        raise ValueError("Identical image has conflicting gold answers")
    group_counts = {split: sum(split in found for found in groups.values()) for split in SPLITS}
    if group_counts["train"] < min_train_characters:
        raise ValueError(f"At least {min_train_characters} independent training characters required")
    if not rows["val"] or not rows["test"]:
        raise ValueError("A held-out validation and test split are required")
    if output.resolve() == root or output.resolve() == source.parent:
        raise ValueError("Do not overwrite the image root or source annotation directory")

    # Emit only after every record passes, never a partial validated dataset.
    output.mkdir(parents=True, exist_ok=True)
    for split in SPLITS:
        with (output / f"{split}.jsonl").open("w", encoding="utf-8") as target:
            for item in rows[split]:
                target.write(json.dumps(item, ensure_ascii=False) + "\n")
    summary = {
        "schema": "swrlz-qwen3vl-sft-preflight-v1",
        "baseModel": "Qwen/Qwen3-VL-4B-Instruct",
        "allGoldAnswersHumanVerified": True,
        "sampleCount": {key: len(value) for key, value in rows.items()},
        "characterCount": group_counts,
        "splitByCharacter": True,
        "exactImageHashLeakage": False,
        "note": "These checks do not prove annotation truth or catch visually near-identical crops.",
    }
    (output / "preflight-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--image-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--min-train-characters", type=int, default=3)
    args = parser.parse_args()
    result = prepare(args.annotations, args.image_root, args.output,
                     min_train_characters=args.min_train_characters)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
