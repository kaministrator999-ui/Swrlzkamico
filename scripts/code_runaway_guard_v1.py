"""Deterministic guard for repetitious, unverified code candidates.

Do not mutate validated projects or unrelated text. This only removes
adjacent exact duplicate single-line CSS rules after clear repetition.
"""
from __future__ import annotations

import re

_CSS_RULE = re.compile(r"^[ \t]*(\.[A-Za-z_][A-Za-z0-9_-]*)[ \t]*\{[^{}\r\n]{1,300}\}[ \t]*(?:\r?\n)?$")


def collapse_repeated_css_rules(source: str, *, min_run: int = 10):
    """Return (cleaned source, correction evidence or None).

    Only compress an uninterrupted run of >=10 single-line rules for the
    same class selector with <=6 distinct rule bodies and >=7 duplicates.
    Preserve one exact instance of each distinct declaration, and preserve
    all other lines and byte order. Never describe this as compile-verified.
    """
    if not source:
        return source, None
    lines = source.splitlines(keepends=True)
    kept = []
    removed = 0
    selectors = []
    i = 0
    while i < len(lines):
        first = _CSS_RULE.fullmatch(lines[i])
        if not first:
            kept.append(lines[i])
            i += 1
            continue
        selector = first.group(1)
        j = i + 1
        while j < len(lines):
            m = _CSS_RULE.fullmatch(lines[j])
            if not m or m.group(1) != selector:
                break
            j += 1
        run = lines[i:j]
        if len(run) >= min_run:
            seen = set()
            unique = []
            for line in run:
                key = line.rstrip("\r\n").strip()
                if key not in seen:
                    seen.add(key)
                    unique.append(line)
            duplicates = len(run) - len(unique)
            if len(unique) <= 6 and duplicates >= max(7, min_run - 3):
                kept.extend(unique)
                removed += duplicates
                selectors.append(selector)
            else:
                kept.extend(run)
        else:
            kept.extend(run)
        i = j
    if not removed:
        return source, None
    return "".join(kept), {
        "removedRuleLines": removed, "selectors": selectors[:8],
        "verification": "UNVERIFIED_SOURCE_CLEANUP",
    }
