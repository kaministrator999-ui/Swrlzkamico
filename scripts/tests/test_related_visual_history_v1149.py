#!/usr/bin/env python3
"""Synthetic acceptance tests. No accounts, archives, pictures, source credentials."""
from pathlib import Path
import importlib.util
p=Path(__file__).resolve().parents[1]/"releases"/"related_visual_history_v1149.py"
spec=importlib.util.spec_from_file_location("related_visual_history",p)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def vision(message):return message.get("vision")
def message(text,role="user",**extra):
    return {"role":role,"text":text,"createdAt":1730000000000,**extra}
related=[
 {"id":"discussion-no-image","title":"Old design discussion","createdAt":1730000000000,"messages":[
   message("Our brown witch hat has a wide brim and deep folds. We want a talking Sorting Hat with a stitched face."),
   message("Yes, we can add joints to its brim.",role="assistant"),
 ]},
 {"id":"image-earlier","title":"Older image discussion","createdAt":1730100000000,"messages":[
   message("What is it?",meta={"imageSha256":"a"*64},vision={"descriptionSentToChatModel":"A brown pointed witch hat with a wide brim, folds and face."}),
   message("Looks like a witch hat.",role="assistant"),
   message("It is the Sorting Hat from Harry Potter. The fold is its mouth."),
   message("Another image",meta={"imageSha256":"c"*64},vision={"descriptionSentToChatModel":"A blue dog on a meadow."}),
   message("That new one is our dog, not the Sorting Hat."),
 ]},
 {"id":"unrelated","title":"Pizza prep","messages":[
   message("I prepared pizza dough and dough balls in the kitchen."),
   message("I think that's all.",role="assistant"),
 ]},
]
def lookup(q,v="",sha="",threads=related):
    return m.retrieve(threads,"new-thread",q,v,sha,vision)
assert lookup("What do you see?","A textured brown pointed witch hat with a wide brim and folds.")["count"]>=1
txt=lookup("What do you see?","A textured brown pointed witch hat with a wide brim and folds.")["context"]
assert "Old design discussion" in txt and "Our brown witch hat" in txt
assert "Earlier USER discussion" in txt and "retrieval CANDIDATES" in txt
assert "Sorting Hat" in txt
assert "That new one is our dog" not in txt  # no leakage of a DIFFERENT later image
assert lookup("What about that brown witch hat with folds and a wide brim?")["count"]>=1
assert "Older image discussion" in lookup("What about that brown witch hat with folds and a wide brim?")["context"]
assert lookup("I made pizza dough today.")["count"]==0 # no old text-only auto recall
assert lookup("What do you see?","A blue dog on a meadow.","c"*64)["count"]>=1
assert lookup("What do you see?","A completely unrelated yellow truck parked at the beach.")["count"]==0
assert lookup("What do you see?","")["count"]==0
assert lookup("What do you see?","An abstract image.",threads=[])["count"]==0
assert "Old design discussion" not in lookup("What do you see?","A brown witch hat with folds",threads=[
    t for t in related if t["id"]!="discussion-no-image"
])["context"]
# Do not promote history-based identification when there is only a single
# weak shared noun or when the prior statement was assistant-only.
assert lookup("What is this image?","A hat.")["count"]==0
assert lookup("Analyze this object", "A striped bowling ball on a billiard table.")["count"]==0
print("RELATED_VISUAL_HISTORY_V1149_TESTS_PASSED")
