"""R39 v46: contextual social-act repetition + user language preference.

Extends v45. The Brain now recognizes a bounded greeting/check-in family across
surface wording changes while preserving exact-input evidence separately. Chat
relays the user's explicit profanity preference as factual metadata; the Brain
owns how that preference affects response style. Clean language is the default.
"""
from __future__ import annotations
import hashlib
import re
import time
import urllib.request

_V45_COMMIT="991a3bae34ad0cfb8eac6d5b77e007a1239558cd"
_V45_URL=f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V45_COMMIT}/runtime_hot/r39_engine_v45.py"
_req=urllib.request.Request(_V45_URL,headers={"User-Agent":"swrlz-r39-v46"})
with urllib.request.urlopen(_req,timeout=20) as _response:_source=_response.read(4_000_001)
if len(_source)>4_000_000:raise RuntimeError("R39_V45_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"),_V45_URL+"#v46","exec"),globals(),globals())

_V45_INSPECT=inspect_engine
_V45_GENERATE=generate_events
HOT_SERVER_VERSION="2.1.57"
HOT_REVISION="2.1.57-hot-social-act-language-preference-v46"
_impl.HOT_SERVER_VERSION=HOT_SERVER_VERSION
_impl.HOT_REVISION=HOT_REVISION

_GREETING_PATTERNS=(
 r"^(?:hey+|he+y+|hello+|hi+|yo+|sup|wass?up|what'?s up)$",
 r"^(?:good )?(?:morning|afternoon|evening|night)$",
 r"^(?:how(?:'s| is) it going|how are you|how you doing|what(?:'s| is) going on|what(?:'s| is) with you)(?: today| tonight| this morning| this afternoon| this evening)?$",
)

def _surface(value):
    text=str(value or '').lower().replace('§','s')
    text=re.sub(r"[^a-z0-9' ]+"," ",text)
    return " ".join(text.split())

def _social_act(value):
    text=_surface(value)
    if any(re.fullmatch(p,text) for p in _GREETING_PATTERNS):return 'greeting-checkin'
    return ''

def _social_act_streak(payload,act):
    history=payload.get('history') if isinstance(payload,dict) else None
    history=history if isinstance(history,list) else []
    streak=1
    for item in reversed(history):
        if not isinstance(item,dict):continue
        role=str(item.get('role') or '').strip().lower()
        if role in {'assistant','ai','system'}:continue
        if role not in {'user','human'}:continue
        if _social_act(item.get('text') or item.get('content'))==act:streak+=1;continue
        break
    return streak

def _profanity_preference(payload):
    prefs=payload.get('userPreferences') if isinstance(payload,dict) else None
    return 'allowed' if isinstance(prefs,dict) and prefs.get('profanity')=='allowed' else 'clean'

def _with_language_context(payload):
    if not isinstance(payload,dict):return payload
    pref=_profanity_preference(payload)
    out=dict(payload);history=list(out.get('history') or [])
    statement=('User language preference: profanity is allowed when contextually appropriate; do not force it.' if pref=='allowed' else 'User language preference: keep assistant language clean; do not use profanity.')
    out['history']=[{'role':'system','text':statement}]+history
    return out

def _act_reply(payload,streak):
    recent=_recent_assistant_texts(payload,limit=6)
    if streak==2:pool=("Ayy 👋 another check-in 😄 I'm here — what's up?","Hey again 👋😆 different wording still counts. What's going on?","Round two 👋😄 I caught the second check-in.")
    elif streak==3:pool=("Okayyy 👋😂 third check-in — now I'm noticing the pattern, not just the wording.","AYOOO 👋😆 three greeting/check-ins in a row. You are definitely testing the context now.","Third check-in received 😂 different packet, same conversational move.")
    elif streak<=5:pool=(f"Check-in #{streak} 👋😂 changing the wording is not resetting the conversation anymore.",f"Okayyy 😆 #{streak}. Different phrasing, same greeting/check-in streak — caught it.",f"Packet family #{streak} acknowledged 👋😂 the wording changed; the conversational act didn't.")
    else:pool=(f"👋 ACK #{streak} 😂 synonym Gatling gun detected; the greeting/check-in streak is still alive.",f"Check-in #{streak} 😆 §wyrlz is tracking the conversational act now, not just literal duplicates.",f"Packet #{streak} 👋😂 new wording, same ongoing check-in ritual. Still caught it.")
    seed=f"{_request_id(payload)}|{streak}|{_surface((payload or {}).get('prompt'))}"
    start=int.from_bytes(hashlib.sha256(seed.encode()).digest()[:4],'big')%len(pool);immediate=recent[0] if recent else ''
    for off in range(len(pool)):
        candidate=pool[(start+off)%len(pool)]
        if candidate!=immediate:return candidate
    return pool[start]

def inspect_engine():
    result=_V45_INSPECT()
    if isinstance(result,dict):result.update({'hotServerVersion':HOT_SERVER_VERSION,'hotRevision':HOT_REVISION,'socialActRepetitionReasoning':True,'socialActOwner':'lalm','socialActSource':'bounded-canonical-history','socialActContract':'surface-plus-conversational-act-v1','languagePreferenceOwner':'lalm','languagePreferenceDefault':'clean','languagePreferenceContract':'explicit-user-preference-v1','v45SourceCommit':_V45_COMMIT})
    return result

def generate_events(payload,is_cancelled=None):
    act=_social_act((payload or {}).get('prompt'))
    if act:
        streak=_social_act_streak(payload,act)
        exact=_duplicate_streak(payload)
        if streak>1 and exact<=1:
            request_id=_request_id(payload);_payload_camera(payload,request_id);started=time.monotonic();reply=_act_reply(payload,streak)
            _camera(request_id,'social-act-repetition-enter',route='social-act-repetition',socialAct=act,socialActStreak=streak,exactDuplicateStreak=exact,modelPrefillSkipped=True,profanityPreference=_profanity_preference(payload))
            yield {'type':'STATUS','phase':'SOCIAL_REPETITION','reason':'Brain recognized repeated greeting/check-in intent across different surface wording.'}
            yield {'type':'DELTA','phase':'WRITING','text':reply}
            yield {'type':'COMPLETED','phase':'COMPLETE','reason':'Contextual social-act repetition completed.'}
            _camera(request_id,'social-act-repetition-complete',elapsedMs=int((time.monotonic()-started)*1000),socialActStreak=streak,replyChars=len(reply),modelPrefillSkipped=True)
            return
    for event in _V45_GENERATE(_with_language_context(payload),is_cancelled):yield event
