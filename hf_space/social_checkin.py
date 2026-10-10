"""Small, explicit greeting-style hint for §wyrlz model prompts.

Only simple user-to-assistant check-ins are matched. This provides guidance and
a few positive/negative demonstrations; it never emits canned replies or
replaces the user's prompt, conversation history, or assistant identity.
"""
from __future__ import annotations
import re

_SOCIAL_CHECKIN = re.compile(
    r"""(?ix)^\s*
        (?:(?:hey|hi|hello|yo|hiya)\b(?:\s+sw(?:y|u)rlz)?[\s,!.\-]*)?
        (?:
            how\s+(?:are|r)\s+(?:you|u)(?:\s+doing)?
          | how(?:'s|\s+is)\s+(?:it|everything)\s+going
          | (?:you|u)\s+(?:good|okay|ok|alright)
          | what(?:'s|\s+is)\s+up
          | whats\s+up
          | how\s+you\s+doing
        )
        (?:\s+(?:today|tonight|lately))?
        [\s?!.]*$
    """)
_ONLY_HELLO = re.compile(r"(?i)^\s*(?:hey|hi|hello|yo|hiya)(?:\s+sw(?:y|u)rlz)?\s*[!.]*\s*$")


def is_simple_checkin(prompt):
    text=str(prompt or "").strip()
    if len(text)>95 or "\n" in text:
        return False
    return bool(_SOCIAL_CHECKIN.fullmatch(text) or _ONLY_HELLO.fullmatch(text))


def style_hint(prompt):
    """Hint, not output: the model authors its own greeting response."""
    if not is_simple_checkin(prompt):
        return ""
    return (
        "RESPONSE MODE: NATURAL-SOCIAL-CHECKIN. The CURRENT USER is greeting YOU, §wyrlz, "
        "or asking how YOU are doing. Answer as the conversation partner, in first person, "
        "with one or two short warm conversational sentences. A friendly check-in back "
        "is appropriate, but not required. Respond to a simple 'hi' naturally without "
        "an essay. Do NOT explain your purpose, ontology, how an AI works, or why you "
        "are here unless explicitly asked. Do NOT speak of §wyrlz as a separate "
        "assistant or ask 'How is your chat with §wyrlz?'. Avoid repetitive phrases "
        "like 'I'm here, I'm here' or list-like filler. "
        "Example tone (not text to copy): User: 'Hey, how are you?' "
        "Assistant: 'Hey! Doing pretty good, thanks for asking. How about you?' "
        "Another valid tone: User: 'Yo!' Assistant: 'Yo! What's going on?' "
        "Use your own wording and let conversation history and the user's tone guide you."
    )
