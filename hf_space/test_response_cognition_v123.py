from response_cognition import classify_response_cognition, response_cognition_policy

H=[
    {"role":"user","content":"Give me three names for the project."},
    {"role":"assistant","content":"1. Ember\n2. Rift\n3. Halo"},
]

CASES=[
    ("What is a tuple in Python?", [], "standalone", "explain"),
    ("2", H, "selection", "select"),
    ("option 3", H, "selection", "select"),
    ("the second one", H, "selection", "select"),
    ("keep going", H, "continuation", "continue"),
    ("again", H, "continuation", "continue"),
    ("and make it darker", H, "continuation", "continue"),
    ("what about the mobile version", H, "continuation", "continue"),
    ("No, I meant the API response", H, "correction", "correct"),
    ("Actually keep the old function name", H, "correction", "correct"),
    ("go deeper on why", H, "expansion", "continue"),
    ("what do you mean", H, "expansion", "continue"),
    ("yup", H, "confirmation", "confirm"),
    ("exactly", H, "confirmation", "confirm"),
    ("no thanks", H, "decline", "decline"),
    ("nah I'm good", H, "decline", "decline"),
    ("surprise me", H, "creative-delegation", "create"),
    ("you pick", H, "creative-delegation", "create"),
    ("back to the parser issue", H, "return-to-prior", "continue"),
    ("new topic: explain black holes", H, "topic-reset", "explain"),
    ("Compare SQLite vs Postgres", [], "standalone", "compare"),
    ("Rewrite this more professionally", [], "standalone", "rewrite"),
    ("Translate this to Spanish", [], "standalone", "translate"),
    ("Summarize this paragraph", [], "standalone", "summarize"),
]

for prompt,history,relation,operation in CASES:
    state=classify_response_cognition(prompt,history,{})
    assert state["relation"]==relation,(prompt,state)
    assert state["operation"]==operation,(prompt,state)

state=classify_response_cognition("Give me exactly 4 short options, only the list.",H,{})
assert state["requestedCount"]==4,state
assert state["detailMode"]=="compact",state
assert state["outputOnly"] is True,state

state=classify_response_cognition("Only change the error handling; keep the function name the same.",H,{"codingTask":True})
assert state["preserveConstraint"] is True,state
assert state["programming"] is True,state

policy=response_cognition_policy(classify_response_cognition("No, I meant only the second one.",H,{}))
assert "newest correction as a delta" in policy
assert "current user message always has final authority" in policy

policy=response_cognition_policy(classify_response_cognition("keep going",H,{}))
assert "nearest compatible active task/subject" in policy
assert "do not end with a routine follow-up question" in policy.lower()

print("response-cognition-v123 PASS")
