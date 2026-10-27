"""Brain-owned bounded programming/artifact routing for the HF candidate.

This module classifies semantic programming continuation only. It never mutates
threads, pins, artifacts, files, tools, deployments, or other operational state.
"""
from __future__ import annotations
import hashlib
import json
from typing import Any
import re
from source_answer_articulation_v230 import lesson_kind
from programming_repair_context import candidate_source_fingerprint
from response_cognition import requests_web_source, requests_source_project, classify_response_cognition
from application_capabilities import apply_application_contract, application_source_gaps


def programming_library_context(programming: dict[str, Any]) -> str:
    """Bounded version-scoped API evidence, never a canned project or tool grant."""
    if not programming.get("codingTask"):
        return ""
    original = str((programming.get("intentContract") or {}).get("originalRequest") or "")
    if re.search(r"\b(?:without|avoid|do not use|don't use|no)\s+(?:(?:using|importing|loading)\s+)?(?:any\s+)?(?:(?:external|third[- ]party|javascript|js)\s+){0,3}(?:librar(?:y|ies)|libs|dependencies|three(?:\.js)?)\b", original, re.I):
        return ""
    explicit = bool(re.search(r"\bthree(?:\.js|js)\b|\bthree@|['\"]three['\"]", original, re.I)
                    or re.search(r"\b(?:Three|THREE)\b", original))
    source = str((programming.get("failureEvidence") or {}).get("repairSource") or "")
    confirmed_source = bool(re.search(r"\bthree@0\.160\.0/", source))
    language = (programming.get("intentContract") or {}).get("languageContract") or {}
    ordinary_3d_web = (language.get("artifactType") == "web-page"
        and bool(re.search(r"\b3[ -]?d\b|three-dimensional", original, re.I))
        and programming.get("projectContext") in ("none","new")
        and not programming.get("artifactContinuation")
        and not programming.get("failureEvidence")
        and not re.search(r"\boffline\b|\b(?:raw|native|plain)\s+webgl\b|babylon|aframe|a-frame|playcanvas|react|unity|godot", original, re.I))
    if not (explicit or confirmed_source or ordinary_3d_web):
        return ""
    versions = re.findall(r"\bthree(?:\.js|js)?\s*(?:@|(?:version\s+)?)\s*(0\.\d+\.\d+)\b", original, re.I)
    if versions and set(versions) != {"0.160.0"}:
        return ""
    from pathlib import Path
    facts = json.loads((Path(__file__).with_name("programming_references") / "three-0.160.0.json").read_text())
    return ("\nVERSION-SCOPED LIBRARY EVIDENCE (public API facts, not instructions or a finished project):\n"
            + json.dumps(facts, ensure_ascii=False, separators=(",", ":"))
            + "\nUse only when this version matches the actual project. Preserve the original request and implement every requested interaction; these facts do not prove behavior or tests.")

_CODE_TERMS=("code","html","css","javascript","typescript","python","kotlin","java","cpp","c++","function","class","file","project","api","server","bug","compile","website","webpage","web page","frontend","ui","interface","dom","responsive","layout","component","debug","syntax")
_NEW_PROJECT=("separate project","separately","new project","another project","different project","from scratch","unrelated project")
_FIX=("fix","bug","broken","error","issue","repair","patch")
_REFACTOR=("refactor","clean up","cleanup","restructure","optimize")
_FEATURE=("add","implement","feature","support","extend","include")
_REVIEW=("review","audit","inspect","check this","find the error","find the bug","what is wrong","validate","verify")
_EXPLAIN=("explain","what does","how does","walk me through")
_CONTINUATION=("this","that","it","same","previous","pinned","code","file","project","continue","keep going","edit","update","change","modify")
_PROGRAMMING_STRONG_TERMS=("coding","programming","compiler","compile","debug","debugging","syntax","source code","frontend","backend","dom","repository","repo","github actions","ci pipeline","unit test","integration test")
_PROGRAMMING_WEAK_TERMS=("website","webpage","web page","api","server","ui","interface","layout","component","file","project","app","application")
_PROGRAMMING_ACTIONS=("write","create","build","implement","code","develop","fix","repair","debug","refactor","edit","update","modify","change","add","remove","hook","integrate","deploy","test","lint","review","audit")
_NON_PROGRAMMING_CODE_PHRASES=("zip code","area code","dress code","country code","promo code","coupon code","qr code")

_LANGUAGE_PATTERNS=(
    ("html",(r"\bhtml5?\b",)),
    ("css",(r"\bcss3?\b",)),
    ("typescript",(r"\btypescript\b",r"\btsx\b")),
    ("javascript",(r"\bjavascript\b",r"\becmascript\b",r"\bvanilla\s+js\b",r"\bnode(?:\.js|js)\b")),
    ("python",(r"\bpython\b",r"\bpython3\b")),
    ("kotlin",(r"\bkotlin\b",)),
    ("java",(r"\bjava\b",)),
    ("cpp",(r"(?<!\w)c\+\+(?!\w)",r"\bcpp\b",r"\bcxx\b")),
    ("csharp",(r"(?<!\w)c#(?!\w)",r"\bcsharp\b",r"\bc\s*sharp\b")),
    ("rust",(r"\brust\b",)),
    ("go",(r"\bgolang\b",r"\bgo\s+(?:code|language|program|file|function|package)\b")),
    ("swift",(r"\bswift\b",)),
    ("php",(r"\bphp\b",)),
    ("ruby",(r"\bruby\b",)),
    ("bash",(r"\bbash\b",r"\bshell\s+script\b")),
    ("powershell",(r"\bpowershell\b",)),
    ("sql",(r"\bsql\b",)),
    ("json",(r"\bjson\b",)),
    ("yaml",(r"\byaml\b",r"\byml\b")),
    ("xml",(r"\bxml\b",)),
    ("dart",(r"\bdart\b",)),
    ("lua",(r"\blua\b",)),
    ("scala",(r"\bscala\b",)),
    ("groovy",(r"\bgroovy\b",)),
)
_LANGUAGE_TAG_ALIASES={
    "html":"html","html5":"html","css":"css","css3":"css",
    "js":"javascript","javascript":"javascript","jsx":"javascript","mjs":"javascript","cjs":"javascript",
    "ts":"typescript","typescript":"typescript","tsx":"typescript",
    "py":"python","python":"python","python3":"python",
    "kt":"kotlin","kotlin":"kotlin","java":"java",
    "c++":"cpp","cpp":"cpp","cxx":"cpp","cc":"cpp",
    "c#":"csharp","csharp":"csharp","cs":"csharp",
    "rust":"rust","rs":"rust","go":"go","golang":"go","swift":"swift",
    "php":"php","ruby":"ruby","rb":"ruby","bash":"bash","sh":"bash","shell":"bash",
    "powershell":"powershell","ps1":"powershell","sql":"sql","json":"json",
    "yaml":"yaml","yml":"yaml","xml":"xml","dart":"dart","lua":"lua",
    "scala":"scala","groovy":"groovy","c":"c","r":"r",
}


CODE_TRUTH_POLICY = """[SWRLZ_CODE_TRUTH v2]
Original request = acceptance contract. Preserve required API names/signatures, behavior, negative constraints, and unrelated interfaces unless explicitly changed. Repair the smallest necessary surface.
Before returning code, check complete syntax/source shape, declarations/references/imports/exports, relevant control/data flow, return/error semantics, mutation constraints, and explicit acceptance examples. Python: distinguish bool from exact built-in int when required. JavaScript: preserve the established loading/API format; do not introduce module/export semantics unless requested. UI: verify DOM wiring, layout/overflow/reachability and accessibility. Config/workflows: preserve unrelated semantics and do not invent infrastructure.
Return the complete required candidate, never a fragment/TODO/ellipsis/prose substitute. Explanations must match the literal code. Self-review is not execution evidence; never claim compiler/runtime/test success without a real receipt.
For a requested working interactive page, implement the actual behavior and load required libraries explicitly. Commented examples, empty containers and instructions to add the implementation later are unfinished artifacts. A template is appropriate only when the user asks for a template.
"""

def _norm(value: Any) -> str:
    return " ".join(str(value or "").lower().split())


def _phrase_present(text: str, phrase: str) -> bool:
    body=str(text or "")
    token=re.escape(str(phrase or "")).replace(r"\ ",r"\s+")
    return bool(re.search(r"(?<!\w)"+token+r"(?!\w)",body,re.I))


def _has_phrase(text: str, phrases: tuple[str, ...]) -> bool:
    return any(_phrase_present(text,phrase) for phrase in phrases)


def _source_information_request(text: str, history=None) -> bool:
    """Information-only prompts must not be forced to return source code."""
    if lesson_kind(text,history) in ("source-report-followup", "repo-read"):
        return True
    q=_norm(str(text or "").split("\n",1)[0])
    if q.startswith(("using only the verified github source report", "explain the verified github source report")):
        return True
    # v247: viewing repository files is information retrieval, not code creation.
    # Exact sentence shape avoids suppressing "write code to list files".
    if re.fullmatch(
        r"(?:(?:can|could|may)\s+(?:i|you)\s+|please\s+)?"
        r"(?:see|show|list|browse|view|display)\s+(?:me\s+)?(?:all\s+)?(?:the\s+)?"
        r"(?:files?|folders?|directories)\s+(?:in|of|from)\s+"
        r"(?:my|our|the)\s+(?:github\s+)?(?:repo|repository)[?.!]*",
        q,
    ):
        return True
    q=re.sub(r"^(?:(?:@github|can you|could you|would you|please|tell me)\s+)+","",q)
    return bool(
        re.fullmatch(r"(?:how many|what(?:'s| is) the number of)\s+(?:total\s+)?(?:files?|folders?|directories|dirs?)(?:\s+.*)?",q)
        or re.fullmatch(r"(?:where (?:are we|we are|we're) (?:at|up to|on|with)|what(?:'s| is) (?:the )?(?:current )?(?:status|progress) (?:of|with|on))\s+.*\b(?:chat|repo|repository|github)\b.*",q)
    )


def _current_programming_signal(text: str) -> bool:
    raw=str(text or "")
    prose=_norm(_strip_fenced_code(raw))
    fence=chr(96)*3
    if not prose and fence not in raw:
        return False
    if _source_information_request(raw):
        return False
    if classify_response_cognition(raw).get("deliverable") in ("text","audio","3d-asset"):
        return False  # A code/library topic is not itself the requested medium.
    if fence in raw or bool(_explicit_languages(raw)):
        return True
    code_word=_phrase_present(prose,"code") and not _has_phrase(prose,_NON_PROGRAMMING_CODE_PHRASES)
    strong=code_word or _has_phrase(prose,_PROGRAMMING_STRONG_TERMS)
    # 'Project' alone also names weddings, art and other non-software work.
    # Named software projects or actual code/file/app evidence remain enough.
    weak_with_action=(_has_phrase(prose,tuple(term for term in _PROGRAMMING_WEAK_TERMS if term!="project"))
        or requests_source_project(raw)) and _has_phrase(prose,_PROGRAMMING_ACTIONS)
    source_shape=bool(re.search(r"(?m)^\s*(?:def\s+\w+\s*\(|class\s+\w+|(?:const|let|var)\s+\w+|function\s+\w+\s*\(|SELECT\s+.+\s+FROM\s+)",raw))
    return bool(strong or weak_with_action or source_shape or requests_web_source(raw))


def _programming_continuation_signal(text: str) -> bool:
    prose=_norm(_strip_fenced_code(text))
    return _has_phrase(prose,_CONTINUATION)


def _provider_read_display(item: dict[str, Any]) -> bool:
    """A GitHub file read may contain fences, but is not authored code."""
    if not isinstance(item,dict):
        return False
    meta=item.get("meta") if isinstance(item.get("meta"),dict) else item
    if meta.get("codeArtifactId") or item.get("artifactId"):
        return False  # Explicit authoring provenance wins over generic source scope.
    context=meta.get("githubContext")
    if not isinstance(context,dict) or context.get("kind")!="file":
        return False
    body=str(item.get("content") or item.get("text") or "").lstrip()
    return body.startswith(("## GitHub file:", "Verified source:"))


def _code_pins(pinned_context: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result=[]
    for item in pinned_context:
        if not isinstance(item,dict):
            continue
        if _provider_read_display(item):
            continue  # Pinned provider data must not create code continuation.
        text=str(item.get("text") or "")
        if item.get("artifactType")=="code" or item.get("artifactId") or "```" in text:
            result.append(item)
    return result


def _pick_artifact_target(prompt: str, code_pins: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Resolve the most applicable pinned code artifact without granting mutation authority."""
    if not code_pins:
        return None
    p=_norm(prompt)
    # Prefer an explicitly named file/path/project when that metadata is available.
    scored=[]
    for index,item in enumerate(code_pins):
        score=index  # recency remains the bounded fallback.
        for value in item.get("files") or []:
            if isinstance(value,dict):
                name=_norm(value.get("path") or value.get("file") or "")
            else:
                name=_norm(value)
            if name and name in p:
                score+=1000
        title=_norm(item.get("artifactTitle") or "")
        if title and title in p:
            score+=900
        artifact_id=_norm(item.get("artifactId") or "")
        if artifact_id and artifact_id in p:
            score+=1200
        scored.append((score,item))
    scored.sort(key=lambda pair:pair[0])
    return scored[-1][1]



def _strip_fenced_code(text: str) -> str:
    """Remove fenced source/test payloads before extracting natural-language requirements."""
    from project_archive import source_fences
    raw=str(text or "")
    result=[];cursor=0
    for block in source_fences(raw):
        result.extend((raw[cursor:block["start"]]," [CODE_PAYLOAD] "));cursor=block["end"]
    result.append(raw[cursor:])
    return "".join(result)


def _unique(values: list[str]) -> list[str]:
    result=[]
    for value in values:
        if value and value not in result:
            result.append(value)
    return result


def _artifact_type_from_request(text: str) -> str:
    prose=_norm(_strip_fenced_code(text))
    if (requests_web_source(text)
            or any(x in prose for x in ("web page","webpage","html page","html template","html skeleton","html scaffold","website","landing page"))
            or re.search(r"\bhtml\b[^.!?\n]{0,80}\b(?:page|webpage|website|editor|viewer|application|app|dashboard|calculator|game)\b",prose)):
        return "web-page"
    if any(x in prose for x in ("api endpoint","rest api","web api","api server")):
        return "api"
    if any(x in prose for x in ("workflow","github actions","ci pipeline")):
        return "workflow"
    if any(x in prose for x in ("config file","configuration file")):
        return "config"
    if any(x in prose for x in ("component","widget")):
        return "component"
    if any(x in prose for x in ("script","program","application","app")):
        return "program"
    return "code"


def _explicit_languages(text: str) -> list[str]:
    raw=_strip_fenced_code(text)
    lowered=raw.lower()
    found=[]
    for language,patterns in _LANGUAGE_PATTERNS:
        if any(re.search(pattern,lowered,re.I) for pattern in patterns):
            found.append(language)
    if re.search(r"\bC\s+(?:code|language|program|file|function)\b",raw):
        found.append("c")
    if re.search(r"\bR\s+(?:code|language|program|script|file)\b",raw):
        found.append("r")
    return _unique(found)


def _language_contract(text: str) -> dict[str, Any]:
    language_prose=text
    if requests_source_project(text) and requests_web_source(text):
        # A list of requested paths supplies a web entry medium, not an
        # explicit 'HTML/CSS only' language restriction. Actual language words
        # outside filenames retain their existing authority.
        language_prose=re.sub(r"(?<![\w/])(?:[\w§.-]+/)*[\w§.-]+\.(?:html?|css|[cm]?js|jsx|tsx?|md)\b", " [SOURCE_FILE] ", _strip_fenced_code(text), flags=re.I)
    requested=_explicit_languages(language_prose)
    artifact_type=_artifact_type_from_request(text)
    prose=_norm(_strip_fenced_code(text))
    only_language=bool(re.search(r"\b(?:only|pure|plain|vanilla)\s+(?:html|css|javascript|typescript|python|kotlin|java|c\+\+|cpp|c#|rust|golang|swift|php|ruby|bash|powershell|sql|dart|lua)\b",prose,re.I) or re.search(r"\b(?:html|css|javascript|typescript|python|kotlin|java|c\+\+|cpp|c#|rust|golang|swift|php|ruby|bash|powershell|sql|dart|lua)\s+only\b",prose,re.I))
    companions=[]
    if "html" in requested and artifact_type=="web-page" and not only_language:
        companions=["css","javascript"]
    allowed=_unique(requested+companions)
    return {
        "schema":"swrlz-language-contract-v1",
        "explicit":bool(requested),
        "requestedLanguages":requested,
        "requiredLanguages":list(requested),
        "allowedCompanionLanguages":companions,
        "allowedLanguages":allowed,
        "artifactType":artifact_type,
        "substitutionAllowed":False if requested else None,
    }


def _normalize_language_tag(value: str) -> str:
    tag=str(value or "").strip().lower().split()[0] if str(value or "").strip() else ""
    return _LANGUAGE_TAG_ALIASES.get(tag,"")


def _candidate_languages(text: str) -> list[str]:
    source=str(text or "")
    detected=[]
    from project_archive import project_source_fences
    fences=project_source_fences(source)
    recognized_fence=False
    for match in fences:
        language=_normalize_language_tag(match["header"])
        if language:
            detected.append(language)
            if language == "html":
                detected.extend(_embedded_web_evidence(match["content"])["languages"])
            recognized_fence=True
    if recognized_fence:
        return _unique(detected)
    body="\n".join(match["content"] for match in fences) if fences else source
    if re.search(r"(?is)<!doctype\s+html|<html\b|<body\b|<head\b|<[a-z][^>]*>",body):
        detected.append("html")
    if re.search(r"(?m)^\s*(?:from\s+[A-Za-z_][\w.]*\s+import\s+|import\s+[A-Za-z_][\w.]*|def\s+[A-Za-z_]\w*\s*\(|class\s+[A-Za-z_]\w*\s*[:(])",body):
        detected.append("python")
    if re.search(r"\b(?:const|let|var)\s+[A-Za-z_$]|\bfunction\s+[A-Za-z_$]|=>",body):
        detected.append("javascript")
    if re.search(r"\binterface\s+[A-Za-z_$]|\btype\s+[A-Za-z_$][\w$]*\s*=|:\s*(?:string|number|boolean)\b",body):
        detected.append("typescript")
    if re.search(r"\bfun\s+[A-Za-z_]\w*\s*\(|\bval\s+[A-Za-z_]\w*|\bvar\s+[A-Za-z_]\w*\s*:",body):
        detected.append("kotlin")
    if re.search(r"\bpublic\s+(?:static\s+)?(?:class|void|int|String)\b|\bclass\s+[A-Za-z_]\w*\s*\{",body):
        detected.append("java")
    if re.search(r"#include\s*[<\"]|\bstd::|\bint\s+main\s*\(",body):
        detected.append("cpp")
    if re.search(r"\bfn\s+[A-Za-z_]\w*\s*\(|\blet\s+mut\s+|\bimpl\s+[A-Za-z_]",body):
        detected.append("rust")
    if re.search(r"(?im)^\s*(?:SELECT|INSERT|UPDATE|DELETE|CREATE\s+TABLE)\b",body):
        detected.append("sql")
    return _unique(detected)


def _embedded_web_evidence(code: str) -> dict[str, Any]:
    """Recognize languages inside one HTML artifact without executing it."""
    from html.parser import HTMLParser
    class Embedded(HTMLParser):
        def __init__(self):
            super().__init__(); self.script=False; self.style=False
            self.script_parts=[]; self.css=False; self.external=False; self.handler=False
        def handle_starttag(self,tag,attrs):
            attrs=dict(attrs)
            if attrs.get("style"): self.css=True
            if any(k.startswith("on") and v for k,v in attrs.items()): self.handler=True
            if tag=="style": self.style=True
            if tag=="script":
                self.script=(attrs.get("type") or "").lower() in ("", "module", "text/javascript", "application/javascript")
                if self.script and attrs.get("src"): self.external=True
        def handle_endtag(self,tag):
            if tag=="script": self.script=False
            if tag=="style": self.style=False
        def handle_data(self,data):
            if self.script: self.script_parts.append(data)
            if self.style and data.strip(): self.css=True
    parsed=Embedded();parsed.feed(code)
    body="\n".join(parsed.script_parts)
    active=re.sub(r"/\*[\s\S]*?(?:\*/|$)","",body)
    active=re.sub(r"(?m)^\s*//[^\n]*","",active).strip()
    languages=[]
    if parsed.css: languages.append("css")
    if body.strip() or parsed.external or parsed.handler: languages.append("javascript")
    return {"languages":languages,"hasRuntime":bool(active or parsed.external or parsed.handler),
            "unclosedScript":parsed.script}


def _candidate_primary_code(text: str) -> str:
    source=str(text or "").strip()
    from project_archive import ProjectArchiveError, parse_project_files, source_fences
    try:
        files=parse_project_files(source)
    except ProjectArchiveError:
        files=[]
    if len(files)>1:
        executable=[item for item in files if not str(item["path"]).lower().endswith((".md",".txt",".rst"))]
        selected=executable or files
        return "\n".join("FILE "+item["path"]+"\n"+item["content"] for item in selected)
    fenced=source_fences(source)
    return next((part["content"].strip() for part in fenced if part["content"].strip()),source)


def _code_fingerprint(text: str) -> str | None:
    code=_candidate_primary_code(text)
    return candidate_source_fingerprint(code,text)


def _reported_symbols(text: str) -> list[str]:
    raw=str(text or "")
    symbols=[]
    patterns=(
        r"(?i)name\s+['\"]([^'\"]+)['\"]\s+is\s+not\s+defined",
        r"(?i)referenceerror:\s*([A-Za-z_$][\w$]*)\s+is\s+not\s+defined",
        r"(?i)unresolved\s+reference\s*[: ]\s*([A-Za-z_$][\w$]*)",
        r"(?i)cannot\s+find\s+symbol[\s\S]{0,160}?symbol:\s*(?:class|variable|method)?\s*([A-Za-z_$][\w$]*)",
        r"(?i)undefined\s+reference\s+to\s+[`'\"]?([A-Za-z_$][\w$:]*)",
    )
    for pattern in patterns:
        for match in re.finditer(pattern,raw):
            value=str(match.group(1) or "").strip()
            if value and value not in symbols:
                symbols.append(value)
    return symbols[:12]


def _reported_dependencies(text: str) -> list[str]:
    raw=str(text or "")
    values=[]
    patterns=(
        r"(?i)No module named ['\"]([^'\"]+)['\"]",
        r"(?i)Cannot find module ['\"]([^'\"]+)['\"]",
        r"(?i)Can['’]?t resolve ['\"]([^'\"]+)['\"]",
        r"(?i)Module not found[^\n]*['\"]([^'\"]+)['\"]",
        r"(?i)package\s+['\"]?([A-Za-z0-9_.@/\-]+)['\"]?\s+(?:was\s+)?not found",
    )
    for pattern in patterns:
        for match in re.finditer(pattern,raw):
            value=str(match.group(1) or "").strip()
            if value and value not in values:
                values.append(value)
    return values[:12]


def _candidate_dependency_referenced(code: str, dependency: str) -> bool:
    dep=str(dependency or "").strip()
    if not dep:
        return False
    root=dep.split(".")[0]
    patterns=(
        r"(?m)^\s*import\s+"+re.escape(root)+r"\b",
        r"(?m)^\s*from\s+"+re.escape(root)+r"(?:\.|\s)",
        r"(?m)^\s*import\s+[^\n]*\s+from\s+['\"]"+re.escape(dep)+r"['\"]",
        r"\brequire\(\s*['\"]"+re.escape(dep)+r"['\"]\s*\)",
        r"\bimport\(\s*['\"]"+re.escape(dep)+r"['\"]\s*\)",
    )
    return any(re.search(pattern,str(code or ""),re.I) for pattern in patterns)


def _symbol_is_resolved_or_removed(code: str, symbol: str) -> bool:
    if not symbol:
        return True
    simple=symbol.split("::")[-1]
    use=re.search(r"\b"+re.escape(simple)+r"\b",code)
    if not use:
        return True
    declarations=(
        r"(?m)^\s*import\s+"+re.escape(simple)+r"\b",
        r"(?m)^\s*from\s+[A-Za-z_][\w.]*\s+import\s+[^\n]*\b"+re.escape(simple)+r"\b",
        r"\b(?:def|class|function|fun|fn)\s+"+re.escape(simple)+r"\b",
        r"(?m)^\s*(?:const|let|var|val)\s+"+re.escape(simple)+r"\b",
        r"(?m)^\s*"+re.escape(simple)+r"\s*=",
    )
    return any(re.search(pattern,code) for pattern in declarations)


def _apply_literal_ui_contract(contract: dict[str, Any]) -> dict[str, Any]:
    """Make extracted literal text an actionable early acceptance requirement."""
    prefix="Exact visible UI text: "
    requirements=[]
    for index,item in enumerate((contract.get("literalUiText") or [])[:8]):
        if not isinstance(item,dict) or not str(item.get("text") or ""):
            continue
        target=str(item.get("target") or "text")
        literal=json.dumps(str(item["text"]),ensure_ascii=False)
        requirement=(prefix+target+" must display exactly "+literal+
            ". Do not append wording outside this literal; use placement instructions only to position it.")
        if len(requirement)>320:
            requirement=(prefix+target+" must equal literalUiText["+str(index)+
                "].text exactly. Preserve every character. Do not append placement/reference wording.")
        requirements.append(requirement)
    if not requirements:
        return contract
    result=dict(contract)
    result["must"]=requirements+[str(item) for item in contract.get("must") or [] if not str(item).startswith(prefix)]
    return result


def _incomplete_implementation_requested(prompt: str) -> bool:
    """Only an affirmative request can authorize pseudocode/scaffold delivery."""
    prose=_strip_fenced_code(str(prompt or ""))
    for clause in re.split(r"[.;!?\n]+",prose):
        if not re.search(r"\b(?:pseudocode|pseudo-code|scaffold|skeleton|stub|template|TODO(?:\s+(?:comments?|placeholders?))?|commented\s+(?:example|placeholder)s?)\b",clause,re.I):
            continue
        if re.search(r"\b(?:no|not|never|without|avoid|don't|do not|working|functional|complete|finish|finished|fully implement)\b",clause,re.I):
            continue
        if re.search(r"\b(?:write|show|provide|return|use|allow|include|create|make|give|want|need)\b",clause,re.I):
            return True
    return False


def _apply_implementation_contract(contract: dict[str, Any], instruction: str) -> dict[str, Any]:
    result=dict(contract)
    original=str(contract.get("originalRequest") or "")
    explicitly_complete=bool(re.search(r"\b(?:no|never|without|avoid|don't|do not)\s+(?:use|return|include|provide)?\s*(?:pseudocode|pseudo-code|placeholders?|stubs?)\b|\b(?:fully\s+implement|finish\s+(?:it|this|the)|make\s+(?:it|this)\s+(?:working|functional|complete))\b", _strip_fenced_code(instruction), re.I))
    policy="explicit-scaffold" if not explicitly_complete and (_incomplete_implementation_requested(instruction) or
        _incomplete_implementation_requested(original)) else "complete-source"
    result["implementationPolicy"]=policy
    prefix="Implementation completeness: "
    must=[str(item) for item in contract.get("must") or [] if not str(item).startswith(prefix)]
    must_not=[str(item) for item in contract.get("mustNot") or [] if not str(item).startswith(prefix)]
    if policy=="complete-source":
        requirement=prefix+"return complete usable code implementing the requested behavior; explanatory comments may describe implemented behavior."
        # Keep both application capabilities and this general rule inside the
        # compact repair context's first ten requirements.
        position=1 if must and must[0].startswith("3D scene editor prototype:") else 0
        must.insert(position,requirement)
        must_not.insert(0,prefix+"do not substitute pseudocode, TODO/FIXME stubs or commented placeholders for implementation unless explicitly requested.")
    if policy=="explicit-scaffold":
        result.pop("applicationCapabilities",None)
        must=[item for item in must if not item.startswith("3D scene editor prototype:")]
    result["must"]=must;result["mustNot"]=must_not
    return result


def _implementation_placeholder_gaps(text: str, contract: dict[str, Any]) -> list[str]:
    """Source-only obvious stub checks, preserving real explanatory comments."""
    if contract.get("implementationPolicy")=="explicit-scaffold":
        return []
    from project_archive import (ProjectArchiveError, parse_project_files, source_fences,
        leading_file_metadata, leading_file_metadata_matches_path)
    gaps=[]
    request=str(contract.get("currentInstruction") or contract.get("originalRequest") or "")
    requested_noop=bool(re.search(r"\b(?:no[- ]?op|noop)\b|\bempty\s+(?:function|callback)\b",request,re.I))
    requested_unimplemented_error=bool(re.search(r"\b(?:raises?|throws?)\b[^.\n]{0,60}\bNotImplementedError\b",request,re.I))
    for fence in source_fences(str(text or "")):
        tag=str(fence.get("header") or "").strip().split()[0].lower() if str(fence.get("header") or "").strip() else ""
        if tag in ("pseudocode","pseudo","pseudo-code"):
            gaps.append("pseudocode-instead-of-implementation")
    try: files=parse_project_files(text)
    except ProjectArchiveError: files=[]
    if not files:
        files=[{"path":"source","content":str(text or ""),"language":""}]
    import ast
    import io
    import tokenize
    from application_capabilities import _lexical_mask
    for item in files:
        path=str(item.get("path") or "").lower()
        if path.endswith((".md",".markdown",".rst",".txt",".pyi",".d.ts")):
            continue
        content=str(item.get("content") or "")
        language=str(item.get("language") or "").lower()
        python=path.endswith(".py") or language in ("python","py","python3")
        comments=[]
        if python:
            try:
                comments=[tok.string for tok in tokenize.generate_tokens(io.StringIO(content).readline) if tok.type==tokenize.COMMENT]
            except (tokenize.TokenError,IndentationError): pass
            try:
                tree=ast.parse(content)
                protocol_methods={id(method) for cls in ast.walk(tree) if isinstance(cls,ast.ClassDef)
                    and any((isinstance(base,ast.Name) and base.id=="Protocol") or
                            (isinstance(base,ast.Attribute) and base.attr=="Protocol") for base in cls.bases)
                    for method in cls.body if isinstance(method,(ast.FunctionDef,ast.AsyncFunctionDef))}
                for node in ast.walk(tree):
                    if not isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) or id(node) in protocol_methods: continue
                    if any((isinstance(d,ast.Name) and d.id=="abstractmethod") or
                           (isinstance(d,ast.Attribute) and d.attr=="abstractmethod") for d in node.decorator_list): continue
                    body=list(node.body)
                    if body and isinstance(body[0],ast.Expr) and isinstance(body[0].value,ast.Constant) and isinstance(body[0].value.value,str): body=body[1:]
                    if len(body)!=1: continue
                    statement=body[0]
                    stub=not requested_noop and (isinstance(statement,ast.Pass) or (isinstance(statement,ast.Expr) and isinstance(statement.value,ast.Constant) and statement.value.value is Ellipsis))
                    if isinstance(statement,ast.Raise) and not requested_unimplemented_error:
                        exception=statement.exc.func if isinstance(statement.exc,ast.Call) else statement.exc
                        stub=stub or (isinstance(exception,ast.Name) and exception.id=="NotImplementedError")
                    if stub:gaps.append("unfinished-function-stub:"+node.name[:80])
            except (SyntaxError,ValueError): pass
        else:
            # JS/CSS/HTML comment extraction preserves string literals, so URLs
            # and text that happens to contain TODO do not become false stubs.
            token=re.compile(r'<!--[\s\S]*?-->'+r'|/\*[\s\S]*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|`(?:\\.|[^`\\])*`')
            comments=[m.group() for m in token.finditer(content) if m.group().startswith(("<!--","/*","//"))]
            clean=_lexical_mask(content,strings=False)
            if not requested_unimplemented_error and re.search(r"\bthrow\s+new\s+(?:Error|NotImplementedError)\s*\(\s*['\"](?:not\s+implemented|todo|implement\s+(?:me|this))\b",clean,re.I):
                gaps.append("unfinished-not-implemented-error")
        # A safe filename label on the leading metadata line is a name, even
        # when that name starts with TODO/FIXME. Exempt exactly that first
        # comment; later comments and all implementation bodies still count.
        if (comments and leading_file_metadata_matches_path(content,language,str(item.get("path") or ""))
                and leading_file_metadata(comments[0],language)==leading_file_metadata(content,language)):
            comments=comments[1:]
        for comment in comments:
            if re.search(r"(?im)^\s*(?://|#|/\*|\*|<!--)?\s*(?:TODO|FIXME)\b",comment) or re.search(r"\b(?:TODO|FIXME)\b\s*(?::|\b(?:implement|add|fill|write|replace|finish|your|here)\b)",comment,re.I) or re.search(r"\b(?:add|insert|implement|write|replace|fill)\b[^\n]{0,100}\b(?:your|here|implementation|this\s+later)\b",comment,re.I):
                gaps.append("unfinished-implementation-placeholder")
    return _unique(gaps)


def _web_delivery_gaps(code: str, original: str, language: dict[str, Any], project_files=None) -> list[str]:
    """Detect explicit unfinished web artifacts, not semantic correctness."""
    if "html" not in (language.get("requiredLanguages") or []):
        return []
    if _incomplete_implementation_requested(original):
        return []
    gaps = []
    if language.get("artifactType")=="web-page" and not re.search(r"\b(?:vite|webpack|parcel|bundler|next\.?js|react|angular|repository|repo)\b", _strip_fenced_code(original), re.I):
        from web_module_contract import module_dependency_gaps
        gaps.extend(module_dependency_gaps(code,project_files))
    if re.search(r"(?im)^\s*(?://|/\*|<!--)\s*(?:add|insert|implement|write|replace)\b[^\n]*\b(?:your|here|implementation)\b", code):
        gaps.append("unfinished-implementation-placeholder")
    if re.search(r"\b(?:interactive|3d|modeling|modelling|editor|calculator|game)\b", original, re.I):
        evidence=_embedded_web_evidence(code)
        if evidence["unclosedScript"]:
            gaps.append("unclosed-runtime-script")
        if not evidence["hasRuntime"]:
            gaps.append("dynamic-page-has-no-runtime-implementation")
    return gaps


def _source_delivery_gaps(text: str, original: str, language: dict[str, Any]) -> list[str]:
    """Bounded completed-source checks; these are not syntax or runtime proof."""
    source=str(text or "")
    active=None
    for line in source.splitlines():
        match=re.match(r"^[ \t]{0,3}(`{3,}|~{3,})([^\n]*)$",line)
        if not match:
            continue
        marker,tail=match.groups()
        if active is None:
            active=marker
        elif marker[0]==active[0] and len(marker)>=len(active) and not tail.strip():
            active=None
    gaps=["unclosed-code-fence"] if active is not None else []
    from project_archive import ProjectArchiveError, parse_project_files
    try:
        files=parse_project_files(source)
    except ProjectArchiveError as exc:
        gaps.append("invalid-project-files:"+str(exc)[:140])
        files=[]
    if len(files)>1 and re.search(r"\b(?:single[- ]file|one\s+(?:complete\s+)?html\s+file)\b",original,re.I):
        gaps.append("single-file-request-has-multiple-files")
    for item in files:
        # Header attributes copied into a source body are not executable file
        # contents. Reject the unambiguous multi-attribute protocol mistake;
        # never strip it or guess a new filename on the model's behalf.
        first=next((line.strip() for line in str(item.get("content") or "").splitlines() if line.strip()),"")
        attribute=r'''(?:file|path|filename|project|group)=(?:"[^"\r\n]*"|'[^'\r\n]*'|[^\s]+)'''
        if (str(item.get("language") or "").lower() in ("javascript","js","typescript","ts","jsx","tsx","css","scss","less")
                and re.fullmatch(attribute+r"(?:[ \t]+"+attribute+r")+",first)
                and re.search(r"(?:^|[ \t])(?:file|path|filename)=",first)
                and re.search(r"(?:^|[ \t])(?:project|group)=",first)):
            gaps.append("misplaced-project-file-metadata:"+str(item.get("path") or "")[:100])
        if str(item.get("path") or "").lower().endswith(".json"):
            try:
                json.loads(item.get("content") or "")
            except (ValueError,TypeError):
                gaps.append("invalid-json-project-file:"+str(item.get("path") or "")[:100])
    html_sources=[str(item.get("content") or "") for item in files
                  if str(item.get("language") or "").lower() in ("html","html5")
                  or str(item.get("path") or "").lower().endswith((".html",".htm"))]
    if not files and (source.lstrip().startswith("<") or
            ("html" in (language.get("requiredLanguages") or []) and language.get("artifactType")=="web-page")):
        html_sources=[_candidate_primary_code(source)]
    fragment=bool(re.search(r"\b(?:fragment|snippet|opening\s+tag|start\s+tag)\b",original,re.I))
    if fragment:
        return _unique(gaps)
    from html.parser import HTMLParser
    class Shape(HTMLParser):
        void={"area","base","br","col","embed","hr","img","input","link","meta","param","source","track","wbr"}
        optional={"html","head","body","p","li","dt","dd","rt","rp","optgroup","option","colgroup","thead","tbody","tfoot","tr","td","th"}
        def __init__(self):
            super().__init__();self.stack=[];self.errors=[];self.html=False;self.html_closed=False
        def handle_starttag(self,tag,attrs):
            if tag=="html":self.html=True
            if tag not in self.void and tag not in self.optional:self.stack.append(tag)
        def handle_startendtag(self,tag,attrs):
            pass
        def handle_endtag(self,tag):
            if tag=="html":self.html_closed=True
            if tag in self.void or tag in self.optional:return
            if tag not in self.stack:self.errors.append("unexpected-html-close:"+tag[:30]);return
            if self.stack[-1]!=tag:self.errors.append("mismatched-html-close:"+tag[:30])
            index=len(self.stack)-1-self.stack[::-1].index(tag)
            self.stack=self.stack[:index]
    for html in html_sources:
        parsed=Shape();parsed.feed(html)
        if re.match(r"\s*<(?:/?[A-Za-z]|!|\?)",parsed.rawdata):gaps.append("unfinished-html-token")
        if parsed.html and not parsed.html_closed:gaps.append("unclosed-html-document")
        if parsed.stack:gaps.append("unclosed-html-element:"+parsed.stack[-1][:30])
        gaps.extend(parsed.errors[:4])
    return _unique(gaps)[:12]


def _literal_ui_gaps(text: str, contract: dict[str, Any]) -> list[str]:
    literals=[item for item in (contract.get("literalUiText") or [])[:8] if isinstance(item,dict)]
    if not literals:
        return []
    from html import unescape
    from html.parser import HTMLParser
    class Visible(HTMLParser):
        tags={"h1","h2","h3","h4","h5","h6","title","header","div","span","p","label","button","a"}
        def __init__(self):
            super().__init__();self.active=[];self.values=[];self.ignore=0;self.script=False;self.scripts=[]
        def handle_starttag(self,tag,attrs):
            if tag=="script":self.script=str(dict(attrs).get("type") or "").lower() in ("","module","text/javascript","application/javascript")
            if tag in ("script","style"):self.ignore+=1
            if tag in self.tags:self.active.append([tag,[]])
        def handle_data(self,data):
            if self.script:self.scripts.append(data)
            if not self.ignore:
                for item in self.active:item[1].append(data)
        def handle_endtag(self,tag):
            if tag=="script":self.script=False
            if tag in ("script","style") and self.ignore:self.ignore-=1
            for index in range(len(self.active)-1,-1,-1):
                if self.active[index][0]==tag:
                    item=self.active.pop(index);self.values.append((tag,"".join(item[1]).strip()));break
    from project_archive import ProjectArchiveError, parse_project_files
    try:
        files=parse_project_files(text)
    except ProjectArchiveError:
        files=[]
    html=[str(item.get("content") or "") for item in files
          if str(item.get("language") or "").lower() in ("html","html5")
          or str(item.get("path") or "").lower().endswith((".html",".htm"))]
    source="\n".join(html) if html else str(text or "")
    parsed=Visible();parsed.feed(source)
    values=list(parsed.values)
    # A literal text assignment can satisfy a dynamic page. This is source
    # evidence only; comments and arbitrary prose are never display evidence.
    executable="\n".join(str(item.get("content") or "") for item in files
                          if str(item.get("language") or "").lower() in ("javascript","js"))
    import ast
    token=re.compile(r"\s+|//[^\n]*|/\*[\s\S]*?\*/|\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`|/(?:\\.|[^/\\\n])+/[dgimsuvy]*|[A-Za-z_$][\w$]*|.",re.S)
    tokens=[]
    for match in token.finditer("\n".join(parsed.scripts)+"\n"+executable):
        value=match.group()
        if value.isspace() or value.startswith(("//","/*")):continue
        if value[:1] in ('"',"'"):
            try:decoded=ast.literal_eval(value)
            except (ValueError,SyntaxError):decoded=None
            tokens.append(("string",decoded))
        elif value.startswith(('`','/')):tokens.append(("opaque",None))
        else:tokens.append(("token",value))
    for index in range(3,len(tokens)):
        kind,value=tokens[index]
        if (kind=="string" and isinstance(value,str) and tokens[index-3]==("token",".")
                and tokens[index-2][1] in ("textContent","innerText","innerHTML")
                and tokens[index-1]==("token","=")):
            if tokens[index-2][1]=="innerHTML":value=unescape(re.sub(r"<[^>]*>","",value))
            values.append(("dynamic",value.strip()))
    gaps=[]
    for item in literals:
        expected=str(item.get("text") or "").strip()
        target=item.get("target")
        tags=({"h1","h2","h3","h4","h5","h6","header","dynamic"} if target=="heading"
              else {"title","h1","h2","header","dynamic"} if target=="title"
              else {"button","dynamic"} if target=="button" else None)
        applicable=[value for tag,value in values if (tags is None and tag!="title") or (tags is not None and tag in tags)]
        if expected and expected not in applicable:gaps.append("literal-ui-text-mismatch:"+expected[:100])
    return gaps


def candidate_contract_gate(text: str, programming: dict[str, Any], history: list[dict[str, Any]]) -> dict[str, Any]:
    """Shared deterministic contract gate for every programming model route."""
    if not isinstance(programming,dict) or not programming.get("codingTask"):
        return {"status":"NOT_APPLICABLE","reasons":[],"executionVerified":False}
    if programming.get("needsFailureEvidence"):
        return {
            "status":"EVIDENCE_REQUIRED",
            "reasons":["failure-evidence-required"],
            "executionVerified":False,
            "verificationState":"AWAITING_FAILURE_EVIDENCE",
        }
    reasons=[]
    contract=programming.get("intentContract") if isinstance(programming.get("intentContract"),dict) else {}
    language=contract.get("languageContract") if isinstance(contract.get("languageContract"),dict) else {}
    delta_text=str(text or "")
    revision_file_count=None
    revision_base_languages=[]
    if (programming.get("artifactMutationRequested") and programming.get("artifactTargetId")
            and programming.get("artifactEditSource") and not programming.get("newProject")
            and type(programming.get("baseRevision")) is int and programming["baseRevision"]>0
            and re.fullmatch(r"[a-f0-9]{64}",str(programming.get("baseSourceHash") or ""))):
        # Validate the resulting owned project, while the model supplies only
        # complete changed files. Selection/owner/base checks remain Station's.
        from project_archive import ProjectArchiveError, parse_project_files, project_markdown
        from project_revision_workspace import merge_project_revision_files
        try:
            revision_base_files=parse_project_files(str(programming["artifactEditSource"]))
            revision_files=merge_project_revision_files(
                revision_base_files,delta_text)
            text=project_markdown(revision_files)
            revision_file_count=len(revision_files)
            revision_base_languages=_candidate_languages(project_markdown(revision_base_files))
        except ProjectArchiveError as exc:
            reasons.append("invalid-project-revision:"+str(exc)[:140])
    detected=_candidate_languages(text)
    required=[str(x) for x in (language.get("requiredLanguages") or [])]
    allowed=[str(x) for x in (language.get("allowedLanguages") or [])]
    # A JavaScript-only edit does not substitute away preserved HTML/CSS.
    allowed=_unique(allowed+revision_base_languages)
    project_files=[]
    if language.get("artifactType")=="web-page":
        from project_archive import ProjectArchiveError, parse_project_files
        try:
            project_files=parse_project_files(text)
        except ProjectArchiveError:
            pass  # The completed-source gate records the precise parse failure.
        if len(project_files)>1 and not re.search(r"\b(?:html\s+only|only\s+html|single[- ]file)\b",str(contract.get("originalRequest") or ""),re.I):
            for item in project_files:
                tag=_normalize_language_tag(item.get("language"))
                suffix=str(item.get("path") or "").lower()
                if (tag=="json" and suffix.endswith(".json")) or (tag=="yaml" and suffix.endswith((".yaml",".yml"))):
                    if tag not in allowed:allowed.append(tag)
    if language.get("explicit") or language.get("inferredFrom"):
        for item in required:
            if item not in detected:
                reasons.append("missing-required-language:"+item)
        for item in detected:
            if item not in allowed:
                reasons.append("language-contract-mismatch:"+item)
    evidence=programming.get("failureEvidence") if isinstance(programming.get("failureEvidence"),dict) else {}
    semantics=evidence.get("receiptSemantics") if isinstance(evidence.get("receiptSemantics"),dict) else {}
    repair_source=str(evidence.get("repairSource") or "")
    if evidence and repair_source:
        before=_code_fingerprint(repair_source) or str(evidence.get("repairSourceFingerprint") or "")
        after=_code_fingerprint(text)
        if before and after and before==after:
            reasons.append("diagnostic-repair-no-executable-change")
    candidate_code=_candidate_primary_code(text)
    if language.get("artifactType")=="web-page":
        html_files=[item for item in project_files if str(item.get("path") or "").lower().endswith((".html",".htm")) or str(item.get("language") or "").lower() in ("html","html5")]
        if html_files:
            # The entry may follow README/CSS fences. Validate the actual page,
            # not whichever support file happened to be emitted first.
            candidate_code="\n".join(str(item["content"]) for item in html_files)
    if programming.get("changeClass") not in ("review", "explain"):
        if revision_file_count is not None:
            # Raw fence completeness and newly introduced placeholders are
            # checked before serialization; old unchanged files are not edits.
            reasons.extend(_source_delivery_gaps(delta_text,str(contract.get("originalRequest") or ""),language))
        reasons.extend(_source_delivery_gaps(text,str(contract.get("originalRequest") or ""),language))
        reasons.extend(_web_delivery_gaps(candidate_code, str(contract.get("originalRequest") or ""), language,project_files))
        reasons.extend(_literal_ui_gaps(text,contract))
        reasons.extend(_implementation_placeholder_gaps(delta_text,contract))
        if contract.get("implementationPolicy")!="explicit-scaffold":
            reasons.extend(application_source_gaps(text,contract))
    for symbol in semantics.get("reportedSymbols") or []:
        if not _symbol_is_resolved_or_removed(candidate_code,str(symbol)):
            reasons.append("diagnostic-symbol-resolution-unproven:"+str(symbol)[:80])
    constraints=programming.get("repairConstraints") if isinstance(programming.get("repairConstraints"),dict) else {}
    active_dependencies=_unique(
        [str(x) for x in (constraints.get("forbiddenDependencies") or []) if str(x).strip()]
        +[str(x) for x in (semantics.get("reportedDependencies") or []) if str(x).strip()]
    )
    for dependency in active_dependencies:
        if _candidate_dependency_referenced(candidate_code,str(dependency)):
            reasons.append("dependency-still-referenced:"+str(dependency)[:100])
    behavior=programming.get("behaviorLedger") if isinstance(programming.get("behaviorLedger"),dict) else {}
    repair_base=programming.get("behaviorRepairBase") if isinstance(programming.get("behaviorRepairBase"),dict) else {}
    after_fp=_code_fingerprint(text)
    base_fp=_code_fingerprint(str(programming.get("behaviorRepairBaseSource") or "")) or str(repair_base.get("sourceFingerprint") or "")
    if repair_base.get("mode")=="best-known-tested-source" and base_fp and after_fp==base_fp:
        reasons.append("behavior-repair-base-unchanged")
    verification="AWAITING_EXTERNAL_RECEIPT" if evidence else "NOT_EXECUTION_VERIFIED"
    return {
        "status":"REJECT" if reasons else "PASS",
        "reasons":_unique(reasons),
        "languageContract":language,
        "detectedLanguages":detected,
        "projectRevisionFileCount":revision_file_count,
        "literalUiText":[dict(item) for item in (contract.get("literalUiText") or [])[:8] if isinstance(item,dict)],
        "diagnosticGrounded":bool(evidence) and not any(x.startswith("diagnostic-") for x in reasons),
        "receiptCategories":list(semantics.get("categories") or [])[:12],
        "activeRepairConstraints":{
            "dependencyPolicy":constraints.get("dependencyPolicy"),
            "unavailableDependencies":list(constraints.get("unavailableDependencies") or [])[:16],
            "carriedUnavailableDependencies":list(constraints.get("carriedUnavailableDependencies") or [])[:16],
        },
        "behaviorLedger":{
            "currentScore":dict(behavior.get("currentScore") or {}) if isinstance(behavior.get("currentScore"),dict) else None,
            "bestKnownScore":dict(behavior.get("bestKnownScore") or {}) if isinstance(behavior.get("bestKnownScore"),dict) else None,
            "regressedCases":list(behavior.get("regressedCases") or [])[:20],
            "resolvedCases":list(behavior.get("resolvedCases") or [])[:20],
            "preservePassingCases":list(behavior.get("preservePassingCases") or [])[:30],
            "rebaseRecommended":bool(behavior.get("rebaseRecommended")),
            "bestKnownArtifact":dict(behavior.get("bestKnownArtifact") or {}) if isinstance(behavior.get("bestKnownArtifact"),dict) else None,
            "repairBaseMode":repair_base.get("mode"),
        },
        "structuredReceipt":dict(semantics.get("structuredReceipt") or {}),
        "executionVerified":False,
        "verificationState":verification,
    }


def _vague_failure_report(text: str) -> bool:
    raw=str(text or "").strip()
    if not raw or _failure_receipt_detected(raw):
        return False
    normalized=_norm(raw)
    patterns=(
        r"\b(?:it|this|that|the code|your code)\s+(?:still\s+)?(?:does(?:n['’]?t| not)\s+work|isn['’]?t\s+working|is not working|fails?|failed|broke|is broken)\b",
        r"\b(?:does(?:n['’]?t| not)\s+work|not working|still broken|keeps? failing|compiler error|compile error|runtime error|test error)\b",
        r"\b(?:i\s+get|getting|got)\s+(?:an?\s+)?error\b",
    )
    return any(re.search(pattern,normalized,re.I) for pattern in patterns)


def _last_assistant_artifact(history: list[dict[str, Any]]) -> dict[str, Any]:
    for item in reversed(history or []):
        if not isinstance(item,dict) or str(item.get("role") or "")!="assistant":
            continue
        if _provider_read_display(item):
            continue
        meta=item.get("meta") if isinstance(item.get("meta"),dict) else {}
        text=str(meta.get("artifactSourceSnapshot") or item.get("content") or item.get("text") or "")
        if meta.get("codeArtifactId") or "```" in text:
            return {
                "messageId":str(item.get("id") or ""),
                "artifactId":str(meta.get("codeArtifactId") or ""),
                "artifactRevision":int(meta.get("artifactRevision") or 0),
                "artifactSourceHash":str(meta.get("artifactSourceHash") or ""),
                "text":text,
            }
    return {}


def _programming_intent_contract(prompt: str, change_class: str) -> dict[str, Any]:
    """Compile bounded acceptance requirements from prose, keeping source/test payloads separate."""
    raw=str(prompt or "").strip()
    prose=_strip_fenced_code(raw)
    clauses=[part.strip(" \t-*") for part in re.split(r"(?:\r?\n+|(?<=[.!?;])\s+)",prose) if part.strip(" \t-*") and part.strip()!="[CODE_PAYLOAD]"]
    must=[]; must_not=[]; preserve=[]; evidence=[]
    negative=re.compile(r"\b(?:must\s+not|mustn't|do\s+not|don't|never|without|avoid|no\s+)\b",re.I)
    preserve_rx=re.compile(r"\b(?:keep|preserve|unchanged|do not change|don't change|change only|only change|same\s+(?:name|signature|settings?|config|configuration|permissions?))\b",re.I)
    requirement_rx=re.compile(r"\b(?:must|should|need(?:s)?\s+to|has\s+to|have\s+to|make\s+sure|ensure|require(?:s|d)?|implement|add|fix|accept|reject|support|compile|build|test|pass)\b",re.I)
    requested_behavior_rx=re.compile(r"^(?:please\s+)?(?:create|write|show|include|use|return|render|provide|allow|enable|wire)\b",re.I)
    for clause in clauses[:32]:
        item=" ".join(clause.split())[:500]
        if negative.search(item): must_not.append(item)
        elif preserve_rx.search(item): preserve.append(item)
        elif requirement_rx.search(item) or requested_behavior_rx.search(item): must.append(item)
    if not must and raw:
        must.append("Satisfy the requested "+str(change_class or "programming")+" operation without changing unrelated behavior.")
    evidence.extend([
        "technical-validity: returned candidate must be complete and syntactically/build valid when applicable",
        "intent-validity: original requirements and preservation constraints must be rechecked after every repair",
        "api-validity: required wrapper/name/signature must remain present unless explicitly changed",
    ])
    return {
        "schema":"swrlz-programming-intent-contract-v3","originalRequest":raw,
        "must":must[:16],"mustNot":must_not[:16],"preserve":preserve[:16],
        "languageContract":_language_contract(raw),
        "literalUiText":_literal_ui_text(raw),
        "acceptanceEvidence":evidence,
        "completionRule":"done only when complete-source, technical validity, and intent validity all pass",
    }


def _literal_ui_text(text: str) -> list[dict[str, str]]:
    """Extract bounded user-specified UI strings, separate from location prose."""
    raw=_strip_fenced_code(str(text or ""))
    if not re.search(r"\b(?:add|set|change|replace|put|use|make|rename)\b",raw,re.I):
        return []
    if not re.search(r"\b(?:text|heading|header|title|label|button|caption)\b",raw,re.I):
        return []
    target=("heading" if re.search(r"\b(?:heading|header)\b|\btext\b[^.!?\n]{0,70}\b(?:to|at|on)\s+(?:the\s+)?top\b",raw,re.I)
            else "title" if re.search(r"\btitle\b",raw,re.I)
            else "button" if re.search(r"\bbutton\b",raw,re.I) else "text")
    result=[]
    for match in re.finditer(r'(["\u201c])([^"\u201d\n]{1,180})["\u201d]|\u2018([^\u2019\n]{1,180})\u2019|\'([^\'\n]{1,180})\'',raw):
        prefix=raw[max(0,match.start()-100):match.start()]
        if not re.search(r"\b(?:saying|says?|read(?:ing|s)?|text|heading|header|title|label|caption|to|as)\s*[:=]?\s*$",prefix,re.I):
            continue
        value=next((group for group in match.groups()[1:] if group is not None),"").strip()
        if value and not any(item["text"]==value for item in result):
            result.append({"text":value,"target":target,"source":"quoted"})
    if result:
        return result[:8]
    # 'Text to the top saying NAME of that viewer' has a trailing UI location,
    # not a longer title. Only cut a demonstrative application locator, after
    # an explicit top/header/text placement request; ordinary prose is intact.
    if re.search(r"\btop\b",raw,re.I):
        match=re.search(r"\bsaying\s+(.{1,180}?)\s+(?:of|on|in|to)\s+(?:this|that)\s+"
                        r"(?:(?:3[ -]?d|model|existing|web)\s+){0,3}"
                        r"(?:viewer|editor|page|website|app|application)\s*[.!?]*$",raw,re.I)
        if match:
            return [{"text":match.group(1).strip(),"target":target,"source":"locator-bounded"}]
    return []


def _fresh_web_project_request(text: str) -> bool:
    """Independently requested application pages start a clean project scope.

    Creation verbs and optional articles describe the new deliverable; only an
    explicit reference/conversion of the current page retains its source scope.
    Purpose clauses can still reuse colors/assets without mutating that page.
    """
    if not (requests_web_source(text) or requests_source_project(text)):
        return False
    raw=_strip_fenced_code(text).strip()
    lead=re.match(r"^(?:(?:please|hey|now|okay|ok)[,!\s]+)?"
                  r"(?:(?:can|could|would|will)\s+you\s+|i\s+(?:want|need)\s+you\s+to\s+|"
                  r"go\s+ahead\s+and\s+)?"
                  r"(?:make|do|create|build|write|develop|implement|code)\b",raw,re.I)
    if not lead:
        return False
    head=re.split(r"\b(?:using|with|for|based\s+on)\b",raw[lead.end():],maxsplit=1,flags=re.I)[0]
    return not bool(re.search(r"^\s*(?:it|this|that)(?:\s+one)?\b|"
                              r"\b(?:this|that|same|existing|current|previous|above)\s+"
                              r"(?:(?:3[ -]?d|model|scene|web|html)\s+){0,4}"
                              r"(?:viewer|editor|page|website|app|application)\b|"
                              r"\b(?:turn|convert|change|extend|upgrade)\s+(?:this|that|it)\b|\binto\b",head,re.I))


def _extract_candidate_code(text: str) -> str:
    """Return the primary executable candidate, ignoring prose/examples/comments."""
    raw=str(text or "").strip()
    candidate=_candidate_primary_code(raw)
    lines=[]
    for line in candidate.strip().splitlines():
        stripped=line.strip()
        if not stripped or stripped.startswith(("#","//","/*","*","*/")):
            continue
        lines.append(line.rstrip())
    return "\n".join(lines)



def _receipt_shape_detected(text: str) -> bool:
    """Detect receipt-shaped execution output without treating error words in source/prose as proof."""
    raw=str(text or "")
    if not raw.strip():
        return False
    strong=(
        r"(?im)^\s*Traceback \(most recent call last\):",
        r"(?im)^\s*[A-Za-z_][A-Za-z0-9_]*(?:Error|Exception|Failure)\s*:\s*\S",
        r"(?im)^(?:[^\n]+\.(?:ts|tsx)\(\d+,\d+\):\s*)?error\s+TS\d{3,6}\s*:",
        r"(?im)^\s*\d+:\d+\s+error\s+\S",
        r"(?im)^\s*[✖×x]\s+\d+\s+problems?\s+\(\d+\s+errors?",
        r"(?im)^[^\n:]+\.[A-Za-z0-9_]+:\d+(?::\d+)?:\s*(?:fatal\s+)?error:",
        r"(?im)^\s*(?:FAIL|FAILED|ERROR)\b",
        r"(?im)^\s*(?:npm\s+ERR!|fatal\s+error:|error:)\s+\S",
        r"(?i)\b(?:failed to compile|compilation failed|build failed|tests? failed|test suite failed)\b",
        r"(?i)\b(?:cannot find symbol|unresolved reference|undefined reference|module not found|no module named|cannot resolve)\b",
        r'(?i)"(?:passed|success|ok)"\s*:\s*false\b',
        r"(?i)\b(?:exit(?:\s+code|\s+status)?|status)\s*[:=]?\s*[1-9]\d*\b",
        r"(?i)\b\d+\s+failed\b",
    )
    if any(re.search(pattern,raw) for pattern in strong):
        return True
    expected=bool(re.search(r"(?i)\bexpected\b",raw))
    observed=bool(re.search(r"(?i)\b(?:actual|got|received)\b",raw))
    return expected and observed


def _receipt_evidence_text(raw: str) -> str:
    """Separate execution receipt text from fenced source before semantic parsing."""
    source=str(raw or "")
    blocks=list(re.finditer(r"```([^\n`]*)\n([\s\S]*?)```",source))
    outside=re.sub(r"```[^\n`]*\n[\s\S]*?```","\n",source)
    pieces=[outside]
    for block in blocks:
        body=str(block.group(2) or "")
        if _receipt_shape_detected(body):
            pieces.append(body)
    return "\n".join(piece for piece in pieces if piece.strip()).strip()


def _looks_like_source_body(body: str) -> bool:
    text=str(body or "")
    if not text.strip() or _receipt_shape_detected(text):
        return False
    return bool(re.search(
        r"<!doctype\s+html|<html\b|<body\b|"
        r"^\s*(?:from\s+[A-Za-z_][\w.]*\s+import\s+|import\s+[A-Za-z_][\w.]*|def\s+[A-Za-z_]\w*\s*\(|class\s+[A-Za-z_]\w*)|"
        r"\b(?:function|const|let|var|interface|type|fun|fn|public\s+class)\b|"
        r"#include\s*[<\"]|\bstd::|"
        r"^\s*(?:SELECT|INSERT|UPDATE|DELETE|CREATE\s+TABLE)\b",
        text,
        re.I|re.M|re.S,
    ))


def _inline_source_from_prompt(raw: str) -> str:
    """Return the first actual source fence, never a log/output fence."""
    source=str(raw or "")
    fallback=""
    for match in re.finditer(r"```([^\n`]*)\n([\s\S]*?)```",source):
        tag=str(match.group(1) or "").strip().split()[0] if str(match.group(1) or "").strip() else ""
        body=str(match.group(2) or "").strip()
        language=_normalize_language_tag(tag)
        if language and not _receipt_shape_detected(body):
            return body
        if not fallback and _looks_like_source_body(body):
            fallback=body
    return fallback


def _latest_user_source(history: list[dict[str, Any]]) -> tuple[str, str]:
    for item in reversed(history or []):
        if not isinstance(item,dict) or str(item.get("role") or "")!="user":
            continue
        text=str(item.get("content") or item.get("text") or "")
        source=_inline_source_from_prompt(text)
        if source:
            return source,str(item.get("id") or "")
    return "",""


def _json_receipt_spans(text: str) -> list[tuple[int, int, Any]]:
    """Decode bounded JSON values embedded in otherwise textual receipt output."""
    raw=str(text or "")
    decoder=json.JSONDecoder()
    values=[]
    cursor=0
    while cursor < len(raw) and len(values) < 8:
        match=re.search(r"[\[{]",raw[cursor:])
        if not match:
            break
        start=cursor+match.start()
        try:
            value,end=decoder.raw_decode(raw[start:])
        except (json.JSONDecodeError,TypeError,ValueError):
            cursor=start+1
            continue
        if isinstance(value,(dict,list)):
            values.append((start, start + end, value))
        cursor=start+max(1,end)
    return values


def _json_receipt_values(text: str) -> list[Any]:
    return [value for _start, _end, value in _json_receipt_spans(text)]


def _failure_classification_text(text: str) -> str:
    """Keep plain diagnostics and failed JSON cases, excluding passed-case data."""
    def prune(value, depth=0):
        if depth > 8:
            return None
        if isinstance(value, list):
            return [item for item in (prune(v, depth+1) for v in value[:80]) if item is not None]
        if not isinstance(value, dict):
            return value
        status = next((value[k] for k in ("passed", "success", "ok") if isinstance(value.get(k), bool)), None)
        named = str(value.get("status") or value.get("result") or value.get("outcome") or "").lower()
        if status is True or (status is not False and named in {"pass", "passed", "ok", "success"}):
            # A successful transport/aggregate can still contain failed cases.
            # Retain nested result containers, never a passed case's data fields.
            children = {k: prune(v, depth+1) for k,v in list(value.items())[:80]
                        if isinstance(v,(dict,list)) and k not in {"expected","actual","got","received","observed"}}
            return children or None
        return {k: prune(v, depth+1) for k,v in list(value.items())[:80]
                if k not in {"passing", "passingTests", "passedTests", "passedCases"}}
    pieces=[]; cursor=0
    for start,end,value in _json_receipt_spans(text):
        pieces.append(text[cursor:start])
        pieces.append(json.dumps(prune(value), ensure_ascii=False))
        cursor=end
    pieces.append(text[cursor:])
    return "\n".join(pieces)


def _structured_json_receipt_semantics(text: str) -> dict[str, Any]:
    values=_json_receipt_values(text)
    failing_tests=[]
    mismatches=[]
    failure_signals=[]
    locations=[]
    categories=[]
    cases=[]
    case_count=0
    failed_count=0
    visited=0

    def add(target,value,limit=12,chars=360):
        value=str(value or "").strip()
        if value and value not in target and len(target)<limit:
            target.append(value[:chars])

    def scalar(value):
        if isinstance(value,(str,int,float,bool)) or value is None:
            return value
        if isinstance(value,(dict,list)):
            return json.dumps(value, ensure_ascii=False, separators=(",", ":"))[:500]
        return None

    def walk(node,depth=0):
        nonlocal case_count,failed_count,visited
        if depth>8 or visited>=160:
            return
        visited+=1
        if isinstance(node,list):
            for item in node[:80]:
                walk(item,depth+1)
            return
        if not isinstance(node,dict):
            return

        status_keys=("passed","success","ok")
        bool_status=next((node.get(key) for key in status_keys if isinstance(node.get(key),bool)),None)
        status_text=str(node.get("status") or node.get("result") or node.get("outcome") or "").strip().lower()
        explicit_case=bool_status is not None or status_text in {"pass","passed","ok","success","failed","fail","error"}
        failed=(bool_status is False) or status_text in {"failed","fail","error"}
        if explicit_case:
            case_count+=1
        if failed:
            failed_count+=1

        name=""
        for key in ("test","testName","name","id","case","title"):
            value=node.get(key)
            if isinstance(value,(str,int)) and str(value).strip():
                name=str(value).strip()
                break

        expected=scalar(node.get("expected"))
        actual=None
        for key in ("actual","received","got","observed"):
            if key in node:
                actual=scalar(node.get(key))
                break
        message=""
        for key in ("error","message","reason","failure"):
            value=node.get(key)
            if isinstance(value,str) and value.strip():
                message=value.strip()
                break

        if explicit_case and name and len(cases)<40:
            case_status="failed" if failed else "passed"
            cases.append({
                "id":name[:180],
                "status":case_status,
                "expected":repr(expected)[:220] if expected is not None else None,
                "actual":repr(actual)[:220] if actual is not None else None,
                "message":message[:280] if message else None,
            })

        if failed:
            if name:
                add(failing_tests,name)
            if expected is not None and actual is not None:
                prefix=(name+": ") if name else ""
                add(mismatches,prefix+"expected="+repr(expected)+"; actual="+repr(actual))
                if "behavior-mismatch" not in categories:
                    categories.append("behavior-mismatch")
            if message:
                add(failure_signals,((name+": ") if name else "")+message)
                neq=re.search(r"(?s)([^\n]{0,140}?)\s*!==\s*([^\n]{0,140})",message)
                if neq:
                    left=neq.group(1).strip()
                    right=neq.group(2).strip()
                    add(mismatches,((name+": ") if name else "")+"actual="+left+"; expected="+right)
                    if "behavior-mismatch" not in categories:
                        categories.append("behavior-mismatch")
            if "assertion" not in categories:
                categories.append("assertion")

        file_value=""
        for key in ("file","fileName","filename","path"):
            value=node.get(key)
            if isinstance(value,str) and value.strip():
                file_value=value.strip()
                break
        line_value=node.get("line")
        column_value=node.get("column")
        if file_value and isinstance(line_value,int) and not (explicit_case and not failed):
            loc=file_value+":"+str(line_value)
            if isinstance(column_value,int):
                loc+=":"+str(column_value)
            add(locations,loc)

        for key,value in list(node.items())[:80]:
            if explicit_case and not failed and key in {"expected","actual","got","received","observed"}:
                continue  # Passed observations are data, not additional tests.
            if isinstance(value,(dict,list)):
                walk(value,depth+1)

    for value in values:
        walk(value)

    return {
        "formats":["json"] if values else [],
        "jsonObjectCount":len(values),
        "caseCount":case_count,
        "failedCaseCount":failed_count,
        "failingTests":failing_tests[:12],
        "expectedActual":mismatches[:12],
        "failureSignals":failure_signals[:12],
        "sourceLocations":locations[:12],
        "categories":categories[:8],
        "cases":cases[:40],
    }


def _receipt_semantics(raw: str) -> dict[str, Any]:
    """Extract bounded repair facts from receipt-shaped output only."""
    full_text=_receipt_evidence_text(raw)
    structured=_structured_json_receipt_semantics(full_text)
    text=_failure_classification_text(full_text) if structured.get("caseCount") else full_text
    lines=[line.strip() for line in text.splitlines() if line.strip()]
    exceptions=[]
    for line in lines:
        match=re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*(?:Error|Exception|Failure))\s*:",line)
        if match and match.group(1) not in exceptions:
            exceptions.append(match.group(1))
    exit_codes=[]
    for match in re.finditer(r"(?i)\b(?:exit(?:\s+code|\s+status)?|status)\s*[:=]?\s*(-?\d+)\b",text):
        value=int(match.group(1))
        if value not in exit_codes:
            exit_codes.append(value)

    failing=[]; passing=[]; mismatches=[]
    for line in lines:
        json_false=bool(re.search(r'(?i)"(?:passed|success|ok)"\s*:\s*false\b',line))
        json_true=bool(re.search(r'(?i)"(?:passed|success|ok)"\s*:\s*true\b',line))
        if json_false:
            failing.append(line[:500])
        else:
            if re.search(r"(?i)\b(?:fail(?:ed|ure)?|assert(?:ion)?|mismatch|expected|actual|error|exception|undefined|unresolved)\b",line):
                failing.append(line[:500])
            if json_true or re.search(r"(?i)\b(?:pass(?:ed)?|\bok\b|success(?:ful)?)\b",line):
                passing.append(line[:500])
        if re.search(r"(?i)\bexpected\b",line) and re.search(r"(?i)\b(?:actual|got|received)\b",line):
            mismatches.append(line[:500])

    categories=[]
    probes=(
        ("syntax",r"(?i)\bsyntax(?:error)?\b|parse error|unexpected token|indentationerror"),
        ("type",r"(?i)\btypeerror\b|wrong type|type mismatch|possibly ['\"]?null|not assignable to type"),
        ("name-or-symbol",r"(?i)\bnameerror\b|\breferenceerror\b|cannot find symbol|unresolved reference|not defined"),
        ("assertion",r"(?i)\bassertionerror\b|assertion failed|tests? failed"),
        ("build",r"(?im)compilation failed|build failed|failed to compile|^\s*(?:fatal\s+)?error:\s|^[^\n:]+\.[A-Za-z0-9_]+:\d+(?::\d+)?:\s*(?:fatal\s+)?error:"),
        ("runtime",r"(?i)\bruntimeerror\b|\bexception\b|traceback"),
        ("timeout",r"(?i)timeout|timed out"),
        ("behavior-mismatch",r"(?i)expected[\s\S]{0,240}(?:actual|got|received)|(?:actual|got|received)[\s\S]{0,240}expected"),
        ("lint",r"(?i)\blint(?:er|ing)?\b|\beslint\b|\bruff\b|\bflake8\b|\bpylint\b|\d+:\d+\s+error\s+.*\b[A-Za-z][\w-]+\b"),
        ("typecheck",r"(?i)\btypecheck\b|type-check|\bmypy\b|\bpyright\b|\btsc\b|\berror\s+TS\d{3,6}\b|typescript[^\n]*error"),
        ("dependency",r"(?i)module not found|no module named|cannot resolve|package[^\n]*not found|dependency|\bmodulenotfounderror\b|\bimporterror\b"),
    )
    for name,pattern in probes:
        if re.search(pattern,text):
            categories.append(name)

    locations=[]
    def add_location(value):
        value=str(value or "").strip()
        if value and value not in locations:
            locations.append(value[:300])

    for match in re.finditer(r"(?m)([A-Za-z0-9_./\\-]+\.[A-Za-z0-9_]+):(\d+)(?::(\d+))?",text):
        add_location(":".join(x for x in match.groups() if x))
    for match in re.finditer(r"(?m)([A-Za-z0-9_./\\-]+\.(?:ts|tsx))\((\d+),(\d+)\)",text,re.I):
        add_location(":".join(match.groups()))
    for match in re.finditer(r'(?i)File "([^"]+)", line (\d+)(?:, in ([^\n]+))?',text):
        add_location(":".join(x for x in match.groups() if x))
    for match in re.finditer(r"(?i)\bline\s+(\d+)(?:[, :]\s*column\s+(\d+))?",text):
        add_location("line:"+":".join(x for x in match.groups() if x))

    current_file=""
    for line in lines:
        if re.match(r"^(?:[A-Za-z]:)?[/\\].+\.[A-Za-z0-9_]+$",line) or re.match(r"^[A-Za-z0-9_./\\-]+\.[A-Za-z0-9_]+$",line):
            current_file=line
            continue
        match=re.match(r"^(\d+):(\d+)\s+(?:error|warning)\b",line,re.I)
        if match and current_file:
            add_location(current_file+":"+match.group(1)+":"+match.group(2))

    test_names=[]
    for line in lines:
        # unittest: FAIL: test_01 (module.Class.test_01)
        match=re.search(r"(?i)^(?:FAIL|ERROR):\s+([A-Za-z_][\w.]*)\s+\(([^)]+)\)",line)
        if match:
            short=str(match.group(1) or "").strip()
            qualified=str(match.group(2) or "").strip()
            value=qualified if qualified and short in qualified else short
            if value and value not in test_names:
                test_names.append(value[:300])
            continue
        # pytest: FAILED tests/test_file.py::test_name - ...
        match=re.search(r"(?i)^FAILED\s+([^\s]+::[^\s]+)",line)
        if match:
            value=str(match.group(1) or "").strip()
            if value and value not in test_names:
                test_names.append(value[:300])
            continue
        # Generic named FAIL/ERROR record, excluding summary tuples like (failures=4).
        match=re.search(r"(?i)^(?:FAIL|FAILED|ERROR)\s+([^\s:]+(?:::[^\s:]+)*)",line)
        if match:
            value=str(match.group(1) or "").strip()
            if value and not value.startswith("(") and "=" not in value and value not in test_names:
                test_names.append(value[:300])
            continue
        match=re.search(r"^[✕×]\s+(.+)$",line)
        if match:
            name=match.group(1).strip()[:300]
            if name and name not in test_names:
                test_names.append(name)

    passing.extend("PASS "+case["id"] for case in structured.get("cases",[]) if case.get("status")=="passed")
    for value in structured.get("categories") or []:
        if value not in categories:
            categories.append(value)
    for value in structured.get("failingTests") or []:
        if value not in test_names:
            test_names.append(value)
    for value in structured.get("expectedActual") or []:
        if value not in mismatches:
            mismatches.append(value)
    for value in structured.get("failureSignals") or []:
        if value not in failing:
            failing.append(value)
    for value in structured.get("sourceLocations") or []:
        add_location(value)

    return {
        "categories":categories[:12],
        "exceptionTypes":exceptions[:8],
        "exitCodes":exit_codes[:8],
        "failingSignals":_unique(failing)[:12],
        "passingSignals":_unique(passing)[:8],
        "expectedActual":_unique(mismatches)[:8],
        "sourceLocations":locations[:12],
        "failingTests":test_names[:12],
        "reportedSymbols":_reported_symbols(text),
        "reportedDependencies":_reported_dependencies(text),
        "structuredReceipt":{
            "formats":structured.get("formats") or [],
            "jsonObjectCount":int(structured.get("jsonObjectCount") or 0),
            "caseCount":int(structured.get("caseCount") or 0),
            "failedCaseCount":int(structured.get("failedCaseCount") or 0),
        },
        "behaviorCases":[dict(item) for item in (structured.get("cases") or [])[:40] if isinstance(item,dict)],
    }


def _failure_receipt_detected(text: str) -> bool:
    """Recognize execution receipts after separating source fences from output evidence."""
    evidence=_receipt_evidence_text(text)
    return _receipt_shape_detected(evidence)


def _repair_actions(semantics: dict[str, Any]) -> list[str]:
    categories=set(str(x) for x in (semantics.get("categories") or []))
    actions=[]
    mapping=(
        ("syntax","repair parser/syntax failure at the reported source location before changing behavior"),
        ("name-or-symbol","restore or correctly resolve the reported identifier/module/symbol without renaming required public APIs"),
        ("type","trace concrete runtime types through the failing operation and change the operation or validation causing the mismatch"),
        ("assertion","map each failing assertion to the exact source operation that produces its observed value"),
        ("behavior-mismatch","change the producer of the actual value so it matches the expected contract; do not patch only the displayed example"),
        ("build","repair the failing build/compile stage while preserving unrelated build configuration"),
        ("runtime","trace the exception to its first relevant application frame and repair the causing state/operation"),
        ("timeout","remove the blocking/unbounded operation while preserving required ordering and completion semantics"),
        ("lint","repair the reported lint rule at the implicated source without changing unrelated behavior"),
        ("typecheck","repair the static type mismatch at the producer/consumer boundary while preserving runtime semantics"),
        ("dependency","repair the import/module/dependency boundary using only dependencies supported by project evidence"),
    )
    for key,action in mapping:
        if key in categories: actions.append(action)
    if not actions:
        actions.append("use the failing receipt to identify the first concrete failing operation, then change that operation while preserving passing behavior")
    return actions[:6]


def _user_failure_evidence(prompt: str, history: list[dict[str, Any]]) -> dict[str, Any] | None:
    raw=str(prompt or "").strip()
    receipt_text=_receipt_evidence_text(raw)
    if not _receipt_shape_detected(receipt_text):
        return None

    assistants=[m for m in reversed(history or []) if isinstance(m,dict) and str(m.get("role") or "")=="assistant"]
    code_assistants=[]
    for item in assistants:
        meta=item.get("meta") if isinstance(item.get("meta"),dict) else {}
        item_text=str(item.get("content") or item.get("text") or "")
        if _provider_read_display(item):
            continue
        fenced_source=_inline_source_from_prompt(item_text)
        if meta.get("codeArtifactId") or fenced_source:
            code_assistants.append(item)
    prior=code_assistants[0] if code_assistants else None
    prior_text=str((prior or {}).get("content") or (prior or {}).get("text") or "").strip()
    prior_meta=(prior or {}).get("meta") if isinstance((prior or {}).get("meta"),dict) else {}
    assistant_source=str(prior_meta.get("artifactSourceSnapshot") or "").strip()
    if not assistant_source:
        assistant_source=_inline_source_from_prompt(prior_text)
    if not assistant_source and prior_text and prior_meta.get("codeArtifactId") and "```" in prior_text:
        assistant_source=_candidate_primary_code(prior_text)

    inline_source=_inline_source_from_prompt(raw)
    historical_user_source,historical_user_source_id=_latest_user_source(history or [])
    raw_norm=" ".join(raw.lower().split())
    user_seed_markers=("original user seed","original seed","user seed","provided source","supplied source","baseline source","original source")
    assistant_owned=any(marker in raw_norm for marker in ("your code","your function","your candidate","assistant code","assistant candidate","previous response","previous assistant"))
    explicit_user_seed=bool(inline_source) or any(marker in raw_norm for marker in user_seed_markers)

    if explicit_user_seed and not assistant_owned:
        ownership="user-seed"
        repair_source=inline_source or historical_user_source
        repair_source_message_id="" if inline_source else historical_user_source_id
        repair_target_message_id=""
        repair_target_artifact_id=""
        repair_target_artifact_revision=0
        repair_target_artifact_source_hash=""
    else:
        ownership="previous-assistant-candidate"
        repair_source=assistant_source
        repair_source_message_id=str((prior or {}).get("id") or "")
        meta=(prior or {}).get("meta") if isinstance((prior or {}).get("meta"),dict) else {}
        repair_target_message_id=repair_source_message_id
        repair_target_artifact_id=str(meta.get("codeArtifactId") or "")
        repair_target_artifact_revision=int(meta.get("artifactRevision") or 0)
        repair_target_artifact_source_hash=str(meta.get("artifactSourceHash") or "")

    if not repair_source:
        return None

    repair_source_fingerprint=_code_fingerprint(repair_source)
    exact_repeat_count=0
    if repair_source_fingerprint:
        for item in history or []:
            if not isinstance(item,dict) or str(item.get("role") or "")!="assistant":
                continue
            candidate=str(item.get("content") or item.get("text") or "")
            if _code_fingerprint(candidate)==repair_source_fingerprint:
                exact_repeat_count+=1

    receipt_failure_lines=[
        line.strip()[:500]
        for line in receipt_text.splitlines()
        if re.search(r"(?i)\b(?:fail(?:ed|ure)?|assert(?:ion)?|expected|actual|mismatch|error|exception|undefined|unresolved)\b",line)
        or re.search(r'(?i)"(?:passed|success|ok)"\s*:\s*false\b',line)
    ][:12]
    semantics=_receipt_semantics(receipt_text)
    return {
        "schema":"swrlz-user-failure-evidence-v6",
        "kind":"execution-failure",
        "source":"user-response",
        "evidence":receipt_text[:6000],
        "receiptTextSeparatedFromSource":True,
        "receiptSourceOwnership":ownership,
        "repairTarget":ownership,
        "repairTargetMessageId":repair_target_message_id,
        "repairTargetArtifactId":repair_target_artifact_id,
        "repairTargetArtifactRevision":repair_target_artifact_revision,
        "repairTargetArtifactSourceHash":repair_target_artifact_source_hash,
        "repairSource":repair_source,
        "repairSourceMessageId":repair_source_message_id,
        "repairSourceFingerprint":repair_source_fingerprint,
        "candidateFingerprint":repair_source_fingerprint,
        "repairComparator":"canonical-repair-source",
        "previousAssistantCandidateId":str((prior or {}).get("id") or ""),
        "previousAssistantCandidateComparable":bool(assistant_source),
        "exactCandidateRepeatCount":exact_repeat_count,
        "stalledRepair":exact_repeat_count>=1,
        "failureSignals":receipt_failure_lines,
        "receiptSemantics":semantics,
        "repairActions":_repair_actions(semantics),
        "requiresExternalVerification":True,
    }

def _looks_like_failure_receipt(text: str) -> bool:
    return _failure_receipt_detected(text)

def _original_programming_request(history: list[dict[str, Any]]) -> str:
    """Recover the earliest user request in the current coding exchange, excluding execution receipts."""
    for item in history or []:
        if not isinstance(item,dict) or str(item.get("role") or "")!="user":
            continue
        text=str(item.get("content") or item.get("text") or "").strip()
        if not text or _looks_like_failure_receipt(text):
            continue
        if _current_programming_signal(text):
            return text
    return ""

def _behavior_suite_key(case_ids: list[str]) -> str:
    values=sorted(_unique([str(x) for x in case_ids if str(x).strip()]))
    if not values:
        return ""
    return hashlib.sha256("\n".join(values).encode("utf-8")).hexdigest()[:20]


def _artifact_snapshot_for_lineage(
    history: list[dict[str, Any]],
    artifact_id: str,
    revision: int,
    source_hash: str,
) -> str:
    aid=str(artifact_id or "")
    rev=int(revision or 0)
    sh=str(source_hash or "")
    if not aid or rev<=0:
        return ""
    for item in reversed(history or []):
        if not isinstance(item,dict) or str(item.get("role") or "")!="assistant":
            continue
        meta=item.get("meta") if isinstance(item.get("meta"),dict) else {}
        if str(meta.get("codeArtifactId") or meta.get("updatedCodeArtifactId") or "")!=aid:
            continue
        if int(meta.get("artifactRevision") or 0)!=rev:
            continue
        candidate_hash=str(meta.get("artifactSourceHash") or "")
        if sh and candidate_hash and candidate_hash!=sh:
            continue
        snapshot=str(meta.get("artifactSourceSnapshot") or "").strip()
        if snapshot:
            return snapshot
    return ""


def _behavior_ledger(
    prior_state: dict[str, Any],
    new_failure_evidence: dict[str, Any] | None,
) -> dict[str, Any]:
    """Accumulate only externally observed named test behavior across one repair lineage."""
    prior=prior_state.get("behaviorLedger") if isinstance(prior_state.get("behaviorLedger"),dict) else {}
    semantics=(new_failure_evidence or {}).get("receiptSemantics") if isinstance((new_failure_evidence or {}).get("receiptSemantics"),dict) else {}
    raw_cases=[dict(x) for x in (semantics.get("behaviorCases") or []) if isinstance(x,dict) and str(x.get("id") or "").strip()][:40]
    if not raw_cases:
        return dict(prior) if prior else {
            "schema":"swrlz-behavior-ledger-v1",
            "suiteKey":"",
            "currentPassingCases":[],"currentFailingCases":[],
            "previousPassingCases":[],"previousFailingCases":[],
            "knownPassingCases":[],"preservePassingCases":[],
            "resolvedCases":[],"regressedCases":[],"newlyPassingCases":[],
            "currentScore":None,"bestKnownScore":None,
            "currentTestedArtifact":None,"bestKnownArtifact":None,
            "rebaseRecommended":False,
        }

    current_ids=_unique([str(x.get("id") or "") for x in raw_cases if str(x.get("id") or "").strip()])
    current_passing=_unique([str(x.get("id") or "") for x in raw_cases if x.get("status")=="passed"])
    current_failing=_unique([str(x.get("id") or "") for x in raw_cases if x.get("status")=="failed"])
    suite_key=_behavior_suite_key(current_ids)

    prior_suite=str(prior.get("suiteKey") or "")
    comparable=bool(prior_suite and suite_key and prior_suite==suite_key)
    previous_passing=list(prior.get("currentPassingCases") or []) if comparable else []
    previous_failing=list(prior.get("currentFailingCases") or []) if comparable else []
    prior_known=list(prior.get("knownPassingCases") or []) if comparable else []
    known_passing=_unique(prior_known+current_passing)
    regressed=[x for x in current_failing if x in prior_known]
    resolved=[x for x in current_passing if x in previous_failing]
    newly_passing=[x for x in current_passing if x not in prior_known]
    preserved=[x for x in current_passing if x in prior_known]

    target={
        "artifactId":str((new_failure_evidence or {}).get("repairTargetArtifactId") or ""),
        "revision":int((new_failure_evidence or {}).get("repairTargetArtifactRevision") or 0),
        "sourceHash":str((new_failure_evidence or {}).get("repairTargetArtifactSourceHash") or ""),
        "sourceFingerprint":str((new_failure_evidence or {}).get("repairSourceFingerprint") or ""),
    }
    current_score={"passed":len(current_passing),"total":len(current_ids),"failed":len(current_failing)}

    prior_best=prior.get("bestKnownScore") if isinstance(prior.get("bestKnownScore"),dict) else None
    prior_best_artifact=prior.get("bestKnownArtifact") if isinstance(prior.get("bestKnownArtifact"),dict) else None
    if comparable and prior_best and int(prior_best.get("total") or 0)==len(current_ids):
        best_score=dict(prior_best)
        best_artifact=dict(prior_best_artifact or {})
        if len(current_passing)>int(prior_best.get("passed") or 0):
            best_score=dict(current_score)
            best_artifact=dict(target)
    else:
        best_score=dict(current_score)
        best_artifact=dict(target)

    rebase=bool(
        comparable
        and best_score
        and int(best_score.get("total") or 0)==len(current_ids)
        and len(current_passing)<int(best_score.get("passed") or 0)
        and best_artifact
        and (
            str(best_artifact.get("sourceHash") or "")!=str(target.get("sourceHash") or "")
            or int(best_artifact.get("revision") or 0)!=int(target.get("revision") or 0)
        )
    )

    obligations=[]
    by_id={str(x.get("id") or ""):x for x in raw_cases}
    for case_id in current_failing:
        item=by_id.get(case_id) or {}
        obligations.append({
            "caseId":case_id,
            "kind":"restore-regression" if case_id in regressed else "fix-current-failure",
            "expected":item.get("expected"),
            "actual":item.get("actual"),
            "message":item.get("message"),
        })

    return {
        "schema":"swrlz-behavior-ledger-v1",
        "suiteKey":suite_key,
        "receiptComparableToPrevious":comparable,
        "currentPassingCases":current_passing[:40],
        "currentFailingCases":current_failing[:40],
        "previousPassingCases":previous_passing[:40],
        "previousFailingCases":previous_failing[:40],
        "knownPassingCases":known_passing[:40],
        "preservePassingCases":known_passing[:40],
        "preservedPassingCases":preserved[:40],
        "resolvedCases":resolved[:40],
        "regressedCases":regressed[:40],
        "newlyPassingCases":newly_passing[:40],
        "currentScore":current_score,
        "bestKnownScore":best_score,
        "currentTestedArtifact":target,
        "bestKnownArtifact":best_artifact,
        "rebaseRecommended":rebase,
        "repairObligations":obligations[:24],
    }


def _behavior_repair_base(
    ledger: dict[str, Any],
    evidence: dict[str, Any] | None,
    history: list[dict[str, Any]],
) -> dict[str, Any]:
    latest_source=str((evidence or {}).get("repairSource") or "")
    latest_fp=str((evidence or {}).get("repairSourceFingerprint") or "") or _code_fingerprint(latest_source)
    best=ledger.get("bestKnownArtifact") if isinstance(ledger.get("bestKnownArtifact"),dict) else {}
    if ledger.get("rebaseRecommended") and best:
        best_source=_artifact_snapshot_for_lineage(
            history,
            str(best.get("artifactId") or ""),
            int(best.get("revision") or 0),
            str(best.get("sourceHash") or ""),
        )
        best_fp=_code_fingerprint(best_source)
        if best_source and best_fp and best_fp!=latest_fp:
            return {
                "mode":"best-known-tested-source",
                "source":best_source,
                "sourceFingerprint":best_fp,
                "artifactId":str(best.get("artifactId") or ""),
                "revision":int(best.get("revision") or 0),
                "sourceHash":str(best.get("sourceHash") or ""),
            }
    return {
        "mode":"latest-failing-source",
        "source":latest_source,
        "sourceFingerprint":latest_fp,
        "artifactId":str((evidence or {}).get("repairTargetArtifactId") or ""),
        "revision":int((evidence or {}).get("repairTargetArtifactRevision") or 0),
        "sourceHash":str((evidence or {}).get("repairTargetArtifactSourceHash") or ""),
    }


def _dependency_policy(original_request: str) -> str:
    prose=_norm(_strip_fenced_code(original_request))
    if re.search(r"\b(?:standard library|stdlib|built[- ]?ins? only|built in only)\b",prose,re.I):
        return "standard-library-only"
    if re.search(r"\b(?:do not|don't|without|no)\s+(?:install|installation|external dependenc|third[- ]party|package)\b",prose,re.I):
        return "no-install"
    return "evidence-bounded"


def _explicit_dependency_release(text: str, dependency: str) -> bool:
    raw=str(text or "")
    dep=re.escape(str(dependency or ""))
    if not dep:
        return False
    patterns=(
        r"(?i)\b"+dep+r"\b.{0,80}\b(?:is|was)\s+(?:now\s+)?(?:installed|available|present)\b",
        r"(?i)\b(?:installed|available|present)\b.{0,80}\b"+dep+r"\b",
    )
    return any(re.search(pattern,raw) for pattern in patterns)


def _repair_constraints(
    prior_state: dict[str, Any],
    new_failure_evidence: dict[str, Any] | None,
    active_contract: dict[str, Any],
    current_text: str,
) -> dict[str, Any]:
    prior=prior_state.get("repairConstraints") if isinstance(prior_state.get("repairConstraints"),dict) else {}
    unavailable=_unique([str(x) for x in (prior.get("unavailableDependencies") or []) if str(x).strip()])
    previous_unavailable=list(unavailable)

    prior_evidence=prior_state.get("failureEvidence") if isinstance(prior_state.get("failureEvidence"),dict) else {}
    prior_semantics=prior_evidence.get("receiptSemantics") if isinstance(prior_evidence.get("receiptSemantics"),dict) else {}
    for dep in prior_semantics.get("reportedDependencies") or []:
        value=str(dep or "").strip()
        if value and value not in unavailable:
            unavailable.append(value)

    current_semantics=(new_failure_evidence or {}).get("receiptSemantics") if isinstance((new_failure_evidence or {}).get("receiptSemantics"),dict) else {}
    current_dependencies=_unique([str(x) for x in (current_semantics.get("reportedDependencies") or []) if str(x).strip()])
    added=[]
    for dep in current_dependencies:
        if dep not in unavailable:
            unavailable.append(dep)
            added.append(dep)

    released=[]
    for dep in list(unavailable):
        if _explicit_dependency_release(current_text,dep):
            unavailable.remove(dep)
            released.append(dep)

    original_request=str(active_contract.get("originalRequest") or "")
    policy=_dependency_policy(original_request)
    carried=[dep for dep in unavailable if dep in previous_unavailable and dep not in current_dependencies]
    return {
        "schema":"swrlz-repair-constraints-v1",
        "dependencyPolicy":policy,
        "unavailableDependencies":unavailable[:16],
        "forbiddenDependencies":unavailable[:16],
        "currentReceiptDependencies":current_dependencies[:16],
        "addedDependencies":added[:16],
        "carriedUnavailableDependencies":carried[:16],
        "releasedDependencies":released[:16],
        "constraintCount":len(unavailable),
    }


def programming_intent(prompt: str, history: list[dict[str, Any]], pinned_context: list[dict[str, Any]], prior_state: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return bounded semantic routing metadata consumed by the Workstation."""
    text=str(prompt or "").strip()
    p=_norm(text)
    pins=_code_pins(pinned_context or [])
    prior_state=prior_state if isinstance(prior_state,dict) else {}
    prior_contract=prior_state.get("intentContract") if isinstance(prior_state.get("intentContract"),dict) else {}
    prior_failure_evidence=prior_state.get("failureEvidence") if isinstance(prior_state.get("failureEvidence"),dict) else {}
    last_artifact=_last_assistant_artifact(history or [])
    new_project=any(x in p for x in _NEW_PROJECT) or _fresh_web_project_request(text)
    # A prior false-positive coding contract is not authority by itself.
    # Keep legitimate explicit programming requests and authored artifacts.
    if (prior_contract and not (pins or last_artifact or
            _current_programming_signal(str(prior_contract.get("originalRequest") or "")))):
        prior_contract={}
    new_failure_evidence=_user_failure_evidence(text,[] if new_project else (history or []))
    failure_evidence=new_failure_evidence
    vague_failure=not new_project and _vague_failure_report(text) and bool(prior_contract or last_artifact or pins)
    prior_failure_history=prior_state.get("failureHistory") if not new_project and isinstance(prior_state.get("failureHistory"),list) else []
    failure_history=[dict(x) for x in prior_failure_history[-3:] if isinstance(x,dict)]
    if new_failure_evidence:
        failure_history.append({
            "categories":list((failure_evidence.get("receiptSemantics") or {}).get("categories") or [])[:6],
            "failureSignals":list(failure_evidence.get("failureSignals") or [])[:8],
            "candidateFingerprint":failure_evidence.get("candidateFingerprint"),
            "repairActions":list(failure_evidence.get("repairActions") or [])[:6],
            "reportedDependencies":list((failure_evidence.get("receiptSemantics") or {}).get("reportedDependencies") or [])[:12],
            "structuredReceipt":dict((failure_evidence.get("receiptSemantics") or {}).get("structuredReceipt") or {}),
        })
        failure_history=failure_history[-4:]
    correction_direction=bool(prior_contract) and any(x in p for x in ("still","instead","required","requirement","must","should","keep","preserve","do not","don't","wrong","incorrect","guidance","fix","repair","change only","return only"))
    canonical_carry=bool(prior_contract) and not new_failure_evidence and not vague_failure and correction_direction and not any(x in p for x in _NEW_PROJECT)
    if canonical_carry and not failure_evidence and prior_failure_evidence:
        failure_evidence=dict(prior_failure_evidence)
        failure_evidence["source"]="prior-repair-lineage"
        failure_evidence["continuedByGuidance"]=True
    original_request=_original_programming_request(history or []) if new_failure_evidence else ""
    continuation_reference=_programming_continuation_signal(text)
    inherited=continuation_reference and (bool(pins) or bool(prior_contract) or bool(last_artifact))
    coding=not _source_information_request(text,history) and (_current_programming_signal(text) or inherited or bool(failure_evidence) or vague_failure)
    if not coding:
        return {
            "schema":"swrlz-programming-intent-v1",
            "codingTask":False,"projectContext":"none","changeClass":"none",
            "artifactContinuation":False,"artifactMutationRequested":False,
            "artifactTargetId":"","artifactTargetMessageId":"","baseRevision":0,"baseSourceHash":"",
            "newProject":False,"source":"brain-router"
        }

    if new_project:
        # A fresh artifact must not inherit another project's heading, repair
        # target, unavailable dependency list or behavior score.
        prior_contract={}
        canonical_carry=False
        failure_evidence=new_failure_evidence
        failure_history=failure_history[-1:] if new_failure_evidence else []
    if failure_evidence or vague_failure:
        change="fix"
    elif new_project:
        change="create"
    elif any(x in p for x in _FIX):
        change="fix"
    elif any(x in p for x in _REFACTOR):
        change="refactor"
    elif last_artifact and re.search(r"\b(?:make|turn|convert|transform|upgrade)\s+(?:this|that|it|the\s+existing)\b",p):
        change="feature"
    elif any(x in p for x in _FEATURE):
        change="feature"
    elif last_artifact and re.match(
            r"^(?:(?:now|please|then|next|and|also|okay|ok)\s+|(?:can|could|would|will)\s+you\s+|"
            r"i\s+(?:want|need)\s+you\s+to\s+)*(?:edit|update|change|modify|revise|continue)\b",p):
        change="feature"
    elif any(x in p for x in _REVIEW):
        change="review"
    elif any(x in p for x in _EXPLAIN):
        change="explain"
    else:
        change="create" if not pins else "feature"

    explicit_reference=_programming_continuation_signal(text) or any(
        _norm((value.get("path") or value.get("file") or "") if isinstance(value,dict) else value) in p
        for item in pins for value in (item.get("files") or [])
        if _norm((value.get("path") or value.get("file") or "") if isinstance(value,dict) else value)
    )
    target=_pick_artifact_target(text,pins) if (bool(pins) and not new_project and explicit_reference) else None
    if (target is None and not new_project and explicit_reference
            and change in ("feature","fix","refactor","migrate")
            and last_artifact.get("artifactId")
            and int(last_artifact.get("artifactRevision") or 0)>0
            and re.fullmatch(r"[a-f0-9]{64}",str(last_artifact.get("artifactSourceHash") or ""))):
        # Canonical Station history supplies revision identities. Authored code
        # alone never invents a persistent mutation target or bypasses the
        # Station's owned-thread/revision/hash checks.
        target=dict(last_artifact)
    artifact_id=str((target or {}).get("artifactId") or "")
    target_message_id=str((target or {}).get("messageId") or "")
    base_revision=int((target or {}).get("artifactRevision") or 0)
    base_source_hash=str((target or {}).get("artifactSourceHash") or "")
    if failure_evidence and failure_evidence.get("repairTargetArtifactId"):
        artifact_id=str(failure_evidence.get("repairTargetArtifactId") or "")
        target_message_id=str(failure_evidence.get("repairTargetMessageId") or "")
        base_revision=int(failure_evidence.get("repairTargetArtifactRevision") or 0)
        base_source_hash=str(failure_evidence.get("repairTargetArtifactSourceHash") or "")
    elif vague_failure and last_artifact:
        artifact_id=str(last_artifact.get("artifactId") or "")
        target_message_id=str(last_artifact.get("messageId") or "")
        base_revision=int(last_artifact.get("artifactRevision") or 0)
        base_source_hash=str(last_artifact.get("artifactSourceHash") or "")
    continuation=bool(artifact_id or target)
    mutation=bool(continuation and change in {"fix","refactor","feature","migrate"} and not vague_failure)

    last_source=str((last_artifact or {}).get("text") or "")
    web_source_continuation=bool(not new_project and continuation_reference
        and re.search(r"<!doctype\s+html\b|<html\b",last_source,re.I))
    source_edit=web_source_continuation and change in ("feature","fix","refactor","migrate")
    if prior_contract and (failure_evidence or vague_failure or canonical_carry or source_edit):
        active_contract=dict(prior_contract)
        if not isinstance(active_contract.get("languageContract"),dict):
            source_request=str(active_contract.get("originalRequest") or original_request or text)
            active_contract["languageContract"]=_language_contract(source_request)
            active_contract["schema"]="swrlz-programming-intent-contract-v3"
    else:
        active_contract=_programming_intent_contract(original_request or text,change)
    if source_edit:
        delta=_programming_intent_contract(text,change)
        active_contract=dict(active_contract)
        for key in ("must","mustNot","preserve"):
            active_contract[key]=_unique(list(active_contract.get(key) or [])+list(delta.get(key) or []))[:24]
        active_contract["currentInstruction"]=text
    requested_literals=_literal_ui_text(text)
    if requested_literals:
        active_contract=dict(active_contract)
        previous_literals=list(active_contract.get("literalUiText") or [])
        # Explicitly replacing text retires the old literal condition; it does
        # not require both the old and replacement title simultaneously.
        if re.search(r"\b(?:set|change|replace|rename)\b",text,re.I):
            replaced_targets={item.get("target") for item in requested_literals}
            previous_literals=[item for item in previous_literals if item.get("target") not in replaced_targets]
        active_contract["literalUiText"]=(previous_literals+[item for item in requested_literals if item not in previous_literals])[:8]

    # A concrete application page has an implicit browser-source medium. A
    # follow-up such as adding a heading also retains the supplied HTML source
    # medium, without inventing a pin, artifact target or persistent mutation.
    active_language=active_contract.get("languageContract") or {}
    explicit_web_request=requests_web_source(text)
    chosen_frontend=bool(re.search(r"\b(?:react|next(?:\.js|js)?|vue|nuxt|svelte|angular|astro|vite|webpack|parcel)\b",_strip_fenced_code(text),re.I))
    if (not active_language.get("requestedLanguages")
            and (web_source_continuation or (explicit_web_request and not chosen_frontend))):
        active_contract=dict(active_contract)
        active_contract["languageContract"]={
            **active_language,
            "explicit":False,
            "requestedLanguages":[],
            "requiredLanguages":["html"],
            "allowedCompanionLanguages":["css","javascript"],
            "allowedLanguages":["html","css","javascript"],
            "artifactType":"web-page",
            "substitutionAllowed":False,
            "inferredFrom":"html-source-continuation" if web_source_continuation else "application-page-request",
        }

    # Named interactive applications carry bounded capability defaults. The
    # original source request remains authoritative; explicit narrower user
    # scope replaces the default and survives compact repair context.
    if not active_contract.get("applicationCapabilities"):
        active_contract=apply_application_contract(active_contract,_strip_fenced_code(str(active_contract.get("originalRequest") or "")))
    active_contract=apply_application_contract(active_contract,_strip_fenced_code(text))

    active_contract=_apply_implementation_contract(active_contract,text)
    active_contract=_apply_literal_ui_contract(active_contract)

    repair_constraints=_repair_constraints(
        {} if new_project else prior_state,
        new_failure_evidence,
        active_contract,
        text,
    )
    behavior_ledger=_behavior_ledger({} if new_project else prior_state,new_failure_evidence)
    if canonical_carry and not new_failure_evidence and isinstance(prior_state.get("behaviorLedger"),dict):
        behavior_ledger=dict(prior_state.get("behaviorLedger") or {})
    behavior_repair_base=_behavior_repair_base(
        behavior_ledger,
        failure_evidence,
        history or [],
    )

    evidence_request=(
        "I can repair it, but I need the failure evidence first. Paste the compiler, test, runtime, browser-console, linter, or type-checker error output you get. "
        "Include the file/line it points to if that is shown."
        if vague_failure else ""
    )
    return {
        "schema":"swrlz-programming-intent-v1",
        "codingTask":True,
        "projectContext":"new" if new_project else ("existing" if continuation or pins or web_source_continuation or
            re.search(r"\b(?:existing\s+project|repo(?:sitory)?|github)\b", _strip_fenced_code(text), re.I) else "none"),
        "changeClass":change,
        "artifactContinuation":continuation,
        "artifactMutationRequested":mutation,
        "artifactTargetId":artifact_id,
        "artifactTargetMessageId":target_message_id,
        "artifactEditSource":str((target or {}).get("text") or "") if mutation else "",
        "baseRevision":base_revision,
        "baseSourceHash":base_source_hash,
        "newProject":new_project,
        "pinnedCodeArtifactCount":len(pins),
        "intentContract":active_contract,
        "repairDirection":text if ((failure_evidence and original_request) or canonical_carry) else "",
        "canonicalCarry":canonical_carry,
        "failureEvidence":failure_evidence,
        "failureHistory":failure_history,
        "repairConstraints":repair_constraints,
        "behaviorLedger":behavior_ledger,
        "behaviorRepairBase":{
            "mode":behavior_repair_base.get("mode"),
            "sourceFingerprint":behavior_repair_base.get("sourceFingerprint"),
            "artifactId":behavior_repair_base.get("artifactId"),
            "revision":behavior_repair_base.get("revision"),
            "sourceHash":behavior_repair_base.get("sourceHash"),
        },
        "behaviorRepairBaseSource":str(behavior_repair_base.get("source") or ""),
        "needsFailureEvidence":vague_failure,
        "evidenceRequest":evidence_request,
        "repairLifecycleState":"EVIDENCE_REQUIRED" if vague_failure else ("REPAIR_CANDIDATE" if failure_evidence else "CANDIDATE_GENERATION"),
        "source":"brain-router",
    }

