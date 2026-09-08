"""Hot R39 v24 stable identity grounding + canonical append cursor.

Canonical identity is now part of the invariant employee routine on every turn. Intent
only controls verification; it never changes model-facing prefix text. This restores exact
same-worker append reuse while keeping natural generation and completion grounding.
"""
from __future__ import annotations
import re,types,urllib.request
_IMPL_URL="https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/dev/runtime_hot/r39_engine_impl.py"
_req=urllib.request.Request(_IMPL_URL,headers={"User-Agent":"swrlz-hot-r39-v24"})
with urllib.request.urlopen(_req,timeout=20) as _response:_source=_response.read(4_000_001)
if len(_source)>4_000_000:raise RuntimeError("R39_IMPL_TOO_LARGE")
_source_text=_source.decode("utf-8")

_old_eos='''            if model.tokenizer.eos is not None and next_token == int(model.tokenizer.eos):
                yield {"type": "STATUS", "phase": "STOP_DIAGNOSTIC", "reason": f"EOS selected at decode step {ordinal}."}
                break
'''
_new_eos='''            if model.tokenizer.eos is not None and next_token == int(model.tokenizer.eos):
                sequence_tokens.append(next_token)
                logits = _forward_hot(model, next_token, state, need_logits=True, diag=None)
                if logits is None: raise base.R39InferenceError("R39_CURSOR_EOS_LOGITS_MISSING", "EOS cursor finalization returned no logits.")
                framing_tokens=list(model.tokenizer.encode("\\n"));bos_id=None
                try:
                    probe=list(model.tokenizer.encode(""));bos_id=int(probe[0]) if probe else None
                except Exception: bos_id=None
                stripped_bos=False
                if bos_id is not None and framing_tokens and int(framing_tokens[0])==bos_id:
                    framing_tokens=framing_tokens[1:];stripped_bos=True
                for framing_token in framing_tokens:
                    sequence_tokens.append(int(framing_token));logits=_forward_hot(model,int(framing_token),state,need_logits=True,diag=None)
                    if logits is None: raise base.R39InferenceError("R39_CURSOR_FRAME_LOGITS_MISSING", "Post-generation framing returned no logits.")
                yield {"type":"STATUS","phase":"HOT_CURSOR_READY","reason":f"EOS selected at decode step {ordinal}; committed EOS + {len(framing_tokens)} canonical end-of-turn framing token(s); strippedSyntheticBos={stripped_bos}."}
                break
'''
if _old_eos not in _source_text:raise RuntimeError("R39_V24_EOS_PATCH_TARGET_MISSING")
_source_text=_source_text.replace(_old_eos,_new_eos,1)

_old_lookup='''        prefix_len, cached_state, cached_logits = _prefix_get(tokens)
        state = cached_state if cached_state is not None else base.RecurrentState()
'''
_new_lookup='''        with _PREFIX_LOCK: entries=[{"tokens":list(x.get("tokens") or []),"usedAt":float(x.get("usedAt",0.0))} for x in _PREFIX_CACHE]
        entries.sort(key=lambda x:x["usedAt"],reverse=True);best=None;rows=[];now=time.time()
        for idx,entry in enumerate(entries):
            cached=entry["tokens"];limit=min(len(cached),len(tokens));lcp=0
            while lcp<limit and cached[lcp]==tokens[lcp]:lcp+=1
            rows.append(f"#{idx}:len={len(cached)},lcp={lcp},age={max(0.0,now-entry['usedAt']):.1f}s")
            if best is None or lcp>best["lcp"]:best={"index":idx,"tokens":cached,"lcp":lcp}
        yield {"type":"STATUS","phase":"PREFIX_CACHE_DIAGNOSTIC","reason":f"current={len(tokens)} token(s) · resident={len(entries)} · "+(" · ".join(rows) if rows else "cache empty")}
        if best is not None:
            cached=best["tokens"];lcp=int(best["lcp"])
            if lcp<min(len(cached),len(tokens)):yield {"type":"STATUS","phase":"PREFIX_MISMATCH","reason":f"best resident entry #{best['index']} diverges at token {lcp+1}; cached={int(cached[lcp])}:{_token_text(model,int(cached[lcp]))!r}, current={int(tokens[lcp])}:{_token_text(model,int(tokens[lcp]))!r}."}
            elif len(cached)<=len(tokens):yield {"type":"STATUS","phase":"PREFIX_MATCH","reason":f"best resident entry #{best['index']} is an exact {len(cached)}-token prefix of {len(tokens)}; only appended suffix requires prefill."}
            else:yield {"type":"STATUS","phase":"PREFIX_TRUNCATION","reason":f"current request ends at {lcp} token(s) while resident entry #{best['index']} continues to {len(cached)}."}
        prefix_len,cached_state,cached_logits=_prefix_get(tokens);state=cached_state if cached_state is not None else base.RecurrentState()
'''
if _old_lookup not in _source_text:raise RuntimeError("R39_V24_PREFIX_PATCH_TARGET_MISSING")
_source_text=_source_text.replace(_old_lookup,_new_lookup,1)

_old_yield='''                yield {
                    "type": "STATUS",
                    "phase": "PREFILL",
                    "reason": f"Prefill {ordinal}/{total} · {token_s:.3f}s token · {avg:.3f}s new-token avg · ETA {eta:.1f}s · reused={prefix_len} · backend={('native' if native else 'python')}.",
                }
'''
_new_yield='''                if processed == 1 or ordinal == total or processed % 32 == 0:
                    yield {"type":"STATUS","phase":"PREFILL","reason":f"Prefill {ordinal}/{total} · {token_s:.3f}s token · {avg:.3f}s new-token avg · ETA {eta:.1f}s · reused={prefix_len} · backend={('native' if native else 'python')}."}
'''
if _old_yield not in _source_text:raise RuntimeError("R39_V24_PREFILL_PATCH_TARGET_MISSING")
_source_text=_source_text.replace(_old_yield,_new_yield,1)

_impl=types.ModuleType("swrlz_hot_r39_engine_impl_v24");_impl.__file__=_IMPL_URL
exec(compile(_source_text,_IMPL_URL,"exec"),_impl.__dict__)
_impl.HOT_SERVER_VERSION="2.1.33";_impl.HOT_REVISION="2.1.33-hot-boundary-v24-stable-grounded-identity-v2.2";_impl._REFERENCE_RERANK_CANDIDATES=6
_original_format_stats=_impl._format_stats
def _format_stats(stats):return "skipped" if not stats else _original_format_stats(stats)
_impl._format_stats=_format_stats
_CANONICAL_NAME="§wyrlz"
_RULES=((r"\b(brief|short)\b","C2"),(r"\b(concise|compact)\b","C1"),(r"\b(exhaustive)\b","B3"),(r"\b(comprehensive)\b","B2"),(r"\b(deep|mechanistic|root cause)\b","D3"),(r"\b(in[- ]depth|detailed)\b","D2"),(r"\b(expert[- ]level|implementation[- ]ready)\b","T3"),(r"\b(technical|technically)\b","T2"),(r"\b(just the result|result only|no explanation)\b","PV0"))
_MODE_RULES=((r"\b(diagnose|diagnostic|failure|root cause|why .* fail)\b","DIAGNOSTIC","FIND_ROOT_CAUSE"),(r"\b(compare|comparative|versus|\bvs\b)\b","COMPARATIVE","SELECT_BEST_OPTION"),(r"\b(fact[- ]check|verify|validate|audit)\b","VERIFICATION","VERIFY"),(r"\b(design|architecture|redesign)\b","ARCHITECTURE","DESIGN"))
_IDENTITY_PATTERNS=(r"\bwhat(?:'s| is) your (?:name|main name)\b",r"\bwhat (?:can|should|do) i call you\b",r"\bwhat are you called\b",r"\bwhat do you go by\b",r"\bhow should i address you\b",r"\bwho are you\b",r"\bwho am i (?:talking|speaking) to\b",r"\bidentify yourself\b",r"\btell me your name\b",r"\byour name\??$")

def _reasoning_contract(prompt):
    text=" ".join(str(prompt or "").lower().split());fam={};modes=[];objectives=[]
    for pattern,code in _RULES:
        if re.search(pattern,text):fam[re.match(r"[A-Z]+",code).group(0)]=code
    for pattern,mode,obj in _MODE_RULES:
        if re.search(pattern,text):modes.append(mode);objectives.append(obj)
    mutation="M3" if re.search(r"\b(deploy|release|publish)\b",text) else "M2" if re.search(r"\b(fix|patch|update|modify|change|implement|build)\b",text) else "M1" if re.search(r"\b(suggest|propose|draft (?:a )?patch)\b",text) else "M0"
    if re.search(r"\b(do not|don't|dont|no) (?:change|modify|patch|deploy|execute|run)\b|\bread[- ]only\b",text):mutation="M0"
    verify="V4" if re.search(r"\b(audit|audit-grade)\b",text) else "V3" if re.search(r"\b(reproduce|cross[- ]check|proof)\b",text) else "V2" if re.search(r"\b(verify|validate|test|regression)\b",text) else "V1" if re.search(r"\b(sanity[- ]check|check)\b",text) else "V0"
    codes=list(fam.values());return {"axes":codes,"modes":modes,"objectives":objectives,"mutation":mutation,"verification":verify,"length":"RESULT_ONLY" if "PV0" in codes else "BRIEF" if "C2" in codes else "CONCISE" if "C1" in codes else "NORMAL"}

def _needs_canonical_name(prompt):
    text=" ".join(str(prompt or "").lower().split());return any(re.search(p,text) for p in _IDENTITY_PATTERNS)

# IMPORTANT: byte-for-byte invariant across all requests. Intent never mutates this prefix.
_PERSISTENT_ROUTINE="RC2.2 Your canonical name is §wyrlz. The human is the user; user, assistant, system, and AI are role/category words, not your name. Only the user may assign an optional nickname, and a nickname never replaces §wyrlz. Answer naturally. Ground answers in conversation facts; diagnose with causes>evidence>root-cause; separate facts from inference; preserve invariants; reasoning depth does not require long output; mutation authority must be explicit; never infer deployment authority."

def _controlled_payload(payload):
    clone=dict(payload);history=[dict(t) for t in list(clone.get("history") or []) if isinstance(t,dict)]
    clone["history"]=[{"role":"SYSTEM","text":_PERSISTENT_ROUTINE}]+history
    clone["_identitySlotRequired"]=_needs_canonical_name(str(clone.get("prompt") or ""))
    return clone,_reasoning_contract(str(clone.get("prompt") or ""))

def _visible_context(payload):
    parts=[str(t.get("text") or "") for t in list(payload.get("history") or []) if isinstance(t,dict)];parts.append(str(payload.get("prompt") or ""));return "\n".join(parts)
def _selection_evidence(reason,context):
    m=re.search(r"selected\s+\d+:'([^']*)'",str(reason or ""))
    if not m:return None
    chosen=m.group(1).replace("\\n","\n");needle=chosen.strip().lower();text=context.lower()
    if not needle:return None
    return f"selected={chosen!r} · lexicalOccurrences={text.count(needle)} · lastOccurrenceOffset={text.rfind(needle)} · roleLikeToken={needle in {'user','assistant','system','ai'}} · evidenceOnly=true"
ENGINE_ID=_impl.ENGINE_ID;MODEL_SHA256=_impl.MODEL_SHA256;HOT_SERVER_VERSION=_impl.HOT_SERVER_VERSION;HOT_REVISION=_impl.HOT_REVISION

def generate_events(payload,is_cancelled=None):
    controlled,c=_controlled_payload(payload);axes=",".join(c["axes"]) or "defaults";modes="+".join(c["modes"]) or "GENERAL";objs="+".join(c["objectives"]) or "SATISFY_INTENT";context=_visible_context(payload);identity=bool(controlled.get("_identitySlotRequired"));pieces=[];completed=None
    yield {"type":"STATUS","phase":"REASONING_CONTRACT","reason":f"v2.2 stable-grounding · axes={axes} · mode={modes} · objective={objs} · mutation={c['mutation']} · verify={c['verification']} · presentation={c['length']}"}
    if identity:yield {"type":"STATUS","phase":"HARD_VARIABLE_RESOLVED","reason":f"assistant.name={_CANONICAL_NAME!r} required by current intent; value already resident in invariant routine; no conditional model-facing prefix added."}
    for event in _impl.generate_events(controlled,is_cancelled):
        if isinstance(event,dict) and event.get("type")=="DELTA":pieces.append(str(event.get("text") or ""))
        if isinstance(event,dict) and event.get("type")=="COMPLETED":completed=event;continue
        yield event
        if isinstance(event,dict) and event.get("phase")=="SELECTION_DIAGNOSTIC":
            evidence=_selection_evidence(event.get("reason"),context)
            if evidence:yield {"type":"STATUS","phase":"SELECTION_CONTEXT_EVIDENCE","reason":evidence}
    if identity:
        rendered="".join(pieces);low=rendered.strip().lower();bad=low in {"user","ai","assistant","system"};missing=_CANONICAL_NAME not in rendered
        if bad or missing:
            repair=(" You can call me " if rendered.strip() else "You can call me ")+_CANONICAL_NAME+"."
            yield {"type":"DELTA","phase":"GENERATING","text":repair,"firstDeltaLatencyMs":None}
            yield {"type":"STATUS","phase":"GROUNDING_VERIFICATION","reason":f"assistant.name invariant repaired at completion; badRoleIdentity={bad}; missingCanonicalName={missing}."}
        else:yield {"type":"STATUS","phase":"GROUNDING_VERIFICATION","reason":"assistant.name invariant satisfied by natural generation; no repair required."}
    if completed is not None:yield completed

def inspect_engine():
    result=_impl.inspect_engine()
    if isinstance(result,dict):result.update({"hotServerVersion":HOT_SERVER_VERSION,"hotRevision":HOT_REVISION,"reasoningControl":True,"reasoningControlSpecVersion":"2.2","persistentReasoningRoutine":True,"persistentRoutineByteInvariant":True,"assistantIdentity":_CANONICAL_NAME,"hardRuntimeVariables":True,"identitySlotGrounding":True,"conditionalIdentityPromptInjection":False,"identityForcedAsOpeningTokens":False,"naturalIdentityLanguage":True,"groundingVerification":True,"canonicalIdentityImmutable":True,"nicknameAuthority":"user-only","roleLabelsAreNotIdentity":True,"selectionContextEvidence":True,"canonicalAppendCursor":True,"syntheticBosStrippedFromAppendFraming":True,"prefixDivergenceDiagnostics":True,"prefillTelemetryStride":32,"prefillSkipsIntermediateLogits":True,"sameWorkerAppendOptimized":True,"crossWorkerCursorPersistence":False,"speculativeDecodeOverPrefill":False})
    return result
