"""Focused §C Markdown ordered-list UI continuity tests."""
from __future__ import annotations
import subprocess
import unittest

from scripts.hf_chat_markdown_list_continuity_v1 import ORIGINAL,patched,MARKER,NEW

FIXTURE=(
    '<script>\n'
    'const closeList=()=>{list=null;listType="";};\n'
    'const line=rawLine.trimEnd(),heading=line.match(/^(#{1,6})\\s+(.+)$/),'
    'ordered=line.match(/^\\s*\\d+[.)]\\s+(.+)$/),'
    'unordered=line.match(/^\\s*[-*+]\\s+(.+)$/);\n'
    'if(ordered||unordered){const type=ordered?"ol":"ul";doSomething()}\n'
    +ORIGINAL+'\n'
    '</script>\n'
)


class MarkdownListContinuityTests(unittest.TestCase):
    def test_exact_source_patch_is_scoped_and_idempotent_guarded(self):
        candidate=patched(FIXTURE.encode()).decode()
        self.assertIn(MARKER,candidate)
        self.assertEqual(candidate.count(MARKER),1)
        self.assertEqual(candidate.count("const closeList="),1)
        with self.assertRaises(RuntimeError):
            patched(candidate.encode())

    def test_actual_blank_line_branch_preserves_numbering_across_spaced_items(self):
        # Execute the exact inserted UI source, not a reimplemented algorithm.
        snippet=NEW
        script=r"""
function countLists(input) {
  const lines=input.split("\n");
  let list=null,listType="",lists=0;
  const closeList=()=>{list=null;listType="";};
  const addParagraph=()=>{};
  for(let lineIndex=0;lineIndex<lines.length;lineIndex++) {
    const rawLine=lines[lineIndex];
    const line=rawLine.trimEnd();
    const ordered=line.match(/^\s*\d+[.)]\s+(.+)$/);
    const unordered=line.match(/^\s*[-*+]\s+(.+)$/);
    if(ordered||unordered) {
      const type=ordered?"ol":"ul";
      if(!list||listType!==type){list={};listType=type;lists++;}
      continue;
    }
    __EXACT_PATCH__
  }
  return lists;
}
const trials=[
  ["1. Amazon\n\n1. Barbarian\n\n1. Druid",1],
  ["1. Amazon\n\n2. Barbarian\n\n3. Druid",1],
  ["- Amazon\n\n- Barbarian\n\n- Druid",1],
  ["1. Amazon\n\nAn unrelated paragraph.\n\n1. Druid",2],
  ["1. Amazon\n\n- Barbarian",2],
];
for(const [value,expected] of trials) {
  const actual=countLists(value);
  if(actual!==expected)throw Error(JSON.stringify({value,expected,actual}));
}
console.log("SWRLZ_MARKDOWN_LISTS_CONTINUITY_PASS");
""".replace("__EXACT_PATCH__",snippet)
        result=subprocess.run(["node","-e",script],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn("SWRLZ_MARKDOWN_LISTS_CONTINUITY_PASS",result.stdout)


if __name__=="__main__":
    unittest.main()
