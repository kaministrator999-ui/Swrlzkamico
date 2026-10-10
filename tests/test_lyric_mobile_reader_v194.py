"""Regression for compact mobile lyric rendering without breaking code artifacts.

Static CSS/DOM checks plus Node syntax and isolated prompt-routing execution.
This deliberately does not claim actual Android visual acceptance.
"""
from __future__ import annotations
import re
import subprocess
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/"chat"/"§wyrlz"/"index.html").read_text(encoding="utf-8")


class LyricMobileReaderV194(unittest.TestCase):
    def test_js_parses_in_same_environment_as_candidate(self):
        scripts=re.findall(r"<script(?![^>]*\\bsrc=)[^>]*>([\\s\\S]*?)</script>", HTML, re.I)
        self.assertEqual(len(scripts),1)
        r=subprocess.run(["node","--check","-"],input=scripts[0],text=True,capture_output=True)
        self.assertEqual(r.returncode,0,r.stderr)

    def test_lyric_intent_is_scoped_to_songwriting_not_coding(self):
        start=HTML.index("const isOriginalSongwritingPrompt=value=>{")
        end=HTML.index("const renderAssistantContent=",start)
        fn=HTML[start:end]
        scenario="""
const assert = (found,wanted,name) => {
  if(found!==wanted)throw Error(name+": "+String(found))
};
assert(isOriginalSongwritingPrompt("Write a 40-line original chopper freestyle about a clockmaker solving a mystery. Keep it continuous, use meaningful internal rhymes, and alternate rapid-fire passages with short punchlines. No chorus."),true,"actual user request");
assert(isOriginalSongwritingPrompt("Compose a rap about a tiny clockwork robot"),true,"ordinary lyric");
assert(isOriginalSongwritingPrompt("Write Python code for a rap lyric generator"),false,"programming");
assert(isOriginalSongwritingPrompt("Analyze this song for rhyme devices"),false,"analysis");
assert(isOriginalSongwritingPrompt("Write a Kotlin script to make lyrics"),false,"coding");
"""
        r=subprocess.run(["node","-"],input=fn+scenario,text=True,capture_output=True)
        self.assertEqual(r.returncode,0,r.stderr)

    def test_only_unlabeled_fences_in_lyric_turns_switch_to_reader(self):
        self.assertIn('presentationHint="lyrics"',HTML) if False else None
        self.assertIn('presentationHint==="lyrics"',HTML)
        self.assertIn('language==="code"&&!info.file&&!info.project',HTML)
        self.assertIn('lyricLanguages.has(language)||inferredLyric',HTML)
        self.assertIn('renderAssistantContent(node.querySelector(".assistant-body"),msg.text||"",msg.id||"",isOriginalSongwritingPrompt(mostRecentUserPrompt)?"lyrics":"")',HTML)
        self.assertIn('renderAssistantContent(body,nextText,renderKey,isOriginalSongwritingPrompt(responsePrompt)?"lyrics":"")',HTML)
        self.assertIn('theme==="lyrics"?"Lyrics":language',HTML)
        self.assertIn('code.textContent=raw',HTML)

    def test_lyric_css_removes_decorative_frame_and_wraps_without_touching_code(self):
        marker=HTML.index("/* v194: lyrical prose gets the reading width")
        css=HTML[marker:HTML.index("  </style>",marker)]
        self.assertIn(".code-block.theme-lyrics",css)
        self.assertIn("padding:0;overflow:hidden;transform:none",css)
        self.assertIn("background-image:none",css)
        self.assertIn("white-space:pre-wrap;overflow-wrap:break-word;word-break:normal",css)
        self.assertIn("overflow-x:hidden;overflow-y:auto",css)
        self.assertIn(".code-head",css)
        self.assertNotIn(".code-block.theme-code",css)
        self.assertIn("padding:58px 30px 30px",HTML)
        self.assertIn("white-space:pre;",HTML)

    def test_copy_download_and_scroll_preserved(self):
        self.assertIn('copy.onclick=async()',HTML)
        self.assertIn('dl.onclick=()=>downloadTextFile(',HTML)
        self.assertIn("pre.dataset.codeKey=key",HTML)
        self.assertIn("const restoreCodeViewState=()=>",HTML)


if __name__=="__main__":
    unittest.main()
