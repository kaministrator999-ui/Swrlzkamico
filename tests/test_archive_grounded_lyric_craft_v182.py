"""Static and runtime-gating checks for privacy-safe original-lyric craft guidance.

These tests verify prompt integration, not actual generation quality or trained weights.
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "hf_space"))

from lyric_craft_school import LYRIC_CRAFT_SCHOOL, lyric_craft_policy


def test_creative_requests_get_the_craft_school():
    for prompt in (
        "Write me a complete original rap song about a clock, 800 words.",
        "Freestyle",
        "Spit some bars over a violin beat",
        "Next song",
        "Craft a catchy hook about the old clock",
        "Write a melancholy verse with internal rhymes",
    ):
        assert lyric_craft_policy(prompt) == LYRIC_CRAFT_SCHOOL, prompt


def test_lookup_and_analysis_do_not_get_songwriting_prefill():
    for prompt in (
        "Find lyrics to a song online",
        "Analyze those song lyrics",
        "Review all the songs we made",
        "Who wrote that rap?",
        "Search for a rap song by title",
        "What is a chorus?",
        "Please explain songwriting",
    ):
        assert lyric_craft_policy(prompt) == "", prompt


def test_reference_followups_get_craft_without_source_lyrics():
    assert lyric_craft_policy("Do another one", structural_reference=True)
    assert "earlier songs' wording" in LYRIC_CRAFT_SCHOOL
    assert "PRIVATE" not in LYRIC_CRAFT_SCHOOL


def test_700m_route_is_wired_to_the_compact_policy():
    text = (ROOT / "hf_space" / "lfm2_700m_engine.py").read_text(encoding="utf-8")
    assert "from lyric_craft_school import lyric_craft_policy" in text
    assert 'lyric_craft_policy(prompt, structural_reference=bool(reference_structure))' in text
    assert "if craft_policy:" in text


if __name__ == "__main__":
    test_creative_requests_get_the_craft_school()
    test_lookup_and_analysis_do_not_get_songwriting_prefill()
    test_reference_followups_get_craft_without_source_lyrics()
    test_700m_route_is_wired_to_the_compact_policy()
    print("archive-grounded-original-lyrics-v1 PASS")
