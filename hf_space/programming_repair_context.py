"""Shared bounded repair-context and strategy helpers for §wyrlz programming routes.

This module renders already-authoritative Brain state into a compact model-facing
form. It does not own intent, receipt classification, artifact mutation, or
acceptance truth.
"""
from __future__ import annotations

import json
import re
from typing import Any


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
    return direction[:1600]


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
    source=str(evidence.get("repairSource") or "")[:9000]
    direction=_compact_user_direction(programming,prompt)
    prior=[]
    for item in (programming.get("failureHistory") or [])[-2:]:
        if not isinstance(item,dict):
            continue
        prior.append({
            "categories":_bounded(item.get("categories"),6,60),
            "candidateFingerprint":str(item.get("candidateFingerprint") or "")[:40] or None,
            "failureSignals":_bounded(item.get("failureSignals"),3,220),
        })

    state={
        "schema":"swrlz-compact-repair-context-v1",
        "changeClass":str(programming.get("changeClass") or "fix"),
        "originalRequest":str(contract.get("originalRequest") or "")[:2200],
        "must":_bounded(contract.get("must"),10,320),
        "mustNot":_bounded(contract.get("mustNot"),10,320),
        "preserve":_bounded(contract.get("preserve"),10,320),
        "languageContract":{
            "requestedLanguages":list(language.get("requestedLanguages") or [])[:8],
            "requiredLanguages":list(language.get("requiredLanguages") or [])[:8],
            "allowedLanguages":list(language.get("allowedLanguages") or [])[:10],
            "artifactType":language.get("artifactType"),
            "substitutionAllowed":language.get("substitutionAllowed"),
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
        "or repeat a rejected executable candidate. Preserve passing signals. A structural candidate pass is not execution proof; never claim compile/test/runtime success without a new external receipt. "
        "If a prior strategy stalled, materially change the relevant algorithm/dependency/control/data-flow strategy while preserving the contract."
    )
    system=rules+"\n"+str(response_mode or "")+"\nREPAIR STATE:\n"+json.dumps(state,ensure_ascii=False,separators=(",",":"))
    if source:
        system+="\nCANONICAL SOURCE UNDER REPAIR:\n"+source
    fitted_prompt=direction or "Repair the canonical source against the receipt and original contract. Return the complete corrected candidate."
    telemetry={
        "schema":"swrlz-repair-context-budget-v1",
        "mode":"compact-repair",
        "systemChars":len(system),
        "sourceChars":len(source),
        "directionChars":len(fitted_prompt),
        "priorFailureCount":len(prior),
        "receiptCategoryCount":len(state["receipt"]["categories"]),
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
    reasons=[str(x) for x in ((validation or {}).get("reasons") or [])]
    categories=set(str(x) for x in (semantics.get("categories") or []))
    dependencies=[str(x) for x in (semantics.get("reportedDependencies") or []) if str(x)]
    direction=_compact_user_direction(programming,"").lower()

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
    if "repair-stalled-no-executable-change" in reasons or "strategy-repeat-previous-attempt" in reasons:
        directives.append("Do not reuse the same executable fingerprint, algorithmic operation, import path, or wrapper-only edit; change the causal implementation strategy.")
    if any(x.startswith("diagnostic-symbol-resolution-unproven:") for x in reasons):
        directives.append("Resolve or remove the reported unresolved symbol in executable source.")
    if any(x.startswith("missing-required-language:") or x.startswith("language-contract-mismatch:") for x in reasons):
        directives.append("Obey the requested language contract exactly; do not substitute another language/framework.")
    directives.append("Return one complete candidate only; no TODO, ellipsis, fake execution claim, or rejected-source repetition.")
    return " ".join(directives)
