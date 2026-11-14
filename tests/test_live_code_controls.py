"""Contract tests for noninterrupting live coding control plane."""
from __future__ import annotations
import json
import unittest
from dataclasses import dataclass

from api import live_code_controls as ctl

@dataclass
class Job:
    user_id: str = "owner"
    request_id: str = "job-1"
    thread_id: str = "thread-1"
    state: str = "RUNNING"
    last_seq: int = 3
    created_at: float = 1.0
    updated_at: float = 2.0

@dataclass
class Event:
    event_type: str
    payload: dict

class FakeStore:
    def __init__(self):
        self.job=Job()
        self.controls=[]
        self.calls=[]
    def get_generation(self, user_id, request_id):
        if user_id != self.job.user_id or request_id != self.job.request_id:
            return None
        return self.job
    def list_events(self, user_id, request_id, after_seq=-1):
        return [Event("STARTED", {"phase":"PREPARING"}),
                Event("STATUS", {"phase":"CODING"}),
                Event("STATUS", {"phase":"CODING"})]
    def _key(self, *parts):
        return ":".join(parts)
    def _command(self, *args, **kwargs):
        self.calls.append((args,kwargs))
        op=args[0]
        if op=="LRANGE":return list(self.controls)
        if op=="MGET":
            phases=["PREPARING","CODING","CODING"]
            return [json.dumps({"user_id":"owner","event_type":"STATUS",
                   "payload":{"phase":phases[int(k.rsplit(":",1)[-1])-1]}})
                   for k in args[1:]]
        if op=="RPUSH":
            self.controls.append(args[2]);return len(self.controls)
        if op=="LTRIM":
            self.controls=self.controls[-40:];return "OK"
        if op=="EXPIRE":return 1
        if op=="EVAL":
            index=int(args[4]);old=args[5];new=args[6]
            if self.controls[index]!=old:return 0
            self.controls[index]=new;return 1
        raise AssertionError(op)

class Controls(unittest.TestCase):
    def setUp(self):
        self.store=FakeStore()
        self.args=dict(user_id="owner", request_id="job-1", thread_id="thread-1", store=self.store)
    def test_status_is_grounded_no_fabricated_percent(self):
        s=ctl.snapshot(**self.args)
        self.assertEqual(s["phase"],"CODING")
        self.assertIsNone(s["verifiedProgress"])
        self.assertIsNone(s["estimate"])
        self.assertIn("No verified percent",ctl.status_answer(s))
    def test_steer_does_not_cancel_worker_and_does_not_claim_applied(self):
        r=ctl.record_control(kind="STEER",text="Add controller support.",**self.args)
        self.assertTrue(r["accepted"])
        self.assertFalse(r["applied"])
        self.assertEqual(self.store.job.state,"RUNNING")
        self.assertEqual(r["control"]["state"],"RECORDED_PENDING_EXECUTOR")
        self.assertEqual(len(self.store.controls),1)
    def test_checkpoint_request_is_separate(self):
        r=ctl.record_control(kind="CHECKPOINT",**self.args)
        self.assertEqual(r["control"]["kind"],"CHECKPOINT")
        self.assertEqual(r["control"]["text"],"")
    def test_cannot_submit_to_another_owner_or_thread(self):
        with self.assertRaises(LookupError):
            ctl.record_control(user_id="stranger",request_id="job-1",
                               thread_id="thread-1",kind="STEER",text="x",store=self.store)
        with self.assertRaises(LookupError):
            ctl.snapshot(user_id="owner",request_id="job-1",
                         thread_id="wrong",store=self.store)
    def test_rejects_oversized_or_empty_steering(self):
        for text in ("", "x"*4001):
            with self.assertRaises(ValueError):
                ctl.record_control(kind="STEER",text=text,**self.args)
    def test_rejects_terminal_generation(self):
        self.store.job.state="COMPLETE"
        with self.assertRaises(ValueError):
            ctl.record_control(kind="CHECKPOINT",**self.args)
    def test_status_lists_pending_and_ack_is_executor_only(self):
        ctrl=ctl.record_control(kind="STEER",text="Fix UI.",**self.args)["control"]
        current=ctl.snapshot(**self.args)
        self.assertEqual(len(current["controlInbox"]),1)
        self.assertIn("not yet confirmed applied",ctl.status_answer(current))
        self.assertTrue(ctl.mark_applied(user_id="owner",request_id="job-1",
              control_id=ctrl["controlId"],executor_receipt="verified-revision-test",store=self.store))
        new=ctl.snapshot(**self.args)
        self.assertEqual(new["controlInbox"][0]["state"],"APPLIED")

if __name__=="__main__":
    unittest.main()
