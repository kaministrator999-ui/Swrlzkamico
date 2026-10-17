"""Owner export (77) regression: user identity must not become assistant identity.

No runtime weights, external accounts or model calls are needed for these tests.
"""
import sys
from unittest import mock
sys.modules.setdefault("huggingface_hub",mock.MagicMock())
sys.modules.setdefault("llama_cpp",mock.MagicMock())
import lfm2_700m_engine as engine

def answer(prompt, profile="", history=None):
    return engine._direct_identity_answer(prompt,profile,list(history or []))

def assert_user_not_assistant(text):
    assert text and "AI assistant designed" not in text
    assert not text.startswith(("I'm §wyrlz","I'm 𓆩","I am §wyrlz"))

for prompt in ("Who am i","Who am I?","who AM I!"):
    result=answer(prompt)
    assert_user_not_assistant(result)
    assert "don't have a verified name" in result,(prompt,result)
    assert "person I'm talking with" in result
    result=answer(prompt,"Name: Example User")
    assert result=="You're Example User.",(prompt,result)
    history=[{"role":"user","content":"My name is River."}]
    assert answer(prompt,"",history)=="You're River."

assert "wyrlz" in answer("Who are you?")
assert "wyrlz" in answer("What's your name?")
assert answer("Who am I really, beyond my job?")==""  # reflective, not name lookup
assert answer("Write a story about a character asking who am I")==""  # quoted subject
assert answer("Who am I to judge?")==""  # idiomatic expression

# A short user-identity query is answered before even attempting to load 700m.
with mock.patch.object(engine,"load",side_effect=AssertionError("unexpected model load")):
    events=list(engine.generate_events({
        "prompt":"Who am i","history":[],"userProfile":"",
        "profile":"","programmingIntent":{"codingTask":False}
    }))
assert "".join(e.get("text","") for e in events if e.get("type")=="DELTA")==answer("Who am i")
assert events[-1].get("fastPath")=="identity-profile"
assert all(e.get("type") not in ("CANDIDATE_ATTEMPT","CANDIDATE_VALIDATION") for e in events)
print("v278 user identity perspective regression PASS")
