"""Lightweight, evidence-backed §C code-quality policy and HTML diagnostics.

No model calls, source execution, network, user state or external dependencies.
Diagnostics deliberately separate definite syntax/logic defects from potential
performance and cross-device problems; warnings never reject a candidate.
"""
from __future__ import annotations

import re
from typing import Any

VERSION = "swrlz-html-code-quality-v1"


def _is_web_task(prompt: str, programming: dict[str, Any]) -> bool:
    p = str(prompt or "").lower()
    if re.search(r"\b(html|css|javascript|webpage|web page|website|web site|canvas)\b", p):
        return True
    contract = programming.get("intentContract") or {}
    language = contract.get("languageContract") or {}
    tags = [programming.get("artifactType"), contract.get("artifactType"),
            language.get("artifactType"), language.get("language")]
    return any(str(t or "").lower() in {"html", "web-page", "webpage", "website"}
               for t in tags)


def quality_guidance(prompt: str, programming: dict[str, Any] | None) -> str:
    """Short model-side guidance, scoped to coding requests, not casual chat."""
    coding = programming if isinstance(programming, dict) else {}
    if not coding.get("codingTask"):
        return ""
    change = str(coding.get("changeClass") or "").lower()
    existing = coding.get("projectContext") == "existing"
    mode = ("Existing-source edit: inspect and preserve the supplied implementation, "
            "project identity, working interactions and filenames. Make focused "
            "changes rather than replacing the project; a rewrite requires a "
            "demonstrable technical need. " if existing or change in
            {"feature", "bugfix", "fix", "refine", "improve", "extend"}
            else "New creation: match the requested scope; avoid speculative scaffolding. ")
    baseline = ("All advertised controls must work; avoid fake destinations. "
                "Check variable references, complete output, event lifecycle, "
                "and edge cases. Never claim tests ran without a real receipt. ")
    if not _is_web_task(prompt, coding):
        return "\nCODE QUALITY: " + mode + baseline
    return ("\nWEB CODE QUALITY: " + mode + baseline +
            "Use responsive layouts and keyboard/focus support. For canvas or "
            "pointer-driven interactions, prefer Pointer Events so touch, mouse "
            "and pen work without assuming a device. Avoid unbounded per-frame "
            "allocations, repeated expensive blur/shadow work and accidental "
            "quadratic loops; choose explicit performance budgets. Keep tap, "
            "press/hold and drag semantics distinct where appropriate. Validate "
            "CSS color syntax and JS scope; preserve known-good behaviors. ")


def diagnose_html_candidate(source: str) -> dict[str, Any]:
    """No execution. Only high-confidence findings block acceptance."""
    source = str(source or "")
    is_html = bool(re.search(r"<\s*(?:!doctype\s+html|html|canvas|script)\b", source, re.I))
    if not is_html:
        return {"blocking": [], "warnings": [], "inspected": False}
    blocking: list[str] = []
    warnings: list[str] = []
    # CSS does not accept hex notation inside rgba()/rgb() comma arguments.
    if re.search(r"\brgba?\s*\(\s*#[0-9a-fA-F]{3,8}\s*,", source):
        blocking.append("invalid-css-rgb-hex: rgb()/rgba() must not use comma-separated #hex")
    # A template interpolation is invalid when every configured color is hex:
    # hexadecimal CSS colors cannot be passed as comma-separated rgba args.
    configured_colors = re.findall(r"\bcolor\s*:\s*['\"]([^'\"]+)['\"]", source)
    if (configured_colors
            and all(re.fullmatch(r"#[0-9a-fA-F]{3,8}", c) for c in configured_colors)
            and re.search(r"\brgba?\s*\(\s*\$\{\s*(?:config|this\.config)\.color\s*\}\s*,", source)):
        blocking.append("interpolated-hex-rgba: convert the hex color to RGB before rgba()")

    # Only flag this narrowly proven class of state typo (not arbitrary identifiers).
    if (re.search(r"this\.isPaused\s*=\s*!\s*this\.isPaused", source)
            and re.search(r"\blogSystem\s*\(\s*isPaused\s*\?", source)
            and not re.search(r"\b(?:let|const|var)\s+isPaused\b", source)):
        blocking.append("unbound-pause-state: use this.isPaused in the status expression")
    # Warnings are valuable guidance, not proof that a particular phone is slow.
    if (re.search(r"(?:addEventListener\s*\(\s*['\"]mousemove|onmousemove\s*=)", source)
            and re.search(r"<\s*canvas\b", source, re.I)
            and not re.search(r"(?:pointermove|touchmove)", source, re.I)):
        warnings.append("mouse-only-canvas: support pointer input for touch/pen and mouse")
    if re.search(r"\.shadowBlur\s*=", source) and re.search(r"\.arc\s*\(", source):
        warnings.append("canvas-shadow-blur: profile glow work and cache reusable sprites")
    if (re.search(r"for\s*\([^;]*\b(?:j|k)\s*=\s*(?:i\s*\+\s*1|0)", source)
            and "particles" in source):
        warnings.append("particle-pair-loop: consider spatial indexing and draw budgets")
    if "backdrop-filter" in source and re.search(r"<\s*canvas\b", source, re.I):
        warnings.append("animated-backdrop-blur: profile translucent UI over canvas")
    return {"blocking": blocking, "warnings": warnings, "inspected": True}


def extend_candidate_check(base: dict[str, Any], source: str) -> dict[str, Any]:
    """Keep the existing validator authoritative and add definite HTML defects."""
    if not isinstance(base, dict):
        return base
    findings = diagnose_html_candidate(source)
    if not findings["blocking"]:
        return base
    next_check = dict(base)
    previous = next_check.get("reasons") or []
    if not isinstance(previous, list):
        previous = [str(previous)]
    next_check["reasons"] = previous + [r for r in findings["blocking"] if r not in previous]
    next_check["status"] = "REJECT"
    return next_check
