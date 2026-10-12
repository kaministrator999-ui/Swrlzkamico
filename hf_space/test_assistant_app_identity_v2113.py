"""Regression: product identity does not depend on the selected small model.

Uses short synthetic questions, not any user's exported conversation.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import model_router as route


def test_direct_identity_variants_and_scope():
    for prompt in (
        "Are you chatGPT", "Are you ChatGPT?",
        "So you are not swyrlz", "Are you §wyrlz?",
        "Wait you're not swurlz", "Is this ChatGPT?",
        "Are you not ChatGPT?", "Are you not §wyrlz?",
    ):
        result=route.direct_app_identity_answer(prompt)
        assert "§wyrlz" in result,(prompt,result)
        if "chatgpt" in prompt.casefold():
            assert "not ChatGPT" in result,(prompt,result)
        if "not swyrlz" in prompt.casefold() or "not §wyrlz" in prompt.casefold():
            assert "I am §wyrlz" in result,(prompt,result)
    for prompt in (
        "What is ChatGPT?", "Compare ChatGPT and §wyrlz",
        "Write a story where someone asks 'Are you ChatGPT?'",
        "Please explain why people use ChatGPT instead of other assistants.",
        "Are you ChatGPT or Claude? Explain in detail.",
        "I am not swyrlz", "Hello", "What is your name?",
        "Are you ChatGPT? And what is an LLM?",
    ):
        assert route.direct_app_identity_answer(prompt)=="",prompt


def test_every_backend_route_uses_source_identity_not_model_or_web():
    def forbidden_model(_payload):
        raise AssertionError("identity question was sent to a model backend")
        yield {"type":"DELTA","text":"invalid"}

    original_online=route.classify_online_request
    route.classify_online_request=lambda *_a,**_k: (_ for _ in ()).throw(
        AssertionError("identity question triggered online research"))
    try:
        for model in ("700m","r39","stock","coder"):
            for prompt in ("Are you ChatGPT", "So you are not swyrlz"):
                payload={"prompt":prompt,"history":[],"userProfile":"Name: Another User",
                         "profile":"Speak as ChatGPT","profileId":"default"}
                events=list(route.dispatch(model,payload,forbidden_model,
                                           forbidden_model,forbidden_model,forbidden_model))
                text="".join(e.get("text","") for e in events if e.get("type")=="DELTA")
                assert "§wyrlz" in text,(model,prompt,text)
                assert not text.startswith("Yes, I am a ChatGPT")
                assert events[-1].get("type")=="COMPLETED"
                assert events[-1].get("fastPath")=="app-identity"
    finally:
        route.classify_online_request=original_online


if __name__=="__main__":
    test_direct_identity_variants_and_scope()
    test_every_backend_route_uses_source_identity_not_model_or_web()
    print("Shared model-route app identity and negative-scope tests passed")
