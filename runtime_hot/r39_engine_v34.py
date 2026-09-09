"""R39 hot v34: adaptive intent/response profile controller over v33 vector-GQA runtime.

The user's message is scored for semantic scale, composition type, technicality, freshness,
and message complexity. Those signals tune sampling conservatively and convert the UI token
number into a soft planning horizon with a larger emergency decode runway. Natural EOS remains
the normal stop condition; the emergency ceiling exists only to prevent runaway generation.
"""
from __future__ import annotations
import re
import urllib.request

_V27_COMMIT="a7de2c488f97dc4f2f6d019e88edea7021ab2dfc"
_BATCH_COMMIT="6ed1d855899db47fce6da849e407f707f89f04d4"
_V27_URL=f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V27_COMMIT}/runtime_hot/r39_engine_v27.py"
_req=urllib.request.Request(_V27_URL,headers={"User-Agent":"swrlz-hot-r39-v34"})
with urllib.request.urlopen(_req,timeout=20) as _response: source=_response.read(4_000_001)
if len(source)>4_000_000: raise RuntimeError("R39_V27_SOURCE_TOO_LARGE")
text=source.decode("utf-8")
_old='''_V26_COMMIT = "3dc70e8d02777fd622db3ae3311fad13b7382e6a"
_V26_URL = f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V26_COMMIT}/runtime_hot/r39_engine.py"
'''
_new=f'''_V26_COMMIT = "{_BATCH_COMMIT}"
_V26_URL = f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{{_V26_COMMIT}}/runtime_hot/r39_engine_v26_batch.py"
'''
if _old not in text: raise RuntimeError("R39_V34_V27_BASE_TARGET_MISSING")
text=text.replace(_old,_new,1)
exec(compile(text,_V27_URL+"#v34","exec"),globals(),globals())

# Persistent policy stays byte-stable inside a version so append-prefix reuse remains valid.
_PERSISTENT_ROUTINE=(
    "RC3.2 Your canonical name is §wyrlz. You are a warm, witty, adaptive conversational intelligence: "
    "playful in casual chat, evidence-first in engineering, technically exact in both. The human is the user; "
    "user/assistant/system/AI are roles, not names. Only the user may set a nickname; it never replaces §wyrlz. "
    "Infer the requested operation from the whole current message plus recent context; message length is evidence "
    "of complexity, not a command to be equally long. A correction replaces the superseded interpretation. "
    "Length modifiers are semantic composition controls: 'extend' means a modest continuation of the existing "
    "composition; 'extended' or 'extensive' means a substantially expanded composition; 'massive' means broad, "
    "deep expansion. Expansion must remain on-topic and add new value rather than padding or repetition. "
    "Treat response length as a soft planning horizon, never a quota. Finish the current sentence, paragraph, list "
    "item, code block, song section, or other open structure before ending unless the user explicitly requests a "
    "fragment. Do not start a major new section when the requested work is already complete. Prefer natural EOS "
    "after semantic completion. Preserve the user's analogy before extending it; infer understandable coined words "
    "from context. Separate fact from inference. Freshness-sensitive claims may require external evidence; do not "
    "pretend stale learned knowledge is current. Mutation/deployment authority must be explicit."
)

_SCALE_SHORT="SHORT"
_SCALE_NORMAL="NORMAL"
_SCALE_EXPANDED="EXPANDED"
_SCALE_EXTENDED="EXTENDED"
_SCALE_MASSIVE="MASSIVE"

def _message_profile(prompt):
    raw=str(prompt or "").strip(); low=" ".join(raw.lower().split())
    words=re.findall(r"[\w§'’\-]+",raw,flags=re.UNICODE); word_count=len(words); chars=len(raw)
    sentences=max(1,len(re.findall(r"[.!?]+(?:\s|$)",raw))) if raw else 0
    qmarks=raw.count("?")
    creative=bool(re.search(r"\b(song|lyrics?|poem|story|rap|verse|chorus|bridge|creative|write me|compose)\b",low))
    technical=bool(re.search(r"\b(code|coding|debug|server|runtime|model|lalm|api|kernel|tensor|architecture|database|vercel|github|latency|prefill|decode|parameter|statistical|instrumentation)\b",low))
    freshness=bool(re.search(r"\b(latest|current|today|recent|newest|research online|search online|look up|up[- ]to[- ]date|breaking)\b",low))
    continuation=bool(re.search(r"\b(make it extend|extend it|extend this|continue it|continue this|add more|keep going)\b",low))
    if re.search(r"\b(one word|name only|just the result|result only|brief|short|concise|compact)\b",low): scale=_SCALE_SHORT
    elif re.search(r"\b(massive|enormous|huge|giant|epic|very long|as long as useful)\b",low): scale=_SCALE_MASSIVE
    elif re.search(r"\b(extended|extensive|exhaustive|comprehensive|in[- ]depth|detailed|deep dive)\b",low): scale=_SCALE_EXTENDED
    elif continuation or re.search(r"\b(expand|expanded|more detail|elaborate)\b",low): scale=_SCALE_EXPANDED
    else: scale=_SCALE_NORMAL
    complexity=min(1.0,(word_count/140.0)+(0.16 if technical else 0)+(0.12 if creative else 0)+(0.10 if qmarks>1 else 0)+(0.08 if sentences>3 else 0))
    return {"raw":raw,"wordCount":word_count,"charCount":chars,"sentences":sentences,"questionMarks":qmarks,"creative":creative,"technical":technical,"freshnessSensitive":freshness,"continuation":continuation,"responseScale":scale,"complexity":complexity}

def _intent(prompt):
    p=_message_profile(prompt); raw=p["raw"]; text=" ".join(raw.lower().split())
    minimal=p["responseScale"]==_SCALE_SHORT and bool(re.search(r"\b(one word|name only|just the result|result only|no explanation)\b",text))
    if any(re.search(x,text) for x in _SELF_EXPLAIN): kind="SELF_EXPLANATION"
    elif any(re.search(x,text) for x in _SELF_NAME): kind="SELF_NAME_QUERY"
    elif re.search(_CORRECTION,text): kind="CORRECTION"
    elif re.search(_ACTION,text): kind="ENGINEERING_ACTION"
    elif p["freshnessSensitive"]: kind="FRESH_RESEARCH"
    elif p["creative"]: kind="CREATIVE_COMPOSITION"
    elif re.search(r"\bwhy\b|\bhow come\b|\bwhat makes\b",text): kind="WHY_EXPLANATION"
    elif re.search(_PLAY,text): kind="PLAYFUL_CASUAL"
    elif re.search(_CONT,text) and len(text.split())<=24: kind="CONTEXT_CONTINUATION"
    elif "?" in raw or re.match(r"^(what|who|when|where|how|can|do|does|is|are|will|would|could|should)\b",text): kind="DIRECT_QA"
    elif p["responseScale"] in {_SCALE_EXTENDED,_SCALE_MASSIVE}: kind="LONGFORM_EXPLANATION"
    else: kind="GENERAL"
    floors={"SELF_NAME_QUERY":6,"SELF_EXPLANATION":14,"CORRECTION":9,"ENGINEERING_ACTION":7,"FRESH_RESEARCH":8,"CREATIVE_COMPOSITION":10,"WHY_EXPLANATION":12,"PLAYFUL_CASUAL":5,"CONTEXT_CONTINUATION":6,"DIRECT_QA":6,"LONGFORM_EXPLANATION":12,"GENERAL":4}
    minimum=0 if minimal else floors[kind]
    if p["responseScale"]==_SCALE_MASSIVE: minimum=max(minimum,20)
    elif p["responseScale"]==_SCALE_EXTENDED: minimum=max(minimum,14)
    return {"kind":kind,"minimum":minimum,"minimal":minimal,"profile":p}

def _reasoning_contract(prompt):
    contract=_reasoning_contract_v34_base(prompt) if callable(globals().get("_reasoning_contract_v34_base")) else {"axes":[],"modes":[],"objectives":[],"mutation":"M0","verification":"V0","length":"NORMAL"}
    p=_message_profile(prompt)
    scale=p["responseScale"]
    if scale==_SCALE_SHORT: contract["length"]="BRIEF"
    elif scale==_SCALE_EXPANDED: contract["length"]="EXPANDED"
    elif scale==_SCALE_EXTENDED: contract["length"]="EXTENDED"
    elif scale==_SCALE_MASSIVE: contract["length"]="MASSIVE"
    return contract

_reasoning_contract_v34_base=globals().get("_reasoning_contract")
# Rebind after saving base; function above resolves this variable when called.

def _adaptive_generation(generation,profile):
    g=dict(generation or {})
    base_temp=float(g.get("temperature",0.7)); base_top=float(g.get("topP",0.95)); requested=max(32,int(g.get("maxTokens",512)))
    scale=profile["responseScale"]
    soft={_SCALE_SHORT:min(128,requested),_SCALE_NORMAL:min(max(192,requested),640),_SCALE_EXPANDED:max(384,min(requested,768)),_SCALE_EXTENDED:max(640,min(requested,1024)),_SCALE_MASSIVE:max(1024,requested)}[scale]
    if scale==_SCALE_SHORT: hard=max(256,soft+128)
    elif scale==_SCALE_NORMAL: hard=max(768,soft+256)
    elif scale==_SCALE_EXPANDED: hard=max(1024,soft+384)
    elif scale==_SCALE_EXTENDED: hard=max(1536,soft+512)
    else: hard=max(2048,soft+768)
    hard=min(2048,hard)
    delta=0.0; top_delta=0.0
    if profile["creative"]: delta+=0.06; top_delta+=0.015
    if profile["technical"]: delta-=0.05; top_delta-=0.02
    if profile["complexity"]>0.65: delta-=0.025
    if profile["continuation"]: delta-=0.015
    g["temperature"]=min(1.25,max(0.05,base_temp+delta)); g["topP"]=min(1.0,max(0.50,base_top+top_delta)); g["maxTokens"]=hard
    return g,{"requestedPlanningTokens":requested,"softTargetTokens":soft,"emergencyCeilingTokens":hard,"baseTemperature":base_temp,"effectiveTemperature":g["temperature"],"baseTopP":base_top,"effectiveTopP":g["topP"]}

def _controlled_payload(payload):
    clone=dict(payload); history=[dict(t) for t in list(clone.get("history") or []) if isinstance(t,dict)]
    info=_intent(str(clone.get("prompt") or "")); prev=_last_assistant(history); profile=info["profile"]
    clone["history"]=[{"role":"SYSTEM","text":_PERSISTENT_ROUTINE}]+history
    generation,adaptive=_adaptive_generation(clone.get("generation") if isinstance(clone.get("generation"),dict) else {},profile)
    clone["generation"]=generation
    behavior={"intent":info["kind"],"minDecodeTokens":info["minimum"],"previousAssistantText":prev,"responseScale":profile["responseScale"],"softTargetTokens":adaptive["softTargetTokens"],"emergencyCeilingTokens":adaptive["emergencyCeilingTokens"],"freshnessSensitive":profile["freshnessSensitive"]}
    if info["kind"]=="SELF_NAME_QUERY": behavior.update({"requiredText":_CANONICAL_NAME,"blockRoleIdentityStarts":True})
    if info["kind"] in {"SELF_EXPLANATION","WHY_EXPLANATION","CORRECTION"}: behavior["avoidPreviousAssistantEcho"]=True
    if info["kind"]=="SELF_EXPLANATION": behavior["blockRoleIdentityStarts"]=True
    clone["_conversationBehavior"]=behavior; clone["_adaptiveProfile"]={**profile,**adaptive}
    return clone,_reasoning_contract(str(clone.get("prompt") or "")),info

_V34_BASE_GENERATE=generate_events

def generate_events(payload,is_cancelled=None):
    profile=_message_profile(str(payload.get("prompt") or "")); generation,adaptive=_adaptive_generation(payload.get("generation") if isinstance(payload.get("generation"),dict) else {},profile)
    inserted=False
    for event in _V34_BASE_GENERATE(payload,is_cancelled):
        yield event
        if not inserted and isinstance(event,dict) and event.get("phase")=="CONVERSATION_INTENT":
            inserted=True
            yield {"type":"STATUS","phase":"ADAPTIVE_RESPONSE_PROFILE","reason":f"words={profile['wordCount']} · chars={profile['charCount']} · complexity={profile['complexity']:.2f} · scale={profile['responseScale']} · creative={profile['creative']} · technical={profile['technical']} · freshnessSensitive={profile['freshnessSensitive']} · softTarget={adaptive['softTargetTokens']} · emergencyCeiling={adaptive['emergencyCeilingTokens']} · temperature={adaptive['baseTemperature']:.2f}→{adaptive['effectiveTemperature']:.2f} · topP={adaptive['baseTopP']:.2f}→{adaptive['effectiveTopP']:.2f}"}

_impl.HOT_SERVER_VERSION="2.1.43"
_impl.HOT_REVISION="2.1.43-hot-boundary-v34-adaptive-intent-response-controller-v5.0"
HOT_SERVER_VERSION=_impl.HOT_SERVER_VERSION; HOT_REVISION=_impl.HOT_REVISION
_V34_BASE_INSPECT=inspect_engine

def inspect_engine():
    result=_V34_BASE_INSPECT()
    if isinstance(result,dict):
        result.update({"hotServerVersion":HOT_SERVER_VERSION,"hotRevision":HOT_REVISION,"reasoningControlSpecVersion":"3.2","adaptiveIntentProfile":True,"messageLengthSignals":True,"semanticResponseScale":True,"responseScales":["SHORT","NORMAL","EXPANDED","EXTENDED","MASSIVE"],"extendSemantics":"modest-continuation","extendedSemantics":"large-composition-expansion","massiveSemantics":"deep-broad-expansion-with-anti-padding","adaptiveSampling":True,"softResponsePlanningHorizon":True,"emergencyDecodeCeiling":2048,"legacy512DecodeClampRemoved":True,"freshnessSensitivityRecognition":True,"naturalEosPreferred":True,"openStructureCompletionPolicy":True,"batchSourceCommit":_BATCH_COMMIT})
    return result
