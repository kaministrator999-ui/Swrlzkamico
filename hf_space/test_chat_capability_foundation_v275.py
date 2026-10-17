"""Privacy-safe, cross-domain Chat foundation regression cases.

Fixtures are generalized from owner feedback; not private exported conversations.
This is deterministic source-policy verification, NOT proof of 700M/Qwen
semantic generalization, actual media rendering or a user-visible acceptance.
"""
from response_cognition import (
    classify_response_cognition, response_cognition_policy,
    response_cognition_camera,
)

HISTORY = [
    {"role": "user", "content": "Could you inspect the project layout?"},
    {"role": "assistant", "content": "I have a source inventory; no edits made."},
]

OUTPUT_CASES = (
    ("Please make me an instrumental WAV", "audio"),
    ("Can you render an original 3D game-ready character model?", "3d-asset"),
    ("Produce a film-ready rigged 3D model", "3d-asset"),
    ("Build a Python script to parse project files", "code"),
    ("Write a Kotlin class to validate an API response", "code"),
    ("Make a downloadable ZIP archive of the source package", "file"),
    ("Give me an original rap verse about learning to code", "text"),
    ("Write lyrics for a song about the ocean", "text"),
    ("Make me a poem about a mountain", "text"),
    ("Make something amazing", "unspecified"),
    ("I want to build music tools in our engine later", "none"),
    ("Wouldn't it be cool to make an instrumental someday?", "none"),
    ("I was joking about what you put inside that file", "none"),
    ("What do you think of that file? 😂", "none"),
    ("Read write-action-tests/test.txt", "none"),
)
for prompt, expected in OUTPUT_CASES:
    state = classify_response_cognition(prompt, HISTORY)
    assert state["deliverable"] == expected, (prompt, state)
    assert not state.get("toolExecuted"), (prompt, state)

SOURCE_CASES = (
    ("Review the architecture in our GitHub repository", "project"),
    ("Read write-action-tests/test.txt", "project"),
    ("Check official documentation online", "public"),
    ("Search the web for latest news", "public"),
    ("Compare our repo with official documentation", "both"),
    ("Now let's joke about dragons", "unspecified"),
    ("Create an original song", "unspecified"),
)
for prompt, expected in SOURCE_CASES:
    state = classify_response_cognition(prompt, HISTORY)
    assert state["sourcePreference"] == expected, (prompt, state)

# User corrections and ordinary continuing chat are not new tool approval.
FOLLOWUP_CASES = (
    ("No, I meant keep this in the web Chat, not the app.", "correction", "correct"),
    ("Actually, don't create music tools yet.", "correction", "correct"),
    ("And make the code maintain its old API.", "continuation", "continue"),
    ("Exactly", "confirmation", "confirm"),
    ("Back to the Chat architecture", "return-to-prior", "continue"),
    ("New topic: what's a hash?", "topic-reset", "explain"),
)
for prompt, relation, operation in FOLLOWUP_CASES:
    state = classify_response_cognition(prompt, HISTORY)
    assert (state["relation"], state["operation"]) == (relation, operation), (prompt, state)

for prompt, fragment in (
    ("Please make me an instrumental WAV", "ACTUAL playable audio"),
    ("Render a 3D game-ready model", "actual editable/rendered artifact"),
    ("Write a Python function to parse JSON", "requested deliverable is an actual complete source/file"),
    ("Make a downloadable ZIP archive", "requested deliverable is an actual complete source/file"),
    ("Write an original rap", "Deliver the requested written content itself"),
    ("Review code in our GitHub repository", "authenticated pinned source"),
    ("Search the web for official documentation", "real available research source"),
    ("Compare our repository with official documentation", "Reconcile actual project/repository evidence"),
):
    state = classify_response_cognition(prompt, HISTORY)
    policy = response_cognition_policy(state)
    assert fragment in policy, (prompt, fragment)
    assert "tool" not in state, (prompt, state)

camera = response_cognition_camera(classify_response_cognition(
    "Please make me an instrumental WAV, user token private-secret", HISTORY,
))
assert camera["deliverable"] == "audio", camera
assert "sourcePreference" in camera, camera
assert "private-secret" not in repr(camera), camera
assert "user token" not in repr(camera), camera

print("chat-capability-foundation-v275 deterministic cases PASS")
