"""Fast contract tests: broad original-song pedagogy without lookup hijacks.

Test the deterministic selector and wiring, not artistic benchmark quality.
"""
from __future__ import annotations

import importlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "hf_space"))

from lyric_craft_school import LYRIC_CRAFT_SCHOOL, _catalog, lyric_craft_policy


def test_creative_requests_activate_without_forcing_one_style():
    for prompt in (
        "Write me a complete original rap song about a clock, 800 words.",
        "Freestyle",
        "Spit some bars over a violin beat",
        "Next song",
        "Craft a catchy hook about the old clock",
        "Write a melancholy verse with internal rhymes",
        "Make a full song about a botanist on the moon",
        "Give me another rap",
    ):
        result = lyric_craft_policy(prompt)
        assert result.startswith(LYRIC_CRAFT_SCHOOL), prompt
        assert "FOCUSED ORIGINAL SONGWRITING TOOLS" in result, prompt
        assert len(result) < 2900, prompt


def test_noncreative_requests_never_receive_music_generation_instructions():
    for prompt in (
        "Find lyrics to a song online",
        "Analyze those song lyrics",
        "Review all the songs we made",
        "Who wrote that rap?",
        "Search for a rap song by title",
        "What is a chorus?",
        "Please explain songwriting",
        "Write an analysis of a famous rap song",
        "Draft a critique of those lyrics",
        "Compare two verses",
    ):
        assert lyric_craft_policy(prompt) == "", prompt


def test_structural_reference_isolation():
    reply = lyric_craft_policy("Do another one", structural_reference=True)
    assert reply.startswith(LYRIC_CRAFT_SCHOOL)
    assert "learn only the abstract musical form" in reply
    assert "Never recycle earlier songs' wording" in reply


def test_catalog_structure_is_bounded_and_privacy_safe():
    path = ROOT / "hf_space" / "lyric_craft_catalog_v2.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["schema"] == "swrlz-lyric-craft-router-catalog-v2"
    assert data["count"] == 48
    cards = _catalog()
    assert len(cards) == 48
    assert len({(c["axis"], c["role"]) for c in cards}) == 48
    assert set(c["role"] for c in cards) == {"build", "perform", "repair"}
    assert all(c["cue"] and len(c["cue"]) <= 260 for c in cards)


def test_teaching_is_prompt_bounded_and_deterministic():
    p = "Write a fast chopper freestyle about the last train"
    a = lyric_craft_policy(p)
    b = lyric_craft_policy(p)
    assert a == b
    assert "high-speed:" in a or "freestyle:" in a
    assert a.count("FOCUSED ORIGINAL SONGWRITING TOOLS") == 1
    assert "song title" not in a.lower()


def test_700m_route_is_wired_at_the_existing_music_owner():
    text = (ROOT / "hf_space" / "lfm2_700m_engine.py").read_text(encoding="utf-8")
    assert text.count("from lyric_craft_school import lyric_craft_policy") == 1
    assert text.count('lyric_craft_policy(prompt, structural_reference=bool(reference_structure))') == 1
    assert text.count("if craft_policy:") == 1
    assert "from music_structure import music_model_policy" in text


def test_public_practice_bank_excludes_private_source_and_labels_training_honestly():
    path = ROOT / "training" / "lyrics" / "lyric_ocean_practice_v2.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["caseCount"] == 768
    assert data["contrastCount"] == 64
    assert len({c["id"] for c in data["cases"]}) == 768
    assert all(c["grade"] == "NOT_RUN" for c in data["cases"])
    assert all(c["source"] == "SYNTHETIC_ORIGINAL_PROMPT_NO_PRIVATE_ARCHIVE_TEXT" for c in data["cases"])
    assert not any("assistant_response" in c or "conversation_id" in c for c in data["cases"])



def test_synthetic_examples_are_varied_and_have_true_line_counts():
    study = ROOT / "training" / "lyrics"
    demos = json.loads((study / "original_demonstrations_v2.json").read_text(encoding="utf-8"))
    full = json.loads((study / "original_full_compositions_v2.json").read_text(encoding="utf-8"))
    assert demos["count"] == 24
    assert len(set(demos["genres"])) == 24
    assert sum(s["lineCount"] for s in demos["examples"]) == 192
    assert full["count"] == 6
    assert sum(s["lineCount"] for s in full["songs"]) == 196
    assert len({s["title"] for s in full["songs"]}) == 6
    assert all(s["lineCount"] == len(s["lines"]) for s in full["songs"])
    assert all(s["form"].endswith("_" + str(len(s["lines"])) + "_lines") for s in full["songs"])
    assert all(s["grade"] == "NOT_RUN" and s["weightTrainable"] is False for s in full["songs"])


def test_ocean_covers_distinct_skills_scenarios_and_contrasts():
    raw = json.loads((ROOT / "training" / "lyrics" / "lyric_ocean_practice_v2.json").read_text(encoding="utf-8"))
    assert len({c["scene"] for c in raw["cases"]}) == 48
    assert len({c["focus"] for c in raw["cases"]}) == 16
    assert len(raw["contrastiveRepairs"]) == 64
    assert len({c["fault"] for c in raw["contrastiveRepairs"]}) == 16
    assert all(c["grade"] == "NOT_RUN" for c in raw["contrastiveRepairs"])


if __name__ == "__main__":
    for obj in list(globals().values()):
        if callable(obj) and getattr(obj, "__name__", "").startswith("test_"):
            obj()
    print("archive-grounded-lyric-ocean-v2 PASS")
