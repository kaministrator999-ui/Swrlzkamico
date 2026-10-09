"""Direct original-song formal acceptance regression tests — no model weights required."""
from __future__ import annotations
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"hf_space"))
from lyric_output_contract import lyric_shape_request, verify_original_lyrics, clean_lyric_container, recoverable_continuous_lines, extend_continuous_lyrics, continuation_shape_receipt
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



def test_24_of_40_case_reports_malformed_suffix_without_exposing_words():
    prefix=[f"Original clockmaker clue {i+1}" for i in range(24)]
    overlong="\n".join(f"Additional unique lyric {i+1}" for i in range(18))
    receipt=continuation_shape_receipt(prefix,overlong,SHAPE)
    assert receipt["observedLyricLines"]==24
    assert receipt["observedSuffixNonemptyLines"]==18
    assert receipt["remainingLyricLines"]==16
    assert "too-many-continuation-lines" in receipt["reasons"]
    assert "Additional unique lyric" not in str(receipt)
    assert extend_continuous_lyrics(prefix,overlong,SHAPE) is None
    duplicate=prefix[4]+"\n"+"\n".join(f"New line {i+1}" for i in range(7))
    assert "prior-lyric-line-repeated" in continuation_shape_receipt(prefix,duplicate,SHAPE)["reasons"]
    assert "refusal-in-continuation" in continuation_shape_receipt(
        prefix,"I'm sorry, I cannot write more",SHAPE)["reasons"]

def test_short_continuations_preserve_authored_prefix_and_finish_exactly_40():
    prefix=[f"Unique clockmaker premise line {i+1}" for i in range(24)]
    first="\n".join(f"The broken watch gave clue {i+1}" for i in range(8))
    second="\n".join(f"The clockwork mystery resolved {i+1}" for i in range(8))
    s1=extend_continuous_lyrics(prefix,first,SHAPE)
    assert s1 is not None and len(s1)==32
    s2=extend_continuous_lyrics(s1,second,SHAPE)
    assert s2 is not None and len(s2)==40
    assert s2[:24]==prefix
    assert verify_original_lyrics("\n".join(s2),SHAPE)["status"]=="PASS"

def test_telemetry_counts_all_four_actual_lyric_attempts_without_text():
    from programming_telemetry import generation_summary
    receipts=[
        {"attempt":i+1,"validationStatus":"REJECT","accepted":False,"durationMs":100.0}
        for i in range(4)
    ]
    kwargs={"total_latency_ms":400,"load_latency_ms":0,
            "visible_first_delta_latency_ms":400,"guarded_turn":False,
            "repair_turn":False,"strict_language":False}
    default=generation_summary(receipts,**kwargs)
    assert default["attemptCount"]==3
    full=generation_summary(receipts,max_attempts=6,**kwargs)
    assert full["attemptCount"]==4
    assert full["totalCandidateGenerationMs"]==400
    assert [v["attempt"] for v in full["attempts"]]==[1,2,3,4]


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
    assert "next_lines=min(8,missing)" in source
    assert "segment_messages=[" in source
    assert "partialReturned" in source
    assert "max_attempts=6 if strict_lyric_turn else 3" in source
    assert "invalid-or-overlong-lyric-continuation" in source
    assert 'candidate_check=check' in source
    assert "clean_lyric_container(candidate_raw)" in source
    assert "2048 if requested and requested>=64" in source
    assert "MYSTERY ARC: Establish a specific anomaly" in source

if __name__=="__main__":
    for value in tuple(globals().values()):
        if callable(value) and getattr(value,"__name__","").startswith("test_"):
            value()
    print("direct-original-lyric-acceptance-v187 PASS")
