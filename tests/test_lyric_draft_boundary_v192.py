"""v192 whole-draft length boundary: regression from Dragon Chat (37).

These are deterministic synthetic stream tests. Real 700M artistic quality
and token-level performance require a separate live export.
"""
from __future__ import annotations

import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "hf_space"))

from lyric_bounded_continuation import (
    buffered_bounded_original_lyrics,
    buffered_bounded_lyric_continuation,
)
from lyric_output_contract import (
    lyric_shape_request,
    verify_original_lyrics,
    recoverable_continuous_lines,
    extend_continuous_lyrics,
)

REQUEST = (
    "Write a 40-line original chopper freestyle about a clockmaker solving a mystery. "
    "Keep it continuous, use meaningful internal rhymes, and alternate rapid-fire "
    "passages with short punchlines. No chorus."
)
SHAPE = lyric_shape_request(REQUEST)


class StreamingFakeModel:
    def __init__(self, chunks):
        self.chunks = chunks
        self.produced = 0

    def create_chat_completion(self, **kwargs):
        assert kwargs.get("stream") is True
        for chunk in self.chunks:
            self.produced += 1
            yield {"choices": [{"delta": {"content": chunk}}]}


def get_bounded(chunks, count=40):
    m = StreamingFakeModel(chunks)
    body, receipt = buffered_bounded_original_lyrics(
        m,
        [{"role": "user", "content": REQUEST}],
        1600,
        0.40,
        max_lines=count,
    )
    return m, body, receipt


class FullDraftLineBoundaryV192(unittest.TestCase):
    def test_139_line_model_stops_at_40_during_generation(self):
        lines = [f"Unique clockmaker witness clue {i}" for i in range(1, 140)]
        model, result, receipt = get_bounded([line + "\n" for line in lines])
        self.assertEqual(model.produced, 40)
        self.assertEqual(len(result.splitlines()), 40)
        self.assertEqual(result.splitlines()[0], lines[0])
        self.assertEqual(result.splitlines()[-1], lines[39])
        self.assertNotIn(lines[40], result)
        self.assertTrue(receipt["stoppedAtLineBoundary"])
        self.assertEqual(receipt["returnedSegmentLines"], 40)
        # Syntactic acceptance never certifies thematic/musical quality.
        gate = verify_original_lyrics(result, SHAPE)
        self.assertEqual(gate["status"], "PASS")
        self.assertIs(gate["semanticQualityVerified"], False)

    def test_chunk_containing_ninth_surplus_is_clipped_only_at_complete_line(self):
        chunks = [
            "Gears glint; ",
            "clues click\n",
            "\n",
            "Blue steel bruise\n" + "\n".join(f"Mark {i}" for i in range(3, 41)) + "\n",
            "The model should never decode this trailing chunk\n",
        ]
        model, body, receipt = get_bounded(chunks, 40)
        self.assertEqual(model.produced, 4)
        self.assertEqual(len([x for x in body.splitlines() if x.strip()]), 40)
        self.assertTrue(body.endswith("Mark 40\n"))
        self.assertTrue(receipt["stoppedAtLineBoundary"])

    def test_28_line_clean_underflow_can_continue_eight_plus_four(self):
        raw = [f"Clockmaker reads physical scratch {i}" for i in range(1, 29)]
        _, first, meta = get_bounded([x + "\n" for x in raw])
        self.assertEqual(len(first.splitlines()), 28)
        self.assertFalse(meta["stoppedAtLineBoundary"])
        original = recoverable_continuous_lines(first, SHAPE)
        self.assertEqual(len(original), 28)
        eight = [f"Brass-cut clue verified {i}" for i in range(1, 9)]
        m, continuation, _ = get_bounded([x + "\n" for x in eight + eight], 8)
        self.assertEqual(m.produced, 8)
        stage = extend_continuous_lyrics(original, continuation, SHAPE)
        self.assertEqual(len(stage), 36)
        final_four = [f"Suspect and motive established {i}" for i in range(1, 5)]
        _, last, _ = get_bounded([x + "\n" for x in final_four], 4)
        full = extend_continuous_lyrics(stage, last, SHAPE)
        self.assertEqual(len(full), 40)
        self.assertEqual(verify_original_lyrics("\n".join(full), SHAPE)["status"], "PASS")

    def test_refusal_does_not_become_acceptable_by_stopping_at_forty(self):
        lines = ["I can't do a forty-line freestyle."] + [f"Claimed line {i}" for i in range(2, 141)]
        _, body, _ = get_bounded([x + "\n" for x in lines])
        gate = verify_original_lyrics(body, SHAPE)
        self.assertEqual(len(body.splitlines()), 40)
        self.assertEqual(gate["status"], "REJECT")
        self.assertIn("unrequested-refusal", gate["reasons"])

    def test_refusal_recognition_does_not_reject_literary_first_person(self):
        lines = ["I can't do much about the rusty gears"] + [
            f"The inspector discovers unique witness scar {i}" for i in range(2, 41)
        ]
        _, body, _ = get_bounded([x + "\n" for x in lines])
        self.assertEqual(verify_original_lyrics(body, SHAPE)["status"], "PASS")

    def test_verse_spacing_is_not_autoaccepted_without_cleaning(self):
        many = []
        for i in range(40):
            many.extend([f"Measure {i}", "\n"])
        _, body, _ = get_bounded([s + ("\n" if s != "\n" else "") for s in many])
        self.assertEqual(len([x for x in body.splitlines() if x.strip()]), 40)
        self.assertIn("continuous-verse-broken-into-stanzas", verify_original_lyrics(body, SHAPE)["reasons"])

    def test_previous_small_continuations_still_max_out_at_eight(self):
        model = StreamingFakeModel([f"Next new bar {i}\n" for i in range(1, 15)])
        text, timing = buffered_bounded_lyric_continuation(
            model, [{"role": "user", "content": REQUEST}],
            1600, 0.4, max_lines=40,
        )
        self.assertEqual(model.produced, 8)
        self.assertEqual(len(text.splitlines()), 8)
        self.assertEqual(timing["requestedSegmentLines"], 8)

    def test_existing_engine_has_explicitly_bounded_first_and_rewrite_only(self):
        source = (ROOT / "hf_space/lfm2_700m_engine.py").read_text()
        lyric = source.split("        elif strict_lyric_turn:\n            # Keep useful model-authored", 1)[1]
        self.assertIn("def complete_original_draft(draft_messages, draft_temperature):", lyric)
        self.assertIn("buffered_bounded_original_lyrics(", lyric)
        self.assertIn("candidate_raw,timing=complete_original_draft(messages,temperature)", lyric)
        self.assertIn("draft,timing2=complete_original_draft(", lyric)
        self.assertIn("buffered_bounded_lyric_continuation(", lyric)
        self.assertIn("candidate_check=check", lyric)
        self.assertIn("clean_lyric_container(candidate_raw)", lyric)


if __name__ == "__main__":
    unittest.main()
