"""v171 regression: continuous unmarked lyric runs survive extraction and export stage diagnostics."""
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"hf_space"))

import online_tools

SUBJECT='"test signal" by example artist'
PAGE="""Navigation
Example Artist
Tyga style page chrome
Test Signal Lyrics
Signal opens in the midnight
Current runs beneath the station
Every circuit holds the cadence
Noisy sparks become the motion
Second current keeps the rhythm
Another current crosses over
Final signal keeps on moving
Closing current ends the motion
Encore current turns the corner
Last signal fades into the morning
Submit corrections
Related songs
"""

analysis=online_tools._lyrics_extract_analysis(PAGE,"full-lyrics",SUBJECT)
text=analysis["text"]
diag=analysis["diagnostics"]

assert text,diag
assert "Signal opens in the midnight" in text,text
assert "Last signal fades into the morning" in text,text
assert "Submit corrections" not in text,text
assert diag["decision"]=="ACCEPTED",diag
assert diag["reason"]=="ANCHORED_CONTINUOUS_FULL_LYRICS",diag
assert diag["anchorLine"]=="Test Signal Lyrics",diag
assert diag["contentLineCount"]>=10,diag
assert diag["acceptedBlockCount"]==1,diag
assert diag["continuousRunEligible"] is True,diag
assert diag["resultLineCount"]>=10,diag
assert diag["terminalBoundaryKind"] in {"POST_SONG_META_BOUNDARY","HARD_BOUNDARY"},diag

# The compatibility wrapper must return the same text.
assert online_tools._lyrics_extract_candidate(PAGE,"full-lyrics",SUBJECT)==text

# An anchor with too little material must still fail closed.
SHORT="""Test Signal Lyrics
This is one line
This is two lines
This is three lines
Privacy Policy
"""
short=online_tools._lyrics_extract_analysis(SHORT,"full-lyrics",SUBJECT)
assert short["text"]=="",short
assert short["diagnostics"]["decision"]=="REJECTED",short
assert short["diagnostics"]["resultChars"]==0,short

# Diagnostics must survive the Dragon Chat / Online Camera projection.
raw_debug=[{
    "attempt":1,
    "origin":"test",
    "requestedUrl":"https://lyrics.example/test",
    "finalUrl":"https://lyrics.example/test",
    "searchResultTitle":"Example Artist - Test Signal Lyrics",
    "fetchedPageTitle":"Example Artist - Test Signal Lyrics",
    "fetchStatus":200,
    "fetchedContent":online_tools._lyrics_debug_preview(PAGE,SUBJECT,600),
    "extractorOutput":online_tools._lyrics_debug_preview(text,SUBJECT,600),
    "extractorDiagnostics":diag,
    "sourceIdentityVerified":True,
    "sourceIdentityScore":8,
    "snippetOverlapCount":0,
    "snippetInformativeTokenCount":0,
    "snippetSequenceSpan":0,
    "musicalSectionCount":0,
    "performerCueCount":0,
    "outcome":"VERIFIED",
    "rejectionReason":"VERIFIED",
}]
projected=online_tools.copy_lyrics_debug(raw_debug)
assert len(projected)==1,projected
pd=projected[0]["extractorDiagnostics"]
assert pd["reason"]=="ANCHORED_CONTINUOUS_FULL_LYRICS",pd
assert pd["rawLineCount"]==diag["rawLineCount"],pd
assert pd["scopedNonEmptyLineCount"]==diag["scopedNonEmptyLineCount"],pd
assert pd["acceptedBlockCount"]==1,pd
assert pd["resultLineCount"]>=10,pd

# v172 live acceptance: every real lyric line may be separated by a blank.
# No song-specific phrase, stanza count, or site-domain exception is needed.
SPACED=PAGE.replace("\n","\n\n")
spaced=online_tools._lyrics_extract_analysis(SPACED,"full-lyrics",SUBJECT)
sd=spaced["diagnostics"]
assert spaced["text"],sd
assert sd["anchorLine"]=="Test Signal Lyrics",sd
assert sd["blankSeparatedChunkCount"]>=10,sd
assert sd["acceptedBlockCount"]==1,sd
assert sd["continuousRunEligible"] is True,sd
assert sd["reason"]=="ANCHORED_CONTINUOUS_FULL_LYRICS",sd
assert sd["resultLineCount"]==diag["resultLineCount"],(sd,diag)
assert spaced["text"]==text,(spaced["text"],text)
assert "Submit corrections" not in spaced["text"]

# Page chrome and insufficient text must not become accepted lyrics.
spaced_short=online_tools._lyrics_extract_analysis(SHORT.replace("\n","\n\n"),"full-lyrics",SUBJECT)
assert spaced_short["text"]=="",spaced_short
unanchored=online_tools._lyrics_extract_analysis(
    SPACED.replace("Test Signal Lyrics","Unrelated website"),
    "full-lyrics",SUBJECT,
)
assert unanchored["text"]=="",unanchored

print("continuous-lyric-extractor-diagnostics-v171 PASS")
print("blank-separated-line-extractor-v172 PASS")
