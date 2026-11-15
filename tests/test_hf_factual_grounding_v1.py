"""§C public research claim-gate and source coverage regressions."""
import ast
import json
import sys
import types
import unittest

from api.factual_claim_guard_v1 import (
    inspect_answer, evidence_only_reply, sourced_answer,
)
from api.selective_retrieval import (
    enrich_payload, extended_reference_pages,
)
from scripts.hf_chat_factual_grounding_v1 import patch_engine, MARKER


BUNDLE = {
    "contractId":"swrlz-selective-evidence-v1",
    "resultCount":4,
    "evidence":[
        {"title":"Diablo II original game release dates",
         "url":"https://www.pcgamingwiki.com/wiki/Diablo_II",
         "excerpt":"Release dates Windows June 29, 2000."},
        {"title":"Diablo II Lord of Destruction expansion date",
         "url":"https://www.pcgamingwiki.com/wiki/Diablo_II",
         "excerpt":"The game received the Lord of Destruction expansion pack in June 2001."},
        {"title":"Blizzard: Diablo II Lord of Destruction history",
         "url":"https://news.blizzard.com/article",
         "excerpt":"The Lord of Destruction expansion was released in 2001. Two new character classes, Druid and Assassin."},
        {"title":"Diablo II: Lord of Destruction expansion features",
         "url":"https://www.gamespot.com/articles/diablo-ii-lord-of-destruction-goes-gold/1100-2779046/",
         "excerpt":"Lord of Destruction adds a new fifth act in the Barbarian Highlands."},
    ]
}

WRONG = """Yes, Diablo II: Resurrected (often referred to as Classic) was
released before Diablo II: Lord of Destruction.
* Diablo II: Resurrected: release date September 2023.
* Diablo II: Lord of Destruction: released December 2000 and January 2024
for the remaster.
The classic base game contains Acts I-III; the expansion adds Acts IV and V.
"""

CORRECT = """Yes. The original Diablo II was released in June 2000.
Lord of Destruction was released in June 2001 as its expansion,
adding two classes, the Druid and the Assassin, and a new fifth act.
The remaster, Diablo II: Resurrected, was not the original Classic version.
"""


class GroundingGuardTests(unittest.TestCase):
    def test_original_model_hallucination_rejected(self):
        verdict=inspect_answer(WRONG,BUNDLE)
        self.assertEqual(verdict["status"],"REJECT")
        self.assertTrue(any("2023" in r or "2024" in r for r in verdict["reasons"]))
        self.assertIn("unsupported_edition_equivalence",verdict["reasons"])
        self.assertTrue(any("unsupported_numbered_acts" in r for r in verdict["reasons"]))

    def test_supported_2000_2001_comparison_accepted(self):
        verdict=inspect_answer(CORRECT,BUNDLE)
        self.assertEqual(verdict["status"],"PASS",verdict)

    def test_correct_distinction_is_not_equivalence(self):
        reply="Diablo II Classic is not Diablo II: Resurrected; these are distinct releases."
        self.assertEqual(inspect_answer(reply,BUNDLE)["status"],"PASS")

    def test_unproven_years_are_rejected_even_with_relevant_titles(self):
        tiny={"contractId":"swrlz-selective-evidence-v1","resultCount":2,
              "evidence":[{"title":"Diablo II",
                           "url":"https://en.wikipedia.org/wiki/Diablo_II",
                           "excerpt":"Diablo II is a 2000 game."},
                          {"title":"Lord of Destruction",
                           "url":"https://en.wikipedia.org/wiki/Diablo_II:_Lord_of_Destruction",
                           "excerpt":"Lord of Destruction is an expansion for Diablo II."}]}
        report=inspect_answer("Lord of Destruction was released in 2001.",tiny)
        self.assertEqual(report["status"],"REJECT")
        self.assertIn("2001"," ".join(report["reasons"]))

    def test_source_fallback_is_explicit_and_attributed(self):
        text=evidence_only_reply("release date",BUNDLE)
        self.assertIn("couldn't verify",text)
        self.assertIn("https://www.pcgamingwiki.com/wiki/Diablo_II",text)
        self.assertNotIn("2023",text)

    def test_unrelated_chat_does_not_route_to_guard(self):
        self.assertFalse(sourced_answer({"prompt":"Hey, how's it going?"}))
        self.assertTrue(sourced_answer({"prompt":"release date",
                                         "onlineContext":BUNDLE}))
        self.assertFalse(sourced_answer({"prompt":"fix code",
                                          "githubSourceChangeTask":"candidate",
                                          "onlineContext":BUNDLE}))

    def test_source_coverage_extracts_subject_specific_years(self):
        urls=[]
        def fetch(url):
            urls.append(url)
            if "pcgamingwiki.com" in url:
                return {"status":200,"finalUrl":url,
                    "extract":("Diablo II Release dates Windows June 29, 2000. "
                               "Sidebar: Expansion pack Modes Diablo Diablo 1997. "
                               "The game received the Lord of Destruction expansion pack in June 2001. "
                               "The game was succeeded by Diablo II: Resurrected September 2021.")}
            if "news.blizzard.com" in url:
                return {"status":200,"finalUrl":url,
                    "extract":("Diablo II five new character classes like the Barbarian and "
                               "Lord of Destruction introduced the Druid and the Assassin. "
                               "Lord of Destruction expansion was released on June 21, 2001.")}
            if "gamespot.com" in url:
                return {"status":200,"finalUrl":url,
                    "extract":("Diablo II Lord of Destruction article: "
                               "the expansion adds a new fifth act with six quests, "
                               "a larger stash, the assassin and druid.")}
            raise AssertionError("Unneeded public fetch: "+url)
        prompt=("Was Diablo II Classic released before Lord of Destruction? "
                "Research both versions and explain the differences.")
        refs=extended_reference_pages(prompt,fetch)
        self.assertGreaterEqual(len(refs),3)
        self.assertTrue(any("2000" in r["snippet"] for r in refs))
        self.assertTrue(any("2001" in r["snippet"] for r in refs))
        actual_expansion=[r for r in refs if "expansion date" in r["title"]]
        self.assertEqual(len(actual_expansion),1)
        self.assertIn("The game received",actual_expansion[0]["snippet"])
        self.assertIn("2001",actual_expansion[0]["snippet"])
        self.assertNotIn("1997",actual_expansion[0]["snippet"])
        self.assertTrue(any("new fifth act" in r["snippet"] for r in refs))
        out,route=enrich_payload({"prompt":prompt},None,fetch_page=fetch,enabled=True)
        self.assertEqual(route["phase"],"RESEARCH_READY")
        self.assertTrue(sourced_answer(out))
        self.assertGreaterEqual(out["onlineContext"]["resultCount"],3)
        self.assertFalse(any("wikipedia.org" in u for u in urls),
                         "Avoid redundant generic lookup when dated source is sufficient")

    def test_safe_fetch_rejects_offsite_misdirection(self):
        def malicious(url):
            return {"status":200,"finalUrl":"https://attacker.example/test",
                    "extract":"Diablo II Release dates Windows June 29, 2000"}
        refs=extended_reference_pages("Was Diablo II released in 2000?",malicious)
        self.assertEqual(refs,[])

    def test_engine_wrapper_patches_valid_existing_source_only(self):
        synthetic=(
            'from __future__ import annotations\nimport os\n'
            'def generate_events(payload):\n'
            '    # swrlz-selective-factual-retrieval-v1\n'
            '    # swrlz-research-answer-limit-recovery-v1\n'
            '    yield {"type":"COMPLETED","phase":"COMPLETE"}\n'
        ).encode()
        code=patch_engine(synthetic).decode()
        ast.parse(code)
        self.assertEqual(code.count(MARKER),1)
        self.assertIn("FACTUAL_VERIFICATION_REJECT",code)
        with self.assertRaises(RuntimeError):
            patch_engine(code.encode())


if __name__ == "__main__":
    unittest.main()
