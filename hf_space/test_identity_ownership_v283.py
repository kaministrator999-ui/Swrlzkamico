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
    "Hey there, I'm just a chatbot here to help you. I don't have a name or a specific identity.",
    "Let me clarify—I don't have a confirmed identity yet.",
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
for text in ("I'm River.","Call me River.","My name is River."):
    assert "user-name-assigned-to-assistant" in e._identity_response_faults(text,user,expected_user_name="River")
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

# Observed native700 failure: a greeting assigned the assistant name to the
# human, and unrelated self-uncertainty passed the missing-human-name check.
for text in ("Hey there, §wyrlz! I'm the Swurlz version of you.",
             "Hello, Swurlz. I'm §wyrlz."):
    assert "assistant-name-used-as-user-address" in e._identity_response_faults(text,assistant,True)
assert "missing-unknown-user-name-calibration" in e._identity_response_faults(
    "I'm an AI assistant, so I don't have a physical form or personal identity like you.",
    user,require_unknown_user=True)
for text in ("I don’t know your name.","I donʼt know your name yet.","You haven’t told me your name."):
    assert not e._identity_response_faults(text,user,require_unknown_user=True),text
assert "user-assigned-assistant-identity" in e._identity_response_faults("You’re an assistant.",user)
for text,expected in (("Call me River","River"),("Actually my name is River.","River"),
                      ("No, my name is Élodie","Élodie")):
    assert e._identity_stated_user_name(text)==expected
for text in ('What if my name is River?', '"My name is River"',"The example says call me River"):
    assert not e._identity_stated_user_name(text),text

assert not e._identity_response_faults("Hi! I'm §wyrlz.",assistant,True)
assert "assistant-name-assigned-to-user" in e._identity_response_faults(
    "Thank you for clarifying, I'll use §wyrlz as your assistant name.",assistant,True)

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
             "retry_faults=identity_faults", "system=focused", "Do not claim you saved names"):
    assert name in src,name
focus_start=src.index("focused=(",src.index("if (concise_identity_turn or identity_followup)"))
focus_end=src.index("if custom_assistant_profile:",focus_start)
assert "ASSISTANT/SELF:" not in src[focus_start:focus_end]
assert "IMPORTANT FACT: No supported personal name" in src
assert '"missing-unknown-user-name-calibration" in faults' in src
assert "A previous assistant's guess is not reliable evidence" in src

# Regression: a v283 edit mistakenly replaced the unrelated programming-repair
# retry contract with identity wording. Preserve existing programming semantics.
guarded_start=src.index("if guarded_turn:")
guarded_end=src.index("elif strict_lyric_turn:",guarded_start)
guarded_src=src[guarded_start:guarded_end]
assert "LANGUAGE/INTENT RETRY GATE:" in guarded_src
assert "strategy_change_directive(programming,candidate_check,2)" in guarded_src
assert "identity attribution error" not in guarded_src
assert "if \"missing-unknown-user-name-calibration\" in faults" not in guarded_src
assert "elif concise_identity_turn or identity_followup:" in src
# The failed second prepublish run had a missing-name rejection followed
# by an oversized retry. Verify the correction is in identity path only.
identity_start=src.index("elif concise_identity_turn or identity_followup:",guarded_end)
identity_end=src.index("elif file_dialogue:",identity_start)
identity_src=src[identity_start:identity_end]
assert 'if "missing-unknown-user-name-calibration" in faults:' in identity_src
assert "SPECIFIC CORRECTION" in identity_src
assert "response_tokens=min(80 if" in src
assert "retry_messages[0]" in identity_src
assert "retry_tokens=min(192,available_output_tokens)" in identity_src
assert identity_src.count("completion_validation(")==2
assert "IMPORTANT FACT: No supported personal name for the human" in src
assert "identity attribution error" not in guarded_src
print("v283 ownership, unknown-name, corrections and jokes regressions PASS")
