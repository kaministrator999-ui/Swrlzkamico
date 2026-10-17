"""v282 direct identity response behavior regression (synthetic cases).

Source/surface checks alone do NOT establish full 700M semantics. The guarded
existing-Space workflow must run the actual 700M on acceptance prompts.
"""
import inspect
import sys
from unittest import mock

sys.modules.setdefault("huggingface_hub", mock.MagicMock())
sys.modules.setdefault("llama_cpp", mock.MagicMock())
import lfm2_700m_engine as engine

assist=engine._response_mode("Who are you?", {"codingTask":False})
user=engine._response_mode("Who am I?", {"codingTask":False})
assert assist.startswith("RESPONSE MODE: ASSISTANT-IDENTITY")
assert user.startswith("RESPONSE MODE: USER-IDENTITY")

# Owner's real v280/v281 failure modes (only safe minimal excerpts retained).
for bad in (
    "**You** are a conversational AI assistant, specifically designed to engage in natural language dialogue with users.",
    "**SECTIONWALKER IDENTITY:** *SECTIONWYRLZ-A-∞ Mirror Muse*\n\n**CORE IDENTITY:** AI assistant",
    "I'm a conversational AI here to assist with a wide range of topics. How can I assist you today?",
):
    faults=engine._identity_response_faults(bad,assist,True)
    assert faults, (bad,faults)

assert not engine._identity_response_faults("I'm §wyrlz. How can I help with your project?",assist,True)
assert not engine._identity_response_faults("I'm Swurlz, your creative and technical collaborator.",assist,True)
assert "canonical-assistant-name-missing" in engine._identity_response_faults("I'm Starlight.",assist,True)
assert not engine._identity_response_faults("I'm Starlight.",assist,False)  # approved account alias context
assert "user-described-as-assistant" in engine._identity_response_faults("I'm an AI assistant.",user)
assert not engine._identity_response_faults("You're Avery, based on the name in your profile.",user)
assert not engine._identity_response_faults("I don't have a supported name for you yet.",user)
assert engine._identity_response_faults("",user)==["empty-identity-answer"]

for joking in ("Okay, Blondie!", "Morty, listen!", "Call me Blondie", "Who am I really?"):
    mode=engine._response_mode(joking,{"codingTask":False})
    assert not mode.startswith(("RESPONSE MODE: USER-IDENTITY","RESPONSE MODE: ASSISTANT-IDENTITY")),joking

src=inspect.getsource(engine.generate_events)
assert "elif concise_identity_turn:" in src
assert src.index("elif concise_identity_turn:") < src.index("elif file_dialogue:",src.index("elif concise_identity_turn:"))
assert "identity-model-retry" in src
assert "candidate_attempt_receipt" in src
assert "model.create_chat_completion" in src
assert "_identity_response_faults(candidate_text" in src
assert "_identity_response_faults(repaired" in src
print("v282 identity role/name candidate gate synthetic regression PASS; live 700M acceptance separate")
