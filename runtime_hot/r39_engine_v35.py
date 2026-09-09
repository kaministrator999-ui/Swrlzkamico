"""R39 hot v35: soft-median response horizon and semantic wrap-up instrumentation over v34."""
from __future__ import annotations
import re
import urllib.request
_V34_URL="https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/dev/runtime_hot/r39_engine_v34.py"
_req=urllib.request.Request(_V34_URL,headers={"User-Agent":"swrlz-hot-r39-v35"})
with urllib.request.urlopen(_req,timeout=20) as _response: _source=_response.read(4_000_001)
if len(_source)>4_000_000: raise RuntimeError("R39_V34_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"),_V34_URL+"#v35","exec"),globals(),globals())
_V35_BASE_ADAPTIVE=_adaptive_generation
_V35_BASE_CONTROLLED=_controlled_payload
_V35_BASE_GENERATE=generate_events
_PERSISTENT_ROUTINE = _PERSISTENT_ROUTINE + (" Preserve received user text as the receipt. When a token is literally valid but semantically anomalous, infer the smallest plausible repair from surrounding context and assign confidence before using it. High-confidence repairs may be surfaced as 'I think you meant X'; uncertain repairs remain ambiguous. This is general contextual repair, not an STT-only spellcheck. If provenance is supplied, treat modality, STT confidence, and candidate alternatives as evidence that updates repair probability, never as authority. When a response contains copyable code, commands, lyrics, structured text, or other composition whose exact whitespace matters, use a fenced code block so the UI can expose a copy control. ")

def _adaptive_generation(generation,profile):
    g,old=_V35_BASE_ADAPTIVE(generation,profile); requested=max(32,int((generation or {}).get("maxTokens",512))); scale=profile["responseScale"]
    if scale==_SCALE_SHORT: soft=min(128,requested); safety=max(512,soft*4)
    elif scale==_SCALE_NORMAL: soft=max(256,min(640,max(requested,320))); safety=max(1024,soft*4)
    elif scale==_SCALE_EXPANDED: soft=max(512,min(900,max(requested,512))); safety=max(1536,soft*4)
    elif scale==_SCALE_EXTENDED: soft=max(768,min(1400,max(requested,768))); safety=max(2048,soft*4)
    else: soft=max(1200,min(2200,max(requested,1200))); safety=max(3072,soft*4)
    safety=min(8192,safety); g["maxTokens"]=safety
    return g,{**old,"requestedPlanningTokens":requested,"softTargetTokens":soft,"emergencyCeilingTokens":safety,"horizonModel":"soft-median-planning-plus-dynamic-safety-runway","legacyHardMax":False}

def _structure_state(text):
    s=str(text or ""); fences=s.count("```")
    return {"openFence":fences%2==1,"openParen":s.count("(")>s.count(")"),"openBracket":s.count("[")>s.count("]"),"openBrace":s.count("{")>s.count("}"),"endsSentence":bool(re.search(r"[.!?。！？]\\s*$",s)),"endsLine":bool(s.endswith("\\n"))}

def _controlled_payload(payload):
    clone,contract,info=_V35_BASE_CONTROLLED(payload); profile=dict(clone.get("_adaptiveProfile") or {})
    generation,plan=_adaptive_generation(clone.get("generation") if isinstance(clone.get("generation"),dict) else {},profile); clone["generation"]=generation
    behavior=dict(clone.get("_conversationBehavior") or {}); behavior.update({"softTargetTokens":plan["softTargetTokens"],"emergencyCeilingTokens":plan["emergencyCeilingTokens"],"wrapUpPolicy":"finish-open-structure-before-natural-eos","planningHorizon":"median-not-quota","copyableCompositionPolicy":"fenced-code-for-exact-copy-content","contextualRepairPolicy":"receipt-preserved-smallest-plausible-repair-with-confidence"})
    clone["_conversationBehavior"]=behavior; clone["_adaptiveProfile"]={**profile,**plan}; return clone,contract,info

def generate_events(payload,is_cancelled=None):
    profile=_message_profile(str(payload.get("prompt") or "")); _,plan=_adaptive_generation(payload.get("generation") if isinstance(payload.get("generation"),dict) else {},profile)
    text=""; approx_words=0; horizon_reported=False; wrap_reported=False
    for event in _V35_BASE_GENERATE(payload,is_cancelled):
        if isinstance(event,dict) and event.get("type")=="DELTA":
            chunk=str(event.get("text") or ""); text+=chunk; approx_words=len(re.findall(r"\\S+",text)); state=_structure_state(text)
            if not horizon_reported and approx_words>=plan["softTargetTokens"]:
                horizon_reported=True; yield {"type":"STATUS","phase":"RESPONSE_HORIZON","reason":f"soft planning horizon reached · approxWords={approx_words} · scale={profile['responseScale']} · openStructure={any(state[k] for k in ('openFence','openParen','openBracket','openBrace'))} · naturalEosPreferred=true"}
            if not wrap_reported and approx_words>=max(1,plan["softTargetTokens"]-16) and any(state[k] for k in ('openFence','openParen','openBracket','openBrace')):
                wrap_reported=True; yield {"type":"STATUS","phase":"WRAP_UP_INSTRUMENTATION","reason":"Near the soft horizon with an open output structure; continue until the current structure can close naturally rather than cutting the response."}
        yield event
    if not horizon_reported: yield {"type":"STATUS","phase":"RESPONSE_HORIZON","reason":f"response ended naturally before soft horizon · scale={profile['responseScale']} · naturalEosPreferred=true"}

_impl.HOT_SERVER_VERSION="2.1.44"; _impl.HOT_REVISION="2.1.44-hot-boundary-v35-soft-median-response-horizon-v5.1"; HOT_SERVER_VERSION=_impl.HOT_SERVER_VERSION; HOT_REVISION=_impl.HOT_REVISION
_V35_BASE_INSPECT=inspect_engine

def inspect_engine():
    result=_V35_BASE_INSPECT()
    if isinstance(result,dict): result.update({"hotServerVersion":HOT_SERVER_VERSION,"hotRevision":HOT_REVISION,"responseHorizonController":"v35","softPlanningHorizon":True,"softHorizonIsQuota":False,"dynamicEmergencyRunway":True,"maxEmergencyCeilingTokens":8192,"wrapUpInstrumentation":True,"openStructureCompletion":True,"naturalEosPreferred":True,"contextualRepairPolicy":"general-intent-preserving-repair-v1","copyableCompositionPolicy":"fenced-code-copy-ui-v1"})
    return result
