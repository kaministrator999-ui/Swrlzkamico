"""§C adaptive multi-pass public research regressions, subject-agnostic."""
from __future__ import annotations

import ast
import copy
import unittest
from unittest.mock import patch

from api.adaptive_public_research_v1 import (
    should_research_public_explanation,
    plan_public_research,facet_coverage,adaptive_enrich,
    MAX_SEARCH_PASSES,
)
from api.research_evidence_envelope_v1 import build_envelope
from scripts.hf_chat_adaptive_research_v1 import (
    patch_selective, patch_envelope, MARKER,
)

QUESTION=("Explain how eclipses work, including lunar geometry, "
          "eclipse types, and eye safety.")
FIRST={
    "contractId":"swrlz-selective-evidence-v1",
    "resultCount":1,
    "evidence":[{
        "title":"NASA eclipse geometry",
        "url":"https://science.nasa.gov/eclipses/geometry/",
        "excerpt":"Lunar geometry and the alignment of Earth, Moon and Sun create eclipses.",
    }],
    "coverage":"references_unverified",
}
SECOND={
    "evidence":[
        {"title":"NASA eclipse types",
         "url":"https://science.nasa.gov/eclipses/types/",
         "snippet":"Solar eclipse types include total, partial and annular events."},
        {"title":"NASA eclipse eye safety",
         "url":"https://science.nasa.gov/eclipses/safety/",
         "snippet":"Eye safety matters: use approved solar viewing glasses."},
        {"title":"NASA eclipse geometry",
         "url":"https://science.nasa.gov/eclipses/geometry/",
         "snippet":"Lunar geometry is about lunar positions."},
    ],
}


def dummy_bounded(bundle,query="",max_items=10,max_chars=6500):
    result=[]
    for item in bundle.get("evidence",[])[:max_items]:
        text=item.get("snippet") or item.get("extract") or ""
        if text:
            result.append({"title":item["title"],"url":item["url"],
                           "excerpt":text,"referenceRole":item.get("referenceRole")})
    return {"contractId":"swrlz-selective-evidence-v1",
            "resultCount":len(result),"evidence":result}


class AdaptiveResearchTests(unittest.TestCase):
    def test_conservative_public_knowledge_trigger(self):
        yes=("Explain Diablo II.","Tell me about photosynthesis.",
             "How does nuclear fusion work?","What is Diablo II LoD?",
             "Describe advances in renewable energy.")
        no=("How are you?","Hello","Tell me a joke about cats",
            "Explain our project","Explain my medications",
            "How does this work?","Make me a cool webpage")
        for item in yes:self.assertTrue(should_research_public_explanation(item),item)
        for item in no:self.assertFalse(should_research_public_explanation(item),item)

    def test_plan_three_facet_queries_without_topic_hardcoding(self):
        plan=plan_public_research(QUESTION)
        self.assertEqual(len(plan["facets"]),3,plan)
        self.assertTrue(plan["complex"])
        self.assertTrue(all("eclipses" in query.lower() for query in plan["searchQueries"]))
        self.assertIn("eye safety",plan["searchQueries"][-1])
        self.assertFalse(plan_public_research("What are the moons of Mars?")["complex"])

    def test_lexical_coverage_does_not_claim_factual_verification(self):
        plan=plan_public_research(QUESTION)
        covered=facet_coverage(plan,FIRST)
        self.assertEqual(covered["covered"],["lunar geometry"])
        self.assertEqual(covered["missing"],["eclipse types","eye safety"])
        self.assertEqual(covered["coverageType"],
                         "topical_lexical_relevance_not_fact_verification")

    def test_researches_only_uncovered_topics_and_merges_real_source_cards(self):
        calls=[]
        def researcher(request):
            calls.append(request)
            return SECOND
        original={"prompt":QUESTION,"onlineContext":copy.deepcopy(FIRST)}
        updated,receipt=adaptive_enrich(
            original,{"phase":"RESEARCH_READY","reason":"explicit_research"},
            researcher,bounded_evidence=dummy_bounded)
        self.assertEqual(len(calls),1)
        self.assertEqual(calls[0]["prompt"],QUESTION)
        self.assertEqual(len(calls[0]["researchQueries"]),2)
        self.assertNotIn("history",calls[0])
        self.assertEqual(updated["onlineContext"]["resultCount"],3)
        self.assertEqual(updated["onlineContext"]["adaptiveResearch"]["passesAttempted"],2)
        self.assertEqual(updated["onlineContext"]["adaptiveResearch"]["facetsNeedingVerification"],[])
        self.assertEqual(updated["onlineContext"]["adaptiveResearch"]["coverageSemantics"],
                         "retrieved_text_relevance_only_not_verified_facts")
        self.assertEqual(original["onlineContext"]["resultCount"],1)
        self.assertEqual(receipt["sourceCount"],3)

    def test_stops_when_first_sources_cover_facets(self):
        evidence=dummy_bounded({"evidence":FIRST["evidence"]+SECOND["evidence"]},query=QUESTION)
        evidence["coverage"]="references_unverified"
        called=[]
        updated,route=adaptive_enrich(
            {"prompt":QUESTION,"onlineContext":evidence},
            {"phase":"RESEARCH_READY","reason":"explicit_research"},
            lambda request:called.append(request),
            bounded_evidence=dummy_bounded)
        self.assertEqual(called,[])
        self.assertEqual(updated["onlineContext"]["adaptiveResearch"]["passesAttempted"],1)

    def test_provider_failure_preserves_initial_evidence_and_marks_gaps(self):
        def broken(_request):
            raise TimeoutError("Search unavailable")
        updated,route=adaptive_enrich(
            {"prompt":QUESTION,"onlineContext":copy.deepcopy(FIRST)},
            {"phase":"RESEARCH_READY"},broken,bounded_evidence=dummy_bounded)
        self.assertEqual(updated["onlineContext"]["resultCount"],1)
        self.assertEqual(
            updated["onlineContext"]["adaptiveResearch"]["facetsNeedingVerification"],
            ["eclipse types","eye safety"])
        self.assertLessEqual(updated["onlineContext"]["adaptiveResearch"]["passesAttempted"],
                             MAX_SEARCH_PASSES)

    def test_verified_roster_and_simple_questions_are_unmodified(self):
        facts=copy.deepcopy(FIRST)
        facts["verifiedContext"]={"verification":"source_extracted_count_and_named_members"}
        output,route=adaptive_enrich(
            {"prompt":QUESTION,"onlineContext":facts},
            {"phase":"RESEARCH_READY"},
            lambda _r: (_ for _ in ()).throw(RuntimeError("should not search")),
            bounded_evidence=dummy_bounded)
        self.assertIs(output["onlineContext"],facts)
        simple="Research the moons of Mars"
        output,route=adaptive_enrich(
            {"prompt":simple,"onlineContext":copy.deepcopy(FIRST)},
            {"phase":"RESEARCH_READY"},
            lambda _r: (_ for _ in ()).throw(RuntimeError("should not search")),
            bounded_evidence=dummy_bounded)
        self.assertNotIn("adaptiveResearch",output["onlineContext"])

    def test_role_tagged_packet_exposes_gaps_not_private_thread_history(self):
        updated,_=adaptive_enrich(
            {"prompt":QUESTION,"history":[{"role":"user","text":"secret personal context"}],
             "onlineContext":copy.deepcopy(FIRST)},
            {"phase":"RESEARCH_READY"},
            lambda _q:SECOND,
            bounded_evidence=dummy_bounded)
        packet=build_envelope(updated)
        self.assertEqual(packet["research_process"]["passesAttempted"],2)
        self.assertEqual(packet["research_process"]["unresolvedEvidenceFacets"],[])
        self.assertIn("not a claim-verification",packet["research_process"]["coverageMeaning"])
        self.assertNotIn("secret personal context",str(packet))
        self.assertEqual(packet["research_results"]["claim_status"],
                         "retrieved_not_automatically_verified")

    def test_exact_source_append_and_envelope_patch_reject_repeats(self):
        baseline=(
            "from dataclasses import dataclass\n"
            "# swrlz-generic-public-research-wikipedia-fallback-v1\n"
            "@dataclass\nclass Decision:\n"
            "    action:str\n    reason:str\n    query:str=''\n"
            "def _normalized(x):return str(x)\n"
            "def bounded_evidence(*a,**k):return {}\n"
            "def historical_class_reference_pages(*a,**k):return []\n"
            "def choose_retrieval(prompt,*,has_evidence=False,has_attachment=False,"
            "source_change=False,private_context=False):\n"
            "    return Decision('direct','concept_or_conversation')\n"
            "def enrich_payload(payload,researcher,*,fetch_page=None,enabled=False):\n"
            "    return payload,{'phase':'DIRECT'}\n"
        ).encode()
        revised=patch_selective(baseline)
        self.assertIn(MARKER,revised.decode())
        ast.parse(revised.decode())
        with self.assertRaises(RuntimeError):patch_selective(revised)
        envelope=(
            "def build_envelope(bundle):\n"
            "    packet={'conversation_context':{}}\n"
            "    checked=None;verified=None\n"
            "    def _plain(x,n):return str(x)[:n]\n"
            "    if checked and isinstance(verified, dict):\n"
            "        packet[\"checked_findings\"] = {}\n"
            "    return packet\n"
        ).encode()
        staged=patch_envelope(envelope)
        ast.parse(staged.decode())
        self.assertIn("research_process",staged.decode())
        with self.assertRaises(RuntimeError):patch_envelope(staged)


if __name__=="__main__":
    unittest.main()
