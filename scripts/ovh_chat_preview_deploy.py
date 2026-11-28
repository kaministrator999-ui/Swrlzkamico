#!/usr/bin/env python3
"""Apply the first OVH chat-context migration to the existing private preview."""
import ast
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time
import urllib.request
import json

SOURCE = Path("/srv/swrlz/source")
PREVIEW = Path("/srv/swrlz/staging/chat-ovh-preview")
TARGET = PREVIEW / "lfm2_700m_engine.py"
PYTHON = "/srv/swrlz/chat-venv/bin/python"
UNIT = "swrlz-chat-preview.service"

def replace_once(s, old, new):
    if s.count(old) != 1:
        raise RuntimeError("Unexpected source shape: " + old[:100])
    return s.replace(old, new, 1)

def patch(s):
    if "OVH_ADAPTIVE_CONTEXT_V1" not in s:
        raise RuntimeError("Expected deployed V1 context patch")
    if "OVH_ADAPTIVE_CONTEXT_V2" in s:
        return s
    start=s.index("    # OVH_ADAPTIVE_CONTEXT_V1")
    end=s.index("    started=time.perf_counter()",start)
    s=s[:start]+r'''
    # OVH_ADAPTIVE_CONTEXT_V1
    # OVH_ADAPTIVE_CONTEXT_V2: port guarded 9B social prefill policy.
    compact_allowed = (
        not file_dialogue and not concise_identity_turn and not identity_followup
        and not reference_structure and not music_policy
        and not any(programming.get(k) for k in (
            "codingTask","failureEvidence","canonicalCarry","artifactMutationRequested",
            "artifactContinuation","newProject","intentContract","needsFailureEvidence"))
        and not any(payload.get(k) for k in (
            "nativeEditorEvidence","onlineContext","githubSourceChangeTask",
            "projectThreadEvidence","archiveEvidence","widgetPresentation",
            "forgeContext","githubAction","githubStart","sourceChangeIdentity","pinnedContext"))
    )
    clean = " ".join(prompt.split())
    compact_math = compact_allowed and not history and bool(re.fullmatch(
        r"(?:(?:hey|hi)\s+§?wyrlz\s*[,!:]?\s*)?"
        r"(?:(?:what is|what's|calculate|compute|solve)\s+)?"
        r"[+-]?\d+(?:\.\d+)?"
        r"(?:\s*[-+*/×÷]\s*[+-]?\d+(?:\.\d+)?)+\s*[?=.]?",
        clean, re.I))
    compact_social = compact_allowed and len(clean)<=170 and bool(re.fullmatch(
        r"(?:"
        r"(?:hi|hello|hey|yo|howdy)(?:[,! ]+§?wyrlz)?(?:[,! ]+(?:how (?:are|r) you|how'?s it going|what'?s up))?"
        r"|how (?:are|r) you|how'?s it going|how have you been|what'?s up"
        r"|(?:pretty|really) (?:good|great|fine|okay)(?: actually| thanks| today)?"
        r"|(?:doing|i'?m doing) (?:good|great|fine|okay|alright)(?: thanks)?"
        r"|that took (?:a while|forever|so long)(?: for you to respond)?(?: lol| lmao)?"
        r"|(?:lol|lmao|lmfao|haha|hahaha|yep|yeah|exactly|nice|cool|awesome)"
        r")[!?. ,]*",clean,re.I))
    # Narrow standalone educational questions, no history or evidence discarded.
    compact_explain = compact_allowed and not history and len(clean)<=160 and bool(re.fullmatch(
        r"(?:what (?:is|are)|define|explain)\s+(?:the\s+)?(?:[A-Za-z][A-Za-z0-9 -]{0,65})"
        r"(?: in (?:one|two|three) sentences)?[?.]?",clean,re.I
    )) and not re.search(r"\b(?:today|current|latest|now|my|our|your|price|weather|news|version|time|date|code|function|script|file|project|repair|fix|write|generate|how|should|best)\b",clean,re.I)
    compact_kind = ("math" if compact_math else "social" if compact_social
                    else "explain" if compact_explain else "standard")
    if compact_kind != "standard":
        system = (
            "You are §wyrlz (Swurlz), an AI assistant distinct from the user. "
            "Answer the actual message directly, naturally and accurately. "
            "Use supplied history for continuity; never invent shared memories, "
            "facts, tool results or actions. Match humor when appropriate. "
            "Be concise for simple questions; honor explicit answer constraints. "
            "Acknowledge uncertainty when necessary."
        )
        if custom_assistant_profile:
            system += "\nUSER ASSISTANT PREFERENCES:\n" + custom_assistant_profile
        if user_profile:
            system += "\nCURRENT USER PROFILE (not assistant identity):\n" + user_profile
        if compact_social:
            system += "\nRespond conversationally using actual supplied context."
        elif compact_math:
            system += "\nCalculate accurately."
    yield {"type":"STATUS","phase":"OVH_PREFILL_PROFILE","reason":compact_kind}

''' + s[end:]
    s=replace_once(s,'        if compact_math:\n            response_tokens=min(128,available_output_tokens)\n            temperature=0.2\n',
        '        if compact_math or compact_social or compact_explain:\n'
        '            response_tokens=min(128 if compact_math else 256,available_output_tokens)\n'
        '            temperature=0.2 if compact_math else 0.4\n')
    s=replace_once(s,'    print(f"CONTEXT_RECEIPT compact_math={compact_math} input_tokens={input_tokens}", flush=True)',
        '    print(f"CONTEXT_RECEIPT profile={compact_kind} input_tokens={input_tokens}", flush=True)')
    return s


def patch_v3(s):
    if "OVH_ADAPTIVE_CONTEXT_V3" in s:
        return s
    if "OVH_ADAPTIVE_CONTEXT_V2" not in s:
        s=patch(s)
    helper=r'''
class _OVHRequestTokenModel:
    """Exact token reuse for one generation only; no shared private text."""
    def __init__(self,model):
        self.model=model
        self.cache={}
        self.hits=0
        self.misses=0
    def tokenize(self,text,add_bos=False):
        key=(bytes(text),bool(add_bos))
        if key in self.cache:
            self.hits+=1
            return list(self.cache[key])
        self.misses+=1
        tokens=self.model.tokenize(text,add_bos=add_bos)
        if len(self.cache)<64 and len(key[0])<=65536:
            self.cache[key]=tuple(tokens)
        return tokens
    def create_chat_completion(self,**kwargs):
        return self.model.create_chat_completion(**kwargs)


def _ovh_small_code(prompt,programming,payload,history):
    if not programming.get("codingTask") or history:
        return False
    if any(programming.get(k) for k in (
        "failureEvidence","canonicalCarry","repairDirection","artifactContinuation",
        "artifactMutationRequested","artifactTargetId","needsFailureEvidence",
        "newProject","failureHistory","behaviorRepairBaseSource","pinnedCodeArtifactCount")):
        return False
    ledger=programming.get("behaviorLedger") or {}
    constraints=programming.get("repairConstraints") or {}
    if any(ledger.get(k) for k in ("suiteKey","currentFailingCases","knownPassingCases",
        "preservePassingCases","regressedCases","resolvedCases","currentTestedArtifact",
        "bestKnownArtifact","currentScore","bestKnownScore")):
        return False
    if any(constraints.get(k) for k in ("unavailableDependencies","forbiddenDependencies",
        "currentReceiptDependencies","carriedUnavailableDependencies","addedDependencies")):
        return False
    if any(payload.get(k) for k in (
        "nativeEditorEvidence","onlineContext","projectThreadEvidence","archiveEvidence",
        "githubContext","githubAction","githubSourceChangeTask","forgeContext","forgeLeaseId",
        "visionJobId","visionReceipt","fileDialogue","pinnedContext","uploadedFiles",
        "attachments","sourceChangeIdentity","privateHistoryIntent","projectVersionRecall")):
        return False
    clean=" ".join(prompt.split())
    if not clean or len(clean)>230 or re.search(r"https?://|www\.|§[eEcC]\b|[{}\x60]|/api/",clean,re.I):
        return False
    if not re.search(r"\b(?:write|create|implement|generate|show|make)\b",clean,re.I):
        return False
    if not re.search(r"\b(?:function|method|short|simple|small|snippet|hello world|example)\b",clean,re.I):
        return False
    if re.search(r"\b(?:fix|debug|repair|refactor|rewrite|edit|modify|update|change|extend|import|repository|repo|github|commit|deploy|existing|project|integration|integrate|engine|server|database|frontend|backend|file|directory|folder|component|error|stack trace|test failure|architecture|library|framework|endpoint|application|webpage|website|web page)\b",clean,re.I):
        return False
    contract=programming.get("intentContract") or {}
    if len(json.dumps(contract,ensure_ascii=False))>4500:
        return False
    if (contract.get("artifactType") in ("web-page","application","repository")
        or (contract.get("languageContract") or {}).get("artifactType") in ("web-page","application","repository")):
        return False
    return True

'''
    s=replace_once(s,"def generate_events(payload):",helper+"def generate_events(payload):")
    anchor='    yield {"type":"STATUS","phase":"OVH_PREFILL_PROFILE","reason":compact_kind}'
    s=replace_once(s,anchor,r'''
    # OVH_ADAPTIVE_CONTEXT_V3: guarded standalone code, preserve full repair contracts.
    if _ovh_small_code(prompt,programming,payload,history):
        compact_kind="code"
        contract=dict(programming.get("intentContract") or {})
        if contract.get("originalRequest")==prompt:
            contract.pop("originalRequest")
        system=("You are §wyrlz. Implement the exact requested language, signature, "
                "behavior, examples and negative constraints. Return complete usable code. "
                "Do not claim execution without a real execution receipt. Check the original "
                "requirements against the returned code. Respect requested output format."
                "\n"+CODE_TRUTH_POLICY+"\n"+_response_mode(prompt,programming,history))
        if contract:
            system+="\nSTRUCTURED ACCEPTANCE CONTRACT:\n"+json.dumps(contract,ensure_ascii=False,separators=(",",":"))
        if custom_assistant_profile:
            system+="\nASSISTANT PREFERENCES:\n"+custom_assistant_profile
        if user_profile:
            system+="\nUSER PROFILE (human only):\n"+user_profile
''' + anchor)
    s=replace_once(s,"    model=load()","    model=_OVHRequestTokenModel(load())")
    s=replace_once(s,'    print(f"CONTEXT_RECEIPT profile={compact_kind} input_tokens={input_tokens}", flush=True)',
        '    print(f"CONTEXT_RECEIPT profile={compact_kind} input_tokens={input_tokens}", flush=True)\n'
        '    yield {"type":"STATUS","phase":"OVH_TOKENIZER_CACHE","reason":f"{model.hits}:{model.misses}"}')
    s=replace_once(s,"        elif file_dialogue:\n            response_tokens=min(320,available_output_tokens);temperature=0.35",
        "        elif compact_kind=='code':\n            response_tokens=min(1024,available_output_tokens);temperature=0.30\n"
        "        elif file_dialogue:\n            response_tokens=min(320,available_output_tokens);temperature=0.35")
    # Python 3.11 rejects global (?m) flags embedded in regex alternations.
    rows=s.splitlines(keepends=True)
    matches=[i for i,line in enumerate(rows) if "code_like=bool(re.search(" in line]
    if len(matches)!=1: raise RuntimeError("Unexpected coding validator source shape")
    i=matches[0]
    line=rows[i]
    if "(?m)" in line:
        line=line.replace("(?m)","").replace(r"\\s",r"\s").replace(r"\\b",r"\b")
        line=line.replace(",source,re.I))",",source,re.I|re.M))")
        rows[i]=line
    s="".join(rows)
    ast.parse(s)
    return s



def patch_v4(s):
    s=patch_v3(s)
    if "OVH_ADAPTIVE_CONTEXT_V4" in s: return s
    helper=r'''
def _ovh_conversation_profile(prompt,cognition,programming,payload,history):
    """Select ordinary conversation by existing turn semantics."""
    if programming.get("codingTask") or cognition.get("programming"):
        return False
    if cognition.get("operation") not in ("respond","answer","explain","confirm","decline","correct","continue"):
        return False
    if cognition.get("relation") in ("return-to-prior","expansion","selection","creative-delegation"):
        return False
    if cognition.get("detailMode")=="expanded" or cognition.get("requestedCount") or cognition.get("preserveConstraint"):
        return False
    if cognition.get("sourcePreference")!="unspecified" or cognition.get("deliverable")!="none":
        return False
    if any(payload.get(k) for k in ("privateHistoryIntent","projectVersionRecall","verifiedPrivateAnswer",
        "nativeEditorEvidence","onlineContext","githubSourceChangeTask","projectThreadEvidence",
        "archiveEvidence","widgetPresentation","forgeContext","githubAction","githubStart",
        "sourceChangeIdentity","pinnedContext","uploadedFiles","attachments","visionReceipt")):
        return False
    clean=" ".join(prompt.split())
    if not clean or len(clean)>600 or re.search(r"https?://|www\.|\x60{3}|[{}]",clean,re.I):
        return False
    if re.search(r"\b(?:remember|recall|previous conversations?|saved memory|what did i say|my name|your name|who am i|who are you|how do you work|your capabilities|your limitations|latest|current price|today's news|search|look up|calculate|diagnose|dosage|legal advice|investment advice|write|create|generate|build|deploy|repair|debug|execute|install)\b",clean,re.I):
        return False
    if cognition.get("operation")=="continue" and re.search(r"^(?:continue|keep going|go on|more|again|next|another|do it|go ahead|carry on|finish it|run it|send it)\b",clean,re.I):
        return False
    if history and cognition.get("relation") in ("confirmation","correction","decline","continuation"):
        if any(re.search(r"\x60{3}|\b(?:deploy|commit|execute|repair|source code)\b",str(m.get("content") or m.get("text") or ""),re.I) for m in history[-2:]):
            return False
    return True

def _ovh_compact_core():
    wanted=("DYNAMIC MIRROR","SIMPLE-FIRST","CORRECTION ECONOMY","NO ECHO TAX",
            "OWNERSHIP BEFORE INFERENCE","HUMOR CAUSALITY","EVIDENCE BEFORE AGREEMENT")
    return "\n".join(line for line in BUILTIN_ASSISTANT_PROFILE.splitlines()
                     if any(line.startswith(k+":") for k in wanted))

'''
    s=replace_once(s,"def generate_events(payload):",helper+"def generate_events(payload):")
    anchor='    yield {"type":"STATUS","phase":"OVH_PREFILL_PROFILE","reason":compact_kind}'
    s=replace_once(s,anchor,r'''
    # OVH_ADAPTIVE_CONTEXT_V4: broad, guarded natural conversational turns.
    if compact_kind=="standard" and compact_allowed and _ovh_conversation_profile(
            prompt,response_cognition,programming,payload,history):
        compact_kind="conversation"
        system=("You are §wyrlz (Swurlz), an AI assistant distinct from the user. "
                "Respond naturally and directly to the current turn. Maintain real conversation "
                "continuity, preserve the user's preferences and correct attribution. "
                "Do not fabricate memories, experiences, identity, tool results or actions. "
                "Use concise answers when sufficient; expand when the question needs it. "
                "Do not claim a persistent change or action without a verified receipt.\n"
                +" Follow the active thread, interpret humor and metaphor literally only when intended, "
                "prefer the smallest sufficient answer, apply corrections as deltas, avoid repetition, "
                "preserve speaker ownership, and distinguish evidence from agreement. "
                "In the user's messages I/me means the user and you means the assistant. "
                "Respect explicit scope and output constraints. "
                +"Current turn relation: "+str(response_cognition.get("relation"))+
                "; operation: "+str(response_cognition.get("operation"))+".")
        if custom_assistant_profile:
            system+="\nUSER ASSISTANT PREFERENCES:\n"+custom_assistant_profile
        if user_profile:
            system+="\nCURRENT USER PROFILE:\n"+user_profile
        if temporal and re.search(r"\b(?:earlier|today|yesterday|last night|tomorrow|ago|since|this morning)\b",prompt,re.I):
            system+="\nServer-derived time context (not physical location): "+json.dumps(temporal,ensure_ascii=False,separators=(",",":"))
        if social_style:
            system+="\n"+social_style
        if version_lesson:
            system+="\n"+version_lesson
        if lesson:
            system+="\n"+lesson
''' + anchor)
    s=replace_once(s,'    yield {"type":"STATUS","phase":"LOADING"}',
        '    yield {"type":"STATUS","phase":"OVH_CONTEXT_PREP","reason":"Preparing the relevant conversation context."}\n'
        '    yield {"type":"STATUS","phase":"LOADING","reason":"Connecting to the resident model."}')
    anchor='        yield {"type":"RESOURCE","cpuCapacity":_cpu_capacity(),"decodeThreads":_thread_plan()[0],"batchThreads":_thread_plan()[1],"maxResponseTokens":response_tokens}'
    s=replace_once(s,anchor,anchor+'\n'
        '        yield {"type":"STATUS","phase":"OVH_MODEL_PREFILL","reason":f"Processing {input_tokens} context tokens with the resident model."}\n'
        '        if guarded_turn:\n'
        '            yield {"type":"STATUS","phase":"OVH_GUARDED_GENERATION","reason":"Generating a candidate; validation runs before release."}')
    s=replace_once(s,'    yield {"type":"DIAGNOSTIC","trace":_diagnostic_trace(history,user_profile,custom_assistant_profile)}',
        '    yield {"type":"STATUS","phase":"OVH_INTENT_READY","reason":"Reading your request and conversation context."}\n'
        '    yield {"type":"DIAGNOSTIC","trace":_diagnostic_trace(history,user_profile,custom_assistant_profile)}')
    ast.parse(s)
    return s

def patch_ui(s):
    if "OVH_PROGRESS_V4" in s:return s
    anchor='      const activityLabelsV238={'
    s=replace_once(s,anchor,anchor+r'''
        // OVH_PROGRESS_V4: genuine transport/engine milestones, not answer tokens.
        OVH_INTENT_READY:"Reading your request",OVH_CONTEXT_PREP:"Preparing relevant context",
        OVH_PREFILL_PROFILE:"Selected response context",OVH_TOKENIZER_CACHE:"Context tokenized",
        OVH_MODEL_PREFILL:"Processing context with the model",OVH_GUARDED_GENERATION:"Generating and checking code",
        LOADING:"Connecting to resident model",
''')
    s=replace_once(s,'        const message=String(g.text||"").trim()?"Still responding":"Preparing response";',
        r'''        const latestPhase=String((g.status||[]).at(-1)?.phase||g.phase||"CONNECTING").toUpperCase();
        const message=String(g.text||"").trim()?"Writing the response":
          ({CONNECTING:"Sending your message",QUEUED:"Message received; awaiting processing",
            OVH_INTENT_READY:"Reading your request",OVH_CONTEXT_PREP:"Selecting relevant context",
            OVH_MODEL_PREFILL:"Processing context before the first answer token",
            OVH_GUARDED_GENERATION:"Generating and validating the candidate before release",
            CANDIDATE_ATTEMPT:"Checking the generated candidate",
            RESOURCE_ALLOCATED:"Inference resources ready"}[latestPhase]||activityNameV238(latestPhase));
''')
    return s



def patch_v5(s):
    s=patch_v4(s)
    if "OVH_ADAPTIVE_CONTEXT_V5" in s:return s
    # Output constraints alone are not a reason for the full engineering profile.
    s=replace_once(s,'("respond","answer","explain","confirm","decline","correct","continue")',
        '("respond","answer","explain","confirm","decline","correct","continue","translate","compare","calculate")')
    s=replace_once(s,'if cognition.get("detailMode")=="expanded" or cognition.get("requestedCount") or cognition.get("preserveConstraint"):',
        'if cognition.get("detailMode")=="expanded" or cognition.get("preserveConstraint"):')
    # Support bounded nontechnical numbered lists without authorizing deliverables.
    s=replace_once(s,'if cognition.get("sourcePreference")!="unspecified" or cognition.get("deliverable")!="none":',
        'if cognition.get("sourcePreference")!="unspecified" or cognition.get("deliverable") not in ("none","unspecified"):')
    anchor='    yield {"type":"STATUS","phase":"OVH_PREFILL_PROFILE","reason":compact_kind}'
    s=replace_once(s,anchor,r'''
    # OVH_ADAPTIVE_CONTEXT_V5: retain explicit response shape on compact turns.
    if compact_kind=="conversation":
        if response_cognition.get("outputOnly"):
            system+="\nReturn only the requested answer or artifact, with no introduction or follow-up."
        if response_cognition.get("requestedCount"):
            system+="\nReturn exactly "+str(response_cognition["requestedCount"])+" requested items."
        if response_cognition.get("detailMode")=="compact":
            system+="\nKeep the answer brief and complete."
        system+="\nIf the user corrects an earlier fact, the latest explicit user statement overrides older ones. If the information is absent, say so without inventing it."
''' + anchor)
    ast.parse(s)
    return s


def patch_memory(s):
    if "OVH_MEMORY_POSTINGS_V1" in s:
        return s
    helper=r'''
# OVH_MEMORY_POSTINGS_V1: exact candidate shortlist, not a new relevance policy.
def _ovh_postings(docs):
    postings={}
    for i,doc in enumerate(docs):
        for term in doc["terms"]:
            postings.setdefault(term,[]).append(i)
    return postings

def _ovh_score(docs,frequencies,query,postings=None):
    count=max(1,len(docs))
    if postings is None:
        candidates=range(len(docs))
    else:
        candidates=sorted({i for w in query for i in postings.get(w,())})
    scored=[]
    for i in candidates:
        doc=docs[i]
        score=sum(math.log1p((count+1)/(1+frequencies[w]))*
                  (2.3 if w in doc["titleTokens"] else 1.0)*
                  (1+min(2,doc["terms"].get(w,0))*.14)
                  for w in query if doc["terms"].get(w))
        if score>=1.3:scored.append((score,doc["timestamp"],doc))
    scored.sort(key=lambda v:(v[0],v[1]),reverse=True)
    return scored

'''
    s=replace_once(s,"def _build(owner,token):",helper+"def _build(owner,token):")
    s=replace_once(s,'        for entry in docs: freq.update(entry["terms"].keys())',
        '        for entry in docs: freq.update(entry["terms"].keys())\n        postings=_ovh_postings(docs)')
    s=replace_once(s,'"docs":docs,"frequency":freq}', '"docs":docs,"frequency":freq,"postings":postings}')
    s=replace_once(s,'        frequencies=state["frequency"]','        frequencies=state["frequency"]\n        postings=state.get("postings")')
    start=s.index("    count=max(1,len(docs))",s.index("def retrieve("))
    end=s.index("    if not scored:return",start)
    s=s[:start]+"    scored=_ovh_score(docs,frequencies,query,postings)\n"+s[end:]
    s=replace_once(s,"        hits=sum(min(2,_terms(text[:2000]).count(k)) for k in keywords)",
        "        terms=Counter(_terms(text[:2000]))\n        hits=sum(min(2,terms[k]) for k in keywords)")
    ast.parse(s)
    return s

def verify_local():
    # No imported account history, credentials, or user prompt contents in receipts.
    program=r'''
from lfm2_700m_engine import _OVHRequestTokenModel,_ovh_small_code,_candidate_structure_check,_ovh_conversation_profile
from response_cognition import classify_response_cognition
from brain_programming import programming_intent
from chatgpt_account_memory import _ovh_postings,_ovh_score
from collections import Counter
import time,json
class Fake:
    def __init__(self): self.calls=0
    def tokenize(self,t,add_bos=False):
        self.calls+=1
        return list(t)+([0] if add_bos else [])
f=Fake(); m=_OVHRequestTokenModel(f)
assert m.tokenize(b"abc")==[97,98,99]
assert m.tokenize(b"abc")==[97,98,99]
assert m.tokenize(b"abc",True)==[97,98,99,0]
assert m.hits==1 and f.calls==2
assert _OVHRequestTokenModel(f).tokenize(b"abc")==[97,98,99] and f.calls==3
p="Write a Python function double(x) that returns x multiplied by 2. Return only code."
intent=programming_intent(p,[],[],{})
assert _ovh_small_code(p,intent,{},[]), ("Standalone code profile not selected", {k:bool(v) for k,v in intent.items()}, intent.get("behaviorLedger"), intent.get("repairConstraints"))
for key in ("failureEvidence","canonicalCarry","artifactContinuation","artifactMutationRequested"):
    assert not _ovh_small_code(p,dict(intent,**{key:True}),{},[])
assert not _ovh_small_code(p,intent,{"archiveEvidence":"fixture"},[])
assert not _ovh_small_code(p,intent,{},[{"role":"user","content":"previous"}])
assert not _ovh_small_code("Fix the existing Python function",intent,{},[])
assert not _ovh_small_code("Create a simple HTML application",intent,{},[])
assert _candidate_structure_check("\x60\x60\x60python\ndef double(x):\n    return x*2\n\x60\x60\x60",intent,[])["status"]=="PASS"
assert _candidate_structure_check("No candidate",intent,[])["status"]=="REJECT"

h=[{"role":"user","content":"Hey"},{"role":"assistant","content":"Hey, how are you doing?"}]
for p2 in ("Doing fine I see your inference speed is pretty on point","I had a pretty good day at work","That was actually pretty funny","Can you explain why the sky is blue?"):
    i2=programming_intent(p2,h,[],{})
    assert _ovh_conversation_profile(p2,classify_response_cognition(p2,h,i2),i2,{},h), p2
for p2 in ("Find the latest news","Write a Python function","Remember what we talked about yesterday","Explain more in depth"):
    i2=programming_intent(p2,h,[],{})
    assert not _ovh_conversation_profile(p2,classify_response_cognition(p2,h,i2),i2,{},h),p2
assert not _ovh_conversation_profile("Hey",classify_response_cognition("Hey",h,{}),{},{"archiveEvidence":"fixture"},h)
docs=[{"id":i,"timestamp":i%31,"terms":{"common":2,"term"+str(i%401):1},
       "titleTokens":{"term"+str(i%401)}} for i in range(12000)]
freq=Counter(w for d in docs for w in d["terms"])
post=_ovh_postings(docs)
for q in (["term31"],["term2","term3"],["common"],["absent"],["common","term19"]):
    assert _ovh_score(docs,freq,q)==_ovh_score(docs,freq,q,post)
q=["term31"]
t=time.perf_counter()
for _ in range(20): _ovh_score(docs,freq,q)
old=time.perf_counter()-t
t=time.perf_counter()
for _ in range(20): _ovh_score(docs,freq,q,post)
new=time.perf_counter()-t
print("SWRLZ_LOCAL_REGRESSION_OK "+json.dumps({"tokenizerHits":m.hits,
    "memoryFixtureDocs":len(docs),"matchingDocs":len(post[q[0]]),
    "fullScanMs":round(old*50,3),"indexedMs":round(new*50,3)}))
'''
    p=subprocess.run([PYTHON,"-c",program],cwd=PREVIEW,timeout=60,capture_output=True,text=True)
    print(p.stdout,file=__import__("sys").stderr,flush=True)
    if p.returncode:
        print(p.stderr[-3500:],file=__import__("sys").stderr,flush=True)
        raise RuntimeError("Synthetic local regression failed")

def cpu_receipt():
    # Observe only. Inference unit has separate administrative authority.
    try:
        with urllib.request.urlopen("http://127.0.0.1:16947/props",timeout=5) as r:
            props=json.load(r)
        settings=props.get("default_generation_settings") or {}
        safe={k:settings[k] for k in ("n_ctx","n_batch","n_ubatch","n_threads","n_threads_batch") if k in settings}
        help_text=subprocess.check_output(
            ["/srv/swrlz/runtime/llama.cpp/build/bin/llama-server","--help"],
            stderr=subprocess.STDOUT,text=True,timeout=15)
        defaults=[line.strip() for line in help_text.splitlines() if re.match(r"\s*-b,|\s*-ub,",line)][:4]
        print("SWRLZ_CPU_OBSERVATION "+json.dumps({"reportedSettings":safe,"binaryDefaults":defaults,
            "changed":False,"reason":"inference restart outside preview gate"}),file=__import__("sys").stderr,flush=True)
    except Exception as e:
        print("SWRLZ_CPU_OBSERVATION unavailable "+type(e).__name__,file=__import__("sys").stderr,flush=True)


def write_atomic(path, data):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as f:
        temp = Path(f.name)
        f.write(data)
    try:
        os.chmod(temp, path.stat().st_mode & 0o777)
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)

def health():
    with urllib.request.urlopen("http://127.0.0.1:16947/health", timeout=3) as r:
        assert json.load(r)["status"] == "ok"
    with urllib.request.urlopen("http://127.0.0.1:8766/api/hf/models", timeout=3) as r:
        models = json.load(r)["models"]
        assert any(m["available"] and m["model_id"] == "700m" for m in models)
    with urllib.request.urlopen("http://127.0.0.1:8766/", timeout=3) as r:
        assert r.status == 200

def restart():
    subprocess.run(["/usr/bin/sudo", "-n", "/usr/bin/systemctl", "restart", UNIT], check=True, timeout=45)
    for _ in range(20):
        try:
            health()
            return
        except Exception:
            time.sleep(1)
    raise RuntimeError("Preview health failed")


def probe(label,prompt,expected,session=None):
    import http.cookiejar
    import urllib.parse
    import uuid
    base="http://127.0.0.1:8766"
    opener,tid=session or (urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())),"ovh-perf-"+str(uuid.uuid4()))
    rid=str(uuid.uuid4())
    body={"modelId":"700m","prompt":prompt,"threadId":tid,
          "requestId":rid,"profileId":"LALM","profile":"","userProfile":"","timeZone":"UTC"}
    started=time.monotonic()
    req=urllib.request.Request(base+"/api/lalm_station/send",data=json.dumps(body).encode(),
                              headers={"Content-Type":"application/json"},method="POST")
    with opener.open(req,timeout=15) as r:
        if r.status!=202: raise RuntimeError("Probe not accepted")
        r.read()
    first=None; parts=[]; terminal=None; tokens=None; profile=None; cache=None; progress=None; phases=[]
    with opener.open(base+"/api/lalm_station/stream?"+urllib.parse.urlencode({"requestId":rid}),timeout=90) as r:
        for raw in r:
            if time.monotonic()-started>100: raise RuntimeError("Probe deadline")
            try: event=json.loads(raw)
            except ValueError: continue
            kind=event.get("type")
            if kind=="STATUS":
                phases.append(event.get("phase"))
                if progress is None and event.get("phase")=="OVH_INTENT_READY": progress=round(time.monotonic()-started,3)
            if kind=="STATUS" and event.get("phase")=="OVH_PREFILL_PROFILE":
                profile=event.get("reason")
            if kind=="STATUS" and event.get("phase")=="OVH_TOKENIZER_CACHE":
                cache=event.get("reason")
            if kind=="CONTEXT": tokens=event.get("estimatedInputTokens")
            if kind=="DELTA":
                piece=str(event.get("text") or "")
                if piece and first is None: first=round(time.monotonic()-started,2)
                parts.append(piece)
            if kind in ("COMPLETE","COMPLETED","FAILED","CANCELLED"):
                terminal=kind;break
    # Station stores CONTEXT in its session projection, not the NDJSON stream.
    with opener.open(base+"/api/lalm_station/sync",timeout=10) as r:
        active=json.load(r).get("activeGeneration") or {}
    if active.get("requestId")!=rid:
        raise RuntimeError("Probe session generation mismatch")
    tokens=(active.get("contextBudget") or {}).get("estimatedInputTokens",tokens)
    receipt={"case":label,"profile":profile,"inputTokens":tokens,"firstVisibleSec":first,
             "totalSec":round(time.monotonic()-started,2),"terminal":terminal,"outputChars":len("".join(parts)),"tokenizerCache":cache,"firstProgressSec":progress}
    print("SWRLZ_PERF_RECEIPT "+json.dumps(receipt,separators=(",",":")),file=__import__("sys").stderr,flush=True)
    if terminal not in ("COMPLETE","COMPLETED") or not parts or first is None:
        # These probes are isolated synthetic guest requests, never account history.
        failed=[str(x.get("reason") or "")[:240] for x in active.get("status",[]) if x.get("phase")=="FAILED"]
        attempts=[{"status":a.get("validationStatus"),"reasons":a.get("validationReasons"),"firstMs":a.get("firstTokenLatencyMs")} for a in active.get("candidateAttempts",[])]
        print("SWRLZ_PROBE_FAILURE "+json.dumps({"case":label,"failure":failed,"attempts":attempts}),file=__import__("sys").stderr,flush=True)
        raise RuntimeError("End-to-end generation failed: "+label)
    if profile!=expected or not isinstance(tokens,int) or tokens>(2200 if expected=="conversation" else 1800 if label=="code" else 512):
        raise RuntimeError("Compact profile budget not verified: "+label)
    if label=="math" and not re.search(r"(?<!\d)4(?!\d)","".join(parts)):
        raise RuntimeError("Arithmetic acceptance failed")
    if not cache or int(cache.split(":")[0])<1:
        raise RuntimeError("Tokenizer cache not verified: "+label)
    if label=="code":
        answer="".join(parts).strip()
        match=re.search(r"\x60{3}(?:python)?\s*\n([\s\S]*?)\x60{3}",answer,re.I)
        code=match.group(1) if match else answer
        tree=ast.parse(code)
        funcs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="double"]
        if len(funcs)!=1 or [a.arg for a in funcs[0].args.args]!=["x"]:
            raise RuntimeError("Generated code signature failed")
        # Check a tiny expression structurally; never execute model-generated code in deploy account.
        statements=[n for n in funcs[0].body if not (isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str))]
        if len(statements)!=1 or not isinstance(statements[0],ast.Return):
            raise RuntimeError("Generated code shape failed")
        value=statements[0].value
        accepted=[ast.dump(ast.parse(x,mode="eval").body) for x in ("x*2","2*x","x+x")]
        if ast.dump(value) not in accepted:
            raise RuntimeError("Generated code arithmetic failed")
        print("SWRLZ_CODE_STATIC_ACCEPTANCE_OK",file=__import__("sys").stderr,flush=True)
    if progress is None or "OVH_MODEL_PREFILL" not in phases:
        raise RuntimeError("Missing real progress events: "+label)
    if label=="followup" and (active.get("contextBudget") or {}).get("historyMessagesKept",0)<2:
        raise RuntimeError("Multi-turn history lost")
    if first>(85 if label=="code" else 30 if label=="followup" else 45):
        raise RuntimeError("First token latency exceeded 45 seconds: "+label)

def main():
    if os.geteuid() == 0:
        raise RuntimeError("Run as deployment user, not root")
    rev = subprocess.check_output(["git", "-C", str(SOURCE), "rev-parse", "HEAD"], text=True).strip()
    memory=PREVIEW/"chatgpt_account_memory.py"
    ui=PREVIEW/"chat/§wyrlz/index.html"
    originals={p:p.read_bytes() for p in (TARGET,memory,ui)}
    updates={TARGET:patch_v5(originals[TARGET].decode()).encode(),
             memory:patch_memory(originals[memory].decode()).encode(),
             ui:patch_ui(originals[ui].decode()).encode()}
    for p,data in updates.items():
        if p.suffix==".py": ast.parse(data.decode())
    changed=[]
    try:
        for p,data in updates.items():
            if data==originals[p]: continue
            backup=p.with_name(p.name+".ovh-"+rev[:12]+".bak")
            if not backup.exists():
                with backup.open("xb") as f: f.write(originals[p])
            write_atomic(p,data)
            changed.append(p)
        verify_local()
        subprocess.run([PYTHON, "-c", "from ovh_chat import app"], cwd=PREVIEW, check=True, timeout=45)
        restart()
        probe('code','Write a Python function double(x) that returns x multiplied by 2. Return only code.','code')
        probe('math','Hey §wyrlz, what is 2 + 2?','math')
        import http.cookiejar,uuid
        session=(urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())), 'ovh-conversation-'+str(uuid.uuid4()))
        probe('social','Hello §wyrlz!','social',session)
        probe('followup','Doing fine I see your inference speed is pretty on point','conversation',session)
        probe('explain','What is RAM?','explain')
        cpu_receipt()
        subprocess.run([PYTHON,str(SOURCE/"scripts/ovh_extended_response_qa.py")],check=True,timeout=360)
    except Exception:
        for p in reversed(changed):
            write_atomic(p,originals[p])
        if changed:
            restart()
        raise
    subprocess.run(["/usr/bin/python3",str(SOURCE/"scripts/ovh_static_hosting.py")],check=True,timeout=180)
    print("SWRLZ_CHAT_PREVIEW_DEPLOY_OK")
    print(rev)

if __name__ == "__main__":
    main()
