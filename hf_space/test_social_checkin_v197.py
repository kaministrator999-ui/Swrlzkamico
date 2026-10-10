"""Short-greeting policy regression: targeted coaching, no canned model answers."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from social_checkin import is_simple_checkin,style_hint

POSITIVE=(
    "Hey how are you","Hey, how are you?","Hi, how are you doing?",
    "How are you?","How's it going?","Hi §",  # The lone non-greeting is checked below
    "Yo!","Hello!","Hey","You good?","What's up","how you doing",
)
NEGATIVE=(
    "Hi §", "How are you feeling about this code?", "Write a rap called Hey How Are You",
    "How are you implementing the storage layer?", "Describe a chatbot responding to how are you",
    "What should you say when someone asks 'how are you'?",
    "I'm making an app: how are you planning to deploy it?",
    "How are you?\nPlease generate a 40-line song", ""
)

def test_simple_greeting_routing():
    for utterance in POSITIVE:
        if utterance=="Hi §":continue
        assert is_simple_checkin(utterance),repr(utterance)
        hint=style_hint(utterance)
        assert "NATURAL-SOCIAL-CHECKIN" in hint
        assert "first person" in hint
        assert "Do NOT speak of §wyrlz as a separate" in hint
        assert "Do NOT explain your purpose" in hint
        assert len(hint)<1500
    for utterance in NEGATIVE:
        assert not is_simple_checkin(utterance),repr(utterance)
        assert style_hint(utterance)=="",repr(utterance)

def test_model_policy_routing_and_preserved_conversation_paths():
    for path in ("lfm2_700m_engine.py","qwen_coder_engine.py"):
        code=Path(__file__).with_name(path).read_text()
        assert "from social_checkin import style_hint as _social_checkin_style_hint" in code
        assert '_social_checkin_style_hint(prompt)' in code
        assert 'if not programming.get("codingTask"):' in code
        assert 'if social_style:' in code
        assert '_response_mode(prompt,programming)' in code
        assert 'projectThreadEvidence' in code
        # Native generation remains in charge of its reply; no fixed text DELTA.
    stock=Path(__file__).with_name("original_engine.py").read_text()
    assert 'is_simple_checkin(prompt)' in stock
    assert "messages.extend(history[-16:]" in stock
    assert "model.create_chat_completion" in stock
    station=Path(__file__).with_name("station.py").read_text()
    assert "account_chat_store.save_login" in station
    assert "account_chat_store.load_chat(owner)" in station
    assert "account_chat_store.save_chat(owner,s,expected_revision)" in station

if __name__=="__main__":
    test_simple_greeting_routing()
    test_model_policy_routing_and_preserved_conversation_paths()
    print("Natural social check-ins: targeted style coaching and durable chat integration checks passed")
