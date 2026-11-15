"""Contract tests: v2 live Station patch is bounded and preserves source."""
from __future__ import annotations

import hashlib
import threading
import time
import unittest

from hf_chat_html_quality_v2_release import patch_station, local_candidate

FIXTURE = '''def _swrlz_auto_code_chain(events,payload,key,request_id):
    started=time.monotonic()
    last_size=0
    checkpoints=0
    while True:
        saved=None
        for event in events:
            if isinstance(event,dict) and event.get("type")=="CODE_OUTPUT_CHECKPOINT":
                cp=event.get("checkpoint") if isinstance(event.get("checkpoint"),dict) else {}
                source=str(cp.get("source") or "")
                valid=(cp.get("schema")=="swrlz-long-code-checkpoint-v1"
                       and bool(source) and not cp.get("repairNeeded")
                       and len(source.encode("utf-8"))<=240*1024
                       and hashlib.sha256(source.encode("utf-8")).hexdigest()==cp.get("sourceSha256"))
                # Finite work budget, no-progress guard, and exact saved bytes.
                can_resume=(valid and _coder_generate is not None
                    and len(source)>last_size+16 and checkpoints<32
                    and time.monotonic()-started<10800)
                if can_resume:
                    yield event
                    saved=cp
                    break
            yield event
        if saved is None:
            return
        try:
            events.close()
        except (AttributeError,ValueError):
            pass
        checkpoints+=1
        last_size=len(str(saved["source"]))
        with _lock:
            session=_sessions.get(key) or {}
            generation=session.get("activeGeneration") or {}
            if (generation.get("requestId")!=request_id or generation.get("cancelRequested")):
                return
            notes=generation.get("liveCodeInstructions") or []
            carry=[]
            for note in notes:
                if note.get("state")=="QUEUED":
                    note["state"]="FORWARDED_UNVERIFIED"
                    carry.append(str(note.get("text") or "")[:1000])
            guidance="; ".join(carry)[:3600]
            if guidance:
                generation["status"].append({"phase":"CODE_GUIDANCE_FORWARDED",
                    "reason":"New requirements forwarded to continuation. Prior sections may require a later revision."})
        payload["codeContinuation"]=saved
        payload["liveCodeSteering"]=guidance
        yield {"type":"STATUS","phase":"CODE_CONTINUING_AUTOMATICALLY",
               "reason":"Continuing saved source in the same task after checkpoint "+
                  str(checkpoints)+"; source remains unverified until validation."}
        events=_coder_generate(payload)
'''


def checkpoint(repair: bool, source: str) -> dict:
    return {"type": "CODE_OUTPUT_CHECKPOINT", "checkpoint": {
        "schema": "swrlz-long-code-checkpoint-v1",
        "source": source, "repairNeeded": repair,
        "sourceSha256": hashlib.sha256(source.encode()).hexdigest()
    }}


class StationRepairTests(unittest.TestCase):
    def factory(self, follow):
        changes = patch_station(FIXTURE.encode()).decode()
        observed = []
        def coder(payload):
            observed.append(payload["codeContinuation"]["sourceSha256"])
            return iter(follow)
        env = {"time": time, "hashlib": hashlib, "_lock": threading.RLock(),
               "_sessions": {"owned": {"activeGeneration": {
                   "requestId": "job", "cancelRequested": False,
                   "liveCodeInstructions": [], "status": []}}},
               "_coder_generate": coder}
        exec(changes, env)
        return env["_swrlz_auto_code_chain"], observed

    def test_automatic_repair_once_from_validation_checkpoint(self):
        source = "<html>original source missing pointer listener</html>"
        run, observed = self.factory([{"type": "COMPLETED"}])
        events = list(run(iter([checkpoint(True, source)]), {}, "owned", "job"))
        self.assertEqual(len(observed), 1)
        self.assertEqual([e["phase"] for e in events if e.get("phase")],
                         ["CODE_CONTINUING_AUTOMATICALLY"])
        self.assertEqual(events[-1]["type"], "COMPLETED")

    def test_identical_failed_source_does_not_loop(self):
        original = "<html>same code fails validation despite repair</html>"
        run, observed = self.factory([checkpoint(True, original)])
        events = list(run(iter([checkpoint(True, original)]), {}, "owned", "job"))
        self.assertEqual(len(observed), 1)
        self.assertEqual(sum(e.get("phase") == "CODE_CONTINUING_AUTOMATICALLY"
                             for e in events), 1)

    def test_normal_length_checkpoint_unchanged(self):
        run, observed = self.factory([{"type": "COMPLETED"}])
        events = list(run(iter([checkpoint(False, "<html>incomplete length-bound source</html>")]),
                          {}, "owned", "job"))
        self.assertEqual(len(observed), 1)
        self.assertEqual(events[-1]["type"], "COMPLETED")

    def test_invalid_hash_is_not_resumed(self):
        item = checkpoint(True, "<html>broken</html>")
        item["checkpoint"]["sourceSha256"] = "0" * 64
        run, observed = self.factory([{"type": "COMPLETED"}])
        events = list(run(iter([item]), {}, "owned", "job"))
        self.assertEqual(len(observed), 0)
        self.assertEqual(events, [item])

    def test_only_one_function_changed_and_second_patch_rejected(self):
        sample = ("FLAG=1\n" + FIXTURE + "\nSENTINEL=42\n").encode()
        patched = patch_station(sample)
        self.assertIn(b"FLAG=1", patched)
        self.assertIn(b"SENTINEL=42", patched)
        self.assertIn(b"swrlz-validator-auto-repair-v1", patched)
        with self.assertRaises(RuntimeError):
            patch_station(patched)

    def test_quality_helper_has_release_marker(self):
        self.assertIn(b"swrlz-html-code-quality-v2", local_candidate())


if __name__ == "__main__":
    unittest.main()
