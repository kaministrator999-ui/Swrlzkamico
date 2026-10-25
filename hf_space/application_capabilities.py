"""Small application contracts and conservative source evidence, never runtime proof.

A named editor must provide editing interactions. This checker rejects obvious
render-only drafts; its PASS remains subject to independent browser acceptance.
It does not execute generated code or prescribe a library/implementation.
"""
from __future__ import annotations

from html.parser import HTMLParser
import re
from typing import Any

_PREFIX = "3D scene editor prototype: "
_ACTIONS = {
    "create": r"(?:add(?:ing)?|creat(?:e|ing)|spawn(?:ing)?)",
    "select": r"select(?:ing|ion)?",
    "delete": r"(?:delet(?:e|ing|ion)|remov(?:e|ing|al))",
    "transform": r"(?:transform(?:ing|ation)?|mov(?:e|ing)|translat(?:e|ing|ion)|rotat(?:e|ing|ion)|scal(?:e|ing))",
}
_MODES = {"translate": r"(?:mov(?:e|ing)|translat(?:e|ing|ion))",
          "rotate": r"rotat(?:e|ing|ion)", "scale": r"scal(?:e|ing)"}


def infer_application_capabilities(prompt: str) -> dict[str, Any] | None:
    """Derive a bounded scene-editor default, allowing explicit narrower scope."""
    text = str(prompt or "")
    if not (re.search(r"\b(?:3[ -]?d|three-dimensional|model|scene|mesh|modeling|modelling)\b", text, re.I)
            and re.search(r"\b(?:editor|editing|edit(?:able)?\s+(?:3[ -]?d\s+)?(?:models?|meshes|objects|scenes?))\b", text, re.I)):
        return None
    if re.search(r"\b(?:language|machine.learning|weights?|neural)\s+model\b", text, re.I):
        return None
    required = ["create", "select", "transform", "delete"]
    modes = ["translate", "rotate", "scale"]
    narrowed = False
    # 'Only move/scale/selection' narrows capabilities; 'only HTML/buttons' does
    # not. Scope words must be immediately adjacent to the capability phrase.
    only = re.search(r"\b(?:only\s+(?:allow\s+|support\s+|for\s+)?|(?:support|allow)\s+only\s+)([^.;\n]{1,110})", text, re.I)
    if only is None:
        only = re.search(r"\b((?:object\s+)?(?:" + "|".join(_ACTIONS.values()) + r"))\s+only\b", text, re.I)
    if only:
        phrase = re.split(r"\b(?:using|with|in|but)\b", only.group(1), maxsplit=1, flags=re.I)[0]
        if re.match(r"\s*(?:object\s+)?(?:" + "|".join(_ACTIONS.values()) + r")\b", phrase, re.I):
            requested = [key for key, pattern in _ACTIONS.items() if re.search(r"\b"+pattern+r"\b", phrase, re.I)]
            required = [key for key in required if key in requested or (key == "select" and requested)]
            explicit_modes = [key for key, pattern in _MODES.items() if re.search(r"\b"+pattern+r"\b", phrase, re.I)]
            if explicit_modes:
                modes = explicit_modes
            narrowed = True
    negative_actions = {**_ACTIONS, "transform": r"transform(?:ing|ation)?s?"}
    operation_word = "|".join(negative_actions.values())
    negative_prefix = r"\b(?:no|without|disable|exclude|do not (?:allow|support)|don't (?:allow|support))\s+"
    preceding_operations = r"(?:(?:"+operation_word+r")\s*(?:objects?\s*)?(?:[,/]\s*|(?:or|and)\s*)){0,3}"
    for key, pattern in negative_actions.items():
        if re.search(negative_prefix+preceding_operations+r"(?:object\s+)?"+pattern+r"\b", text, re.I):
            required = [item for item in required if item != key]
            narrowed = True
    for key, pattern in _MODES.items():
        if re.search(r"\b(?:no|without|disable|exclude)\s+"+pattern+r"\b", text, re.I):
            modes = [item for item in modes if item != key]
            narrowed = True
    if "transform" not in required:
        modes = []
    return {"kind": "3d-scene-editor", "required": required, "transformModes": modes,
            "scope": "explicit-narrowing" if narrowed else "prototype-default"}


def apply_application_contract(contract: dict[str, Any], prompt: str) -> dict[str, Any]:
    capabilities = infer_application_capabilities(prompt)
    if capabilities is None and (contract.get("applicationCapabilities") or {}).get("kind") == "3d-scene-editor":
        scoped = infer_application_capabilities("3D scene editor; " + str(prompt or ""))
        if scoped and scoped.get("scope") == "explicit-narrowing":
            capabilities = scoped
    if capabilities is None:
        return contract
    result = dict(contract)
    result["applicationCapabilities"] = capabilities
    operations = ", ".join(capabilities["required"]) or "the explicitly requested interactions"
    if capabilities["transformModes"]:
        operations += " (" + ", ".join(capabilities["transformModes"]) + " on the selected scene object)"
    requirement = _PREFIX + "implement reachable user controls for " + operations + ". A rendered object or camera orbit alone is insufficient."
    # First position survives the existing compact repair-context requirement
    # bound; a narrower follow-up replaces the previous derived default.
    result["must"] = [requirement] + [str(item) for item in contract.get("must", []) if not str(item).startswith(_PREFIX)]
    return result


def _lexical_mask(source: str, *, strings: bool) -> str:
    # Preserve offsets/newlines while hiding comments and optionally literals.
    token = re.compile(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|`(?:\\.|[^`\\])*`')
    def replace(match):
        value = match.group()
        if value.startswith(("//", "/*")) or strings:
            return "".join("\n" if char == "\n" else " " for char in value)
        return value
    return token.sub(replace, source)


def _balanced_end(mask: str, start: int, opening: str = "{", closing: str = "}") -> int:
    depth = 0
    for index in range(start, len(mask)):
        if mask[index] == opening:
            depth += 1
        elif mask[index] == closing:
            depth -= 1
            if not depth:
                return index + 1
    return len(mask)


def _interactive_source(scripts: str, inline_handlers: list[str]) -> str:
    """Collect actual input handlers and statically referenced local functions.

    This is bounded source evidence. It deliberately excludes animation, resize,
    renderer-control change notifications and unrelated global initialization.
    """
    mask = _lexical_mask(scripts, strings=True)
    functions: dict[str, str] = {}
    patterns = (
        r"\bfunction\s+([\w$]+)\s*\([^)]*\)\s*\{",
        r"\b([\w$]+)\s*=\s*(?:async\s+)?(?:\([^)]*\)|[\w$]+)\s*=>\s*\{",
        r"\b([\w$]+)\s*\([^)]*\)\s*\{",
    )
    for pattern in patterns:
        for match in re.finditer(pattern, mask):
            if match.group(1) in ("if", "for", "while", "switch", "catch", "function"):
                continue
            start = match.end() - 1
            functions[match.group(1)] = scripts[start:_balanced_end(mask, start)]
    handlers = list(inline_handlers)
    clean = _lexical_mask(scripts, strings=False)
    event = r"(?:click|dblclick|pointer(?:down|up|move)|mouse(?:down|up|move)|touch(?:start|end|move)|key(?:down|up)|input|change|submit)"
    listener = re.compile(r"\.addEventListener\s*\(\s*(['\"])"+event+r"\1\s*,", re.I)
    for match in listener.finditer(clean):
        # Exclude TransformControls/OrbitControls 'change' rendering callbacks.
        before = clean[max(0, match.start()-80):match.start()]
        if re.search(r"(?:transformControls?|orbitControls?|controls)\s*$", before, re.I) and re.search(r"['\"]change['\"]", match.group(), re.I):
            continue
        start = match.end()
        paren = clean.rfind("(", match.start(), match.end())
        end = _balanced_end(mask, paren, "(", ")")
        handlers.append(scripts[start:end])
    for match in re.finditer(r"\.on(?:click|pointerdown|mousedown|touchstart|keydown|input|change|submit)\s*=", mask, re.I):
        start = match.end()
        brace = mask.find("{", start, start+180)
        semicolon = mask.find(";", start)
        if brace >= 0 and (semicolon < 0 or brace < semicolon):
            handlers.append(scripts[start:_balanced_end(mask, brace)])
        else:
            handlers.append(scripts[start:semicolon if semicolon >= 0 else len(scripts)])
    collected = list(handlers)
    seen: set[str] = set()
    for _ in range(8):
        names = set(re.findall(r"\b([\w$]+)\s*(?:\(|(?=[,;)\s]))", "\n".join(collected)))
        todo = (names & functions.keys()) - seen
        if not todo:
            break
        seen.update(todo)
        collected.extend(functions[name] for name in todo)
    return _lexical_mask("\n".join(collected), strings=False)


class _PageSource(HTMLParser):
    def __init__(self):
        super().__init__(); self.script = False; self.scripts: list[str] = []; self.handlers: list[str] = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script":
            self.script = str(attrs.get("type") or "").lower() in ("", "module", "text/javascript", "application/javascript")
        for key, value in attrs.items():
            if re.fullmatch(r"on(?:click|input|change|pointerdown|mousedown|touchstart|keydown|submit)", key, re.I) and value:
                self.handlers.append(value)
    def handle_data(self, data):
        if self.script:
            self.scripts.append(data)
    def handle_endtag(self, tag):
        if tag == "script": self.script = False


def application_source_gaps(text: str, contract: dict[str, Any]) -> list[str]:
    """Reject clearly missing scene editor source operations, not prove execution."""
    capabilities = contract.get("applicationCapabilities") or {}
    if capabilities.get("kind") != "3d-scene-editor":
        return []
    from project_archive import ProjectArchiveError, parse_project_files
    try:
        files = parse_project_files(text)
    except ProjectArchiveError:
        return []  # Other source gates report the precise parse failure.
    scripts, handlers, markup = [], [], []
    for item in files:
        path, language, content = str(item["path"]).lower(), str(item.get("language") or "").lower(), str(item["content"])
        if path.endswith((".html", ".htm")) or language in ("html", "html5"):
            page = _PageSource(); page.feed(content)
            scripts.extend(page.scripts); handlers.extend(page.handlers); markup.append(content)
        elif path.endswith((".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx")) or language in ("js", "javascript", "typescript"):
            scripts.append(content)
    if not files and str(text).lstrip().startswith("<"):
        page = _PageSource(); page.feed(text); scripts.extend(page.scripts); handlers.extend(page.handlers); markup.append(text)
    source = _lexical_mask("\n".join(scripts), strings=False)
    active = _interactive_source(source, handlers)
    code = _lexical_mask(active, strings=True)
    # Ignore DOM class toggles: they do not create/remove scene objects.
    operations = re.sub(r"\b[\w$]+\.classList\.(?:add|remove)\s*\([^)]*\)", "", code)
    present = {
        "create": bool(re.search(r"\.(?:add|push|spawn|addMesh|addObject|createObject|createMesh|instantiate)\s*\(", operations)),
        "select": bool(re.search(r"\b(?:selected\w*|selection|activeObject|activeMesh)\s*=|\.(?:attach|select|selectObject|setSelected|setSelection)\s*\(", operations, re.I)),
        "delete": bool(re.search(r"\.(?:remove|splice|delete|removeMesh|removeObject|deleteObject|dispose)\s*\(", operations)),
    }
    attached = bool(re.search(r"\.attach\s*\(\s*[^)\s]+", _lexical_mask(source, strings=True)))
    mode_switch = bool(re.search(r"\.setMode\s*\(", code))
    mode_text = source + "\n" + "\n".join(markup)
    transform = {}
    for mode, prop in (("translate", "position"), ("rotate", "rotation"), ("scale", "scale")):
        direct = bool(re.search(r"\."+prop+r"(?:\s*\[[^\]]+\]|\s*\.[\w$]+)*\s*(?:[+*/-]?=|\+\+|--)|\."+prop+r"\s*\.\s*(?:set|copy|setScalar|fromArray)\s*\(|\.(?:set"+prop.title()+r"|"+mode+r")\s*\(", code))
        gizmo = attached and (mode == "translate" or (mode_switch and re.search(r"['\"]"+mode+r"['\"]", mode_text)))
        transform[mode] = bool(direct or gizmo)
    present["transform"] = all(transform.get(mode, False) for mode in capabilities.get("transformModes") or [])
    gaps = ["missing-editor-source-capability:"+key for key in capabilities.get("required") or [] if not present.get(key, False)]
    if "transform" in (capabilities.get("required") or []):
        gaps.extend("missing-editor-source-transform:"+mode for mode in capabilities.get("transformModes") or [] if not transform.get(mode, False))
    return gaps
