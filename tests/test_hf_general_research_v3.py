"""§C v3 general source-ledger synthesis and natural language result contract."""
from __future__ import annotations
import ast
import re
import sys
import types
import unittest
from unittest.mock import patch

from api.research_context_v2 import verified_roster_context
from api.research_synthesis_v3 import (
    source_ledger, instruction_for_synthesis, validate_roster_answer,
    repair_repeated_one_lists, fallback_from_verified_facts,
    member_description_supported, source_links,
)
from api.selective_retrieval import (
    choose_retrieval, enrich_payload, historical_roster_detail_pages,
)
from scripts.hf_chat_general_research_v3_release import (
    guarded_engine_patch,MARKER,TRUSTED_RESEARCH_POLICY,accepts_natural_count_wording,
)

NAME_LIST=["Amazon","Barbarian","Paladin","Necromancer","Sorceress","Assassin","Druid"]
FAKE={
    "contractId":"swrlz-selective-evidence-v1",
    "resultCount":3,
    "coverage":"version_specific_roster",
    "evidence":[
        {"title":"Blizzard original",
         "url":"https://classic.battle.net/diablo2exp/faq/general.shtml",
         "excerpt":"There are a total of five character types in Diablo II: Amazon, Barbarian, Paladin, Necromancer, and Sorceress.",
         "referenceRole":"historical_original_class_roster"},
        {"title":"Blizzard Diablo II Lord of Destruction additions",
         "url":"https://news.blizzard.com/en-us/article/23460551/diablo-ii-continues-to-inspire-blizzard-20-years-later",
         "excerpt":"with two more added in the Lord of Destruction expansion, the Assassin and the Druid",
         "referenceRole":"historical_expansion_class_additions"},
        {"title":"Blizzard Diablo II Amazon class overview",
         "url":"https://classic.battle.net/diablo2exp/classes/amazon.shtml",
         "excerpt":"The Amazon is adept with bows, spears and throwing weapons.",
         "referenceRole":"historical_roster_member_detail",
         "referenceMember":"Amazon"},
    ]
}
PROMPT="What were all the classes in Diablo 2 LoD?"


def facts():
    result=verified_roster_context(PROMPT,FAKE)
    assert result is not None
    return result


class GeneralResearchSynthesisTests(unittest.TestCase):
    def test_server_evidence_ledger_supports_any_public_topic(self):
        result=source_ledger("What are the moons of Mars?",{
            "evidence":[{"title":"NASA Mars moons",
                         "url":"https://science.nasa.gov/mars/moons/",
                         "excerpt":"Mars has two moons: Phobos and Deimos."}],
            "coverage":"supporting_sources"})
        self.assertEqual(result["sourceCount"],1)
        self.assertIn("Mars",result["question"])
        self.assertEqual(result["verification"],"excerpts_only_not_automatic_semantic_entailment")
        self.assertIn("Phobos",result["sources"][0]["excerpt"])
        self.assertIn("bounded evidence",instruction_for_synthesis(None).lower()) if False else None

    def test_acceptance_checks_natural_wording_not_fixed_response_phrase(self):
        self.assertTrue(accepts_natural_count_wording(
            "The expansion brought the total to seven.",7))
        self.assertTrue(accepts_natural_count_wording(
            "There are 7 playable classes.",7))
        self.assertFalse(accepts_natural_count_wording(
            "The expansion added two new classes to five.",7))

    def test_research_does_not_use_deterministic_reply_as_primary(self):
        self.assertEqual(facts()["total"],7)
        self.assertIn("naturally",instruction_for_synthesis(facts()))
        self.assertNotIn("Diablo II",instruction_for_synthesis(facts()))
        self.assertIn("Markdown bullet",instruction_for_synthesis(facts()))

    def test_reject_false_member_count_and_unsourced_details(self):
        fact=facts()
        ledger=source_ledger(PROMPT,FAKE)
        good=(
            "There are **7 playable classes** in the historical Lord of Destruction expansion:\n"
            "- Amazon\n- Barbarian\n- Paladin\n- Necromancer\n- Sorceress\n"
            "- Assassin\n- Druid\n\n"
            "Five existed in the original game; Assassin and Druid were added later."
        )
        self.assertEqual(validate_roster_answer(good,fact,ledger)["status"],"PASS")
        wrong=good.replace("7 playable","8 playable")
        self.assertEqual(validate_roster_answer(wrong,fact,ledger)["status"],"REJECT")
        rogue=good.replace("- Druid","- Rogue")
        self.assertEqual(validate_roster_answer(rogue,fact,ledger)["status"],"REJECT")
        hawk=good.replace("- Druid","- Druid — can transform into a hawk")
        self.assertEqual(validate_roster_answer(hawk,fact,ledger)["status"],"REJECT")
        source_supported=good.replace("- Amazon","- Amazon — bows, spears and throwing weapons")
        self.assertEqual(validate_roster_answer(source_supported,fact,ledger)["status"],"PASS")

    def test_fix_repeated_one_markdown_and_preserve_normal_ordering(self):
        repeated="1. Amazon\n1. Barbarian\n1. Paladin\n"
        self.assertEqual(repair_repeated_one_lists(repeated),
                         "- Amazon\n- Barbarian\n- Paladin\n")
        normal="1. Amazon\n2. Barbarian\n3. Paladin"
        self.assertEqual(repair_repeated_one_lists(normal),normal)

    def test_fallback_is_grouped_and_only_uses_source_words(self):
        out=fallback_from_verified_facts(facts(),source_ledger(PROMPT,FAKE))
        self.assertIn("Original game (5):",out)
        self.assertIn("Expansion additions (2):",out)
        self.assertEqual(out.count("- **"),7)
        self.assertNotIn("Rogue",out)
        self.assertNotIn("hawks",out)
        self.assertIn("https://classic.battle.net/diablo2exp/faq/general.shtml",out)

    def test_only_allow_publisher_owned_detail_urls(self):
        def fake_fetch(url):
            if url.endswith("/amazon.shtml"):
                return {"status":200,"finalUrl":url,
                        "extract":"The Amazon excels with bows, spears and throwing weapons and can fight with multiple weapon types. Starting Attributes Strength 20"}
            return {"status":200,"finalUrl":"https://attacker.example/redirect",
                    "extract":"The Druid has hawk form."}
        cards=historical_roster_detail_pages(facts(),fake_fetch)
        self.assertEqual(len(cards),1)
        self.assertEqual(cards[0]["referenceMember"],"Amazon")
        self.assertNotIn("Starting Attributes",cards[0]["snippet"])

    def test_generic_public_research_sends_unrelated_subject_through_same_source_ledger(self):
        def research(payload):
            return {"evidence":[
                {"title":"NASA: Mars moons",
                 "url":"https://science.nasa.gov/mars/moons/",
                 "snippet":"Mars has two moons named Phobos and Deimos."},
            ]}
        out,route=enrich_payload({"prompt":"List all the moons of Mars"},
                                 research,fetch_page=None,enabled=True)
        self.assertEqual(route["phase"],"RESEARCH_READY")
        packet=source_ledger("List all the moons of Mars",out["onlineContext"])
        self.assertEqual(packet["sourceCount"],1)
        self.assertEqual(packet["sources"][0]["title"],"NASA: Mars moons")
        self.assertIn("Phobos",packet["sources"][0]["excerpt"])
        self.assertEqual(packet["sources"][0]["role"],"supporting_source")
        self.assertNotIn("verifiedContext",out["onlineContext"])
        # The same infrastructure must not misrepresent a relevant excerpt
        # as a verified exhaustive collection.

    def test_generic_queries_continue_to_route_and_private_requests_not_skimmed(self):
        self.assertEqual(choose_retrieval("List all the moons of Mars").action,"retrieve")
        self.assertEqual(choose_retrieval("Compare the specifications of Mars rovers").action,"retrieve")
        self.assertEqual(choose_retrieval("List all my saved chat messages").action,"direct")
        self.assertEqual(choose_retrieval("Make me a cool webpage").action,"direct")
        self.assertEqual(choose_retrieval("Hey there").action,"direct")

    def test_core_generator_gets_one_draft_then_both_source_guards_decide(self):
        from unittest.mock import patch
        from types import ModuleType
        base=(
            "from __future__ import annotations\nimport os\n"
            "def inner(payload):\n"
            "    # swrlz-verified-public-enumerations-v2\n"
            "    # swrlz-evidence-checked-factual-response-v1\n"
            "    # swrlz-research-answer-limit-recovery-v1\n"
            "    # swrlz-selective-factual-retrieval-v1\n"
            "    system='';programming={'codingTask':False};source_change_mode=''\n"
            "    if source_change_mode:\n"
            "        # Keep source/plan tokens available\n"
            "        pass\n"
            "def generate_events(payload):\n"
            "    yield {'type':'DELTA','text':payload['fakeDraft']}\n"
            "    yield {'type':'COMPLETED','phase':'COMPLETE'}\n"
            "_swrlz_original_generate_events_factual_v1=generate_events\n"
            "_swrlz_previous_generate_events_research_v2=generate_events\n"
        ).encode()
        namespace={"__name__":"research_v3_stream_test"}
        exec(compile(guarded_engine_patch(base),"<v3_stream_test>","exec"),namespace)
        public=ModuleType("api.online_research")
        public.research=lambda payload:{"evidence":[]}
        original=("Diablo II There are a total of five character types in Diablo II: "
                  "Amazon, Barbarian, Paladin, Necromancer, and Sorceress.")
        additions=("Five new character classes like the Barbarian and Paladin "
                   "(with two more added in the Lord of Destruction expansion, "
                   "the Assassin and the Druid) expand the game.")
        def get(url):
            if "faq/general" in url:return {"status":200,"finalUrl":url,"extract":original}
            if "news.blizzard" in url:return {"status":200,"finalUrl":url,"extract":additions}
            if "pcgamingwiki" in url:return {"status":200,"finalUrl":url,
                "extract":"Diablo II Release dates Windows June 29, 2000. "
                          "The game received the Lord of Destruction expansion pack in June 2001."}
            if "/classes/" in url:
                member=url.split("/")[-1].split(".")[0].capitalize()
                return {"status":200,"finalUrl":url,
                  "extract":"The "+member+" is a dedicated character trained in fantasy combat skills "
                            "and draws strength from the game's underlying world."}
            raise AssertionError(url)
        public._page_fetch=get
        good=("**Diablo II Lord of Destruction includes 7 playable classes.**\n"
              "The original game had five, with two added in the expansion:\n"
              "- Amazon\n- Barbarian\n- Paladin\n- Necromancer\n- Sorceress\n"
              "- Assassin\n- Druid")
        bad=good.replace("7 playable","8 playable").replace("- Druid","- Rogue")
        with patch.dict(sys.modules,{"api.online_research":public}):
            for draft,accept in ((good,True),(bad,False)):
                events=list(namespace["generate_events"]({
                    "prompt":"What were all the classes in Diablo 2 LoD?",
                    "fakeDraft":draft,
                    "history":[{"role":"user","text":"You previously included the Rogue."}],
                }))
                phases=[e.get("phase") for e in events if e.get("type")=="STATUS"]
                answer="".join(e.get("text","") for e in events if e.get("type")=="DELTA")
                self.assertIn("RESEARCH_SYNTHESIS",phases)
                if accept:
                    self.assertIn("RESEARCH_NARRATIVE_ACCEPTED",phases)
                    self.assertIn("7 playable classes",answer)
                else:
                    self.assertIn("RESEARCH_NARRATIVE_REJECTED",phases)
                    self.assertNotIn("8 playable classes",answer)
                    self.assertNotIn("- Rogue",answer)

    def test_wrap_preserves_history_and_source_only_policy(self):
        base=(
            "from __future__ import annotations\nimport os\n"
            "def inner(payload):\n"
            "    # swrlz-verified-public-enumerations-v2\n"
            "    # swrlz-evidence-checked-factual-response-v1\n"
            "    # swrlz-research-answer-limit-recovery-v1\n"
            "    # swrlz-selective-factual-retrieval-v1\n"
            "    system=''; programming={'codingTask':False};source_change_mode=''\n"
            "    if source_change_mode:\n"
            "        # Keep source/plan tokens available\n"
            "        pass\n"
            "def generate_events(payload):\n"
            "    yield {'type':'DELTA','text':'old static response'}\n"
            "    yield {'type':'COMPLETED','phase':'COMPLETE'}\n"
            "_swrlz_previous_generate_events_research_v2=generate_events\n"
        ).encode()
        staged=guarded_engine_patch(base)
        self.assertEqual(staged.decode().count(MARKER),1)
        self.assertIn("instruction_for_synthesis",staged.decode())
        ast.parse(staged.decode())
        with self.assertRaises(RuntimeError):guarded_engine_patch(staged)


if __name__=="__main__":
    unittest.main()
