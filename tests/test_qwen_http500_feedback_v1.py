"""No model or user data; deterministic HTTP500 retry and routing cases."""
from __future__ import annotations
import unittest
from contextlib import contextmanager
from scripts.qwen_http500_recovery_v1 import native_stream_once_retry
from scripts.music_transform_quality_v1 import transformation_contract, music_feedback_followup

class Http500RecoveryTests(unittest.TestCase):
    def test_native_500_prebody_retries_once_uncached(self):
        sent=[]
        @contextmanager
        def open_response(payload):
            sent.append(dict(payload))
            if len(sent)==1: raise RuntimeError("QWEN35_HTTP_500")
            yield [b"data: {ok}\n",b"data: [DONE]\n"]
        retry=[]
        events=list(native_stream_once_retry(
            {"messages":[{"role":"user","content":"redacted"}],"cache_prompt":True},
            open_response,lambda:False,lambda:retry.append(True)))
        self.assertEqual(len(sent),2)
        self.assertTrue(sent[0]["cache_prompt"])
        self.assertFalse(sent[1]["cache_prompt"])
        self.assertEqual(len(retry),1)
        self.assertEqual(events,[b"data: {ok}\n",b"data: [DONE]\n"])

    def test_persistent_500_propagates_with_two_attempt_limit(self):
        attempts=[]
        @contextmanager
        def bad(payload):
            attempts.append(payload)
            raise RuntimeError("QWEN35_HTTP_500")
            yield None
        with self.assertRaisesRegex(RuntimeError,"QWEN35_HTTP_500"):
            list(native_stream_once_retry({"cache_prompt":True},bad,lambda:False))
        self.assertEqual(len(attempts),2)

    def test_other_http_errors_not_retried(self):
        attempts=[]
        @contextmanager
        def bad(payload):
            attempts.append(payload)
            raise RuntimeError("QWEN35_HTTP_400")
            yield None
        with self.assertRaisesRegex(RuntimeError,"QWEN35_HTTP_400"):
            list(native_stream_once_retry({},bad,lambda:False))
        self.assertEqual(len(attempts),1)

    def test_no_restart_after_partial_stream(self):
        attempts=[]
        @contextmanager
        def partial(payload):
            attempts.append(payload)
            def body():
                yield b"data: first\n"
                raise RuntimeError("QWEN35_HTTP_500")
            yield body()
        stream=native_stream_once_retry({},partial,lambda:False)
        self.assertEqual(next(stream),b"data: first\n")
        with self.assertRaisesRegex(RuntimeError,"QWEN35_HTTP_500"):
            list(stream)
        self.assertEqual(len(attempts),1)

    def test_stop_prevents_retry_before_initial_start(self):
        called=[]
        @contextmanager
        def response(payload):
            called.append(True)
            yield []
        self.assertEqual(list(native_stream_once_retry({},response,lambda:True)),[])
        self.assertFalse(called)

    def test_stop_between_attempts_blocks_uncached_retry(self):
        attempts=[]
        cancelled=[False]
        @contextmanager
        def first(payload):
            attempts.append(payload)
            raise RuntimeError("QWEN35_HTTP_500")
            yield None
        def on_retry():cancelled[0]=True
        self.assertEqual(list(native_stream_once_retry({},first,lambda:cancelled[0],on_retry)),[])
        self.assertEqual(len(attempts),1)

    def test_stop_mid_stream_suppresses_later_events(self):
        cancelled=[False]
        @contextmanager
        def response(payload):
            def bytes_stream():
                yield b"data: one\n"
                cancelled[0]=True
                yield b"data: two\n"
            yield bytes_stream()
        stream=native_stream_once_retry({},response,lambda:cancelled[0])
        self.assertEqual(list(stream),[b"data: one\n"])

class MusicFeedbackClassificationTests(unittest.TestCase):
    def test_reported_followup_is_feedback_not_song_generation(self):
        texts=[
            "I was just trying to tell you this is the issues with your remix version of the song",
            "I was saying that's what I saw wrong with your remix version",
            "Your remix has duplicate verses, not different flows",
            "That remix repeated the hook in every verse",
            "Why did you reuse the lines in your remix?",
            "I want to explain what's wrong with your remix",
            "The parody needs more variation but I haven't asked you to rewrite it yet",
        ]
        for text in texts:
            with self.subTest(text=text):
                self.assertIsNone(transformation_contract(text,reference_available=True))

    def test_explicit_new_composition_commands_are_preserved(self):
        cases={
            "Write a parody song about an observatory":"parody",
            "Can you remix those lyrics?":"remix",
            "Remaster my song, keep its hook":"remaster",
            "Create a mashup of these two tracks":"mashup",
            "Rewrite this song with a different plot":"paraphrase",
            "Adapt the song into folk music":"adaptation",
            "Write a new cover song":"cover",
            "Please flip this track":"remix",
            "I want a new remix of that song":"remix",
            "Please fix the repeated verses in your remix":"remix",
        }
        for prompt,mode in cases.items():
            with self.subTest(prompt=prompt):
                contract=transformation_contract(prompt,reference_available=True)
                self.assertIsNotNone(contract)
                self.assertEqual(contract["mode"],mode)

if __name__=="__main__":
    unittest.main()
