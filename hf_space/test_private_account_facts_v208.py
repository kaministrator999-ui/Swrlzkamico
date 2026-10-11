"""v208 synthetic regression: real live acceptance prompt forms, no private data."""
import os
import sys
from datetime import datetime, timezone
from unittest.mock import patch
sys.path.insert(0,os.path.dirname(__file__))
import private_account_facts_v208 as facts
import personal_history_lookup as lookup
import chatgpt_account_memory as memory

OWNER="google:synthetic-owner-123"
threads=[
 {"id":"native-1","messages":[{"role":"user","text":"test"},{"role":"assistant","text":"answer"}]},
 {"id":"native-2","messages":[{"role":"user","text":"hello"}]}
]
def fake_redis(c,command,*args):
    assert command=="ZCARD" and args[0]==facts.archive._index(OWNER)
    return 2556

assert facts.classify("Can you tell me how many exported conversation threads we have imported right now")=="imported-threads"
assert facts.classify("How many chat threads do we have")=="all-threads"
assert facts.classify("Can you tell me how many chat messages we have imported")=="imported-messages"
assert facts.classify("How many native §wyrlz messages do we have")=="native-messages"
assert facts.classify("Do you remember what conversations we had yesterday?")==""
assert facts.classify("Can you tell me what chat threads we had 5 months ago")==""
assert facts.classify("How many jokes in that song?")==""
assert lookup.relevant("Can you tell me what chat threads we had 5 months ago")
assert lookup.relevant("Do you remember what conversations we had yesterday?")
NOW=datetime(2026,10,11,15,1,tzinfo=timezone.utc)
window=lookup._bounds("What chat threads did we have 5 months ago?","America/Chicago",NOW)
assert window[0]==datetime(2026,5,1,5,tzinfo=timezone.utc),window
assert window[1]==datetime(2026,6,1,5,tzinfo=timezone.utc),window
assert not lookup._keywords("Can you tell me what chat threads we had 5 months ago"), lookup._keywords("Can you tell me what chat threads we had 5 months ago")

with patch.object(facts.account_chat_store,"_config",return_value={"stub":"yes"}),\
     patch.object(facts.gh,"_redis",side_effect=fake_redis),\
     patch.object(facts,"_count_status",return_value={"state":"counting","done":110,"total":2556}):
    counts=facts.answer(OWNER,threads,"Can you tell me how many exported conversation threads we have imported right now")
    assert "2,556 stored imported" in counts,counts
    assert "2 native" in counts,counts
    native=facts.answer(OWNER,threads,"How many native §wyrlz messages do we have")
    assert "3 visible" in native,native
    pending=facts.answer(OWNER,threads,"Can you tell me how many chat messages we have imported")
    assert "being checked" in pending and "110 of 2,556" in pending,pending
    assert "10,492" not in pending
    assert "5-20" not in counts and "1-10" not in counts

with patch.object(facts.account_chat_store,"_config",return_value={"stub":"yes"}),\
     patch.object(facts.gh,"_redis",side_effect=fake_redis),\
     patch.object(facts,"_count_status",return_value={"state":"ready","messages":98765,"total":2556,"done":2556}):
    answer=facts.answer(OWNER,threads,"How many imported messages do we have")
    assert "98,765 stored text messages" in answer,answer

with patch.object(memory,"_STATE",{OWNER:{"state":"ready","docs":[
    {"messageCount":7},{"messageCount":4}],"total":2}}),\
     patch.object(facts.account_chat_store,"_config",return_value={"stub":"yes"}),\
     patch.object(facts.gh,"_redis",return_value=2),\
     patch.object(facts,"_count_status",side_effect=AssertionError("recomputed ready index")):
    value=facts.answer(OWNER,threads,"How many imported chat messages")
    assert "11 stored visible text messages" in value,value

facts._CACHE[OWNER]={"state":"ready","messages":999,"total":2556}
facts.invalidate(OWNER)
assert OWNER not in facts._CACHE

# This is a lexical test, not a successful signed-in HF acceptance test.
with open(os.path.join(os.path.dirname(__file__),"station.py"),encoding="utf8") as f:
    station=f.read()
assert 'verifiedPrivateAnswer' in station
assert 'private_account_facts_v208.answer(' in station
assert 'private_account_facts_v208.classify(' in station
assert 'Sign in with Google to check private conversation totals.' in station

print("v208 PASS: real prompt forms, exact owner count, cumulative total not import delta, month ago, native isolation, deterministic Station routing")
