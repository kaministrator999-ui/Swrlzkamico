"""v167 regression: mobile-first lyric divider hierarchy is compiled before Chat."""
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"hf_space"))

from music_structure import (
    LYRIC_OUTER_DIVIDER,
    LYRIC_SECTION_DIVIDER,
    structure_verified_music,
    compile_verified_music_presentation,
    music_structure_debug,
)
import model_router

PAGE="""Example Artist – Test Signal lyrics
[Verse 1: Alpha]
Line one
Line two
Line three
Line four
[Chorus: Alpha]
Hook one
Hook two
Hook three
Hook four
[Verse 2: Beta]
Second verse one
Second verse two
Second verse three
Second verse four
"""

VERIFIED="""Line one
Line two
Line three
Line four

Hook one
Hook two
Hook three
Hook four

Second verse one
Second verse two
Second verse three
Second verse four"""

doc=structure_verified_music(
    VERIFIED,
    PAGE,
    subject='"Test Signal" by Example Artist',
    requested_scope="full-lyrics",
)
presentation=compile_verified_music_presentation(
    doc,
    source_title="Example Artist – Test Signal Lyrics",
    source_url="https://example.test/test-signal",
)
text=presentation["presentationText"]

# Outer boundaries are Markdown horizontal rules: full-width in Chat.
assert LYRIC_OUTER_DIVIDER=="---"
assert text.count("\n\n---\n\n")==2,text

# Internal transitions use the deliberately shorter visual separator.
assert LYRIC_SECTION_DIVIDER=="────────"
assert text.count(f"\n\n{LYRIC_SECTION_DIVIDER}\n\n")==2,text

# Hierarchy: intro -> full-width open -> section -> short -> section -> short ->
# section -> full-width close -> source footer.
intro='Okay — here’s the verified lyric text for **"Test Signal" by Example Artist**:'
source='**Lyrics source:** Example Artist – Test Signal Lyrics — https://example.test/test-signal'
assert text.index(intro) < text.index("\n\n---\n\n")
first=text.index("**[Verse 1: Alpha]**")
chorus=text.index("**[Chorus: Alpha]**")
verse2=text.index("**[Verse 2: Beta]**")
assert first < chorus < verse2,text
assert first < text.index(LYRIC_SECTION_DIVIDER,first) < chorus,text
assert chorus < text.index(LYRIC_SECTION_DIVIDER,chorus) < verse2,text
closing=text.rindex("\n\n---\n\n")
assert verse2 < closing < text.index(source),text

# Divider chrome must not mutate source lines.
for line in VERIFIED.replace("\n\n","\n").splitlines():
    assert line in text,(line,text)
assert presentation["sourceTextRewritten"] is False,presentation

style=presentation["dividerPresentation"]
assert style["outerMeaning"]=="lyric_document_boundary",style
assert style["innerMeaning"]=="lyric_section_transition",style
assert style["blankLinesAroundDividers"] is True,style
assert style["mobileFirst"] is True,style

debug=music_structure_debug(doc,presentation)
assert debug["dividerPresentation"]==style,debug

# Chat/Model Router receives the already-polished payload and returns it unchanged.
result={"modelContext":{"verifiedLyrics":{"presentationText":text}}}
assert model_router._lyrics_retrieval_payload(result,"lyrics please")==text

print("mobile-first-lyric-dividers-v167 PASS")
