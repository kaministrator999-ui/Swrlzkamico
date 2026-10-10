"""v191 exact-line streaming recovery tests: no real model or paid calls."""
from __future__ import annotations

import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "hf_space"))

from lyric_bounded_continuation import buffered_bounded_lyric_continuation
from lyric_output_contract import lyric_shape_request, extend_continuous_lyrics, verify_original_lyrics, continuation_shape_receipt

SHAPE = lyric_shape_request(
    "Write a 40-line original chopper freestyle about a clockmaker solving a mystery. "
    "Keep it continuous, use meaningful internal rhymes, and alternate rapid-fire passages "
    "with short punchlines. No chorus."
)


class FakeStream:
    def __init__(self, chunks):
        self.chunks = chunks
        self.produced = 0

    def create_chat_completion(self, **kwargs):
        assert kwargs.get("stream") is True
        for chunk in self.chunks:
            self.produced += 1
            yield {"choices": [{"delta": {"content": chunk}}]}


def run_fake(chunks, target=8):
    fake = FakeStream(chunks)
    text, timing = buffered_bounded_lyric_continuation(
        fake, [{"role":"user","content":"continue the original clockmaker verse"}],
        300, 0.35, max_lines=target)
    return fake, text, timing


class BoundedOriginalLyricV191Test(unittest.TestCase):
    def test_stop_after_eight_lines_without_decoding_further(self):
        pieces = [f"Fresh gear clue number {i}\n" for i in range(1, 25)]
        fake, text, timing = run_fake(pieces)
        self.assertEqual(fake.produced, 8)
        self.assertEqual(len(text.splitlines()), 8)
        self.assertNotIn("number 9", text)
        self.assertTrue(timing["stoppedAtLineBoundary"])
        self.assertEqual(timing["returnedSegmentLines"], 8)

    def test_chunk_boundary_does_not_split_a_lyric(self):
        fake, text, timing = run_fake(
            ["An original ", "clue arrives\n",
             "Second bar\nThird bar\nFourth bar\n",
             "Fifth bar\nSixth bar\nSeventh bar\n",
             "Eighth bar\nNinth bar\nMore bars never needed\n"])
        self.assertEqual(text.splitlines()[-1], "Eighth bar")
        self.assertEqual(len(text.splitlines()), 8)
        self.assertEqual(fake.produced, 5)
        self.assertTrue(timing["stoppedAtLineBoundary"])

    def test_blank_lines_do_not_count_as_song_lines(self):
        _, text, receipt = run_fake(["\n\nFirst\n", "\nSecond\n", "Third\nFourth\n"], 2)
        self.assertEqual([line for line in text.splitlines() if line.strip()], ["First", "Second"])
        self.assertTrue(receipt["stoppedAtLineBoundary"])

    def test_unterminated_last_line_is_preserved(self):
        _, text, receipt = run_fake(["First\n", "Second - still authored"],2)
        self.assertEqual(text, "First\nSecond - still authored")
        self.assertFalse(receipt["stoppedAtLineBoundary"])
        self.assertEqual(receipt["returnedSegmentLines"], 2)

    def test_28_to_40_with_two_bounded_model_segments(self):
        prefix=[f"A careful clockmaker inspected unique clue {i}" for i in range(1,29)]
        first=[f"A copper gear showed hidden witness mark {i}" for i in range(1,9)]
        second=[f"The mark revealed the real mechanism {i}" for i in range(1,5)]
        fake1, t1, meta1=run_fake([line+"\n" for line in first+first],8)
        self.assertEqual(fake1.produced,8)
        interim=extend_continuous_lyrics(prefix,t1,SHAPE)
        self.assertIsNotNone(interim)
        self.assertEqual(len(interim),36)
        fake2,t2,meta2=run_fake([line+"\n" for line in second+second],4)
        complete=extend_continuous_lyrics(interim,t2,SHAPE)
        self.assertIsNotNone(complete)
        self.assertEqual(len(complete),40)
        self.assertEqual(verify_original_lyrics("\n".join(complete),SHAPE)["status"],"PASS")

    def test_repeated_line_must_still_fail(self):
        prefix=[f"Unrepeated initial clue {i}" for i in range(1,29)]
        new=[f"New mark on gear {i}" for i in range(1,8)]
        _, text, _=run_fake([prefix[4]+"\n"]+[line+"\n" for line in new],8)
        self.assertIsNone(extend_continuous_lyrics(prefix,text,SHAPE))
        self.assertIn("prior-lyric-line-repeated",continuation_shape_receipt(prefix,text,SHAPE)["reasons"])

    def test_scope_and_bounded_attempt_count(self):
        source=(ROOT/"hf_space/lfm2_700m_engine.py").read_text()
        self.assertIn("for continuation_index in range(4):", source)
        self.assertIn("buffered_bounded_lyric_continuation(", source)
        self.assertNotIn("for continuation_index in range(2):",source)
        self.assertIn("max_attempts=6 if strict_lyric_turn else 3",source)


if __name__ == "__main__":
    unittest.main()
