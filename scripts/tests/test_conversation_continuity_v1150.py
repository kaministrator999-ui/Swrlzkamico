#!/usr/bin/env python3
"""Synthetic cross-thread, old-in-thread and relevance-gate checks."""
import importlib.util
from pathlib import Path
file=Path(__file__).resolve().parents[1]/"releases"/"conversation_continuity_v1150.py"
spec=importlib.util.spec_from_file_location("conversation_continuity",file)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def user(content,stamp=1730000000000):
 return {"role":"user","text":content,"createdAt":stamp}
def assistant(content):return {"role":"assistant","text":content,"createdAt":1730000000000}
old_hat={"id":"hat-history","title":"Sorting Hat project","createdAt":1730000000000,
         "messages":[user("We are making a Sorting Hat from Harry Potter with mouth folds and rigging for animation."),assistant("I imagine a magic talking hat.")]}
old_work={"id":"work-history","title":"Kitchen work","createdAt":1730000000000,
          "messages":[user("Yesterday I cooked burgers and cleaned the fryer at the kitchen.")]}
old_device={"id":"vr-history","title":"Quest VR testing","createdAt":1730000000000,
            "messages":[user("My Quest headset VR controllers need better ray dragging in the 3D editor.")]}
active={"id":"now","title":"Current conversation","messages":[user("Much older chat: the moon has craters and ice.")]+
        [user("A recent unrelated question about lighting and music.") for _ in range(18)]}
t=[old_hat,old_work,old_device,active]
assert "Sorting Hat project" in m.retrieve(t,"now","What about our Sorting Hat animation rigging?")["context"]
assert "earlier USER statement" in m.retrieve(t,"now","What about our Sorting Hat animation rigging?")["context"]
assert "Kitchen work" not in m.retrieve(t,"now","What about our Sorting Hat animation rigging?")["context"]
assert m.retrieve(t,"now","Okay")["matches"]==0
assert m.retrieve(t,"now","How about that?")["matches"]==0
assert m.retrieve(t,"now","What about our Sorting Hat animation rigging?",is_visual=True)["matches"]==0
assert m.retrieve([old_work,active],"now","What about our Sorting Hat animation rigging?")["matches"]==0
assert "Quest VR testing" in m.retrieve(t,"now","Can we fix Quest headset VR controllers and ray dragging?")["context"]
assert "Current conversation" in m.retrieve(t,"now","Is the moon covered with craters and ice?")["context"]
# The recent conversation already has its last turns in the model input.
recent={"id":"now","messages":[user("sorting hat rigging animation")]*8}
assert m.retrieve([recent],"now","Can we talk sorting hat rigging animation?")["matches"]==0
# An unrelated assistant's claims must never become purported user's memory.
claim={"id":"assistant-guessed","title":"Assistant guessed","messages":[assistant("The Sorting Hat is definitely our newest released model.")] }
assert m.retrieve([claim],"now","Can we improve the Sorting Hat model?")["matches"]==0
# A past image's model-produced description is excluded from ordinary chat recall.
vision={"id":"image-only","messages":[user("What do you see?\n\n[Uploaded image — vision description, not original pixels]\nA Sorting Hat with mouth folds and leather texture.\n[/Uploaded image]")]}
assert m.retrieve([vision],"now","Sorting Hat leather folds")["matches"]==0
print("CONVERSATION_CONTINUITY_V1150_TESTS_PASSED")
