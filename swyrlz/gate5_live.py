from __future__ import annotations

import hashlib
import json
import os
import struct
import time
from pathlib import Path

RAW = Path(os.environ.get("SWRLZ_R39_PATH", "/tmp/swrlz-admin/live/SWYRLZ_LALM_R39_PHYSICAL_BASE_REPAIRED.§wyrlzx"))
EXPECTED_RAW_SIZE = 233_637_480
EXPECTED_RAW_SHA256 = "65e4b5d730f66024c44da25aec27730db27aa0019df0df26c0997d17ce58bdee"
INTEGRITY_MAGIC = b"SXI1"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def inspect_r39() -> dict:
    started = time.monotonic()
    if not RAW.is_file():
        raise FileNotFoundError(f"R39_NOT_PRESENT: {RAW}")
    size = RAW.stat().st_size
    digest = sha256_file(RAW)
    if size != EXPECTED_RAW_SIZE or digest != EXPECTED_RAW_SHA256:
        raise ValueError(f"R39_INTEGRITY_FAILED size={size} sha256={digest}")

    with RAW.open("rb") as handle:
        head = handle.read(128)
        tail_size = min(size, 64 * 1024)
        handle.seek(size - tail_size)
        tail = handle.read(tail_size)

    header_magic = head[:8]
    canonical_header = header_magic == b"SWRLZX\r\n"
    rel = tail.find(INTEGRITY_MAGIC)
    integrity = None
    if rel >= 0 and rel + 40 <= len(tail):
        root_digest = tail[rel + 4:rel + 36].hex()
        count = struct.unpack_from("<I", tail, rel + 36)[0]
        p = rel + 40
        ids = []
        for _ in range(count):
            if p + 36 > len(tail):
                break
            ids.append(struct.unpack_from("<I", tail, p)[0])
            p += 36
        integrity = {
            "offset": size - tail_size + rel,
            "rootDigestSha256": root_digest,
            "declaredRecordCount": count,
            "parsedRecordCount": len(ids),
            "sectionIds": ids,
        }

    section_ids = set(integrity["sectionIds"]) if integrity else set()
    required = {str(sid): sid in section_ids for sid in (3, 4, 5)}
    blockers = []
    if not canonical_header:
        blockers.append("CANONICAL_SWRLZX_HEADER_NOT_PRESENT_AT_OFFSET_0")
    if integrity is None:
        blockers.append("SXI1_NOT_FOUND_IN_FINAL_64K")
    for sid, present in required.items():
        if not present:
            blockers.append(f"SECTION_{sid}_NOT_REGISTERED")
    blockers.append("SECTION_PAYLOAD_LOCATION_AND_INFERENCE_WIRING_PENDING")

    return {
        "ok": True,
        "stage": "gate5-r39-local-readiness",
        "modelPath": str(RAW),
        "rawSize": size,
        "rawSha256": digest,
        "containerVerified": True,
        "canonicalHeaderPresent": canonical_header,
        "headerMagicHex": header_magic.hex(),
        "integrity": integrity,
        "requiredSectionsRegistered": required,
        "oneTokenReady": False,
        "interactiveReady": False,
        "blockers": blockers,
        "bytesInspectedAfterHash": len(head) + min(size, 64 * 1024),
        "inspectionMs": int((time.monotonic() - started) * 1000),
    }


if __name__ == "__main__":
    try:
        print(json.dumps(inspect_r39(), ensure_ascii=False, indent=2))
    except Exception as exc:
        print(json.dumps({"ok": False, "error": f"{type(exc).__name__}: {exc}"}, ensure_ascii=False, indent=2))
        raise
