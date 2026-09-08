"""Hot R39 v26 conversational controller + vectorized attention fast path.

Builds on v25's conversation-aware intent/quality controller while accelerating the
Python-side recurrent attention path. Grouped-query attention and per-head RMS are
vectorized with NumPy, RoPE trig is cached per position, and dynamic conversation controls
remain outside the model-facing prefix so exact same-worker append reuse survives.
"""
from __future__ import annotations
import re, types, urllib.request
import numpy as np

_IMPL_URL="https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/dev/runtime_hot/r39_engine_impl.py"
_req=urllib.request.Request(_IMPL_URL,headers={"User-Agent":"swrlz-hot-r39-v26"})
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
if _old_eos not in _source_text:raise RuntimeError("R39_V26_EOS_PATCH_TARGET_MISSING")
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
if _old_lookup not in _source_text:raise RuntimeError("R39_V26_PREFIX_PATCH_TARGET_MISSING")
_source_text=_source_text.replace(_old_lookup,_new_lookup,1)

_old_yield='''                yield {
                    "type": "STATUS",
                    "phase": "PREFILL",
                    "reason": f"Prefill {ordinal}/{total} · {token_s:.3f}s token · {avg:.3f}s new-token avg · ETA {eta:.1f}s · reused={prefix_len} · backend={('native' if native else 'python')}.",
                }
'''
_new_yield='''                if processed == 1 or ordinal == total or processed % 64 == 0:
                    yield {"type":"STATUS","phase":"PREFILL","reason":f"Prefill {ordinal}/{total} · {token_s:.3f}s token · {avg:.3f}s new-token avg · ETA {eta:.1f}s · reused={prefix_len} · backend={('native' if native else 'python')}."}
'''
if _old_yield not in _source_text:raise RuntimeError("R39_V26_PREFILL_PATCH_TARGET_MISSING")
_source_text=_source_text.replace(_old_yield,_new_yield,1)
_old_trace='''                trace_this = ordinal in {1, total} or ordinal % 32 == 0
'''
_new_trace='''                trace_this = ordinal in {1, total}
'''
if _old_trace not in _source_text:raise RuntimeError("R39_V26_TRACE_PATCH_TARGET_MISSING")
_source_text=_source_text.replace(_old_trace,_new_trace,1)

_old_attention='''            qn = model.vector(f"blk.{i}.attn_q_norm.weight")
            kn = model.vector(f"blk.{i}.attn_k_norm.weight")
            q = np.concatenate([base._rms(q.reshape(16, 64)[h], qn) for h in range(16)]).astype(np.float32)
            k = np.concatenate([base._rms(k.reshape(8, 64)[h], kn) for h in range(8)]).astype(np.float32)
            q = base._rope(q, 16, 64, state.pos)
            k = base._rope(k, 8, 64, state.pos)
            state.kv[i].append((k.copy(), v.copy()))
            att = np.zeros((16, 64), np.float32)
            for h in range(16):
                kh = h // 2
                qh = q.reshape(16, 64)[h]
                scores = np.array([np.dot(qh, kk.reshape(8, 64)[kh]) / 8.0 for kk, _ in state.kv[i]], np.float32)
                weights = np.exp(scores - scores.max(), dtype=np.float32)
                weights /= weights.sum(dtype=np.float32)
                for weight, (_, vv) in zip(weights, state.kv[i]):
                    att[h] += weight * vv.reshape(8, 64)[kh]
            op = model.matvec(f"blk.{i}.attn_output.weight", att.reshape(-1))
            path = "attention"
'''
_new_attention='''            qn = model.vector(f"blk.{i}.attn_q_norm.weight")
            kn = model.vector(f"blk.{i}.attn_k_norm.weight")
            q = _hot_head_rms(q, 16, qn)
            k = _hot_head_rms(k, 8, kn)
            q = base._rope(q, 16, 64, state.pos)
            k = base._rope(k, 8, 64, state.pos)
            state.kv[i].append((k.copy(), v.copy()))
            att = _hot_attention(q, state.kv[i])
            op = model.matvec(f"blk.{i}.attn_output.weight", att.reshape(-1))
            path = "attention-vectorized"
'''
if _old_attention not in _source_text:raise RuntimeError("R39_V26_ATTENTION_PATCH_TARGET_MISSING")
_source_text=_source_text.replace(_old_attention,_new_attention,1)

_old_loop='''        for ordinal in range(1, max_tokens + 1):
            if is_cancelled and is_cancelled():
                raise base.R39InferenceError("REQUEST_CANCELLED", "Generation was cancelled.")
            before_ids = _top_ids(logits, _TRACE_TOP_CANDIDATES)
            next_token = _sample_hot(logits, recent, temperature, top_p, hash(request_id) ^ (state.pos * 0x9E3779B9))
            if ordinal <= 8 or ordinal % 8 == 0:
'''
_new_loop='''        behavior=payload.get("_conversationBehavior") or {}
        min_decode=max(0,min(int(behavior.get("minDecodeTokens") or 0),max(0,max_tokens-1)))
        previous_tokens=[]; emitted=[]; forced_queue=[]; guard_note="sampler"
        if behavior.get("avoidPreviousAssistantEcho") and str(behavior.get("previousAssistantText") or "").strip():
            previous_tokens=list(model.tokenizer.encode(str(behavior.get("previousAssistantText"))))
            try:
                probe=list(model.tokenizer.encode(""))
                if probe and previous_tokens and int(previous_tokens[0])==int(probe[0]):previous_tokens=previous_tokens[1:]
            except Exception:pass
        required_tokens=[]
        if str(behavior.get("requiredText") or "").strip():
            required_tokens=list(model.tokenizer.encode(str(behavior.get("requiredText"))))
            try:
                probe=list(model.tokenizer.encode(""))
                if probe and required_tokens and int(required_tokens[0])==int(probe[0]):required_tokens=required_tokens[1:]
            except Exception:pass
        def _contains_required(seq,needle):
            if not needle:return True
            n=len(needle)
            return any(seq[i:i+n]==needle for i in range(max(0,len(seq)-n+1)))
        role_start_ids=set()
        if behavior.get("blockRoleIdentityStarts"):
            for _label in ("User"," user","AI"," AI","Assistant"," assistant","System"," system"):
                try:
                    _ids=list(model.tokenizer.encode(_label));_probe=list(model.tokenizer.encode(""))
                    if _probe and _ids and int(_ids[0])==int(_probe[0]):_ids=_ids[1:]
                    if _ids:role_start_ids.add(int(_ids[0]))
                except Exception:pass
        for ordinal in range(1, max_tokens + 1):
            if is_cancelled and is_cancelled():
                raise base.R39InferenceError("REQUEST_CANCELLED", "Generation was cancelled.")
            before_ids = _top_ids(logits, _TRACE_TOP_CANDIDATES);guard_note="sampler"
            if forced_queue:
                next_token=int(forced_queue.pop(0));guard_note="grounded-slot"
            else:
                sample_logits=logits
                blocked=[]
                if ordinal==1 and role_start_ids:blocked.extend(role_start_ids)
                if previous_tokens and len(emitted)<len(previous_tokens) and emitted==previous_tokens[:len(emitted)]:blocked.append(int(previous_tokens[len(emitted)]))
                if blocked:
                    sample_logits=logits.copy()
                    for _tid in blocked:
                        if 0<=int(_tid)<len(sample_logits):sample_logits[int(_tid)]=-1e30
                    guard_note="guarded-sampler"
                next_token=_sample_hot(sample_logits,recent,temperature,top_p,hash(request_id) ^ (state.pos * 0x9E3779B9))
                eos_id=int(model.tokenizer.eos) if model.tokenizer.eos is not None else None
                if eos_id is not None and next_token==eos_id and ordinal<=min_decode:
                    retry_logits=sample_logits.copy();retry_logits[eos_id]=-1e30
                    next_token=_sample_hot(retry_logits,recent,temperature,top_p,hash(request_id) ^ (state.pos * 0x9E3779B9));guard_note="early-eos-guard"
                elif eos_id is not None and next_token==eos_id and required_tokens and not _contains_required(emitted,required_tokens):
                    forced_queue=list(required_tokens[1:]);next_token=int(required_tokens[0]);guard_note="required-slot-on-eos"
            if ordinal <= 8 or ordinal % 8 == 0:
'''
if _old_loop not in _source_text:raise RuntimeError("R39_V26_LOOP_PATCH_TARGET_MISSING")
_source_text=_source_text.replace(_old_loop,_new_loop,1)
_old_diag='''                    "reason": f"step {ordinal} selected {next_token}:{_token_text(model, next_token)!r} · top repaired " + "; ".join(f"{int(t)}:{_token_text(model, int(t))!r}={float(logits[int(t)]):.4g}" for t in before_ids),
'''
_new_diag='''                    "reason": f"step {ordinal} selected {next_token}:{_token_text(model, next_token)!r} · source={guard_note} · top repaired " + "; ".join(f"{int(t)}:{_token_text(model, int(t))!r}={float(logits[int(t)]):.4g}" for t in before_ids),
'''
if _old_diag not in _source_text:raise RuntimeError("R39_V26_DIAG_PATCH_TARGET_MISSING")
_source_text=_source_text.replace(_old_diag,_new_diag,1)
_old_recent='''            recent.append(next_token)
            sequence_tokens.append(next_token)
'''
_new_recent='''            recent.append(next_token)
            emitted.append(int(next_token))
            sequence_tokens.append(next_token)
'''
if _old_recent not in _source_text:raise RuntimeError("R39_V26_EMITTED_PATCH_TARGET_MISSING")
_source_text=_source_text.replace(_old_recent,_new_recent,1)

_impl=types.ModuleType("swrlz_hot_r39_engine_impl_v26");_impl.__file__=_IMPL_URL
exec(compile(_source_text,_IMPL_URL,"exec"),_impl.__dict__)

def _hot_head_rms(value,heads,weight):
    a=np.asarray(value,dtype=np.float32).reshape(int(heads),64)
    denom=np.sqrt(np.mean(a*a,axis=1,dtype=np.float32,keepdims=True)+np.float32(1e-5),dtype=np.float32)
    return (a/denom*np.asarray(weight,dtype=np.float32).reshape(1,64)).astype(np.float32).reshape(-1)

def _hot_attention(q,entries):
    length=len(entries)
    qg=np.asarray(q,dtype=np.float32).reshape(8,2,64)
    keys=np.stack([item[0] for item in entries],axis=0).reshape(length,8,64)
    values=np.stack([item[1] for item in entries],axis=0).reshape(length,8,64)
    scores=np.einsum("hqd,thd->hqt",qg,keys,optimize=True)/np.float32(8.0)
    weights=np.exp(scores-scores.max(axis=2,keepdims=True),dtype=np.float32)
    weights/=weights.sum(axis=2,keepdims=True,dtype=np.float32)
    return np.einsum("hqt,thd->hqd",weights,values,optimize=True).astype(np.float32).reshape(16,64)

_ROPE_CACHE={};_ROPE_CACHE_MAX=8192

def _hot_rope(x,heads,hd,pos,theta=1_000_000.0):
    key=(int(pos),int(hd),float(theta))
    pair=_ROPE_CACHE.get(key)
    if pair is None:
        half=int(hd)//2
        inv=1.0/(float(theta)**(np.arange(half,dtype=np.float64)*2.0/int(hd)))
        angle=int(pos)*inv
        pair=(np.cos(angle).astype(np.float32),np.sin(angle).astype(np.float32))
        if len(_ROPE_CACHE)>=_ROPE_CACHE_MAX:_ROPE_CACHE.clear()
        _ROPE_CACHE[key]=pair
    c,s=pair;y=np.asarray(x,dtype=np.float32).reshape(int(heads),int(hd)).copy();half=int(hd)//2
    a=y[:,:half].copy();b=y[:,half:].copy();y[:,:half]=a*c-b*s;y[:,half:]=b*c+a*s
    return y.reshape(-1)

_impl._hot_head_rms=_hot_head_rms
_impl._hot_attention=_hot_attention
_impl.base._rope=_hot_rope
_impl.HOT_SERVER_VERSION="2.1.35"
_impl.HOT_REVISION="2.1.35-hot-boundary-v26-vectorized-attention-conversation-v3.1"
_impl._REFERENCE_RERANK_CANDIDATES=6
_original_format_stats=_impl._format_stats
def _format_stats(stats):return "skipped" if not stats else _original_format_stats(stats)
_impl._format_stats=_format_stats

_CANONICAL_NAME="§wyrlz"
_RULES=((r"\b(brief|short)\b","C2"),(r"\b(concise|compact)\b","C1"),(r"\b(exhaustive)\b","B3"),(r"\b(comprehensive)\b","B2"),(r"\b(deep|mechanistic|root cause)\b","D3"),(r"\b(in[- ]depth|detailed)\b","D2"),(r"\b(expert[- ]level|implementation[- ]ready)\b","T3"),(r"\b(technical|technically)\b","T2"),(r"\b(just the result|result only|no explanation|one word|name only)\b","PV0"))
_MODE_RULES=((r"\b(diagnose|diagnostic|failure|root cause|why .* fail)\b","DIAGNOSTIC","FIND_ROOT_CAUSE"),(r"\b(compare|comparative|versus|\bvs\b)\b","COMPARATIVE","SELECT_BEST_OPTION"),(r"\b(fact[- ]check|verify|validate|audit)\b","VERIFICATION","VERIFY"),(r"\b(design|architecture|redesign)\b","ARCHITECTURE","DESIGN"))
_SELF_NAME=(r"\bwhat(?:'s| is) your (?:name|main name)\b",r"\bwhat (?:can|should|do) i call you\b",r"\bwhat are you called\b",r"\bwhat do you go by\b",r"\bhow should i address you\b",r"\bwho are you\b",r"\bwho am i (?:talking|speaking) to\b",r"\bidentify yourself\b",r"\btell me your name\b")
_SELF_EXPLAIN=(r"\bwhy (?:that|the) name\b",r"\bwhy are you called\b",r"\bwhy (?:do|did) you (?:use|choose|have) (?:that|your) name\b",r"\bwhat does (?:your|that) name mean\b",r"\bwhat's with (?:your|that) name\b")
_CORRECTION=r"^(?:no\b|nah\b|i said\b|i meant\b|not (?:that|what)\b|redo\b|wrong\b|you misunderstood\b|that's not\b|actually i\b)"
_ACTION=r"\b(go ahead|do it|let'?s do it|fix (?:it|that)|update (?:it|that)|patch (?:it|that)|implement (?:it|that)|build (?:it|that))\b"
_PLAY=r"\b(lmao|lmfao|lol|haha|🤣|😂)\b"
_CONT=r"^(?:exactly\b|yeah\b|yep\b|right\b|true\b|that\b|this\b|it\b|but\b|and\b)"

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

def _intent(prompt):
    raw=str(prompt or "").strip();text=" ".join(raw.lower().split())
    minimal=bool(re.search(r"\b(one word|name only|just the name|just answer|no explanation)\b",text))
    if any(re.search(p,text) for p in _SELF_EXPLAIN):kind="SELF_EXPLANATION"
    elif any(re.search(p,text) for p in _SELF_NAME):kind="SELF_NAME_QUERY"
    elif re.search(_CORRECTION,text):kind="CORRECTION"
    elif re.search(_ACTION,text):kind="ENGINEERING_ACTION"
    elif re.search(r"\bwhy\b|\bhow come\b|\bwhat makes\b",text):kind="WHY_EXPLANATION"
    elif re.search(_PLAY,text):kind="PLAYFUL_CASUAL"
    elif re.search(_CONT,text) and len(text.split())<=24:kind="CONTEXT_CONTINUATION"
    elif "?" in raw or re.match(r"^(what|who|when|where|how|can|do|does|is|are|will|would|could|should)\b",text):kind="DIRECT_QA"
    else:kind="GENERAL"
    floors={"SELF_NAME_QUERY":6,"SELF_EXPLANATION":14,"CORRECTION":9,"ENGINEERING_ACTION":7,"WHY_EXPLANATION":12,"PLAYFUL_CASUAL":5,"CONTEXT_CONTINUATION":6,"DIRECT_QA":6,"GENERAL":4}
    return {"kind":kind,"minimum":0 if minimal else floors[kind],"minimal":minimal}

def _last_assistant(history):
    for turn in reversed(history):
        if isinstance(turn,dict) and str(turn.get("role") or "").upper() in {"ASSISTANT","AI"}:
            text=str(turn.get("text") or turn.get("content") or "").strip()
            if text:return text
    return ""

_PERSISTENT_ROUTINE="RC3.1 Your canonical name is §wyrlz. You are a warm, witty, adaptive, elder-dragon-flavored conversational intelligence: playful in casual chat, evidence-first in engineering, technically exact in both. The human is the user; user/assistant/system/AI are roles, not names. Only the user may set a nickname; it never replaces §wyrlz. Track the active topic and resolve short references from recent context. A user correction replaces the superseded interpretation. Answer the requested operation, not merely a related noun: why asks for explanation, name asks for identity. Preserve the user's analogy before extending it; infer understandable coined words from context. Do not leak control labels or mechanically repeat the same opening. Separate fact from inference. Mutation/deployment authority must be explicit."

def _controlled_payload(payload):
    clone=dict(payload);history=[dict(t) for t in list(clone.get("history") or []) if isinstance(t,dict)]
    info=_intent(str(clone.get("prompt") or ""));prev=_last_assistant(history)
    clone["history"]=[{"role":"SYSTEM","text":_PERSISTENT_ROUTINE}]+history
    behavior={"intent":info["kind"],"minDecodeTokens":info["minimum"],"previousAssistantText":prev}
    if info["kind"]=="SELF_NAME_QUERY":behavior.update({"requiredText":_CANONICAL_NAME,"blockRoleIdentityStarts":True})
    if info["kind"] in {"SELF_EXPLANATION","WHY_EXPLANATION","CORRECTION"}:behavior["avoidPreviousAssistantEcho"]=True
    if info["kind"]=="SELF_EXPLANATION":behavior["blockRoleIdentityStarts"]=True
    clone["_conversationBehavior"]=behavior
    return clone,_reasoning_contract(str(clone.get("prompt") or "")),info

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
    controlled,c,info=_controlled_payload(payload);axes=",".join(c["axes"]) or "defaults";modes="+".join(c["modes"]) or "GENERAL";objs="+".join(c["objectives"]) or "SATISFY_INTENT";context=_visible_context(payload);pieces=[];completed=None
    yield {"type":"STATUS","phase":"REASONING_CONTRACT","reason":f"v3.1 conversational-controller · intent={info['kind']} · axes={axes} · mode={modes} · objective={objs} · mutation={c['mutation']} · verify={c['verification']} · presentation={c['length']}"}
    yield {"type":"STATUS","phase":"CONVERSATION_INTENT","reason":f"intent={info['kind']} · minimumDecodeTokens={info['minimum']} · dynamicModelPrefix=false · contextPolicy=recent-thread-first"}
    if info["kind"]=="SELF_NAME_QUERY":yield {"type":"STATUS","phase":"HARD_VARIABLE_RESOLVED","reason":f"assistant.name={_CANONICAL_NAME!r} required; enforcement occurs inside recurrent decode so cached cursor and visible text stay identical."}
    for event in _impl.generate_events(controlled,is_cancelled):
        if isinstance(event,dict) and event.get("type")=="DELTA":pieces.append(str(event.get("text") or ""))
        if isinstance(event,dict) and event.get("type")=="COMPLETED":completed=event;continue
        yield event
        if isinstance(event,dict) and event.get("phase")=="SELECTION_DIAGNOSTIC":
            evidence=_selection_evidence(event.get("reason"),context)
            if evidence:yield {"type":"STATUS","phase":"SELECTION_CONTEXT_EVIDENCE","reason":evidence}
    rendered="".join(pieces).strip()
    if info["kind"]=="SELF_NAME_QUERY":yield {"type":"STATUS","phase":"GROUNDING_VERIFICATION","reason":f"assistant.name present={_CANONICAL_NAME in rendered}; visibleChars={len(rendered)}; repairAppendedOutsideCursor=false"}
    elif info["kind"]=="SELF_EXPLANATION":yield {"type":"STATUS","phase":"CONVERSATION_QUALITY","reason":f"self-explanation chars={len(rendered)}; bareNameOnly={rendered==_CANONICAL_NAME}; previousResponseEchoGuard=true"}
    if completed is not None:yield completed

def inspect_engine():
    result=_impl.inspect_engine()
    if isinstance(result,dict):result.update({"hotServerVersion":HOT_SERVER_VERSION,"hotRevision":HOT_REVISION,"reasoningControl":True,"reasoningControlSpecVersion":"3.1","conversationCurriculum":"runtime_hot/conversation_curriculum_v1.json","conversationController":True,"adaptiveMinimumDecode":True,"earlyEosGuard":True,"previousAssistantEchoGuard":True,"roleLabelIdentityGuard":True,"requiredSlotCommittedInsideCursor":True,"postGenerationUncommittedRepair":False,"persistentReasoningRoutine":True,"persistentRoutineByteInvariant":True,"assistantIdentity":_CANONICAL_NAME,"canonicalIdentityImmutable":True,"nicknameAuthority":"user-only","dynamicModelPrefixInjection":False,"canonicalAppendCursor":True,"syntheticBosStrippedFromAppendFraming":True,"prefixDivergenceDiagnostics":True,"prefillTelemetryStride":64,"prefillDeepDiagnostics":"first+final","prefillSkipsIntermediateLogits":True,"vectorizedAttention":True,"vectorizedHeadRms":True,"ropeTrigCache":True,"sameWorkerAppendOptimized":True,"crossWorkerCursorPersistence":False,"speculativeDecodeOverPrefill":False})
    return result
