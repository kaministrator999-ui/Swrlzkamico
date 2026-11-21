"""§C v2 source-grounded enumeration and version-scope regression suite."""
from __future__ import annotations

import ast
import re
import sys
import types
import unittest
from unittest.mock import patch

from api.research_context_v2 import (
    normalize_prompt, needs_factual_research, request_scope,
    extract_original_roster, extract_expansion_additions,
    verified_roster_context, grounded_roster_reply,
)
from api.selective_retrieval import (
    choose_retrieval, enrich_payload, historical_class_reference_pages,
)
from scripts.hf_chat_research_context_v2_release import (
    guarded_engine_patch, MARKER,
)

ORIGINAL = ("Diablo II There are a total of five character types in Diablo II: "
            "Amazon, Barbarian, Paladin, Necromancer, and Sorceress.")
EXPANSION = ("Five new character classes like the whirling Barbarian and pious Paladin "
             "(with two more added in the Lord of Destruction® expansion, "
             "the Assassin and the Druid) expanded far beyond the original game.")
PUBLIC_URLS=(
    "https://classic.battle.net/diablo2exp/faq/general.shtml",
    "https://news.blizzard.com/en-us/article/23460551/"
    "diablo-ii-continues-to-inspire-blizzard-20-years-later",
)


def fetch_public(url):
    if url==PUBLIC_URLS[0]:
        return {"status":200,"finalUrl":url,"extract":ORIGINAL}
    if url==PUBLIC_URLS[1]:
        return {"status":200,"finalUrl":url,"extract":EXPANSION}
    raise AssertionError("Unexpected public page: "+url)


class ResearchContextTests(unittest.TestCase):
    def test_short_enumeration_routes_to_research(self):
        for prompt in (
            "What where all the classes in diablo 2 lod?",
            "How many classes were in Diablo II Lord of Destruction?",
            "List all classes in Diablo II Classic.",
            "What are all the moons of Mars?",
        ):
            self.assertTrue(needs_factual_research(prompt),prompt)
            route=choose_retrieval(prompt)
            self.assertEqual(route.action,"retrieve",prompt)
        self.assertIn("Diablo II",normalize_prompt("diablo 2 lod"))
        self.assertIn("Lord of Destruction",normalize_prompt("diablo 2 lod"))

    def test_preserve_private_and_nonresearch_turns(self):
        for prompt in (
            "List all my chats.",
            "What are all our projects?",
            "Make me a cool webpage.",
            "Hello, §wyrlz!",
            "Give me all the classes we designed in our repo",
        ):
            self.assertEqual(choose_retrieval(prompt).action,"direct",prompt)
        self.assertEqual(request_scope("Diablo 2 LoD")["scope"],"expansion")
        self.assertEqual(request_scope("Diablo 2 Classic")["scope"],"original")
        self.assertEqual(request_scope("Diablo II Resurrected")["scope"],"remaster")

    def test_parse_generic_count_and_two_additions_from_source_sentences(self):
        self.assertEqual(
            extract_original_roster(ORIGINAL,"Diablo II"),
            ["Amazon","Barbarian","Paladin","Necromancer","Sorceress"])
        self.assertEqual(
            extract_expansion_additions(EXPANSION,"Lord of Destruction"),
            ["Assassin","Druid"])
        self.assertEqual(extract_original_roster(
            "Mystic II There are a total of three character types in Mystic II: "
            "Guardian, Runner, and Mage.","Mystic II"),
            ["Guardian","Runner","Mage"])
        self.assertEqual(extract_original_roster(
            "Mystic II There are five character types in Mystic II: "
            "Guardian, Runner, and Mage.","Mystic II"),[])

    def test_first_party_edition_references_and_no_remaster_leakage(self):
        refs=historical_class_reference_pages(
            "What were all the classes in Diablo 2 LoD?",fetch_public)
        self.assertEqual(len(refs),2,refs)
        self.assertEqual(
            {r["referenceRole"] for r in refs},
            {"historical_original_class_roster",
             "historical_expansion_class_additions"})
        self.assertEqual(historical_class_reference_pages(
            "List all classes in Diablo II: Resurrected",fetch_public),[])
        self.assertEqual(historical_class_reference_pages(
            "List the classes in our Diablo II project",fetch_public),[])
        def wrong_host(url):
            return {"status":200,"finalUrl":"https://attacker.example/",
                    "extract":ORIGINAL+EXPANSION}
        self.assertEqual(historical_class_reference_pages(
            "What are all Diablo II LoD classes?",wrong_host),[])

    def test_verified_context_provenance_and_rendered_roster(self):
        prompt="What were all the classes in Diablo 2 LoD?"
        enriched,receipt=enrich_payload({"prompt":prompt},None,
                                        fetch_page=fetch_public,enabled=True)
        self.assertEqual(receipt["phase"],"RESEARCH_READY",receipt)
        self.assertEqual(receipt["coverage"],"version_specific_roster",receipt)
        bundle=enriched["onlineContext"]
        self.assertEqual(bundle["verifiedContext"]["total"],7)
        self.assertEqual(len(bundle["verifiedContext"]["evidence"]),2)
        reply=grounded_roster_reply(prompt,bundle)
        self.assertIn("7 playable classes",reply)
        for name in ("Amazon","Barbarian","Paladin","Necromancer",
                     "Sorceress","Assassin","Druid"):
            self.assertRegex(reply,r"\b"+name+r"\b")
        self.assertNotIn("Rogue",reply)
        self.assertNotIn("Warlock",reply)
        self.assertIn(PUBLIC_URLS[0],reply)
        self.assertIn(PUBLIC_URLS[1],reply)

    def test_classic_five_and_no_2026_remaster_conflation(self):
        prompt="What were all the classes in Diablo 2 Classic?"
        enriched,receipt=enrich_payload({"prompt":prompt},None,
                                        fetch_page=fetch_public,enabled=True)
        self.assertEqual(receipt["coverage"],"version_specific_roster")
        reply=grounded_roster_reply(prompt,enriched["onlineContext"])
        self.assertIn("5 playable classes",reply)
        self.assertNotIn("Assassin",reply)
        self.assertNotIn("Druid",reply)
        self.assertNotIn("Warlock",reply)

    def test_genuine_absent_evidence_is_not_guessed(self):
        prompt="What were all the classes in Diablo 2 LoD?"
        out,receipt=enrich_payload({"prompt":prompt},None,
            fetch_page=lambda u:{"status":404,"finalUrl":u,"extract":""},enabled=True)
        self.assertIn(receipt["phase"],("RESEARCH_UNAVAILABLE","RESEARCH_READY"))
        self.assertIsNone(grounded_roster_reply(prompt,out.get("onlineContext")))

    def test_no_history_or_code_capture(self):
        out,receipt=enrich_payload({"prompt":"What are all my past conversations?"},
            None,fetch_page=fetch_public,enabled=True)
        self.assertEqual(receipt["phase"],"DIRECT")
        out,receipt=enrich_payload({"prompt":"List all classes in Diablo 2 LoD",
                                    "githubSourceChangeTask":{"active":True}},
                                   None,fetch_page=fetch_public,enabled=True)
        self.assertEqual(receipt["phase"],"DIRECT")

    def test_wrapper_protects_new_and_old_routes(self):
        stub=(
            "from __future__ import annotations\nimport os\n"
            "def generate_events(payload):\n"
            "    # swrlz-evidence-checked-factual-response-v1\n"
            "    # swrlz-research-answer-limit-recovery-v1\n"
            "    # swrlz-selective-factual-retrieval-v1\n"
            "    yield {'type':'DELTA','text':'eight classes: Rogue'}\n"
            "    yield {'type':'COMPLETED','phase':'COMPLETE'}\n"
        ).encode()
        patched=guarded_engine_patch(stub)
        self.assertIn(MARKER,patched.decode())
        ast.parse(patched.decode())
        sandbox={"__name__":"swrlz_research_v2_stub"}
        exec(compile(patched,"<test_engine>","exec"),sandbox)
        public=types.ModuleType("api.online_research")
        public.research=lambda _payload:{"evidence":[]}
        public._page_fetch=fetch_public
        with patch.dict(sys.modules,{"api.online_research":public}):
            historical=list(sandbox["generate_events"]({
                "prompt":"What were all the classes in Diablo 2 LoD?"}))
            answer="".join(x.get("text","") for x in historical if x.get("type")=="DELTA")
            self.assertIn("7 playable classes",answer)
            self.assertNotIn("eight classes",answer)
            self.assertTrue(any(x.get("phase")=="RESEARCH_CONTEXT_CHECK" for x in historical))
            self.assertEqual(historical[-1]["verification"],"PRIMARY_SOURCE_ROSTER")
            casual=list(sandbox["generate_events"]({"prompt":"Hi!"}))
            self.assertIn("eight classes","".join(x.get("text","") for x in casual
                                                    if x.get("type")=="DELTA"))
            self.assertFalse(any(x.get("phase")=="RESEARCH_CONTEXT_CHECK" for x in casual))
        with self.assertRaises(RuntimeError):
            guarded_engine_patch(patched)


if __name__=="__main__":
    unittest.main()
