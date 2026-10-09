"""Direct original-song formal acceptance regression tests — no model weights required."""
from __future__ import annotations
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"hf_space"))
from lyric_output_contract import lyric_shape_request, verify_original_lyrics, clean_lyric_container, recoverable_continuous_lines, extend_continuous_lyrics
from lyric_craft_school import lyric_craft_policy

PROMPT="Write an original 40-line chopper freestyle about an observatory mystery, continuous, with no chorus."
SHAPE=lyric_shape_request(PROMPT)

def lines(n: int=40) -> str:
    return "\n".join(f"A distant telescope records a changing clue {i+1}" for i in range(n))

def test_explicit_request_extraction():
    assert SHAPE["requestedLines"]==40
    assert SHAPE["continuous"] is True
    assert SHAPE["noChorus"] is True
    assert lyric_shape_request("Write a 12-bar rap")["requestedLines"]==12
    assert lyric_shape_request("Write a 999-line rap")["requestedLines"] is None

def test_good_continuous_form_and_copyable_container():
    body=lines()
    check=verify_original_lyrics(body,SHAPE)
    assert check["status"]=="PASS",check
    assert check["observedLyricLines"]==40
    assert check["semanticQualityVerified"] is False
    rendered=clean_lyric_container(body)
    assert rendered.startswith(chr(96)*3+"\n")
    assert verify_original_lyrics(rendered,SHAPE)["status"]=="PASS"

def test_live_failure_class_is_detected_without_copying_private_output():
    # Structurally equivalent to the exported defect, NOT a transcript excerpt.
    paragraphs="\n\n".join(lines(4) for _ in range(9))
    flawed=("I'm sorry, I can't produce exactly forty lines.\n\n"+paragraphs+
             "\n\n(Note: The song matches your request.)")
    result=verify_original_lyrics(flawed,SHAPE)
    assert result["status"]=="REJECT",result
    assert result["observedLyricLines"]==36,result
    assert {"unrequested-refusal","instructional-preface-or-self-grading",
            "continuous-verse-broken-into-stanzas","wrong-explicit-lyric-line-count"
            }.issubset(result["reasons"]),result

def test_negative_chorus_labels_and_no_fake_line_padding():
    assert "invented-section-labels" in verify_original_lyrics("[Verse 1]\n"+lines(),SHAPE)["reasons"]
    assert "unrequested-chorus" in verify_original_lyrics("[Chorus]\n"+lines(),
        lyric_shape_request("Compose a 40-line song with no chorus"))["reasons"]
    assert verify_original_lyrics(lines(36),SHAPE)["status"]=="REJECT"
    assert clean_lyric_container(lines(36)).count("A distant telescope") == 36


def test_recoverability_of_clean_28_lines_without_changing_any_words():
    # Synthetic case matches the observed 28-line / stanza-gap shape.
    raw="\n\n".join("\n".join(lines(28).splitlines()[start:start+4]) for start in range(0,28,4))
    result=recoverable_continuous_lines(raw,SHAPE)
    assert result is not None and len(result)==28
    assert result==lines(28).splitlines()
    assert "continuous-verse-broken-into-stanzas" in verify_original_lyrics(raw,SHAPE)["reasons"]
    assert verify_original_lyrics("\n".join(result),SHAPE)["reasons"]==["wrong-explicit-lyric-line-count"]

def test_append_twelve_new_lines_yields_exactly_forty_without_filler():
    first=[f"Observatory clue {i+1} changes the measured hour" for i in range(28)]
    ending="\n".join(f"The operator checks a new witness mark {i+1}" for i in range(12))
    full=extend_continuous_lyrics(first,ending,SHAPE)
    assert full is not None and len(full)==40
    assert full[:28]==first
    assert full[28:]==ending.splitlines()
    assert verify_original_lyrics("\n".join(full),SHAPE)["status"]=="PASS"

def test_refuse_unsafe_or_fabricated_append_operations():
    base=[f"A unique original line {i+1}" for i in range(28)]
    assert recoverable_continuous_lines("I'm sorry, can't do this\n"+lines(28),SHAPE) is None
    assert recoverable_continuous_lines("Title: Observatory\n"+lines(28),SHAPE) is None
    assert recoverable_continuous_lines("[Verse 1]\n"+lines(28),SHAPE) is None
    fence=chr(96)*3
    assert recoverable_continuous_lines("Hi there\n"+fence+"\n"+lines(28)+"\n"+fence,SHAPE) is None
    assert extend_continuous_lyrics(base,"\n".join(base[0] for _ in range(12)),SHAPE) is None
    assert extend_continuous_lyrics(base,lines(13),SHAPE) is None
    assert extend_continuous_lyrics(base,lines(12),SHAPE) is not None
    assert extend_continuous_lyrics(base,lines(4),SHAPE) is not None
    assert recoverable_continuous_lines(lines(4),lyric_shape_request("Write a 40-line song")) is None


def test_no_song_lookup_or_code_route_affected():
    for prompt in ("Find the lyrics of a song","Explain that song","Review rap lyrics","Write an analysis of a ballad"):
        assert lyric_craft_policy(prompt)=="",prompt
    assert lyric_craft_policy(PROMPT)

def test_engine_route_has_a_bounded_single_retry_and_structural_only_truth():
    source=(ROOT/"hf_space"/"lfm2_700m_engine.py").read_text(encoding="utf-8")
    assert "strict_lyric_turn=bool(direct_creative_lyric_contract" in source
    assert "elif strict_lyric_turn:" in source
    assert "verify_original_lyrics(candidate_raw,shape)" in source
    assert "extend_continuous_lyrics(authored_lines,new_segment,shape)" in source
    assert "for continuation_index in range(2):" in source
    assert 'candidate_check=check' in source
    assert "clean_lyric_container(candidate_raw)" in source
    assert "2048 if requested and requested>=64" in source
    assert "MYSTERY ARC: Establish a specific anomaly" in source

if __name__=="__main__":
    for value in tuple(globals().values()):
        if callable(value) and getattr(value,"__name__","").startswith("test_"):
            value()
    print("direct-original-lyric-acceptance-v187 PASS")
