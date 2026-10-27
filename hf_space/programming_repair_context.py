"""Shared bounded repair-context and strategy helpers for §wyrlz programming routes.

This module renders already-authoritative Brain state into a compact model-facing
form. It does not own intent, receipt classification, artifact mutation, or
acceptance truth.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any


def expanded_project_delivery(programming: dict[str, Any], prompt: str) -> bool:
    """Choose a larger bounded generation allowance for files and editing apps."""
    if not programming.get("codingTask") or programming.get("changeClass") in ("review","explain"):
        return False
    original=str((programming.get("intentContract") or {}).get("originalRequest") or "")
    return bool(re.search(
        r"\b(?:multi[- ]?file|multiple files|separate files|project files|project archive|"
        r"zip|archive|bundle|folder structure|editor|modeling|modelling|ide)\b",
        original+"\n"+str(prompt or ""),re.I))



def response_budget(programming: dict[str, Any], prompt: str) -> dict[str, Any]:
    """Reserve output by requested deliverable size, not incidental large topics.

    These are bounded allowances, not a promise of exact length or automatic
    multi-turn execution. Current user shortening instructions win over a
    carried large-project contract.
    """
    programming=programming if isinstance(programming,dict) else {}
    current=str(prompt or "")
    short=bool(re.search(
        r"\b(?:briefly|concisely|tl;?dr)\b|"
        r"\b(?:keep|make|be|answer|respond)(?:[ \w-]{0,24})\b(?:brief|concise|short)\b|"
        r"\b(?:one|single|1)\s+(?:sentence|paragraph)\b|"
        r"\b(?:only|just)\s+(?:a\s+)?(?:small|tiny|short|quick)\s+(?:fix|change|patch|answer)\b",
        current,re.I))
    word_limits=[int(value.replace(",","")) for value in re.findall(
        r"\b(?:under|at most|no more than|fewer than|max(?:imum)?)\s+(\d[\d,]*)\s+words?\b",current,re.I)]
    if short or any(limit<=500 for limit in word_limits):
        return {"tier":"normal","tokens":4096,"stagedDelivery":False}
    original=str((programming.get("intentContract") or {}).get("originalRequest") or "")
    request=current+"\n"+original
    coding=bool(programming.get("codingTask"))
    action=bool(re.search(r"\b(?:write|produce|generate|create|draft|provide|build|implement|return|give|explain|analyse|analyze)\b",request,re.I))
    action=action or bool(re.match(r"\s*(?:i\s+(?:need|want)|please\s+(?:write|create|generate|produce))\b",request,re.I))
    large_deliverable=bool(re.search(
        r"\b(?:huge|large|substantial|extensive|comprehensive|full[- ]length|long[- ]form|lengthy)"
        r"[ \w,/-]{0,55}\b(?:project|application|app|codebase|implementation|document|documentation|report|guide|manual|chapter|specification|tutorial|essay|article|book|analysis|explanation)\b|"
        r"\b(?:project|document|report|guide|manual|essay|article|book|analysis)\b[ \w,/-]{0,35}\b(?:in depth|very detailed|comprehensive|extensive)\b|"
        r"\b(?:lots|a lot|large amount|substantial amount)\s+of\s+(?:code|content|context|detail|text)\b|"
        r"\b(?:long|detailed|thorough)\s+(?:document|documentation|report|guide|manual|chapter|specification|tutorial|essay|article|book|analysis|explanation)\b",
        request,re.I))
    requested_words=[int(value.replace(",","")) for value in re.findall(
        r"\b(\d[\d,]*)[- ]words?\b",request,re.I)]
    requested_pages=[int(value) for value in re.findall(r"\b(\d+)[- ]pages?\b",request,re.I)]
    if action and (large_deliverable or any(n>=2000 for n in requested_words) or any(n>=5 for n in requested_pages)):
        return {"tier":"large","tokens":16384,"stagedDelivery":True}
    if (action and any(n>=1000 for n in requested_words)) or expanded_project_delivery(programming,prompt):
        return {"tier":"project","tokens":8192,"stagedDelivery":coding}
    return {"tier":"normal","tokens":4096,"stagedDelivery":False}


def long_delivery_policy(budget: dict[str, Any]) -> str:
    """Keep generous decode room separate from unsupported completion claims."""
    if budget.get("tier") not in ("large","project"):
        return ""
    return (
        "\nSUBSTANTIAL DELIVERY: Use the available response room for the requested "
        "complete code or substantive document, rather than an outline standing in "
        "for the work. Do not pad to consume the allowance. If the entire scope "
        "cannot fit in one delivery, state the completed scope and remaining work "
        "explicitly. A staged delivery must contain complete, usable files or a "
        "complete document section; never silently shorten source or label an "
        "unfinished whole project/document complete. Do not claim automatic "
        "continuation, generated files, tests, or downloads without actual results."
    )


def preserve_existing_source(programming: dict[str, Any]) -> bool:
    """Imported source under edit is mandatory even without a stored artifact ID."""
    return bool(programming.get("codingTask") and not programming.get("newProject")
        and not programming.get("artifactEditSource")
        and (programming.get("artifactContinuation") or programming.get("artifactMutationRequested")
             or programming.get("projectContext")=="existing"))


def owned_project_edit_scope(programming: dict[str, Any]) -> dict[str, Any] | None:
    """Project only explicitly named stored files for an ordinary owned edit.

    This is a model-context projection, never a source mutation or an ownership
    grant. Full artifactEditSource remains authoritative for saved revisions and
    composed-project validation. Ambiguous/unscoped/repair work keeps all source.
    """
    if (not programming.get("codingTask") or programming.get("newProject")
            or not programming.get("artifactMutationRequested") or not programming.get("artifactTargetId")
            or programming.get("changeClass") not in ("feature","fix","refactor","migrate")
            or programming.get("failureEvidence") or programming.get("canonicalCarry")
            or programming.get("behaviorRepairBaseSource")):
        return None
    revision=programming.get("baseRevision")
    if (not isinstance(revision,int) or isinstance(revision,bool) or revision<1
            or not re.fullmatch(r"[a-f0-9]{64}",str(programming.get("baseSourceHash") or ""))):
        return None
    contract=programming.get("intentContract") if isinstance(programming.get("intentContract"),dict) else {}
    instruction=str(contract.get("currentInstruction") or contract.get("originalRequest") or "")
    if re.search(r"\b(?:all|every)\s+(?:(?:\d+|remaining|other|existing|stored|dependent|project|source)\s+){0,3}files?\b|"
                 r"\b(?:whole|entire|complete)\s+(?:project|codebase|repository|file\s+set)\b|"
                 r"\bproject[- ]wide\b|\bacross\s+(?:the\s+)?(?:project|codebase|repository)\b",instruction,re.I):
        return None
    from project_archive import ProjectArchiveError,parse_project_files,project_markdown,source_fences
    source=str(programming.get("artifactEditSource") or "")
    if not source:return None
    try: files=parse_project_files(source)
    except ProjectArchiveError:return None
    if len(files)<2:return None
    # Current source/code examples are data, not named editing directions.
    prose=[];cursor=0
    for fence in source_fences(instruction):
        prose.append(instruction[cursor:fence["start"]]);cursor=fence["end"]
    prose.append(instruction[cursor:]);instruction=" ".join(prose)
    boundary=r"[\w§./\\-]"
    def mentioned(path):
        # A sentence-final period is punctuation, while .map or another path
        # continuation must not turn a partial filename into a selected file.
        return bool(re.search(r"(?<!"+boundary+r")"+re.escape(path)+r"(?![\w§/\\-]|\.[\w§./\\-])",instruction))
    selected={item["path"] for item in files if mentioned(item["path"])}
    basenames={}
    for item in files:
        basenames.setdefault(item["path"].rsplit("/",1)[-1],[]).append(item["path"])
    for name,paths in basenames.items():
        if mentioned(name):
            if len(paths)!=1:return None
            selected.add(paths[0])
    if not selected or len(selected)==len(files):return None
    chosen=[item for item in files if item["path"] in selected]
    index={"totalFiles":len(files),"selectedPaths":[item["path"] for item in chosen],
           "listedOtherPaths":[],"omittedOtherPathCount":len(files)-len(chosen),
           "scope":"Only selected file contents are provided; other contents were not inspected. Request further files explicitly if needed."}
    # Bound only this truthful index, never a selected file's source contents.
    if len(json.dumps(index,ensure_ascii=False,separators=(",",":")))>4096:return None
    for item in files:
        if item["path"] in selected:continue
        index["listedOtherPaths"].append(item["path"])
        index["omittedOtherPathCount"]-=1
        if len(json.dumps(index,ensure_ascii=False,separators=(",",":")))>4096:
            index["listedOtherPaths"].pop();index["omittedOtherPathCount"]+=1
            break
    return {"source":project_markdown(chosen),"selectedPaths":index["selectedPaths"],
            "pathIndex":json.dumps(index,ensure_ascii=False,separators=(",",":")),
            "totalFiles":len(files)}


def source_under_edit(programming: dict[str, Any], history: list[dict[str, Any]]) -> str:
    """Find complete mandatory editing source, without manufacturing identity."""
    if (not programming.get("codingTask") or programming.get("newProject")
            or programming.get("changeClass") in ("review","explain")):
        return ""
    evidence=programming.get("failureEvidence") if isinstance(programming.get("failureEvidence"),dict) else {}
    source=str(programming.get("behaviorRepairBaseSource") or evidence.get("repairSource")
               or programming.get("artifactEditSource") or "")
    if source:
        scope=owned_project_edit_scope(programming)
        return scope["source"] if scope else source
    if preserve_existing_source(programming):
        return next((str(item.get("content") or item.get("text") or "")
            for item in reversed(history or []) if item.get("role")=="assistant"
            and source_fence_present(item.get("content") or item.get("text") or "")),"")
    return ""


def source_sized_budget(model: Any, programming: dict[str, Any], history: list[dict[str, Any]],
                        budget: dict[str, Any]) -> dict[str, Any]:
    """A short edit still needs enough decode room to return its complete file."""
    source=source_under_edit(programming,history)
    if not source:return budget
    count=len(model.tokenize(source.encode("utf-8"),add_bos=False))
    if count>16384:
        raise ValueError(
            f"Canonical source needs {count} tokens for complete-source delivery; "
            "the bounded output maximum is 16384. The source was not truncated. "
            "Work on a smaller complete file set/stage before editing this source."
        )
    desired=max(int(budget["tokens"]),min(16384,count+1024))
    if desired==budget["tokens"]:return budget
    return {**budget,"tokens":desired,"tier":"source-complete","sourceTokens":count}


def _application_acceptance_summary(capabilities: dict[str, Any], *, repair: bool = False) -> str:
    """Render required user behavior, without supplying an editor implementation."""
    if not isinstance(capabilities,dict) or capabilities.get("kind")!="3d-scene-editor":
        return ""
    required=[key for key in ("create","select","transform","delete")
              if key in (capabilities.get("required") or [])]
    if not required:return ""
    lines=["APPLICATION ACCEPTANCE"+(" — SOURCE REPAIR" if repair else "")+":"]
    if "create" in required:
        lines.append("- Object creation: user actions must add actual editable objects to the 3D scene at runtime. A static initial object, a button label or a UI card alone is not object creation.")
    if "select" in required:
        line="- Object selection: the user must be able to choose which existing scene object is selected. Selecting one hardcoded initial object regardless of the user's choice is insufficient."
        if "create" in required:
            line+=" Newly created objects must also be selectable."
        lines.append(line)
    if "transform" in required:
        behaviors={"translate":"change its position", "rotate":"change its orientation", "scale":"change its size"}
        requested=[behaviors[mode] for mode in ("translate","rotate","scale")
                   if mode in (capabilities.get("transformModes") or [])]
        line="- Selected-object transformation: user interaction must "
        line+=(", ".join(requested)+" on the selected scene object only." if requested
               else "apply the requested transformation to the selected scene object only.")
        line+=" Other objects must retain their own transforms. Changing a tool-mode label without changing the selected object does not satisfy transformation."
        lines.append(line)
    if "delete" in required:
        lines.append("- Selected-object deletion: the user must be able to remove only the selected scene object. Other objects must remain available for selection and the remaining requested editing operations.")
    lines.append("A rendered viewer or camera movement alone cannot satisfy these editing requirements. Keep the user's specified scope; this summary does not add excluded operations or prescribe a library, UI layout or algorithm.")
    if repair:
        lines.append("The source checker could not find interactive implementation evidence for the behavior above. Correct the returned source while preserving the original requirements. This source feedback is not an execution receipt or proof that the editor works.")
    return "\n"+"\n".join(lines)

def project_delivery_policy(programming: dict[str, Any], prompt: str) -> str:
    """Describe the existing file-fence protocol without inventing download URLs."""
    if not programming.get("codingTask") or programming.get("changeClass") in ("review","explain"):
        return ""
    policy=(
        "\nPROJECT FILE DELIVERY: Finish every requested feature and every file. "
        "A requested single HTML page may be one complete HTML fence. When the "
        "project needs multiple files or the user requests a project archive, "
        "return each COMPLETE file in its own fence with a safe relative path "
        "and the same project identifier. Write the language, file path and project "
        "attributes on the SAME physical line as the opening backticks. "
        "Example HTML opening line: \"```html file=index.html project=my-project\". "
        "The NEXT line begins the actual HTML file contents. Likewise the opening "
        "line for a stylesheet is \"```css file=styles.css project=my-project\" and "
        "for a script is \"```javascript file=src/app.js project=my-project\". "
        "These are opening-line syntax examples only; select the actual language "
        "and filenames required by this project, including non-web source/config "
        "files. Never put bare file=, path=, filename= or project= metadata on a "
        "separate line inside the file body. Such a line becomes literal source, "
        "not a filename declaration, and can break the program. Use only "
        "the files and stack required by this project, close every fence, and keep "
        "relative imports/links consistent. Include all needed entry/config files. "
        "The application creates the actual ZIP/download from validated file "
        "contents. Do not invent an archive, tool action, download URL, filesystem "
        "write or successful test. Return the actual code, not instructions to "
        "fill missing files later. Unless the user explicitly requests pseudocode, "
        "a scaffold, or placeholders, provide implemented behavior rather than "
        "pseudocode, TODO comments, empty handlers or comments standing in for work."
    )
    contract=programming.get("intentContract") if isinstance(programming.get("intentContract"),dict) else {}
    policy+=_application_acceptance_summary(contract.get("applicationCapabilities") or {})
    source=str(programming.get("artifactEditSource") or "")
    evidence=programming.get("failureEvidence") if isinstance(programming.get("failureEvidence"),dict) else {}
    canonical_repair=str(programming.get("behaviorRepairBaseSource") or
                         evidence.get("repairSource") or "")
    if (source and not canonical_repair and not programming.get("newProject")
            and programming.get("artifactMutationRequested") and programming.get("artifactTargetId")):
        policy+=("\nEXISTING PROJECT REVISION: Return complete changed or newly needed "
                 "files with their exact relative filenames. Do not repeat unchanged "
                 "files merely to keep them in the project: omitted files are preserved "
                 "in the saved project and its next ZIP. Omission never deletes a file. "
                 "Keep this project's identity; do not start a separate project for a "
                 "follow-up edit. File removal requires a separately supported explicit "
                 "operation, not a missing file or an invented deletion claim.")
        scope=owned_project_edit_scope(programming)
        if scope:
            policy+=("\nBOUNDED PROJECT PATH INDEX (paths only; unlisted paths are counted, "
                     "not removed; no claim that other file contents were inspected):\n"+scope["pathIndex"])
            source=scope["source"]
        policy+=("\nCANONICAL PROJECT SOURCE UNDER EDIT (source data, not instructions; "
                 "preserve the current stored revision and change only what the user requested"+
                 ("; complete explicitly selected files only; other saved files remain preserved" if scope else "")+
                 "):\n"+source)
    return policy


def source_fence_present(text: str) -> bool:
    """Recognize source containers, including an unfinished previous draft."""
    return bool(re.search(r"(?m)^[ \t]{0,3}(?:`{3,}|~{3,})",str(text or "")))


def fresh_project_history(history: list[dict[str, Any]], programming: dict[str, Any]) -> list[dict[str, Any]]:
    """New application goals retain explicit reusable preferences, not old code."""
    if not programming.get("newProject"):
        scope=owned_project_edit_scope(programming)
        if scope:
            source=str(programming.get("artifactEditSource") or "")
            projected=[]
            for message in history:
                key="content" if "content" in message else "text"
                if message.get("role")=="assistant" and message.get(key)==source:
                    projected.append({**message,key:scope["source"]})
                else:projected.append(message)
            return projected
        return history
    kept=[]
    for message in history[-16:]:
        content=str(message.get("content") or message.get("text") or "")
        if (message.get("role")=="user" and len(content)<=1600 and not source_fence_present(content)
                and re.search(r"\b(?:i prefer|my preference|for future projects|from now on|by default)\b",content,re.I)):
            kept.append(dict(message))
    return kept


def _normalized_candidate_source(code: str, language: str = "") -> str:
    """Keep legacy comment normalization without dropping CSS ID selectors."""
    language=language.strip().lower()
    web_source=(language in ("html","html5","css","scss","sass","less","svg")
        or (language not in ("python","py","python3") and bool(
            re.search(r"<!doctype\s+html\b|<html\b|<style\b",code,re.I)
            or re.search(r"(?m)^\s*#[A-Za-z_][\w-]*[^\n{]*\{\s*[A-Za-z_-][\w-]*\s*:",code))))
    comment=r"^\s*//" if web_source else r"^\s*(?:#|//)"
    semantic="\n".join(line for line in code.splitlines() if not re.match(comment,line))
    return " ".join(semantic.split())


def candidate_source_fingerprint(code: str, original_text: str = "") -> str | None:
    """Fingerprint all executable project files, retaining single-file identity.

    Use the same complete-fence/file parser as storage and validation. A later
    CSS/JavaScript file is part of the candidate even if index.html is unchanged.
    Documentation-only edits cannot disguise an unchanged executable project.
    This remains bounded source identity, not semantic or execution proof.
    """
    from project_archive import ProjectArchiveError, parse_project_files
    try:
        files=parse_project_files(original_text) if original_text else []
    except ProjectArchiveError:
        # The source gate rejects malformed paths separately. Still identify
        # the rejected attempt without opening files or mutating its source.
        files=[]
    if files:
        def documentation(item):
            name=str(item["path"]).rsplit("/",1)[-1].lower()
            return (name.endswith((".md",".markdown",".rst",".txt"))
                    or name in ("readme","license","copying","notice","changelog"))
        executable=[item for item in files if not documentation(item)]
        selected=executable or files
        if len(selected)==1:
            item=selected[0]
            normalized=_normalized_candidate_source(item["content"],item.get("language") or "")
        else:
            normalized=json.dumps([
                {"path":item["path"],"source":_normalized_candidate_source(item["content"],item.get("language") or "")}
                for item in sorted(selected,key=lambda item:item["path"])
            ],ensure_ascii=False,sort_keys=True,separators=(",",":"))
    else:
        fence=re.search(r"```([^\n`]*)\n",str(original_text or ""))
        language=fence.group(1).strip().split()[0] if fence and fence.group(1).strip() else ""
        normalized=_normalized_candidate_source(code,language)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16] if normalized else None


def contract_rejection_context(validation: dict[str, Any]) -> str:
    """Actual bounded source-gate feedback; never an execution/test receipt."""
    reasons=[str(item)[:180] for item in (validation.get("reasons") or [])[:8]]
    context=("\nACTUAL SOURCE CONTRACT REJECTIONS (source checks only; no execution):\n"
             +json.dumps(reasons,ensure_ascii=False)
             +"\nCorrect these source defects while preserving the original requested features. Do not invent a test result.")
    missing_operations={reason.split(":",1)[1] for reason in reasons
        if reason.startswith("missing-editor-source-capability:") and ":" in reason}
    missing_modes={reason.split(":",1)[1] for reason in reasons
        if reason.startswith("missing-editor-source-transform:") and ":" in reason}
    requested_operations=[key for key in ("create","select","transform","delete") if key in missing_operations]
    requested_modes=[mode for mode in ("translate","rotate","scale") if mode in missing_modes]
    if requested_modes and "transform" not in requested_operations:
        requested_operations.append("transform")
    if requested_operations:
        context+=_application_acceptance_summary({"kind":"3d-scene-editor", "required":requested_operations,
            "transformModes":requested_modes},repair=True)
    if any(reason.startswith("literal-ui-text-mismatch:") for reason in reasons):
        literals=[{"target":str(item.get("target") or "text"), "text":str(item.get("text") or "")}
            for item in (validation.get("literalUiText") or [])[:8] if isinstance(item,dict)]
        context+=(
            "\nEXACT VISIBLE TEXT CORRECTION: replace the entire visible text of each "
            "specified UI target with its exact text value below. Preserve characters and case. "
            "Do not append words from the location/reference instruction. A correct browser "
            "title alone does not satisfy a requested visible heading. Preserve the rest of "
            "the existing project.\n"+json.dumps(literals,ensure_ascii=False,separators=(",",":"))
        )
    if any(reason.startswith("unresolved-browser-module:") for reason in reasons):
        context+=(
            "\nBROWSER MODULE RESOLUTION: compare the exact rejected specifier "
            "with the actual document's import-map keys. An exact key resolves "
            "only that name; subpaths need their own exact mapping or a matching "
            "trailing-slash prefix key and URL. Use the applicable verified "
            "library mapping or absolute module URL, respecting the original "
            "project stack. A URL-loaded addon can still import a bare name "
            "internally, which also needs document-level resolution. This "
            "source defect does not prove the dependency is unavailable; do "
            "not remove requested features or claim an installation is needed."
        )
    if any(reason.startswith(("missing-project-module:", "misplaced-project-file-metadata:"))
           for reason in reasons):
        context+=(
            "\nPROJECT FILE PROTOCOL CORRECTION: a linked/imported project module "
            "must be returned as a complete file at its exact resolved relative "
            "path. Put its language and file= path on the same physical line as "
            "the opening backticks, for example \"```javascript file=src/app.js\". "
            "The next line is actual source code. Bare file=/project= lines "
            "inside a fence are file contents, not header metadata. Correct the "
            "returned fences and source yourself; the application does not "
            "remove those lines, invent a missing module or repair the code. "
            "Keep every requested file and behavior. This is source-protocol "
            "feedback, not a runtime or build result."
        )
    return context


def candidate_retry_messages(
    original_messages: list[dict[str, Any]],
    failed_candidate: str,
    instruction: str,
) -> list[dict[str, Any]]:
    """Give the model its complete latest rejected draft, retaining original authority.

    The caller must count this entire context and reject if it cannot fit. Never
    shorten source here: an omitted operation can be the actual defect. Build
    each retry from the original messages so earlier rejected drafts and repair
    directives do not accumulate or replace the canonical user/repair source.
    """
    return [dict(message) for message in original_messages] + [
        {"role": "assistant", "content": failed_candidate},
        {"role": "user", "content": (
            "The preceding assistant draft was rejected by source checks. It is "
            "a candidate to revise, not an execution receipt or a replacement "
            "for the original requirements or canonical repair source. Return "
            "the complete corrected candidate; preserve all original requested "
            "features and constraints.\n" + instruction
        )},
    ]


def _bounded(values: Any, limit: int, chars: int) -> list[str]:
    result=[]
    for value in values or []:
        text=" ".join(str(value or "").split())[:chars]
        if text and text not in result:
            result.append(text)
        if len(result)>=limit:
            break
    return result


def _strip_fences(text: str) -> str:
    return re.sub(r"```[^\n`]*\n[\s\S]*?```"," ",str(text or ""))

def _compact_user_direction(programming: dict[str, Any], prompt: str) -> str:
    direction=str(programming.get("repairDirection") or "").strip() or str(prompt or "").strip()
    direction=_strip_fences(direction)
    evidence=programming.get("failureEvidence") if isinstance(programming.get("failureEvidence"),dict) else {}
    receipt=str(evidence.get("evidence") or "").strip()
    if receipt and receipt in direction:
        direction=direction.replace(receipt," ")
    direction=" ".join(direction.split())
    # This is the user's current repair direction, not an optional history
    # summary. Let the engine's token fitter reject it if it cannot fit intact.
    return direction


def build_compact_repair_context(
    programming: dict[str, Any],
    prompt: str,
    response_mode: str,
) -> tuple[str, str, dict[str, Any]]:
    """Render the minimum authoritative repair state without duplicating full policy prose."""
    programming=programming if isinstance(programming,dict) else {}
    contract=programming.get("intentContract") if isinstance(programming.get("intentContract"),dict) else {}
    evidence=programming.get("failureEvidence") if isinstance(programming.get("failureEvidence"),dict) else {}
    semantics=evidence.get("receiptSemantics") if isinstance(evidence.get("receiptSemantics"),dict) else {}
    language=contract.get("languageContract") if isinstance(contract.get("languageContract"),dict) else {}
    behavior=programming.get("behaviorLedger") if isinstance(programming.get("behaviorLedger"),dict) else {}
    repair_base=programming.get("behaviorRepairBase") if isinstance(programming.get("behaviorRepairBase"),dict) else {}
    source=str(programming.get("behaviorRepairBaseSource") or evidence.get("repairSource") or "")
    direction=_compact_user_direction(programming,prompt)
    prior=[]
    for item in (programming.get("failureHistory") or [])[-2:]:
        if not isinstance(item,dict):
            continue
        prior.append({
            "categories":_bounded(item.get("categories"),6,60),
            "candidateFingerprint":str(item.get("candidateFingerprint") or "")[:40] or None,
            "failureSignals":_bounded(item.get("failureSignals"),3,220),
            "reportedDependencies":_bounded(item.get("reportedDependencies"),8,120),
        })

    constraints=programming.get("repairConstraints") if isinstance(programming.get("repairConstraints"),dict) else {}
    state={
        "schema":"swrlz-compact-repair-context-v2",
        "changeClass":str(programming.get("changeClass") or "fix"),
        "originalRequest":str(contract.get("originalRequest") or ""),
        "must":_bounded(contract.get("must"),10,320),
        "mustNot":_bounded(contract.get("mustNot"),10,320),
        "preserve":_bounded(contract.get("preserve"),10,320),
        "literalUiText":[dict(item) for item in (contract.get("literalUiText") or [])[:16] if isinstance(item,dict)],
        "languageContract":{
            "requestedLanguages":list(language.get("requestedLanguages") or [])[:8],
            "requiredLanguages":list(language.get("requiredLanguages") or [])[:8],
            "allowedLanguages":list(language.get("allowedLanguages") or [])[:10],
            "artifactType":language.get("artifactType"),
            "substitutionAllowed":language.get("substitutionAllowed"),
        },
        "repairConstraints":{
            "dependencyPolicy":constraints.get("dependencyPolicy"),
            "unavailableDependencies":list(constraints.get("unavailableDependencies") or [])[:16],
            "carriedUnavailableDependencies":list(constraints.get("carriedUnavailableDependencies") or [])[:16],
            "currentReceiptDependencies":list(constraints.get("currentReceiptDependencies") or [])[:16],
        },
        "behaviorLedger":{
            "currentScore":behavior.get("currentScore"),
            "bestKnownScore":behavior.get("bestKnownScore"),
            "currentPassingCases":list(behavior.get("currentPassingCases") or [])[:30],
            "currentFailingCases":list(behavior.get("currentFailingCases") or [])[:30],
            "preservePassingCases":list(behavior.get("preservePassingCases") or [])[:30],
            "resolvedCases":list(behavior.get("resolvedCases") or [])[:20],
            "regressedCases":list(behavior.get("regressedCases") or [])[:20],
            "repairObligations":[dict(x) for x in (behavior.get("repairObligations") or [])[:16] if isinstance(x,dict)],
            "repairBaseMode":repair_base.get("mode"),
            "bestKnownArtifact":behavior.get("bestKnownArtifact"),
        },
        "receipt":{
            "ownership":evidence.get("receiptSourceOwnership"),
            "repairSourceFingerprint":evidence.get("repairSourceFingerprint"),
            "categories":list(semantics.get("categories") or [])[:10],
            "exceptionTypes":list(semantics.get("exceptionTypes") or [])[:8],
            "exitCodes":list(semantics.get("exitCodes") or [])[:8],
            "sourceLocations":list(semantics.get("sourceLocations") or [])[:10],
            "failingTests":list(semantics.get("failingTests") or [])[:10],
            "expectedActual":_bounded(semantics.get("expectedActual"),6,280),
            "reportedSymbols":list(semantics.get("reportedSymbols") or [])[:10],
            "reportedDependencies":list(semantics.get("reportedDependencies") or [])[:10],
            "failingSignals":_bounded(semantics.get("failingSignals"),6,280),
            "passingSignals":_bounded(semantics.get("passingSignals"),4,220),
        },
        "repairActions":_bounded(evidence.get("repairActions"),5,420),
        "priorFailures":prior,
        "userDirection":direction,
    }

    rules=(
        "You are §wyrlz's programming repair worker. Repair the CANONICAL SOURCE UNDER REPAIR below. "
        "The ORIGINAL REQUEST and MUST/MUST-NOT/PRESERVE fields are authoritative. The receipt is execution evidence, not a replacement request. "
        "Return one COMPLETE usable candidate in the required language/artifact form; preserve required API/signature and unrelated behavior. "
        "Fix the source operation that causes the observed failure. Do not merely paraphrase the log, change comments, weaken tests, install an unavailable dependency, "
        "or repeat a rejected executable candidate. The BEHAVIOR LEDGER is external evidence: every preservePassingCases item is a behavior already proven at least once and every regressedCases item must be restored. "
        "Do not trade one proven passing case for another fix. When repairBaseMode is best-known-tested-source, treat that source as the safer implementation base while using the newest receipt as the failure delta to repair. "
        "A structural candidate pass is not execution proof; never claim compile/test/runtime success without a new external receipt. "
        "If a prior strategy stalled, materially change the relevant algorithm/dependency/control/data-flow strategy while preserving the contract and behavior ledger."
    )
    system=rules+"\n"+str(response_mode or "")+"\nREPAIR STATE:\n"+json.dumps(state,ensure_ascii=False,separators=(",",":"))
    if source:
        source_label="BEST KNOWN TESTED REPAIR BASE" if repair_base.get("mode")=="best-known-tested-source" else "CANONICAL SOURCE UNDER REPAIR"
        system+="\n"+source_label+":\n"+source
    fitted_prompt=direction or "Repair the canonical source against the receipt and original contract. Return the complete corrected candidate."
    telemetry={
        "schema":"swrlz-repair-context-budget-v1",
        "mode":"compact-repair",
        "systemChars":len(system),
        "sourceChars":len(source),
        "directionChars":len(fitted_prompt),
        "priorFailureCount":len(prior),
        "receiptCategoryCount":len(state["receipt"]["categories"]),
        "activeUnavailableDependencyCount":len(state["repairConstraints"]["unavailableDependencies"]),
        "carriedUnavailableDependencyCount":len(state["repairConstraints"]["carriedUnavailableDependencies"]),
        "behaviorRepairBaseMode":repair_base.get("mode"),
        "behaviorCurrentScore":behavior.get("currentScore"),
        "behaviorBestKnownScore":behavior.get("bestKnownScore"),
        "behaviorRegressionCount":len(behavior.get("regressedCases") or []),
        "behaviorPreserveCount":len(behavior.get("preservePassingCases") or []),
    }
    return system,fitted_prompt,telemetry


def enforce_strategy_change(
    validation: dict[str, Any],
    candidate_fingerprint: str | None,
    repair_target_fingerprint: str | None,
    previous_attempt_fingerprint: str | None,
) -> dict[str, Any]:
    result=dict(validation or {})
    reasons=[str(x) for x in (result.get("reasons") or [])]
    if repair_target_fingerprint and candidate_fingerprint and candidate_fingerprint==repair_target_fingerprint:
        if "repair-stalled-no-executable-change" not in reasons:
            reasons.append("repair-stalled-no-executable-change")
    if previous_attempt_fingerprint and candidate_fingerprint and candidate_fingerprint==previous_attempt_fingerprint:
        if "strategy-repeat-previous-attempt" not in reasons:
            reasons.append("strategy-repeat-previous-attempt")
    result["reasons"]=reasons
    result["status"]="REJECT" if reasons else str(result.get("status") or "PASS")
    return result


def strategy_change_directive(programming: dict[str, Any], validation: dict[str, Any], attempt: int) -> str:
    evidence=programming.get("failureEvidence") if isinstance(programming.get("failureEvidence"),dict) else {}
    semantics=evidence.get("receiptSemantics") if isinstance(evidence.get("receiptSemantics"),dict) else {}
    constraints=programming.get("repairConstraints") if isinstance(programming.get("repairConstraints"),dict) else {}
    behavior=programming.get("behaviorLedger") if isinstance(programming.get("behaviorLedger"),dict) else {}
    repair_base=programming.get("behaviorRepairBase") if isinstance(programming.get("behaviorRepairBase"),dict) else {}
    reasons=[str(x) for x in ((validation or {}).get("reasons") or [])]
    categories=set(str(x) for x in (semantics.get("categories") or []))
    dependencies=[]
    for value in list(constraints.get("forbiddenDependencies") or [])+list(semantics.get("reportedDependencies") or []):
        value=str(value or "").strip()
        if value and value not in dependencies:
            dependencies.append(value)
    contract=programming.get("intentContract") if isinstance(programming.get("intentContract"),dict) else {}
    original=_strip_fences(str(contract.get("originalRequest") or ""))
    direction=(" ".join((_compact_user_direction(programming,""),original))).lower()

    directives=[
        f"STRATEGY CHANGE GATE attempt {int(attempt)}: the previous proposal was rejected.",
        "Produce a materially different executable candidate while preserving the original contract and required API.",
    ]
    if "dependency" in categories or any(x.startswith("dependency-still-referenced:") for x in reasons):
        if dependencies:
            directives.append("Remove the unavailable dependency from executable imports/references: "+", ".join(dependencies[:6])+".")
        else:
            directives.append("Replace the unavailable dependency boundary rather than repeating the same import/call.")
        if any(x in direction for x in ("standard library","stdlib","do not install","don't install","without install","no install")):
            directives.append("The user explicitly forbids installation/external dependency use; implement the behavior with supported built-ins/standard library.")
    preserve=[str(x) for x in (behavior.get("preservePassingCases") or []) if str(x)]
    regressions=[str(x) for x in (behavior.get("regressedCases") or []) if str(x)]
    current_failures=[str(x) for x in (behavior.get("currentFailingCases") or []) if str(x)]
    if preserve:
        directives.append("Preserve externally proven passing cases: "+", ".join(preserve[:20])+".")
    if regressions:
        directives.append("REGRESSION DETECTED: restore previously passing cases now failing: "+", ".join(regressions[:16])+".")
    if current_failures:
        directives.append("Current external failing cases to repair: "+", ".join(current_failures[:20])+".")
    if repair_base.get("mode")=="best-known-tested-source":
        directives.append("Start from the supplied best-known tested source, not the newer regressed implementation; incorporate the latest receipt delta without losing its proven wins.")
    if "repair-stalled-no-executable-change" in reasons or "strategy-repeat-previous-attempt" in reasons or "behavior-repair-base-unchanged" in reasons:
        directives.append("Do not reuse the same executable fingerprint, algorithmic operation, import path, or wrapper-only edit; change the causal implementation strategy while preserving the behavior ledger.")
    if any(x.startswith("diagnostic-symbol-resolution-unproven:") for x in reasons):
        directives.append("Resolve or remove the reported unresolved symbol in executable source.")
    if any(x.startswith("unresolved-browser-module:") for x in reasons):
        directives.append("Change the unresolved executable import path or its matching document import-map declaration; verify exact-name versus trailing-slash prefix resolution against the supplied library evidence. Repeating the same unmapped specifier cannot resolve this source defect.")
    if any(x.startswith("missing-required-language:") or x.startswith("language-contract-mismatch:") for x in reasons):
        directives.append("Obey the requested language contract exactly; do not substitute another language/framework.")
    directives.append("Return one complete candidate only; no TODO, ellipsis, fake execution claim, or rejected-source repetition.")
    return " ".join(directives)
