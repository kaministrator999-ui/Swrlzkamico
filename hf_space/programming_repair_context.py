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
    behavior=programming.get("behaviorLedger") if isinstance(programming.get("behaviorLedger"),dict) else {}
    repair_base=programming.get("behaviorRepairBase") if isinstance(programming.get("behaviorRepairBase"),dict) else {}
    source=str(programming.get("behaviorRepairBaseSource") or evidence.get("repairSource") or "")[:9000]
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
    if any(x.startswith("missing-required-language:") or x.startswith("language-contract-mismatch:") for x in reasons):
        directives.append("Obey the requested language contract exactly; do not substitute another language/framework.")
    directives.append("Return one complete candidate only; no TODO, ellipsis, fake execution claim, or rejected-source repetition.")
    return " ".join(directives)
