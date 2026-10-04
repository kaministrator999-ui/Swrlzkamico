"""Brain-owned bounded programming/artifact routing for the HF candidate.

This module classifies semantic programming continuation only. It never mutates
threads, pins, artifacts, files, tools, deployments, or other operational state.
"""
from __future__ import annotations
import hashlib
from typing import Any
import re

_CODE_TERMS=("code","html","css","javascript","typescript","python","kotlin","java","cpp","c++","function","class","file","project","api","server","bug","compile","website","webpage","web page","frontend","ui","interface","dom","responsive","layout","component","debug","syntax")
_NEW_PROJECT=("separate project","separately","new project","another project","different project","from scratch","unrelated project")
_FIX=("fix","bug","broken","error","issue","repair","patch")
_REFACTOR=("refactor","clean up","cleanup","restructure","optimize")
_FEATURE=("add","implement","feature","support","extend","include")
_REVIEW=("review","audit","inspect","check this","find the error","find the bug","what is wrong","validate","verify")
_EXPLAIN=("explain","what does","how does","walk me through")
_CONTINUATION=("this","that","it","same","previous","pinned","code","file","project","continue","keep going","update","change","modify")

_LANGUAGE_PATTERNS=(
    ("html",(r"\bhtml5?\b",)),
    ("css",(r"\bcss3?\b",)),
    ("typescript",(r"\btypescript\b",r"\btsx\b")),
    ("javascript",(r"\bjavascript\b",r"\becmascript\b",r"\bvanilla\s+js\b",r"\bnode(?:\.js|js)\b")),
    ("python",(r"\bpython\b",r"\bpython3\b")),
    ("kotlin",(r"\bkotlin\b",)),
    ("java",(r"\bjava\b",)),
    ("cpp",(r"\bc\+\+\b",r"\bcpp\b",r"\bcxx\b")),
    ("csharp",(r"\bc#\b",r"\bcsharp\b",r"\bc\s*sharp\b")),
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
"""

def _norm(value: Any) -> str:
    return " ".join(str(value or "").lower().split())


def _code_pins(pinned_context: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result=[]
    for item in pinned_context:
        if not isinstance(item,dict):
            continue
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
    return re.sub(r"```[\s\S]*?```"," [CODE_PAYLOAD] ",str(text or ""),flags=re.M)


def _unique(values: list[str]) -> list[str]:
    result=[]
    for value in values:
        if value and value not in result:
            result.append(value)
    return result


def _artifact_type_from_request(text: str) -> str:
    prose=_norm(_strip_fenced_code(text))
    if any(x in prose for x in ("web page","webpage","html page","website","landing page")):
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
    requested=_explicit_languages(text)
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
    fences=list(re.finditer(r"```([^\n`]*)\n([\s\S]*?)```",source))
    recognized_fence=False
    for match in fences:
        language=_normalize_language_tag(match.group(1))
        if language:
            detected.append(language)
            recognized_fence=True
    if recognized_fence:
        return _unique(detected)
    body="\n".join(match.group(2) for match in fences) if fences else source
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


def _candidate_primary_code(text: str) -> str:
    source=str(text or "").strip()
    fenced=re.findall(r"```[^\n`]*\n([\s\S]*?)```",source)
    return next((part.strip() for part in fenced if part.strip()),source)


def _code_fingerprint(text: str) -> str | None:
    code=_candidate_primary_code(text)
    semantic="\n".join(line for line in code.splitlines() if not re.match(r"^\s*(?:#|//)",line))
    normalized=" ".join(semantic.split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16] if normalized else None


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
    detected=_candidate_languages(text)
    required=[str(x) for x in (language.get("requiredLanguages") or [])]
    allowed=[str(x) for x in (language.get("allowedLanguages") or [])]
    if language.get("explicit"):
        for item in required:
            if item not in detected:
                reasons.append("missing-required-language:"+item)
        for item in detected:
            if item not in allowed:
                reasons.append("language-contract-mismatch:"+item)
    evidence=programming.get("failureEvidence") if isinstance(programming.get("failureEvidence"),dict) else {}
    semantics=evidence.get("receiptSemantics") if isinstance(evidence.get("receiptSemantics"),dict) else {}
    previous=""
    target_mid=str(evidence.get("repairTargetMessageId") or "")
    if evidence.get("receiptSourceOwnership")=="previous-assistant-candidate":
        previous=next((str(m.get("content") or m.get("text") or "") for m in reversed(history or []) if isinstance(m,dict) and str(m.get("role") or "")=="assistant" and (not target_mid or str(m.get("id") or "")==target_mid)),"")
    elif evidence.get("receiptSourceOwnership")=="user-seed":
        previous=str(evidence.get("repairSource") or "")
    if evidence and previous:
        before=_code_fingerprint(previous)
        after=_code_fingerprint(text)
        if before and after and before==after:
            reasons.append("diagnostic-repair-no-executable-change")
    candidate_code=_candidate_primary_code(text)
    for symbol in semantics.get("reportedSymbols") or []:
        if not _symbol_is_resolved_or_removed(candidate_code,str(symbol)):
            reasons.append("diagnostic-symbol-resolution-unproven:"+str(symbol)[:80])
    verification="AWAITING_EXTERNAL_RECEIPT" if evidence else "NOT_EXECUTION_VERIFIED"
    return {
        "status":"REJECT" if reasons else "PASS",
        "reasons":_unique(reasons),
        "languageContract":language,
        "detectedLanguages":detected,
        "diagnosticGrounded":bool(evidence) and not any(x.startswith("diagnostic-") for x in reasons),
        "receiptCategories":list(semantics.get("categories") or [])[:12],
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
        meta=item.get("meta") if isinstance(item.get("meta"),dict) else {}
        text=str(item.get("content") or item.get("text") or "")
        if meta.get("codeArtifactId") or "```" in text:
            return {
                "messageId":str(item.get("id") or ""),
                "artifactId":str(meta.get("codeArtifactId") or ""),
                "artifactRevision":int(meta.get("artifactRevision") or 0),
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
    for clause in clauses[:32]:
        item=" ".join(clause.split())[:500]
        if negative.search(item): must_not.append(item)
        elif preserve_rx.search(item): preserve.append(item)
        elif requirement_rx.search(item): must.append(item)
    if not must and raw:
        must.append("Satisfy the requested "+str(change_class or "programming")+" operation without changing unrelated behavior.")
    evidence.extend([
        "technical-validity: returned candidate must be complete and syntactically/build valid when applicable",
        "intent-validity: original requirements and preservation constraints must be rechecked after every repair",
        "api-validity: required wrapper/name/signature must remain present unless explicitly changed",
    ])
    return {
        "schema":"swrlz-programming-intent-contract-v3","originalRequest":raw[:4000],
        "must":must[:16],"mustNot":must_not[:16],"preserve":preserve[:16],
        "languageContract":_language_contract(raw),
        "acceptanceEvidence":evidence,
        "completionRule":"done only when complete-source, technical validity, and intent validity all pass",
    }


def _extract_candidate_code(text: str) -> str:
    """Return the primary executable candidate, ignoring prose/examples/comments."""
    raw=str(text or "").strip()
    fenced=re.findall(r"```[^\n`]*\n([\s\S]*?)```",raw)
    candidate=next((part for part in fenced if part.strip()),raw)
    lines=[]
    for line in candidate.strip().splitlines():
        stripped=line.strip()
        if not stripped or stripped.startswith(("#","//","/*","*","*/")):
            continue
        lines.append(line.rstrip())
    return "\n".join(lines)



def _receipt_semantics(raw: str) -> dict[str, Any]:
    """Extract bounded, language-agnostic repair facts from compiler/test/runtime logs."""
    text=str(raw or "")
    lines=[line.strip() for line in text.splitlines() if line.strip()]
    exceptions=[]
    for match in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*(?:Error|Exception|Failure))\b",text):
        value=match.group(1)
        if value not in exceptions: exceptions.append(value)
    exit_codes=[]
    for match in re.finditer(r"(?i)\b(?:exit(?:\s+code|\s+status)?|status)\s*[:=]?\s*(-?\d+)\b",text):
        value=int(match.group(1))
        if value not in exit_codes: exit_codes.append(value)
    failing=[]; passing=[]; mismatches=[]
    for line in lines:
        if re.search(r"(?i)\b(?:fail(?:ed|ure)?|assert(?:ion)?|mismatch|expected|actual|error)\b",line):
            failing.append(line[:500])
        elif re.search(r"(?i)\b(?:pass(?:ed)?|ok|success(?:ful)?)\b",line):
            passing.append(line[:500])
        if re.search(r"(?i)\bexpected\b",line) and re.search(r"(?i)\bactual|got|received\b",line):
            mismatches.append(line[:500])
    categories=[]
    probes=(
        ("syntax",r"(?i)syntax|parse error|unexpected token|indentationerror"),
        ("type",r"(?i)typeerror|wrong type|type mismatch"),
        ("name-or-symbol",r"(?i)nameerror|referenceerror|cannot find symbol|unresolved reference|not defined"),
        ("assertion",r"(?i)assertionerror|assertion failed|test failed|tests failed"),
        ("build",r"(?i)compilation failed|build failed|failed to compile"),
        ("runtime",r"(?i)runtimeerror|exception|traceback"),
        ("timeout",r"(?i)timeout|timed out"),
        ("behavior-mismatch",r"(?i)expected.+(?:actual|got|received)|(?:actual|got|received).+expected"),
        ("lint",r"(?i)\\blint(?:er|ing)?\\b|eslint|ruff|flake8|pylint"),
        ("typecheck",r"(?i)typecheck|type-check|mypy|pyright|tsc\\b|typescript.+error"),
        ("dependency",r"(?i)module not found|no module named|cannot resolve|package.+not found|dependency"),
    )
    for name,pattern in probes:
        if re.search(pattern,text): categories.append(name)
    locations=[]
    for pattern in (
        r"(?m)([A-Za-z0-9_./\\-]+\\.[A-Za-z0-9_]+):(\\d+)(?::(\\d+))?",
        r'(?i)File "([^"]+)", line (\\d+)(?:, in ([^\\n]+))?',
        r"(?i)\\bline\\s+(\\d+)(?:[, :]\\s*column\\s+(\\d+))?",
    ):
        for match in re.finditer(pattern,text):
            value=":".join(str(x) for x in match.groups() if x)
            if value and value not in locations: locations.append(value[:300])
    test_names=[]
    for line in lines:
        match=re.search(r"(?i)(?:FAIL|FAILED|ERROR)\\s+([^\\s:]+(?:::[^\\s:]+)*)",line)
        if match and match.group(1) not in test_names:test_names.append(match.group(1)[:300])
    return {
        "categories":categories[:12],"exceptionTypes":exceptions[:8],"exitCodes":exit_codes[:8],
        "failingSignals":failing[:12],"passingSignals":passing[:8],"expectedActual":mismatches[:8],
        "sourceLocations":locations[:12],"failingTests":test_names[:12],
        "reportedSymbols":_reported_symbols(text),
    }


def _failure_receipt_detected(text: str) -> bool:
    """Recognize common compiler, test-runner, build, runtime and CI failure logs."""
    raw=str(text or "")
    if not raw.strip():
        return False
    patterns=(
        r"\b(?:syntaxerror|typeerror|nameerror|referenceerror|assertionerror|indentationerror|runtimeerror|exception|traceback)\b",
        r"\b(?:compilation|build|link|lint|typecheck|test(?:s| suite)?)\s+(?:failed|failure|error)\b",
        r"\b(?:failed to compile|cannot find symbol|unresolved reference|undefined reference|module not found|cannot resolve)\b",
        r"(?im)^\s*(?:FAIL|FAILED|ERROR)\b",
        r"\b(?:exit(?:\s+code|\s+status)?|status)\s*[:=]?\s*[1-9]\d*\b",
        r"\b\d+\s+failed(?:,|\b)",
        r"\bexpected\b[\s\S]{0,240}\b(?:actual|got|received)\b",
        r"\b(?:actual|got|received)\b[\s\S]{0,240}\bexpected\b",
    )
    return any(re.search(pattern,raw,re.I) for pattern in patterns)


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
    if not _failure_receipt_detected(raw):
        return None
    assistants=[m for m in reversed(history or []) if isinstance(m,dict) and str(m.get("role") or "")=="assistant"]
    prior=assistants[0] if assistants else None
    prior_text=str((prior or {}).get("content") or (prior or {}).get("text") or "").strip()
    inline_source=_candidate_primary_code(raw) if "```" in raw else ""
    if not prior and not inline_source:
        return None
    raw_norm=" ".join(raw.lower().split())
    prior_candidate=_extract_candidate_code(prior_text) if prior_text else ""
    prior_norm=" ".join(prior_candidate.lower().split())
    assistant_norms=[]
    for item in history or []:
        if not isinstance(item,dict) or str(item.get("role") or "")!="assistant":
            continue
        candidate_norm=" ".join(_extract_candidate_code(str(item.get("content") or item.get("text") or "")).lower().split())
        if candidate_norm:
            assistant_norms.append(candidate_norm)
    exact_repeat_count=sum(1 for candidate_norm in assistant_norms if prior_norm and candidate_norm==prior_norm)
    receipt_failure_lines=[
        line.strip()[:500]
        for line in raw.splitlines()
        if re.search(r"\b(?:fail(?:ed|ure)?|assert(?:ion)?|expected|actual|mismatch|error|exception|undefined|unresolved)\b",line,re.I)
    ][:12]
    user_seed_markers=("original user seed","original seed","user seed","provided source","supplied source","baseline source","original source")
    seed_owned=bool(inline_source) or any(marker in raw_norm for marker in user_seed_markers)
    assistant_owned=any(marker in raw_norm for marker in ("your code","your function","your candidate","assistant code","assistant candidate","previous response","previous assistant"))
    ownership="user-seed" if seed_owned and not assistant_owned else "previous-assistant-candidate"
    meta=(prior or {}).get("meta") if isinstance((prior or {}).get("meta"),dict) else {}
    semantics=_receipt_semantics(raw)
    return {
        "schema":"swrlz-user-failure-evidence-v5","kind":"execution-failure","source":"user-response",
        "evidence":raw[:6000],"receiptSourceOwnership":ownership,
        "repairTarget":ownership,
        "repairTargetMessageId":str((prior or {}).get("id") or "") if ownership=="previous-assistant-candidate" else "",
        "repairTargetArtifactId":str(meta.get("codeArtifactId") or "") if ownership=="previous-assistant-candidate" else "",
        "repairTargetArtifactRevision":int(meta.get("artifactRevision") or 0) if ownership=="previous-assistant-candidate" else 0,
        "repairSource":inline_source[:12000] if ownership=="user-seed" else "",
        "previousAssistantCandidateId":str((prior or {}).get("id") or ""),
        "previousAssistantCandidateComparable":bool(prior_norm),
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
        if any(term in _norm(text) for term in _CODE_TERMS):
            return text[:4000]
    return ""

def programming_intent(prompt: str, history: list[dict[str, Any]], pinned_context: list[dict[str, Any]], prior_state: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return bounded semantic routing metadata consumed by the Workstation."""
    text=str(prompt or "").strip()
    p=_norm(text)
    pins=_code_pins(pinned_context or [])
    prior_state=prior_state if isinstance(prior_state,dict) else {}
    prior_contract=prior_state.get("intentContract") if isinstance(prior_state.get("intentContract"),dict) else {}
    last_artifact=_last_assistant_artifact(history or [])
    failure_evidence=_user_failure_evidence(text,history or [])
    vague_failure=_vague_failure_report(text) and bool(prior_contract or last_artifact or pins)
    prior_failure_history=prior_state.get("failureHistory") if isinstance(prior_state.get("failureHistory"),list) else []
    failure_history=[dict(x) for x in prior_failure_history[-3:] if isinstance(x,dict)]
    if failure_evidence:
        failure_history.append({
            "categories":list((failure_evidence.get("receiptSemantics") or {}).get("categories") or [])[:6],
            "failureSignals":list(failure_evidence.get("failureSignals") or [])[:8],
            "candidateFingerprint":failure_evidence.get("candidateFingerprint"),
            "repairActions":list(failure_evidence.get("repairActions") or [])[:6],
        })
        failure_history=failure_history[-4:]
    correction_direction=bool(prior_contract) and any(x in p for x in ("still","instead","required","requirement","must","should","keep","preserve","do not","don't","wrong","incorrect","guidance","fix","repair","change only","return only"))
    canonical_carry=bool(prior_contract) and not failure_evidence and not vague_failure and correction_direction and not any(x in p for x in _NEW_PROJECT)
    original_request=_original_programming_request(history or []) if failure_evidence else ""
    recent=" ".join(_norm(m.get("content") or m.get("text")) for m in (history or [])[-4:] if isinstance(m,dict))
    inherited=bool(pins) or bool(prior_contract) or any(term in recent for term in _CODE_TERMS)
    coding=any(term in p for term in _CODE_TERMS) or inherited or bool(failure_evidence) or vague_failure
    if not coding:
        return {
            "schema":"swrlz-programming-intent-v1",
            "codingTask":False,"projectContext":"none","changeClass":"none",
            "artifactContinuation":False,"artifactMutationRequested":False,
            "artifactTargetId":"","artifactTargetMessageId":"","baseRevision":0,
            "newProject":False,"source":"brain-router"
        }

    new_project=any(x in p for x in _NEW_PROJECT)
    if failure_evidence or vague_failure:
        change="fix"
    elif new_project:
        change="create"
    elif any(x in p for x in _FIX):
        change="fix"
    elif any(x in p for x in _REFACTOR):
        change="refactor"
    elif any(x in p for x in _FEATURE):
        change="feature"
    elif any(x in p for x in _REVIEW):
        change="review"
    elif any(x in p for x in _EXPLAIN):
        change="explain"
    else:
        change="create" if not pins else "feature"

    explicit_reference=any(x in p for x in _CONTINUATION) or any(
        _norm((value.get("path") or value.get("file") or "") if isinstance(value,dict) else value) in p
        for item in pins for value in (item.get("files") or [])
        if _norm((value.get("path") or value.get("file") or "") if isinstance(value,dict) else value)
    )
    target=_pick_artifact_target(text,pins) if (bool(pins) and not new_project and explicit_reference) else None
    artifact_id=str((target or {}).get("artifactId") or "")
    target_message_id=str((target or {}).get("messageId") or "")
    base_revision=int((target or {}).get("artifactRevision") or 0)
    if failure_evidence and failure_evidence.get("repairTargetArtifactId"):
        artifact_id=str(failure_evidence.get("repairTargetArtifactId") or "")
        target_message_id=str(failure_evidence.get("repairTargetMessageId") or "")
        base_revision=int(failure_evidence.get("repairTargetArtifactRevision") or 0)
    elif vague_failure and last_artifact:
        artifact_id=str(last_artifact.get("artifactId") or "")
        target_message_id=str(last_artifact.get("messageId") or "")
        base_revision=int(last_artifact.get("artifactRevision") or 0)
    continuation=bool(artifact_id or target)
    mutation=bool(continuation and change in {"fix","refactor","feature","migrate"} and not vague_failure)

    if prior_contract and (failure_evidence or vague_failure or canonical_carry):
        active_contract=dict(prior_contract)
        if not isinstance(active_contract.get("languageContract"),dict):
            source_request=str(active_contract.get("originalRequest") or original_request or text)
            active_contract["languageContract"]=_language_contract(source_request)
            active_contract["schema"]="swrlz-programming-intent-contract-v3"
    else:
        active_contract=_programming_intent_contract(original_request or text,change)

    evidence_request=(
        "I can repair it, but I need the failure evidence first. Paste the compiler, test, runtime, browser-console, linter, or type-checker error output you get. "
        "Include the file/line it points to if that is shown."
        if vague_failure else ""
    )
    return {
        "schema":"swrlz-programming-intent-v1",
        "codingTask":True,
        "projectContext":"new" if new_project else ("existing" if continuation or pins else "none"),
        "changeClass":change,
        "artifactContinuation":continuation,
        "artifactMutationRequested":mutation,
        "artifactTargetId":artifact_id,
        "artifactTargetMessageId":target_message_id,
        "baseRevision":base_revision,
        "newProject":new_project,
        "pinnedCodeArtifactCount":len(pins),
        "intentContract":active_contract,
        "repairDirection":text[:4000] if ((failure_evidence and original_request) or canonical_carry) else "",
        "canonicalCarry":canonical_carry,
        "failureEvidence":failure_evidence,
        "failureHistory":failure_history,
        "needsFailureEvidence":vague_failure,
        "evidenceRequest":evidence_request,
        "repairLifecycleState":"EVIDENCE_REQUIRED" if vague_failure else ("REPAIR_CANDIDATE" if failure_evidence else "CANDIDATE_GENERATION"),
        "source":"brain-router",
    }

