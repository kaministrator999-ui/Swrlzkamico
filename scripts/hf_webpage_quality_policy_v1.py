"""Focused §C webpage quality policy and bounded nonblocking artifact audit.

Scope: website/HTML code generation; never changes unrelated coding prompts,
chat/VR routes, model weights, provider settings, or completed source bytes.
"""
from __future__ import annotations
import ast
MARK="SWRLZ_WEBPAGE_QUALITY_POLICY_V1"

HELPER=r'''
# SWRLZ_WEBPAGE_QUALITY_POLICY_V1
def _swrlz_webpage_quality_policy(prompt, programming):
    """Build one compact, scoped quality target before the native code decode."""
    import re as _web_re
    words=str(prompt or "")
    is_open_ended=bool(_web_re.search(
        r"\b(?:cool|fun|creative|interesting|beautiful|awesome|impressive|"
        r"visually\s+striking|stylish|unique)\b",words,_web_re.I))
    general=(
      "WEBPAGE EXECUTABLE QUALITY CONTRACT: Return an intentionally designed, "
      "complete, self-contained page with a coherent visual concept, clear "
      "hierarchy, consistent spacing/typography, polished treatment of EVERY "
      "section, and an appropriate level of interactivity. Implement responsive "
      "layouts for narrow phone screens (including 320-390px widths): viewport "
      "meta, wrapping/collapsing navigation, no horizontal overflow, readable "
      "forms and tap targets, and no content clipped behind fixed headers. "
      "Buttons, links, tabs, menus, toggles, and forms must do something "
      "meaningful in the provided code. A 'Send message' button must NOT falsely "
      "imply delivery when no actual backend/contact destination was specified: "
      "instead omit it or implement a clearly labeled local demo behavior. "
      "Use accessible labels, keyboard/focus states, reduced-motion support "
      "when using motion, and semantic markup. Avoid dummy href='#', invented "
      "service APIs, broken links, placeholder projects, speculative company "
      "histories, stale copyright years and empty sections. If a feature cannot "
      "function without credentials/backend, do not simulate real success. "
      "Complete the final HTML/script/CSS and close its artifact fence once; "
      "do not ask the user to continue when the file already ends properly."
    )
    if is_open_ended:
        general+=(
          " OPEN-ENDED CREATIVE PAGE: Interpret a short 'make a cool webpage' "
          "request as one cohesive, visually distinctive, WORKING interactive "
          "experience, not a generic digital-agency marketing template or a "
          "collection of unrelated future studios. Prefer a compact polished "
          "concept with one or two implemented interactions over many decorative "
          "buttons. Do not invent three named sample clients or 'Project "
          "Alpha/Beta/Gamma' as filler. Every visible section must earn its place."
        )
    else:
        general+=(
          " USER-SPECIFIC PAGE: Follow supplied branding, structure, content, "
          "scope and preservation constraints exactly; do not replace the "
          "requested site with a generic concept or invent real business facts."
        )
    return general


def _swrlz_webpage_quality_risks(code, original_request):
    """Heuristic warnings only: NEVER change validation PASS to REJECT."""
    import re as _web_re
    src=str(code or "")
    requested=str(original_request or "")
    if not _web_re.search(r"(?is)<!doctype\s+html|<html\b",src):
        return []
    flags=[]
    if not _web_re.search(r"(?is)<meta\b[^>]*name\s*=\s*['\"]viewport['\"]",src):
        flags.append("mobile-viewport-missing")
    if (_web_re.search(r"(?is)<form\b",src)
        and not _web_re.search(
            r"(?is)addEventListener\s*\(\s*['\"]submit['\"]|"
            r"\bonSubmit\s*=|\baction\s*=\s*['\"](?!#|javascript:)[^'\"]+['\"]",
            src)):
        flags.append("form-submission-not-implemented")
    if (_web_re.search(r"(?i)\bProject\s+(?:Alpha|Beta|Gamma)\b",src)
        and not _web_re.search(r"(?i)\bProject\s+(?:Alpha|Beta|Gamma)\b",requested)):
        flags.append("invented-project-placeholder")
    if _web_re.search(r"(?is)<a\b[^>]*href\s*=\s*['\"]#['\"]",src):
        flags.append("unresolved-navigation-anchor")
    return flags
'''

def one(src,needle,replacement,label):
    n=src.count(needle)
    if n!=1:raise RuntimeError("SOURCE_SHAPE_DRIFT_"+label+"_"+str(n))
    return src.replace(needle,replacement,1)

WEB_DELIVERY='''    web_page_delivery=(bool(programming.get("codingTask")) and
        ((programming.get("intentContract") or {}).get("languageContract") or {}).get("artifactType")=="web-page" and
        programming.get("changeClass") not in ("review","explain"))'''

REPAIR_FIT='''        fitted=_fit_repair_messages(model,system,history,fitted_prompt,delivery_output_limit)'''
NORMAL_FIT='''    else:
        fitted=_fit_messages(model,system,history,prompt,delivery_output_limit,preserve_latest_code=preserve_existing_source(programming))'''

SHARED='''    shared=candidate_contract_gate(source,programming,history)
    for reason in shared.get("reasons") or []:
        if reason not in reasons:
            reasons.append(reason)
    result={"status":"REJECT" if reasons else "PASS","reasons":reasons}'''

NEW_SHARED='''    shared=candidate_contract_gate(source,programming,history)
    for reason in shared.get("reasons") or []:
        if reason not in reasons:
            reasons.append(reason)
    result={"status":"REJECT" if reasons else "PASS","reasons":reasons}
    # SWRLZ_WEBPAGE_QUALITY_POLICY_V1: surface honest risks without triggering
    # another multi-minute regeneration loop for a finished HTML file.
    contract=programming.get("intentContract") if isinstance(programming.get("intentContract"),dict) else {}
    webpage=((contract.get("languageContract") or {}).get("artifactType")=="web-page")
    if webpage:
        quality_flags=_swrlz_webpage_quality_risks(candidate_primary,original)
        if quality_flags:
            result["webPageQualityRisks"]=quality_flags'''

def patch_coder(raw):
    src=raw.decode("utf-8")
    if MARK in src:raise RuntimeError("ALREADY_PATCHED")
    if "SWRLZ_CLOSE_COMPLETE_HTML_FENCE_V1" not in src:
        raise RuntimeError("COMPLETED_HTML_GATE_NOT_PRESENT")
    src=one(src,"def generate_events(payload):",HELPER+"def generate_events(payload):","WEB_QUALITY_HELPER")
    if WEB_DELIVERY not in src:raise RuntimeError("HTML_CODING_ROUTE_CHANGED")
    src=one(src,REPAIR_FIT,
       '''        if web_page_delivery and not source_change_mode:
            system+="\\n"+_swrlz_webpage_quality_policy(prompt,programming)
'''+REPAIR_FIT,
       "REPAIR_QUALITY_CONTEXT")
    src=one(src,NORMAL_FIT,
       '''    else:
        if web_page_delivery and not source_change_mode:
            system+="\\n"+_swrlz_webpage_quality_policy(prompt,programming)
        fitted=_fit_messages(model,system,history,prompt,delivery_output_limit,preserve_latest_code=preserve_existing_source(programming))''',
       "NORMAL_QUALITY_CONTEXT")
    src=one(src,SHARED,NEW_SHARED,"NONBLOCKING_QUALITY_RISKS")
    ast.parse(src,filename="qwen_coder_engine.py")
    return src.encode("utf-8")
