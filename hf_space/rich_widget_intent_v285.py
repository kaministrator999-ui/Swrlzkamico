"""§wyrlz v285: bounded conversational intent -> existing swrlz-widget-v1.

A deliberately small Brain-side interpreter for *explicit* visual requests.
Only literal user-owned measurements/equations/primitive names enter widgets.
No language-model generated numbers, arbitrary code/eval, external reads, or
persistence of presentation decisions. Ordinary dialogue remains ordinary.
"""
from __future__ import annotations
import math
import re
from typing import Any

CONTRACT = "swrlz-widget-v1"
_GRAPH = re.compile(
    r"^(?:(?:can|could|would|will)\s+you\s+)?(?:please\s+)?"
    r"(?:(?:show\s+(?:me\s+)?(?:a\s+|the\s+)?)|(?:display\s+(?:a\s+|the\s+)?))?"
    r"(?:graph|plot|visuali[sz]e)\b|^let['’]s\s+(?:graph|plot)\b", re.I)
_3D = re.compile(
    r"^(?:(?:can|could|would|will)\s+you\s+)?(?:please\s+)?"
    r"(?:show|display|preview|render|visuali[sz]e|rotate)\b", re.I)
_SHAPE = re.compile(r"\b(cube|sphere|torus|pyramid)\b", re.I)
_3D_SPEC = re.compile(r"\b(?:3[\s-]*d|three[\s-]*dimensional|wireframe)\b", re.I)
_ASSET = re.compile(r"\b(?:export|download|obj|glb|gltf|stl|fbx|rigged|game.ready|editable.mesh|blender.file|mesh.file)\b", re.I)
_ASSIGNMENT = re.compile(r"(?:^|[\s;])(?:y|f\s*\(\s*x\s*\))\s*=\s*([^;\n]+)", re.I)
_VALUE = re.compile(r"^([A-Za-z][A-Za-z0-9 _-]{0,30})\s*=\s*(-?(?:\d+(?:\.\d+)?|\.\d+))(?:\s*(%|kg|g|ms|s|mph|km/h|usd|\$|gb|mb|w|watts))?$", re.I)
_ITEM = re.compile(r"^([A-Za-z][A-Za-z0-9 ._'-]{0,48})\s*:\s*(.+)$")
_COMPARISON_HEADER = re.compile(r"^(?:compare|comparison|contrast)\b", re.I)
_PREFERENCE = re.compile(r"^(higher|lower)\s+(?:is\s+)?better\s*:\s*(.+)$", re.I)
_BLOCKED = re.compile(r"\b(?:source code|program|javascript|python|kotlin|repository|github|implementation|write code|fix code|syntax|compiler)\b", re.I)


def _num(s: str) -> float | None:
    try:
        value = float(s)
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) and abs(value) <= 100_000 else None


def _widget(kind: str, title: str, data: dict[str, Any]) -> dict[str, Any]:
    return {"contract": CONTRACT, "kind": kind, "version": 1, "title": title,
            "provider": "User-provided input / local rendering", "data": data}


def _poly(expression: str) -> dict[str, Any] | None:
    """Strict polynomial parser, degree <=3; no executable expression language."""
    text = expression.lower().replace("²", "^2").replace("³", "^3")
    text = text.replace("−", "-").replace("×", "*").replace(" ", "")
    if not text or len(text) > 90:
        return None
    if not re.fullmatch(r"[0-9.x^+*\-]+", text):
        return None
    pieces = re.findall(r"[+-]?[^+-]+", text)
    if not pieces or "".join(pieces) != text:
        return None
    coeff = [0.0, 0.0, 0.0, 0.0]
    for piece in pieces:
        sign = -1 if piece.startswith("-") else 1
        term = piece.lstrip("+-")
        if term.count("x") > 1:
            return None
        if "x" in term:
            match = re.fullmatch(r"(?:(\d+(?:\.\d+)?|\.\d+)\*?)?x(?:\^([0-3]))?", term)
            if not match:
                return None
            power = int(match.group(2)) if match.group(2) is not None else 1
            amount = _num(match.group(1)) if match.group(1) is not None else 1.0
        else:
            if not re.fullmatch(r"(?:\d+(?:\.\d+)?|\.\d+)", term):
                return None
            power = 0
            amount = _num(term)
        if amount is None:
            return None
        coeff[power] += sign * amount
        if not math.isfinite(coeff[power]) or abs(coeff[power]) > 100_000:
            return None
    while len(coeff) > 1 and coeff[-1] == 0:
        coeff.pop()
    return {"type": "polynomial", "coefficients": coeff}


def _sine(expression: str) -> dict[str, Any] | None:
    text = expression.lower().replace("−", "-").replace("×", "*").replace(" ", "")
    if not text or len(text) > 90:
        return None
    # Example: -2sin(3x+0.5)+1, sin(x), sin(-x), 3*sin(x)-4.
    match = re.fullmatch(
        r"(?P<amp>[+-]?(?:(?:\d+(?:\.\d+)?|\.\d+)\*?)?)sin\("
        r"(?P<freq>[+-]?(?:(?:\d+(?:\.\d+)?|\.\d+)\*?)?)x"
        r"(?P<phase>[+-](?:\d+(?:\.\d+)?|\.\d+))?"
        r"\)(?P<offset>[+-](?:\d+(?:\.\d+)?|\.\d+))?", text)
    if not match:
        return None
    def signed_factor(raw: str) -> float | None:
        if raw in ("", "+"):
            return 1.0
        if raw == "-":
            return -1.0
        return _num(raw.rstrip("*"))
    amp = signed_factor(match.group("amp"))
    freq = signed_factor(match.group("freq"))
    phase = _num(match.group("phase") or "0")
    offset = _num(match.group("offset") or "0")
    if None in (amp, freq, phase, offset):
        return None
    return {"type": "sine", "amplitude": amp, "frequency": freq,
            "phase": phase, "offset": offset}


def _equation(expression: str) -> dict[str, Any] | None:
    # Strip only a small fixed set of polite suffixes/trailing sentence punctuation.
    # Unrecognized material still rejects the graph instead of partial parsing.
    expression = str(expression or "").strip()
    expression = re.sub(r"\s+(?:please|for me)\s*[!?.]*$", "", expression, flags=re.I)
    expression = expression.rstrip("!?").strip()
    return _sine(expression) or _poly(expression)


def _last_user_equation(history: list[dict[str, Any]]) -> str:
    """Only an explicit recent user-owned equation; previous assistant guesses are not source."""
    for event in reversed(history[-6:]):
        if not isinstance(event, dict) or event.get("role") != "user":
            continue
        body = str(event.get("text") or event.get("content") or "")
        expressions = _ASSIGNMENT.findall(" " + body[:350])
        if expressions:
            expression = expressions[-1].strip()
            if _equation(expression):
                return "y=" + expression
        # Never search deeper across another intervening user topic.
        if body.strip() and not re.search(r"\b(?:graph|plot|equation|function|math)\b", body, re.I):
            break
    return ""


def _graph_plan(prompt: str, history: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not _GRAPH.search(prompt):
        return None
    candidates = _ASSIGNMENT.findall(" " + prompt[:450])
    if not candidates and re.search(r"\b(?:that|this|it|previous|above)\b", prompt, re.I):
        old = _last_user_equation(history)
        candidates = _ASSIGNMENT.findall(" " + old)
    if not candidates or len(candidates) > 5:
        return None
    series = []
    for expr in candidates:
        parsed = _equation(expr.strip())
        if parsed is None:
            return None
        series.append(parsed)
    domain = [-5.0, 5.0]
    samples = []
    for x_index in range(41):
        x = domain[0] + (domain[1] - domain[0]) * x_index / 40
        for fn in series:
            if fn["type"] == "polynomial":
                y = sum(v * x ** i for i, v in enumerate(fn["coefficients"]))
            else:
                y = fn["offset"] + fn["amplitude"] * math.sin(fn["frequency"] * x + fn["phase"])
            if math.isfinite(y) and abs(y) <= 1_000_000:
                samples.append(y)
    if not samples:
        return None
    low = min(samples + [0.0])
    high = max(samples + [0.0])
    pad = max(1.0, (high - low) * 0.10)
    low = max(-1_000_000.0, low - pad)
    high = min(1_000_000.0, high + pad)
    if high - low < 0.001:
        return None
    return _widget("math-graph", "Equation explorer",
                   {"series": series, "domain": domain, "range": [low, high],
                    "note": "Plotted from the user-supplied equation; axes estimated locally."})


def _shape_plan(prompt: str) -> dict[str, Any] | None:
    if not (_3D.search(prompt) and _3D_SPEC.search(prompt)) or _ASSET.search(prompt):
        return None
    shapes = {m.group(1).lower() for m in _SHAPE.finditer(prompt)}
    if len(shapes) != 1:
        return None
    shape = next(iter(shapes))
    return _widget("model-3d", "3D " + shape.capitalize() + " preview",
                   {"shape": shape, "caption": "Interactive primitive wireframe preview; not an exported or editable mesh."})


def _compare_plan(prompt: str) -> dict[str, Any] | None:
    if not _COMPARISON_HEADER.search(prompt.lstrip()) or len(prompt) > 1200:
        return None
    rows = []
    preferences: dict[str, bool] = {}
    source = prompt.replace("\r", "\n")
    # A colon-delimited row per option; semicolon-delimited rows also accepted.
    for line in re.split(r"[\n;]+", source):
        line = line.strip().lstrip("-• ").strip()
        if not line:
            continue
        if _COMPARISON_HEADER.match(line):
            line = _COMPARISON_HEADER.sub("", line, count=1).strip(" :")
            if not line:
                continue
        pref = _PREFERENCE.fullmatch(line)
        if pref:
            for key in pref.group(2).split(","):
                normalized = key.strip().lower().replace(" ", "_")
                if re.fullmatch(r"[a-z][a-z0-9_-]{0,30}", normalized):
                    preferences[normalized] = pref.group(1).lower() == "higher"
            continue
        pair = _ITEM.fullmatch(line)
        if not pair:
            continue
        name = pair.group(1).strip()
        if name.lower() in ("higher is better", "lower is better"):
            continue
        values = {}
        units = {}
        for term in re.split(r"[,|]+", pair.group(2)):
            match = _VALUE.fullmatch(term.strip())
            if not match:
                # Do not partially interpret rows with unknown/fake measurements.
                values = {}
                break
            key = match.group(1).strip().lower().replace(" ", "_")
            val = _num(match.group(2))
            if val is None or key in values:
                values = {}
                break
            values[key] = val
            units[key] = (match.group(3) or "").strip()
        if values:
            rows.append((name, values, units))
    if not 2 <= len(rows) <= 4 or len({n.lower() for n, _, _ in rows}) != len(rows):
        return None
    common = set(rows[0][1])
    for _, values, _ in rows[1:]:
        common &= set(values)
    if not common or len(common) > 6:
        return None
    keys = [key for key in rows[0][1] if key in common]
    metrics = []
    for key in keys:
        unit_set = {units.get(key, "").casefold() for _, _, units in rows}
        if len(unit_set) != 1:
            return None
        preference = preferences.get(key)
        metrics.append({"key": key, "label": key.replace("_", " ").title(),
                        "unit": next(iter(unit_set)), "higherIsBetter": preference})
    items = [{"name": name, "values": {key: values[key] for key in keys}}
             for name, values, _ in rows]
    return _widget("comparison", "Comparison of supplied measurements",
                   {"metrics": metrics, "items": items,
                    "note": "Values are transcribed from this message; no external facts or performance benchmarks are inferred."})


def plan_conversation_widget(prompt: str, history: list[dict[str, Any]] | None = None,
                             programming: dict[str, Any] | None = None,
                             online_requested: bool = False) -> dict[str, Any] | None:
    """Make at most one narrow presentation plan, with no side effects.

    The caller owns routing, model generation and Station event emission.
    """
    prompt = str(prompt or "").strip()
    if not prompt or len(prompt) > 1200 or online_requested:
        return None
    if bool((programming or {}).get("codingTask")) or _BLOCKED.search(prompt):
        return None
    history = history if isinstance(history, list) else []
    widget = (_graph_plan(prompt, history)
              or _shape_plan(prompt)
              or _compare_plan(prompt))
    if widget is None:
        return None
    kind = widget["kind"]
    if kind == "comparison":
        count = len(widget["data"]["items"])
        detail = f"A comparison display has {count} user-supplied items with explicit measurements. Do not imply the figures were externally verified. Do not invent missing metrics or scores."
    elif kind == "math-graph":
        detail = "An interactive graph is being displayed from the user's exact equation. Discuss the curve naturally, do not claim the graph was rendered externally or invent calculated datapoints."
    else:
        detail = "An interactive 3D wireframe primitive preview is being displayed; this is not an editable or downloadable 3D mesh. Do not claim an asset was created or exported."
    return {"widget": widget, "presentationHint": detail, "source": "explicit-user-input",
            "kind": kind}
