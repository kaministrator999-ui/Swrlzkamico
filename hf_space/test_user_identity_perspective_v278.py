"""v280: Identity subjects go through model context; playful address is not a rename.

Offline contract/route checks only. A mock never proves actual 700M social
understanding or learned weights. All identities here are synthetic.
"""
import sys
from unittest import mock

sys.modules.setdefault("huggingface_hub", mock.MagicMock())
sys.modules.setdefault("llama_cpp", mock.MagicMock())
import lfm2_700m_engine as engine

for query in ("Who am I", "Who am I?", "WHO AM I!", "What's my name?"):
    mode = engine._response_mode(query, {"codingTask": False})
    assert mode.startswith("RESPONSE MODE: USER-IDENTITY-DIRECT"), (query, mode)
    assert "assistant's name" in mode

for query in ("Who are you?", "What's your name?", "what are you"):
    mode = engine._response_mode(query, {"codingTask": False})
    assert mode.startswith("RESPONSE MODE: ASSISTANT-IDENTITY-DIRECT"), (query, mode)

for query in (
    "Okay, Blondie 😂", "Listen here, Morty!", "Sure, Captain.",
    "I was just joking about calling you Blondie.",
    "I will call you Starlight.", "Please call me River.",
    "Write a story about a character asking who am I",
    "Who am I to judge?", "Who am I really, beyond my job?",
):
    mode = engine._response_mode(query, {"codingTask": False})
    assert not mode.startswith("RESPONSE MODE: ASSISTANT-IDENTITY-DIRECT"), (query, mode)

# Even repeated jokes do not become an identity classification or write.
history = [{"role":"user","content":"Okay, Blondie."}] * 9
assert not engine._response_mode("Sure, Blondie 😂", {"codingTask":False}, history).startswith("RESPONSE MODE: ASSISTANT-IDENTITY")

policy=engine.BUILTIN_ASSISTANT_PROFILE
for phrase in ("Repetition alone does not prove naming intent",
               "NOT an assignment or durable change",
               "each user's", "authorized save/proposal path"):
    assert phrase.lower() in policy.lower(), phrase
assert "Kamilion" not in policy
assert "Primary Affiliation: Each current user" in policy

# The old 'identity-profile' fast path must not answer before the model loads.
# No model execution is attempted here; this is only a routing regression.
for query in ("Who am I?", "Who are you?"):
    with mock.patch.object(engine, "load", side_effect=RuntimeError("MODEL_ROUTE_REACHED")) as load:
        try:
            list(engine.generate_events({
                "prompt":query, "history":[], "userProfile":"Name: Example User",
                "verifiedAccountDisplayName":"Example Login",
                "profile":"", "programmingIntent":{"codingTask":False}
            }))
        except RuntimeError as exc:
            assert str(exc)=="MODEL_ROUTE_REACHED", exc
        else:
            raise AssertionError("Identity query returned without model routing")
        load.assert_called_once()

print("v280 contextual naming/role routing offline regression PASS (model semantics unverified)")
