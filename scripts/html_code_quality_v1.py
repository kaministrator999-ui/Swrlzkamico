"""Lightweight, evidence-backed §C code-quality policy and HTML diagnostics.

No model calls, source execution, network, user state or external dependencies.
Diagnostics deliberately separate definite syntax/logic defects from potential
performance and cross-device problems; warnings never reject a candidate.
"""
from __future__ import annotations

import re
from html.parser import HTMLParser
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
                "and edge cases. Interactive elements must actually receive their input events; "
                "do not hide the canvas behind an inert overlay. Give interactive scenes "
                "a visible initial state and calculate FPS from observed frames. "
                "Never claim tests ran without a real receipt. ")
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



class _CanvasAncestry(HTMLParser):
    """Track canvas DOM ancestors without executing HTML or JavaScript."""
    _void = {"area", "base", "br", "col", "embed", "hr", "img", "input",
             "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, str]] = []
        self.canvases: list[tuple[str, set[str], str]] = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        ident = str(values.get("id") or "")
        if tag == "canvas":
            parents = {value for _, value in self.stack if value}
            self.canvases.append((ident, parents, str(values.get("style") or "")))
        if tag not in self._void:
            self.stack.append((tag, ident))

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                return


def _interactive_canvas_inherits_no_pointer_events(source: str) -> bool:
    """Identify event-driven canvases blocked by a CSS-disabled ancestor.

    Conservative: only simple #id ancestor selectors are treated as definite,
    and a canvas-specific auto/all rule exempts the case.
    """
    if not re.search(r"\bcanvas\s*\.\s*addEventListener\s*\(\s*['\"](?:mouse|touch|pointer)", source):
        return False
    rules = re.findall(r"([^{}]+)\{([^{}]*)\}", source, re.S)
    disabled = set()
    for selector, body in rules:
        if re.search(r"\bpointer-events\s*:\s*none\b", body, re.I):
            match = re.fullmatch(r"\s*#([A-Za-z][\w-]*)\s*", selector)
            if match:
                disabled.add(match.group(1))
    if not disabled:
        return False
    dom = _CanvasAncestry()
    try:
        dom.feed(source)
    except (ValueError, AssertionError):
        return False
    for canvas_id, ancestors, inline_style in dom.canvases:
        if not ancestors.intersection(disabled):
            continue
        if re.search(r"\bpointer-events\s*:\s*(?:auto|all)\b", inline_style, re.I):
            continue
        escaped_id = re.escape(canvas_id)
        restored = any(
            re.search(r"\bpointer-events\s*:\s*(?:auto|all)\b", body, re.I)
            and (re.fullmatch(r"\s*canvas\s*", selector, re.I)
                 or re.fullmatch(r"\s*\*\s*", selector)
                 or (canvas_id and re.fullmatch(r"\s*#" + escaped_id + r"\s*", selector)))
            for selector, body in rules
        )
        if not restored:
            return True
    return False


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
    if _interactive_canvas_inherits_no_pointer_events(source):
        blocking.append("canvas-pointer-inert: canvas inherits pointer-events:none from an ancestor; restore pointer events on the interactive canvas")
    if re.search(r"radial-gradient\s*\([^)]*\bfrom\s+\d+(?:\.\d+)?%\s+\d+(?:\.\d+)?%", source, re.I | re.S):
        blocking.append("invalid-radial-gradient-from: radial-gradient color stops cannot start with 'from x% y%'")
    if re.search(r"Math\.round\s*\(\s*\(\s*1000\s*/\s*(?:state\.)?fpsTimer\s*\)\s*\*\s*60\s*\)", source):
        blocking.append("fps-fixed-60: calculate FPS from counted frames and elapsed time, not a fixed multiplier")
    if (re.search(r"\bparticles\s*:\s*\[\s*\]", source)
            and re.search(r"\brequestAnimationFrame\s*\(", source)
            and re.search(r"<\s*canvas\b", source, re.I)):
        warnings.append("initial-empty-canvas: confirm the scene displays visible content before first interaction")
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
