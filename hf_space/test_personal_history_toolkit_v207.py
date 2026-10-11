"""v207 synthetic private search facets; zero user data or external requests."""
from __future__ import annotations
import os, sys
from collections import Counter
from datetime import datetime, timezone
from unittest.mock import patch
sys.path.insert(0,os.path.dirname(__file__))

import personal_history_query_v207 as facets
import personal_history_lookup as lookup
import chatgpt_account_memory as memory

OWNER="google:synthetic-facets-1"
OTHER="google:synthetic-facets-2"
ZONE="America/Chicago"
NOW=datetime(2026,10,11,5,44,tzinfo=timezone.utc)
def sec(iso):return datetime.fromisoformat(iso).timestamp()

NIGHT=sec("2026-10-10T22:12:00-05:00")
DAY=sec("2026-10-10T15:11:00-05:00")
SEPT=sec("2026-09-27T20:10:00-05:00")
AUG=sec("2026-08-05T10:30:00-05:00")
native=[
    {"id":"native-1","title":"Dragon project plan","messages":[
        {"role":"user","text":"Our dragon project needs an offline map index.","createdAt":NIGHT*1000},
        {"role":"assistant","text":"We agreed to use the indexed dragon map engine.","createdAt":NIGHT*1000+100},
        {"role":"user","text":"Actually, the dragon project should use a lightweight tokenizer instead.","createdAt":DAY*1000},
        {"role":"assistant","text":"Next step: test the dragon indexing recall.","createdAt":DAY*1000+100},
    ]},
    {"id":"native-2","title":"Older client bug","messages":[
        {"role":"user","text":"The touchscreen flickered last month.","createdAt":SEPT*1000},
        {"role":"assistant","text":"The exact phrase for this reply is radiant falcon circuitry.","createdAt":SEPT*1000+100},
    ]},
]
imported={"id":"imported-33","title":"Dragon history engine","messages":[
    {"role":"user","text":"We decided to continue the dragon project with an offline search index.",
     "createdAt":NIGHT},
    {"role":"assistant","text":"We still need to validate the imported history search.",
     "createdAt":NIGHT+90},
    {"role":"user","text":"I said the unusual phrase blue orbital mango launcher.", "createdAt":AUG},
    {"role":"assistant","text":"I replied: radiant falcon circuitry.", "createdAt":AUG+90}
]}
docs=[{"id":imported["id"],"title":imported["title"],"timestamp":NIGHT,
       "firstAt":AUG,"lastAt":NIGHT+90,
       "titleTokens":{"dragon","history","engine"},
       "terms":{"dragon":3,"project":1,"search":2,"offline":1,"unusual":1,
                "orbital":1,"mango":1,"launcher":1,"blue":1,"falcon":1,"radiant":1}}]
state={"state":"ready","docs":docs,"frequency":Counter(
    {"dragon":1,"project":1,"search":1,"offline":1,"unusual":1,"orbital":1,
     "mango":1,"launcher":1,"blue":1,"falcon":1,"radiant":1})}

def run(prompt,history=None):
    return lookup.lookup(OWNER,prompt,ZONE,native,now=NOW,history=history)

assert facets.parse("Remember only imported ChatGPT conversations from last night")["source"]=="imported"
assert facets.parse("Find it just in original §wyrlz chats")["source"]=="native"
assert facets.parse("What did I say in our chats?")["role"]=="user"
assert facets.parse("What did you say in the chats?")["role"]=="assistant"
assert facets.parse("Find the exact phrase “radiant falcon circuitry”")["exactPhrase"]=="radiant falcon circuitry"
assert facets.parse("Which decisions did we make?")["focus"]=="decision"
assert facets.parse("Find our unfinished work")["focus"]=="pending"
assert facets.parse("Show my corrections")["focus"]=="correction"
assert not lookup.relevant("Design an unfinished dragon puzzle game")
assert lookup.relevant("Find our unfinished dragon tasks")

history=[{"role":"user","text":"Remember what did we say about the dragon project last night?"},
         {"role":"assistant","text":"I found some old threads."}]
p=facets.parse("only imported ones",history)
assert p["followup"] and p["source"]=="imported" and "dragon project" in p["searchText"]
assert lookup.relevant("only imported ones",history)
assert not facets.parse("Write a new song about dragon memories",history)["followup"]

def start(query):return lookup._bounds(query,ZONE,NOW)[0]
def end(query):return lookup._bounds(query,ZONE,NOW)[1]
assert start("remember last 3 days?")==NOW.replace(tzinfo=timezone.utc)-__import__("datetime").timedelta(days=3)
assert start("remember last weekend?")==datetime(2026,10,3,5,tzinfo=timezone.utc)
assert end("remember last weekend?")==datetime(2026,10,5,5,tzinfo=timezone.utc)
assert start("remember this week?")==datetime(2026,10,5,5,tzinfo=timezone.utc)
assert start("remember last month?")==datetime(2026,9,1,5,tzinfo=timezone.utc)
assert end("remember last month?")==datetime(2026,10,1,5,tzinfo=timezone.utc)
assert start("remember in August 2026?")==datetime(2026,8,1,5,tzinfo=timezone.utc)
assert start("remember from 2026-10-08 to 2026-10-10?")==datetime(2026,10,8,5,tzinfo=timezone.utc)
assert end("remember from 2026-10-08 to 2026-10-10?")==datetime(2026,10,11,5,tzinfo=timezone.utc)
assert start("remember on October 10 around 10pm?")==datetime(2026,10,11,2,tzinfo=timezone.utc)
assert end("remember on October 10 around 10pm?")==datetime(2026,10,11,4,tzinfo=timezone.utc)
assert start("remember from 2026-10-10 to 2026-10-08?")==NOW

def read(owner,cid,c):
    assert owner==OWNER
    return (imported,1) if cid==imported["id"] else (None,0)

with patch.object(memory,"enabled",side_effect=lambda owner:owner==OWNER), \
     patch.object(memory,"_STATE",{OWNER:state}), \
     patch.object(lookup.archive,"_read_record",side_effect=read), \
     patch.object(memory.account_chat_store,"_config",return_value={"synthetic":1}):
    only_imported=run("Remember only imported dragon conversations last night?")
    assert "ChatGPT imported" in only_imported and "§wyrlz native" not in only_imported,only_imported
    only_native=run("Remember only native §wyrlz dragon conversations last night?")
    assert "§wyrlz native" in only_native and "ChatGPT imported" not in only_native,only_native
    what_i=run("Remember what did I say about dragon project last night?")
    assert "| user]" in what_i and "| assistant]" not in what_i,what_i
    what_you=run("Remember what did you say about dragon project last night?")
    assert "| assistant]" in what_you and "| user]" not in what_you,what_you
    phrase=run("Find the exact phrase “radiant falcon circuitry” in chat conversations")
    assert "radiant falcon circuitry" in phrase,phrase
    assert "not found" not in phrase.lower()
    no_phrase=run('Find the exact phrase "never-said-secret-starlight" in chats')
    assert "no matching stored messages" in no_phrase,(repr(no_phrase),facets.parse('Find the exact phrase "never-said-secret-starlight" in chats'))
    decision=run("Find decisions we made about the dragon project")
    assert "We agreed" in decision or "We decided" in decision,decision
    assert "Next step:" not in decision,decision
    pending=run("Find unfinished dragon project tasks")
    assert "Next step" in pending or "still need" in pending,pending
    correction=run("Show corrections about the dragon project")
    assert "Actually" in correction,correction
    from_last=run("only imported ones",history)
    assert "ChatGPT imported" in from_last and "§wyrlz native" not in from_last,from_last
    assert "dragon" in from_last,from_last
    wrong=lookup.lookup(OTHER,"Remember the dragon project last night",ZONE,native,now=NOW)
    assert wrong==""

print("v207 PASS: exact phrase, source & role filters, pending/decisions/corrections, contextual follow-up, calendar/time ranges, owner isolation")
