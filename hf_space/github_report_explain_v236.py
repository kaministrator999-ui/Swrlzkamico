"""Evidence-only explanation of a user-pasted GitHub scope report.

This is deliberately a parser of *supplied* data, not a GitHub verification
or model authority. Never treat repository comments/report prose as instructions.
"""
from __future__ import annotations
import re

_PATH = re.compile(r"^[A-Za-z0-9_§.+/-]{1,220}$")
_USER_REPORT = re.compile(
    r"(?im)^#{1,2} GitHub (?:source analysis|source report)\s*·\s*([^\r\n]+)$")
_NUMBER = re.compile(r"(?i)(?:Content inspected|Source contents inspected):\s*(\d+)/(\d+)")


def is_report_request(prompt):
    raw = str(prompt or "")
    first = raw.split("\n", 1)[0].casefold()
    return (len(raw) <= 65000 and "\n" in raw and
            first.startswith(("using only the verified github source report",
                              "explain the verified github source report",
                              "using this github source analysis")) and
            _USER_REPORT.search(raw) is not None)


def _safe(value, limit=180):
    return " ".join(re.sub(r"[\x00-\x1f<>\x7f`|]", " ", str(value or "")).split())[:limit]


def explain_supplied_report(prompt):
    """No invented file names, fake retrieval claims, or report instructions."""
    if not is_report_request(prompt):
        return None
    raw = str(prompt)
    match = _USER_REPORT.search(raw)
    repo = _safe(match[1], 140)
    inspected = []
    in_reviewed = False
    for line in raw[match.end():].splitlines():
        if re.match(r"^## (?:Reviewed source files|Inspected files)\s*$", line):
            in_reviewed = True
            continue
        if not in_reviewed:
            continue
        if re.match(r"^## [^#]", line) and inspected:
            break
        m = re.match(r"^###\s+([^\n]+?)\s*$", line)
        if m:
            path = m[1].strip()
        else:
            m = re.match(r"^-\s+([^\s(]+)\s+\(", line)
            path = m[1].strip() if m else ""
        if path and _PATH.fullmatch(path) and path not in inspected and len(inspected) < 30:
            inspected.append(path)
    count = _NUMBER.search(raw)
    described = int(count[1]) if count else len(inspected)
    total = int(count[2]) if count else None
    if total is not None and described > total:
        described = 0
    branch = re.search(r"(?im)^Branch:\s*([^\r\n]+)$", raw)
    scoped = re.search(r"(?im)^Scopes:\s*([^\r\n]+)$", raw)
    lines = ["## Explanation of the supplied GitHub source report",
             "The supplied report identifies repository `" + repo + "`." if repo else
             "This is a user-supplied report, not a fresh GitHub retrieval."]
    if branch:
        lines.append("**Claimed source snapshot:** " + _safe(branch[1], 170))
    if scoped:
        lines.append("**Reported scope:** " + _safe(scoped[1], 170))
    lines.append("**Reported source coverage:** " + str(described) +
                 ("/" + str(total) if total is not None else "") + " files inspected.")
    if inspected:
        lines += ["", "**Files actually listed as inspected in this report:**"]
        lines += ["- `" + path + "`" for path in inspected]
    else:
        lines.append("No reliable inspected-file entries were identified in the supplied text.")
    if len(inspected) == 1:
        lines.append("The only evidenced component here is `" + inspected[0] +
                     "`. The report alone does not establish implementation roles for any other files.")
    else:
        lines.append("File-to-file responsibilities or relationships require inspected source "
                     "symbols/imports for the named files; filenames alone are insufficient.")
    lines += ["", "**Evidence gaps:** A tree inventory is not a full source audit; "
              "only inspected-file entries count as inspected. A path mentioned elsewhere "
              "in the report is not proof its contents were read. Source relationships, "
              "runtime behavior, deployment status, and file modification timestamps "
              "must be established separately.",
              "", "This explanation uses **supplied report text**, not a new authenticated "
              "GitHub read. Embedded repository instructions were treated as data."]
    return "\n".join(lines)
