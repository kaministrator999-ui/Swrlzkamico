"""R39 v66: same-LALM programming mode + bounded architecture context over v65.

Phase 1 runtime scaffold: coding-task routing, project/change/depth state,
architecture-aware prompt context, proportional new-project behavior,
programming cameras, and deterministic routing self-tests.

This is not a repository tool loop and not a trained coding model.
"""
from __future__ import annotations
import re
import urllib.request

_V65_COMMIT="084f491069045dd4634056a099de83c655099f8a"
_V65_URL=f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V65_COMMIT}/runtime_hot/r39_engine_v65.py"
_req=urllib.request.Request(_V65_URL,headers={"User-Agent":"swrlz-r39-v66"})
with urllib.request.urlopen(_req,timeout=20) as _response:_source=_response.read(4_000_001)
if len(_source)>4_000_000:raise RuntimeError("R39_V65_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"),_V65_URL+"#v66","exec"),globals(),globals())

_V65_INSPECT=inspect_engine
_V65_GENERATE=generate_events
HOT_SERVER_VERSION="2.1.77"
HOT_REVISION="2.1.77-hot-programming-mode-context-v66"
_impl.HOT_SERVER_VERSION=HOT_SERVER_VERSION
_impl.HOT_REVISION=HOT_REVISION

_PROGRAMMING_CONTRACT="swrlz_programming_mode_v1"
_PROGRAMMING_CONTEXT_CONTRACT="swrlz_programming_context_v1"

_CODE_TERM_RE=re.compile(
    r"\b(?:code|coding|program(?:ming)?|software|script|function|class|method|api|endpoint|route|database|schema|"
    r"repository|repo|github|git|branch|commit|frontend|backend|server|client|component|module|package|library|"
    r"framework|html|css|javascript|typescript|python|kotlin|java|swift|rust|golang|react|vue|svelte|node|sql|"
    r"json|yaml|docker|vercel|website|webpage|web\s+page|web\s+app|application|app|codebase|source\s+code|ui|"
    r"auth|oauth|deployment|lalm)\b",re.I)
_FILE_EXT_RE=re.compile(r"\.(?:py|js|mjs|cjs|ts|tsx|jsx|html?|css|scss|kt|java|swift|rs|go|c|cc|cpp|h|hpp|cs|php|rb|sql|json|ya?ml|toml|xml|md)\b",re.I)
_CODE_ACTION_RE=re.compile(r"\b(?:build|create|make|implement|add|change|update|edit|modify|rewrite|fix|debug|repair|refactor|migrate|deploy|integrate|wire|hook|optimi[sz]e|review|audit|test|write|generate|design|architect|remove|rename|move)\b",re.I)
_FIX_RE=re.compile(r"\b(?:fix|debug|repair|bug|regression|broken|failing|failure|error|issue)\b",re.I)
_REFACTOR_RE=re.compile(r"\b(?:refactor|restructure|reorganize|clean\s*up|consolidate)\b",re.I)
_MIGRATE_RE=re.compile(r"\b(?:migrate|migration|schema\s+change|backfill)\b",re.I)
_DEPLOY_RE=re.compile(r"\b(?:deploy|deployment|production\s+release|release\s+pipeline|ci/?cd)\b",re.I)
_REVIEW_RE=re.compile(r"\b(?:review|audit|analy[sz]e|inspect)\b",re.I)
_NEW_PROJECT_RE=re.compile(r"\b(?:from\s+scratch|new\s+(?:project|app|application|website|webpage|site|service|tool|game)|start\s+(?:a|an|the)\s+(?:project|app|application|website|webpage|site|service|tool|game)|build\s+(?:me\s+)?(?:a|an)\s+(?:new\s+)?(?:app|application|website|webpage|site|service|tool|game)|create\s+(?:me\s+)?(?:a|an)\s+(?:new\s+)?(?:app|application|website|webpage|site|service|tool|game))\b",re.I)
_EXISTING_PROJECT_RE=re.compile(r"\b(?:existing|current)\s+(?:project|repo(?:sitory)?|app|application|website|webpage|codebase|code|server|client|module|component)|\b(?:our|my|this)\s+(?:current\s+)?(?:[A-Za-z0-9_-]+\s+){0,2}(?:project|repo(?:sitory)?|app|application|website|webpage|codebase|server|client|module|component)\b|\bin\s+(?:the|this|our|my)\s+repo(?:sitory)?\b|\b(?:add|change|update|fix|refactor|remove|migrate)\s+(?:this|that|the|our|my)\b",re.I)
_LIGHTWEIGHT_RE=re.compile(r"\b(?:simple|small|tiny|quick|standalone|single[-\s]?file|one[-\s]?file|prototype|example|snippet)\b",re.I)
_CROSS_RE=re.compile(r"\b(?:architecture|authentication|authorization|oauth|security|permissions?|database|persistence|state\s+ownership|schema|migration|deployment|rollback|background\s+(?:job|task)|queue|cache|distributed|multi[-\s]?user|tool\s+execution|agent|ai\s+subsystem|streaming|protocol|versioning)\b",re.I)
_CONTINUE_RE=re.compile(r"\b(?:keep\s+going|continue|go\s+ahead|do\s+it|do\s+this|let(?:'|’)s\s+do\s+(?:it|this)|yes|yep|yup|exactly)\b",re.I)
_STOP_RE=re.compile(r"\b(?:don(?:'|’)t|do\s+not|stop|cancel|never\s+mind|nevermind)\b",re.I)
_EXPLAIN_RE=re.compile(r"^\s*(?:what|why|how|explain|teach|show|tell\s+me|can\s+you\s+explain)\b",re.I)


def _prog_latest(payload):
    if not isinstance(payload,dict):return ""
    for key in ("prompt","text","message","input"):
        value=payload.get(key)
        if isinstance(value,str) and value.strip():return value.strip()
    return ""


def _prog_prior_users(payload,limit=8):
    if not isinstance(payload,dict):return []
    out=[]
    for turn in reversed(list(payload.get("history") or [])):
        if not isinstance(turn,dict):continue
        role=str(turn.get("role") or "").strip().lower()
        if role not in {"user","human"}:continue
        text=str(turn.get("text") or turn.get("content") or "").strip()
        if text:
            out.append(text)
            if len(out)>=limit:break
    return out


def _direct_programming_signal(text):
    value=str(text or "")
    term=bool(_CODE_TERM_RE.search(value) or _FILE_EXT_RE.search(value))
    action=bool(_CODE_ACTION_RE.search(value))
    broad=bool(re.search(r"\b(?:page|site|app|project|repo|code|server|api|database|ui|lalm)\b",value,re.I))
    return bool(term or (action and broad))


def _project_context(text,change_hint=""):
    value=str(text or "")
    if _EXISTING_PROJECT_RE.search(value):return "existing"
    if change_hint in {"fix","refactor","migrate","deploy"}:return "existing"
    if _NEW_PROJECT_RE.search(value):return "new"
    if re.search(r"\b(?:build|create|make|start)\b",value,re.I) and re.search(r"\b(?:website|webpage|web\s+page|web\s+app|app|application|site|service|tool|game|project)\b",value,re.I):return "new"
    return "none"


def _change_class(text,project_context):
    value=str(text or "")
    if _DEPLOY_RE.search(value):return "deploy"
    if _MIGRATE_RE.search(value):return "migrate"
    if _FIX_RE.search(value):return "fix"
    if _REFACTOR_RE.search(value):return "refactor"
    if _REVIEW_RE.search(value) and not re.search(r"\b(?:add|change|update|edit|modify|fix|refactor|migrate|deploy|remove|implement|build|create)\b",value,re.I):return "review"
    if project_context=="new":return "create"
    if _CODE_ACTION_RE.search(value):return "feature"
    return "explain"


def _architecture_depth(text,project_context,change_class):
    value=str(text or "")
    if project_context=="none":return "lightweight"
    cross=len(_CROSS_RE.findall(value))
    if change_class in {"migrate","deploy"} or cross>=2:return "deep"
    if project_context=="new" and _LIGHTWEIGHT_RE.search(value) and cross==0:return "lightweight"
    if change_class=="explain":return "lightweight"
    return "normal"


def _programming_profile(payload):
    latest=_prog_latest(payload)
    direct=_direct_programming_signal(latest)
    inherited=False
    source="current-turn" if direct else "none"
    inherited_from=""
    effective=latest
    if not direct and _CONTINUE_RE.search(latest) and not _STOP_RE.search(latest):
        for distance,prior in enumerate(_prog_prior_users(payload,8),start=1):
            if _direct_programming_signal(prior):
                direct=True;inherited=True;source="conversation-bridge";inherited_from=f"user@history_distance_{distance}";effective=prior;break
            if len(re.findall(r"[A-Za-z0-9_]+",prior))>=4:break
    if not direct:
        return {"active":False,"codingTask":False,"projectContext":"none","changeClass":"none","architectureDepth":"none","architectureReconciliation":False,"diagnostics":False,"projectCoaching":False,"toolEvidenceRequired":False,"source":"none","inherited":False,"inheritedFrom":"","implementationTruth":"runtime-scaffolded"}
    hint="fix" if _FIX_RE.search(effective) else "refactor" if _REFACTOR_RE.search(effective) else "migrate" if _MIGRATE_RE.search(effective) else "deploy" if _DEPLOY_RE.search(effective) else ""
    context=_project_context(effective,hint)
    change=_change_class(effective,context)
    depth=_architecture_depth(effective,context,change)
    mutation=change in {"create","feature","fix","refactor","migrate","deploy"}
    return {
        "active":True,"codingTask":True,"projectContext":context,"changeClass":change,"architectureDepth":depth,
        "architectureReconciliation":bool(context=="existing" and mutation),"diagnostics":bool(change=="fix"),
        "projectCoaching":bool(context=="new" and mutation),"toolEvidenceRequired":bool(context=="existing" and mutation),
        "source":source,"inherited":inherited,"inheritedFrom":inherited_from,"implementationTruth":"runtime-scaffolded",
    }


def _programming_context_prompt(profile):
    return (
        "[SWRLZ_PROGRAMMING_MODE v1] Internal programming operating grammar; do not expose this marker verbatim. "
        f"projectContext={profile.get('projectContext')}; changeClass={profile.get('changeClass')}; architectureDepth={profile.get('architectureDepth')}; "
        f"inherited={str(bool(profile.get('inherited'))).lower()}; architectureReconciliation={str(bool(profile.get('architectureReconciliation'))).lower()}; "
        f"diagnostics={str(bool(profile.get('diagnostics'))).lower()}; projectCoaching={str(bool(profile.get('projectCoaching'))).lower()}. "
        "For an existing-project change, separate desired outcome from implementation assumptions. Inspect available project/repository evidence before inventing owners or new structure; identify current authority, relevant state/readers/writers/lifecycle, and related implementations. Prefer reuse -> extend canonical owner -> consolidate/refactor -> migrate+retire -> genuinely new structure. If evidence is unavailable or ownership remains ambiguous, do not fabricate architecture; plan the needed inspection. "
        "For a new user project, design the smallest useful structure justified by current scale and risk; strengthen ownership, state, tests, observability, versioning, and deployment boundaries only as complexity warrants. Respect explicit user choices to simplify optional structure and explain material tradeoffs without repeatedly pressuring them. "
        "For lightweight standalone coding/explanation, answer directly and do not force repository ceremony. For fix/debug work, inspect existing diagnostic evidence first and add bounded instrumentation only when an observability gap prevents reliable diagnosis. Preserve one intentional authority per responsibility and verify behavior plus architecture before claiming completion. This marker does not grant permission to write files, invoke tools, deploy, spend, or bypass any user/server approval boundary."
    )


def _with_programming_context(payload,profile=None):
    if not isinstance(payload,dict):return payload
    profile=dict(profile or _programming_profile(payload))
    if not profile.get("active"):return payload
    out=dict(payload);history=list(out.get("history") or [])
    marker={"role":"system","text":_programming_context_prompt(profile)}
    insert_at=1 if history and isinstance(history[0],dict) and str(history[0].get("role") or "").lower()=="system" else 0
    history.insert(insert_at,marker);out["history"]=history
    return out


def _programming_mode_self_test():
    cases=[]
    def add(name,payload,expected):
        try:
            got=_programming_profile(payload);failures=[]
            for key,want in expected.items():
                value=got.get(key)
                if value!=want:failures.append(f"{key}={value!r} expected {want!r}")
            cases.append({"name":name,"ok":not failures,"failures":failures})
        except Exception as exc:cases.append({"name":name,"ok":False,"failures":[f"{type(exc).__name__}: {exc}"]})
    add("non-programming-question",{"prompt":"Explain quantum physics."},{"active":False,"codingTask":False})
    add("lightweight-code-explanation",{"prompt":"Explain how this Python function works."},{"active":True,"projectContext":"none","changeClass":"explain","architectureDepth":"lightweight","architectureReconciliation":False})
    add("existing-project-feature",{"prompt":"Add response bookmarks to our existing app and update the current repo."},{"active":True,"projectContext":"existing","changeClass":"feature","architectureDepth":"normal","architectureReconciliation":True,"toolEvidenceRequired":True})
    add("existing-project-debug",{"prompt":"Fix the OAuth regression in our current web app."},{"active":True,"projectContext":"existing","changeClass":"fix","diagnostics":True,"architectureReconciliation":True})
    add("new-small-webpage",{"prompt":"Build me a simple personal webpage from scratch in one HTML file."},{"active":True,"projectContext":"new","changeClass":"create","architectureDepth":"lightweight","projectCoaching":True,"architectureReconciliation":False})
    add("cross-cutting-migration",{"prompt":"Migrate our existing app authentication and database schema with rollback support."},{"active":True,"projectContext":"existing","changeClass":"migrate","architectureDepth":"deep","architectureReconciliation":True})
    add("coding-continuation",{"prompt":"Ideal most definitely swyrlz let's do this!","history":[{"role":"user","text":"Add architecture-aware coding mode to our current LALM project."},{"role":"assistant","text":"I can implement the runtime scaffold."}]},{"active":True,"projectContext":"existing","changeClass":"feature","architectureDepth":"normal","inherited":True})
    passed=sum(1 for case in cases if case["ok"])
    return {"ok":passed==len(cases),"passed":passed,"total":len(cases),"failures":[case for case in cases if not case["ok"]],"contract":"swrlz_programming_mode_acceptance_v1"}


def inspect_engine():
    result=_V65_INSPECT()
    if isinstance(result,dict):
        result.update({
            "hotServerVersion":HOT_SERVER_VERSION,"hotRevision":HOT_REVISION,
            "programmingModeRuntimeScaffolded":True,"programmingTaskClassifier":True,"programmingContextCompiler":True,
            "programmingArchitectureState":True,"existingProjectArchitectureReconciliationPrompt":True,
            "newProjectProportionalArchitecturePrompt":True,"programmingContinuationInheritance":True,
            "programmingToolLoop":False,"codingSpecialistDelegation":False,"codingSpecialistModel":False,
            "programmingImplementationTruth":"runtime-scaffolded","programmingModeContract":_PROGRAMMING_CONTRACT,
            "programmingContextContract":_PROGRAMMING_CONTEXT_CONTRACT,"programmingModeSelfTest":_programming_mode_self_test(),
            "v65SourceCommit":_V65_COMMIT,
        })
    return result


def generate_events(payload,is_cancelled=None):
    request_id=_request_id(payload) if isinstance(payload,dict) else ""
    profile=_programming_profile(payload) if isinstance(payload,dict) else {"active":False}
    routed=_with_programming_context(payload,profile) if profile.get("active") else payload
    if profile.get("active"):
        _camera(request_id,"programming-mode",contract=_PROGRAMMING_CONTRACT,projectContext=profile.get("projectContext"),changeClass=profile.get("changeClass"),architectureDepth=profile.get("architectureDepth"),inherited=bool(profile.get("inherited")),architectureReconciliation=bool(profile.get("architectureReconciliation")),diagnostics=bool(profile.get("diagnostics")),projectCoaching=bool(profile.get("projectCoaching")),toolEvidenceRequired=bool(profile.get("toolEvidenceRequired")),implementationTruth="runtime-scaffolded")
    for event in _V65_GENERATE(routed,is_cancelled):yield event
