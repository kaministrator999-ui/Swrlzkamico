"""§C continuity: read-only dispatch, auto-resume, Stop, and integrity regression."""
from __future__ import annotations
import hashlib
import unittest
from api.execution_continuity_v1 import read_only, eligible, stream

PROJECT={"project":"interactive-3d-model-viewer"}
PROMPT=("Inspect the existing viewer, check the deployed webpage, and report findings. "
        "Do not create a duplicate project or modify files yet.")
def checkpoint(source, segments=4):
    return {"schema":"swrlz-long-code-checkpoint-v1", "source":source,
            "sourceSha256":hashlib.sha256(source.encode()).hexdigest(),
            "segmentsCompleted":segments,
            "originalPrompt":"Build the existing project",
            "programmingIntent":{"codingTask":True}}
def paused(source):
    yield {"type":"CANDIDATE_PREVIEW_DELTA", "text":source}
    yield {"type":"CODE_OUTPUT_CHECKPOINT","checkpoint":checkpoint(source)}
    yield {"type":"STATUS","phase":"CODE_DRAFT_SAVED"}
    yield {"type":"DELTA","text":"Send Continue code"}
    yield {"type":"COMPLETED","phase":"CODE_PAUSED"}

class ExecutionContinuityTests(unittest.TestCase):
    def test_read_only_project_does_not_generate_code(self):
        p={"prompt":PROMPT,"activeHtmlProject":PROJECT}
        self.assertTrue(read_only(p))
        self.assertFalse(eligible(p))
        self.assertFalse(read_only({"prompt":PROMPT}))
        self.assertFalse(read_only({"prompt":"Fix this viewer and deploy it","activeHtmlProject":PROJECT}))
    def test_read_only_emits_real_report_phase_and_preserves_answer(self):
        p={"prompt":PROMPT,"activeHtmlProject":PROJECT}
        events=list(stream(p,lambda _:self.fail("must not code"),
                           [{"type":"DELTA","text":"Verified source findings."},
                            {"type":"COMPLETED","phase":"COMPLETE"}]))
        self.assertEqual(events[0]["phase"],"PROJECT_EVIDENCE_REPORT")
        self.assertEqual(events[1]["text"],"Verified source findings.")
        self.assertEqual(events[-1]["phase"],"COMPLETE")
    def test_project_write_path_preserves_approval_gates(self):
        self.assertFalse(eligible({"githubSourceChangeTask":True}))
        self.assertFalse(eligible({"sourceChangeMode":True}))
    def test_automatic_checkpoint_continuation_without_continue_command(self):
        p={"prompt":"Create working HTML","_cancelCheck":lambda:False}
        calls=[]
        def coder(payload):
            calls.append(payload["codeContinuation"]["sourceSha256"])
            yield {"type":"STATUS","phase":"RESUMING_CODE"}
            yield {"type":"CODE_OUTPUT_FINISHED",
                   "sourceSha256":payload["codeContinuation"]["sourceSha256"]}
            yield {"type":"DELTA","text":"<html>complete</html>"}
            yield {"type":"COMPLETED","phase":"COMPLETE"}
        events=list(stream(p,coder,paused("<html>incomplete")))
        self.assertEqual(len(calls),1)
        self.assertEqual(events[-1]["phase"],"COMPLETE")
        self.assertTrue(any(e.get("phase")=="CODE_AUTO_CONTINUING" for e in events))
        self.assertFalse(any("Continue code" in e.get("text","") for e in events))
        self.assertEqual(sum(e["type"]=="CODE_OUTPUT_CHECKPOINT" for e in events),1)
    def test_multiple_progressing_segments_continue_automatically(self):
        p={"prompt":"Build app"}
        calls=[]
        def coder(payload):
            current=payload["codeContinuation"]["source"]
            calls.append(current)
            if len(calls)<3:
                yield from paused(current+"x")
            else:
                yield {"type":"DELTA","text":"Done"}
                yield {"type":"COMPLETED","phase":"COMPLETE"}
        events=list(stream(p,coder,paused("start")))
        self.assertEqual(calls,["start","startx","startxx"])
        self.assertEqual(events[-1]["phase"],"COMPLETE")
    def test_repeated_identical_checkpoint_blocks_not_infinite(self):
        p={"prompt":"Build app"}
        calls=[]
        def coder(payload):
            calls.append(1)
            yield from paused(payload["codeContinuation"]["source"])
        events=list(stream(p,coder,paused("unchanged")))
        self.assertEqual(len(calls),1)
        self.assertEqual(events[-1]["blocker"],"NO_FORWARD_PROGRESS")
        self.assertTrue(events[-1]["outputIncomplete"])
    def test_stop_interrupts_before_next_generation(self):
        state={"cancel":False}
        def initial():
            yield {"type":"CODE_OUTPUT_CHECKPOINT","checkpoint":checkpoint("draft")}
            yield {"type":"DELTA","text":"should not be shown"}
        p={"prompt":"Build app","_cancelCheck":lambda:state["cancel"]}
        iterator=iter(stream(p,lambda _:self.fail("must not resume"),initial()))
        first=next(iterator)
        self.assertEqual(first["type"],"CODE_OUTPUT_CHECKPOINT")
        state["cancel"]=True
        events=list(iterator)
        self.assertEqual(events[-1]["type"],"CANCELLED")
    def test_bad_checkpoint_cannot_be_used(self):
        c=checkpoint("real")
        c["sourceSha256"]="0"*64
        events=list(stream({"prompt":"Build app"},lambda _:self.fail("no retry"),
                           [{"type":"CODE_OUTPUT_CHECKPOINT","checkpoint":c}]))
        self.assertEqual(events[-1]["blocker"],"INVALID_CHECKPOINT")
    def test_normal_prose_remains_untouched(self):
        events=[{"type":"DELTA","text":"Hello"},{"type":"COMPLETED","phase":"COMPLETE"}]
        self.assertEqual(list(stream({"prompt":"Hi"},lambda _:self.fail("no retry"),events)),events)

if __name__=="__main__":
    unittest.main()
