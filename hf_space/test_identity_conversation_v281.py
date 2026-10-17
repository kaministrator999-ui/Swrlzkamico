"""v281 regression: short identity questions use compact inference context.

Synthetic offline checks only. These verify prompt shaping, not the model's
real-world conversational success; phone acceptance is a separate release gate.
"""
import sys
from unittest import mock

sys.modules.setdefault("huggingface_hub", mock.MagicMock())
sys.modules.setdefault("llama_cpp", mock.MagicMock())
import lfm2_700m_engine as engine

def profile_for(question):
    mode = engine._response_mode(question, {"codingTask":False})
    return engine._identity_context_profile(mode)

for question in ("Who are you?", "What's your name?", "What are you?",
                 "Who am I?", "What's my name?", "Do you know my name?"):
    mode=engine._response_mode(question,{"codingTask":False})
    assert mode.startswith(("RESPONSE MODE: USER-IDENTITY-DIRECT",
                            "RESPONSE MODE: ASSISTANT-IDENTITY-DIRECT")),question
    brief=profile_for(question)
    assert "§wyrlz" in brief and "assistant" in brief
    assert len(brief) < len(engine.BUILTIN_ASSISTANT_PROFILE) // 4
    assert "CORE ID:" not in brief
    assert "PRIMARY AFFILIATION:" not in brief
    assert "SECTIONWALKER" not in brief
    assert "jokes" in brief.lower()
    assert "nothing said here silently saves" in brief.lower()

for question in ("Okay, Morty 😂", "Listen here, Blondie!", "I'm calling you Captain",
                 "Let's talk about you and me", "Who am I really?",
                 "Write a story about who you are",
                 "Remind me who I said I was yesterday"):
    assert profile_for(question)==engine.BUILTIN_ASSISTANT_PROFILE,question

# The existing universal identity profile remains available to longer turns;
# no fixed assistant answer, fabricated user name, or account persistence here.
assert not hasattr(engine,"_direct_identity_answer")
assert "Kamilion" not in engine.BUILTIN_ASSISTANT_PROFILE

# Inspect the real code path rather than treating policy text as proof of use.
import inspect
code=inspect.getsource(engine.generate_events)
assert "identity_response_mode=_response_mode" in code
assert "_identity_context_profile(identity_response_mode)" in code
assert "if concise_identity_turn:" in code
assert "IDENTITY RESPONSE DELIVERY:" in code
assert code.index("IDENTITY RESPONSE DELIVERY:")>code.index("_identity_context_profile(identity_response_mode)")
print("v281 compact identity prompt and non-renaming source regression PASS; model quality unverified")
