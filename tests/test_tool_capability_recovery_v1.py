"""Deterministic tool-recovery tests: fictional refs only, no user data/network."""
import unittest
from api.tool_capability_recovery_v1 import (
    accepted_offer, prepare, relevant, needs_recovery, run, _subject_query,
)

def response(text, kind="COMPLETED"):
    yield {"type": "STARTED"}
    for chunk in [text[:len(text)//2], text[len(text)//2:]]:
        yield {"type": "DELTA", "text": chunk}
    yield {"type": kind, "phase": "COMPLETE"}

def answer(events):
    return "".join(x.get("text", "") for x in events if x.get("type")=="DELTA")

def sample_history():
    return [
        {"role": "user", "content": "Please find the lyrics to Night Lantern by Example Group"},
        {"role": "assistant", "content": "I found a page about the song: https://example.org/songs/night-lantern"},
        {"role": "user", "content": "Your remix had repeated verses and used the same hook"},
        {"role": "assistant", "content": "Would you like me to rewrite the song with distinct verses and an original hook?"},
    ]

class ToolRecoveryTests(unittest.TestCase):
    def test_social_is_immediate_and_no_research(self):
        seen=[]
        events=list(run({"prompt":"Hi","history":[]},
            lambda p:(seen.append(p) or response("Hello!")),
            lambda q:self.fail("No research for ordinary chat"),lambda:False))
        self.assertEqual(answer(events),"Hello!")
        self.assertEqual(len(seen),1)

    def test_accepted_yes_is_a_real_rewrite_request(self):
        payload={"prompt":"Yes please","history":sample_history()}
        self.assertTrue(accepted_offer(payload))
        self.assertTrue(relevant(payload))
        revised=prepare(payload)
        self.assertIn("Rewrite the previous remix",revised["prompt"])
        self.assertIn("Night Lantern",revised["prompt"])
        self.assertTrue(revised["_toolRecoveryAcceptedOffer"])
        self.assertEqual(revised["receivedText"],"Yes please")
        seen=[]
        events=list(run(payload,lambda p:(seen.append(p) or response("[Verse 1]\\nUnique lines\\n[Chorus]\\nNew hook")),
                        lambda q:self.fail("No redundant search when model completes"),lambda:False))
        self.assertEqual(len(seen),1)
        self.assertIn("Unique lines",answer(events))
        self.assertNotIn("Would you like",answer(events))

    def test_false_tool_claim_is_researched_then_regenerated_once(self):
        seen=[];queries=[]
        def model(p):
            seen.append(p)
            if not p.get("_toolRecoveryPass"):
                return response("I can't browse the live web to find the lyrics. Please paste the hook.")
            return response("[Verse 1]\\nBright harbor lights\\n[Verse 2]\\nNew road at dawn")
        def lookup(q):
            queries.append(q)
            return {"resultCount":1,"evidence":[{"url":"https://example.org/reference",
                "title":"Fictional Song Analysis","snippet":"A three-part song with a refrain."}]}
        events=list(run({"prompt":"Yes please","history":sample_history()},model,lookup,lambda:False))
        self.assertEqual(len(seen),2)
        self.assertEqual(len(queries),1)
        self.assertIn("Example Group",queries[0])
        self.assertEqual(answer(events),"[Verse 1]\\nBright harbor lights\\n[Verse 2]\\nNew road at dawn")
        self.assertIn("RESEARCH_READY",[x.get("phase") for x in events])
        self.assertIn("TOOL_RECOVERY_REGENERATED",[x.get("phase") for x in events])
        self.assertEqual(events[-1]["type"],"COMPLETED")
        self.assertNotIn("can't browse",answer(events))

    def test_existing_evidence_is_reused(self):
        calls=[];seen=[]
        payload={"prompt":"Research the music style of Night Lantern",
            "onlineContext":{"evidence":[{"title":"Night Lantern structure","url":"https://example.org/structure","snippet":"Three verses"}]}}
        def model(p):
            seen.append(p)
            return response("I cannot search the internet." if len(seen)==1 else "Three distinct verses.")
        events=list(run(payload,model,lambda q:calls.append(q),lambda:False))
        self.assertFalse(calls)
        self.assertIn("RESEARCH_REUSED",[x.get("phase") for x in events])
        self.assertEqual(answer(events),"Three distinct verses.")

    def test_failed_lookup_does_not_claim_success_or_disable_tools(self):
        times=[]
        def model(p):
            times.append(p)
            return response("I don't have access to the internet." if len(times)==1
                            else "I tried researching, but sources were unavailable. Here is an original song.")
        events=list(run({"prompt":"Search online about the fictional Lantern festival"},
                        model,lambda q:{"resultCount":0,"evidence":[]},lambda:False))
        self.assertEqual(len(times),2)
        self.assertIn("RESEARCH_UNAVAILABLE",[x.get("phase") for x in events])
        self.assertIn("sources were unavailable",answer(events))

    def test_second_tool_hallucination_is_suppressed(self):
        seen=[]
        events=list(run({"prompt":"Look up the source on Lantern Road"},
           lambda p:(seen.append(1) or response("I can't browse the web right now.")),
           lambda q:{"evidence":[{"title":"Ref","url":"https://example.org","snippet":"ref"}]},
           lambda:False))
        self.assertEqual(len(seen),2)
        self.assertNotIn("can't browse",answer(events))
        self.assertIn("TOOL_RECOVERY_INCOMPLETE",[x.get("phase") for x in events])

    def test_stop_between_lookup_and_second_model(self):
        stopped=[False];seen=[]
        def research(q):
            stopped[0]=True
            return {"evidence":[]}
        events=list(run({"prompt":"Please search for Lantern Road"},
            lambda p:(seen.append(1) or response("I can't search the web.")),research,
            lambda:stopped[0]))
        self.assertEqual(len(seen),1)
        self.assertEqual(events[-1]["type"],"CANCELLED")
        self.assertFalse(any(x.get("type")=="COMPLETED" for x in events))

    def test_no_tools_for_private_context(self):
        p={"prompt":"Search my private emails for a bill","history":sample_history()}
        self.assertFalse(relevant(p))
        self.assertEqual(_subject_query(p),"")

    def test_feedback_is_not_automatic_song_generation(self):
        p={"prompt":"Your remix duplicated two verses.","history":sample_history()}
        self.assertFalse(accepted_offer(p))
        self.assertFalse(relevant(p))
        self.assertEqual(prepare(p),p)

    def test_non_tool_uncertainty_is_not_flagged(self):
        p={"prompt":"Look up Example Group"}
        self.assertFalse(needs_recovery("I don't know the answer without sources.",p))
        self.assertFalse(needs_recovery("I can browse the web to check.",p))
        self.assertTrue(needs_recovery("I don't have web search tools right now.",p))

    def test_non_complete_failure_is_not_replayed(self):
        seen=[];calls=[]
        events=list(run({"prompt":"Look up Lantern Road"},lambda p:(
            seen.append(1) or response("I can't search the web",kind="FAILED")),
            lambda q:calls.append(q),lambda:False))
        self.assertEqual(len(seen),1)
        self.assertEqual(calls,[])
        self.assertEqual(events[-1]["type"],"FAILED")

if __name__=="__main__":
    unittest.main()
