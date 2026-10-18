"""v283: synthetic replay of identity failures without copying private account data.

These are deterministic validator/context tests, not evidence of model-weight
learning. Protected deploy gate separately runs the actual 700M.
"""
import sys
from unittest import mock
sys.modules.setdefault("huggingface_hub", mock.MagicMock())
sys.modules.setdefault("llama_cpp", mock.MagicMock())
import lfm2_700m_engine as e

assistant=e._response_mode("Who are you",{"codingTask":False})
user=e._response_mode("Who am i",{"codingTask":False})
assert assistant.startswith("RESPONSE MODE: ASSISTANT-IDENTITY")
assert user.startswith("RESPONSE MODE: USER-IDENTITY")

wrong_user=[
    "You are ASSISTANT.",
    "You're an assistant.",
    "You are §wyrlz.",
    "**Your Name:** §wyrlz",
    "Your name is Swurlz.",
    "I'm an AI assistant.",
]
for text in wrong_user:
    faults=e._identity_response_faults(text,user,require_unknown_user=True)
    assert faults and any("assistant" in x or "unknown-user" in x or "user-" in x for x in faults),(text,faults)
for text in (
    "I don't know your name yet.",
    "You haven't told me your preferred name yet.",
    "I don't have a confirmed name for you in this chat.",
):
    assert not e._identity_response_faults(text,user,require_unknown_user=True),(text,e._identity_response_faults(text,user,require_unknown_user=True))

assert not e._identity_response_faults("You're Avery, as your profile says.",user,expected_user_name="Avery")
assert "known-user-name-not-grounded" in e._identity_response_faults("You're a person.",user,expected_user_name="Avery")
assert not e._identity_response_faults("I'm §wyrlz.",assistant,True)
assert "canonical-assistant-name-missing" in e._identity_response_faults("I'm an AI assistant.",assistant,True)
assert "assistant-described-in-second-person" in e._identity_response_faults("You are a chatbot.",assistant,True)

for text in (
    "I was created by an imaginary company.",
    "I'm the character in a famous fantasy series.",
):
    assert "unsupported-assistant-origin-claim" in e._identity_response_faults(
        text,assistant,identity_followup=True),text
assert "assistant-name-assigned-to-user" in e._identity_response_faults(
    "**Your Name:** §wyrlz",user,identity_followup=True)

history=[
    {"role":"user","content":"Who are you"},
    {"role":"assistant","content":"I couldn't generate a reliable response to that identity question yet."},
    {"role":"user","content":"Who am i"},
    {"role":"assistant","content":"You are ASSISTANT."},
]
assert e._identity_followup_subject("Are you sure about that lol?",history)=="user"
assert e._identity_followup_subject("Your name is swyrlz",history)=="assistant"
assert e._identity_followup_subject("Actually I use this § as the S in your name §wyrlz",history)=="assistant"
assert e._identity_followup_subject("You were confused about your name §wyrlz",history)=="assistant"
for tease in ("Okay, Morty 😂","Listen here, Blondie!","Lol!","What if my name were Morty?"):
    assert not e._identity_followup_subject(tease,history),tease
assert not e._identity_followup_subject("Are you sure about that?",[])

assert e._identity_profile_user_name("Name: Avery\nFavorite food: chili")=="Avery"
assert e._identity_profile_user_name("Account display label: Example Person")==""
import inspect
src=inspect.getsource(e.generate_events)
for name in ("identity_followup", "effective_mode", "unknown_name_required", "faults=identity_faults",
             "retry_faults=identity_faults", "system=focused", "No nickname or relationship data is persisted"):
    assert name in src,name
assert "ASSISTANT/SELF:" not in src[src.index("if (concise_identity_turn or identity_followup)"):src.index("system=focused")]

print("v283 ownership, unknown-name, corrections and jokes regressions PASS")
