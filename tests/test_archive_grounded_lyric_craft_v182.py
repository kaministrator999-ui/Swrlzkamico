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



def test_lyric_ocean_v3_complete_songs_are_distinct_and_complete():
    root = ROOT / "training" / "lyrics"
    long_v2 = json.loads((root / "original_full_compositions_v2.json").read_text(encoding="utf-8"))
    long_v3 = json.loads((root / "original_complete_songs_v3.json").read_text(encoding="utf-8"))
    assert long_v3["schema"] == "swrlz-lyric-ocean-original-complete-songs-v3"
    assert long_v3["songCount"] == len(long_v3["songs"]) == 8
    assert long_v3["totalLines"] == sum(s["lineCount"] for s in long_v3["songs"]) == 252
    assert len({s["title"] for s in long_v3["songs"]}) == 8
    assert len({s["form"] for s in long_v3["songs"]}) == 8
    assert all(s["lineCount"] == len(s["lines"]) and s["lineCount"] >= 24 for s in long_v3["songs"])
    assert all(s["noArchiveLyrics"] and s["qualityReview"].startswith("PENDING") for s in long_v3["songs"])
    assert sum(s["lineCount"] for s in long_v2["songs"]) + long_v3["totalLines"] == 448


def test_lyric_ocean_v3_real_rewrite_pairs_preserve_truthful_status():
    src = ROOT / "training" / "lyrics" / "original_revision_pairs_v3.json"
    data = json.loads(src.read_text(encoding="utf-8"))
    assert data["count"] == len(data["cases"]) == 24
    assert len({p["id"] for p in data["cases"]}) == 24
    assert len({p["failure"] for p in data["cases"]}) == 24
    assert all(len(p["before"]) == len(p["after"]) == 2 for p in data["cases"])
    assert all(p["before"] != p["after"] for p in data["cases"])
    assert all(p["assessment"] == "PENDING_INDEPENDENT_REVIEW" for p in data["cases"])


def test_lyric_ocean_v3_rubric_is_not_a_self_awarded_grade():
    path = ROOT / "training" / "lyrics" / "editorial_rubric_v3.json"
    rubric = json.loads(path.read_text(encoding="utf-8"))
    assert rubric["status"] == "UNSCORED_INSTRUCTOR_RUBRIC_ONLY"
    assert len(rubric["dimensions"]) == 12
    assert len({item["id"] for item in rubric["dimensions"]}) == 12
    assert all(item["score"] is None for item in rubric["dimensions"])
    assert all(set(item["levels"]) == {"0", "1", "2", "3", "4"} for item in rubric["dimensions"])


def test_private_feedback_case_text_never_enters_public_v3_structures():
    root = ROOT / "training" / "lyrics"
    names = ("original_complete_songs_v3.json", "original_revision_pairs_v3.json",
             "editorial_rubric_v3.json")
    for name in names:
        text = (root / name).read_text(encoding="utf-8").lower()
        for marker in ('thread_id', 'conversation_id', 'private_feedback', 'private_song_text',
                       'source_assistant_turn_index', 'raw_assistant_output_for_manual_cleaning'):
            assert marker not in text, (name, marker)



def test_v4_provisional_editorial_anchors_match_actual_song_lines():
    root = ROOT / "training" / "lyrics"
    d = json.loads((root / "PROVISIONAL_EDITORIAL_PASS_V4.json").read_text(encoding="utf-8"))
    assert d["status"] == "PROVISIONAL_EDITORIAL_NOT_INDEPENDENT_BLIND_REVIEW"
    a = json.loads((root / "original_full_compositions_v2.json").read_text(encoding="utf-8"))
    b = json.loads((root / "original_complete_songs_v3.json").read_text(encoding="utf-8"))
    by_source = {"original_full_compositions_v2.json": a, "original_complete_songs_v3.json": b}
    assert len(d["reviews"]) == 14
    for review in d["reviews"]:
        songs = by_source[review["sourceAsset"]]["songs"]
        song = next(s for s in songs if s["title"] == review["song"])
        for evidence_key in ("positiveEvidence", "revisionEvidence"):
            evidence = review[evidence_key]
            source_line = song["lines"][evidence["line"] - 1]
            assert evidence["excerpt"].casefold() in source_line.casefold(), (review["song"], evidence_key)
        assert review["trainingApproval"] == "REJECT_PENDING_INDEPENDENT_QC"
        assert review["editorialIndependence"] == "SAME_ASSISTANT_REVIEW_NOT_BLIND"
        assert set(review["provisionalScores"]) == set(d["coverage"]["dimensions"])
        assert all(0 <= value <= 4 for value in review["provisionalScores"].values())


def test_v4_distinct_song_forms_and_contiguous_section_counts():
    root = ROOT / "training" / "lyrics"
    d = json.loads((root / "CROSS_FORM_COMPLETE_SONGS_V4.json").read_text(encoding="utf-8"))
    assert d["schema"] == "swrlz-lyric-ocean-crossform-complete-v4"
    assert d["songCount"] == len(d["songs"]) == 8
    assert d["totalLyricLines"] == sum(s["lineCount"] for s in d["songs"]) == 249
    assert len({s["title"] for s in d["songs"]}) == 8
    assert len({s["form"] for s in d["songs"]}) == 8
    for song in d["songs"]:
        lines = [line for section in song["sections"] for line in section["lines"]]
        assert len(lines) == song["lineCount"] >= 24
        assert all(line.strip() for line in lines)
        assert song["trainingStatus"] == "NOT_WEIGHT_TRAINABLE"
        assert song["editorialStatus"] == "DRAFT_UNREVIEWED"
        assert song["performedMeterVerified"] is False
    v2 = json.loads((root / "original_full_compositions_v2.json").read_text(encoding="utf-8"))
    v3 = json.loads((root / "original_complete_songs_v3.json").read_text(encoding="utf-8"))
    assert len(v2["songs"]) + len(v3["songs"]) + len(d["songs"]) == 22
    assert sum(s["lineCount"] for s in v2["songs"] + v3["songs"]) + d["totalLyricLines"] == 697



if __name__ == "__main__":
    for obj in list(globals().values()):
        if callable(obj) and getattr(obj, "__name__", "").startswith("test_"):
            obj()
    print("archive-grounded-lyric-ocean-v4 structural checks PASS")
