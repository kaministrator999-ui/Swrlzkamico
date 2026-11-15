"""Generic public-source fallback regressions for §C research provider outages."""
from __future__ import annotations
import ast
import json
import unittest
from urllib.parse import parse_qs,urlsplit

from api.generic_public_source_fallback_v1 import (
    wikipedia_public_fallback,search_terms,
)
from scripts.hf_chat_generic_public_fallback_v1 import (
    patch_retrieval,MARKER,OLD,
)

SUMMARY="The two moons of Mars are Phobos and Deimos. Both are irregularly shaped natural satellites of Mars."


def fetched(url):
    parsed=urlsplit(url)
    if parsed.path=="/w/rest.php/v1/search/page":
        topic=parse_qs(parsed.query).get("q",[""])[0]
        assert "moons" in topic.lower() and "mars" in topic.lower(),topic
        return {"status":200,"finalUrl":url,
                "extract":json.dumps({"pages":[
                    {"key":"Moons_of_Mars","title":"Moons of Mars",
                     "excerpt":"Mars has two moons: Phobos and Deimos."},
                    {"key":"List_of_missions_to_Mars","title":"List of missions to Mars",
                     "excerpt":"Space missions proposed to explore Phobos and Deimos."},
                    {"key":"A_Princess_of_Mars","title":"A Princess of Mars",
                     "excerpt":"A novel about Mars."},
                ]})}
    if parsed.path=="/api/rest_v1/page/summary/Moons_of_Mars":
        return {"status":200,"finalUrl":url,
                "extract":json.dumps({"type":"standard","title":"Moons of Mars",
                                       "extract":SUMMARY})}
    raise AssertionError("Unexpected public lookup: "+url)


class GenericPublicSourceFallbackTests(unittest.TestCase):
    def test_topic_normalization_is_about_question_not_fixed_diablo(self):
        self.assertEqual(search_terms(
            "Research: what are the moons of Mars? List their names."),
            "moons of Mars")
        self.assertEqual(search_terms(
            "List all the planets of the Solar System"),
            "planets of Solar System")
        self.assertEqual(search_terms(""),"")

    def test_retrieve_real_matched_summary_and_ignore_irrelevant_search_hits(self):
        cards=wikipedia_public_fallback(
            "Research: what are the moons of Mars? List their names.",fetched)
        self.assertEqual(len(cards),1,cards)
        self.assertIn("Moons of Mars",cards[0]["title"])
        self.assertIn("Phobos",cards[0]["snippet"])
        self.assertIn("Deimos",cards[0]["snippet"])
        self.assertEqual(cards[0]["url"],"https://en.wikipedia.org/wiki/Moons_of_Mars")
        self.assertEqual(cards[0]["referenceRole"],"retrieved_public_encyclopedia_summary")
        self.assertNotIn("Princess",cards[0]["title"])

    def test_reject_off_domain_redirect_and_bad_json(self):
        def hijack(url):
            v=fetched(url) if url.startswith("https://en.wikipedia.org/w/rest.php/") else None
            return v or {"status":200,"finalUrl":"https://attacker.example/",
                         "extract":json.dumps({"title":"Moons of Mars","extract":SUMMARY})}
        self.assertEqual(wikipedia_public_fallback("List moons of Mars",hijack),[])
        self.assertEqual(wikipedia_public_fallback("List moons of Mars",
            lambda url:{"status":200,"finalUrl":url,"extract":"not json"}),[])

    def test_disambiguation_not_treated_as_answer(self):
        def fake(url):
            response=fetched(url)
            if "/api/rest_v1/page/summary/" in url:
                response={**response,"extract":json.dumps({
                    "type":"disambiguation","title":"Moons of Mars","extract":SUMMARY})}
            return response
        self.assertEqual(wikipedia_public_fallback("List moons of Mars",fake),[])

    def test_source_retrieval_patch_is_exact_and_bounded(self):
        original=("from __future__ import annotations\n"
                  "def bounded_evidence(*args,**kwargs): return {'resultCount':0}\n"
                  "def historical_class_reference_pages(x,y): return []\n"
                  "def enrich_payload(payload, researcher, fetch_page=None):\n"
                  "    out={}\n    decision=type('Decision',(),{'query':'Mars'})()\n"
                  "    references=[];searched=[]\n"
                  +OLD+"\n").encode()
        patched=patch_retrieval(original).decode()
        ast.parse(patched)
        self.assertIn(MARKER,patched)
        self.assertIn("wikipedia_public_fallback",patched)
        self.assertIn("if evidence[\"resultCount\"] == 0",patched)
        with self.assertRaises(RuntimeError):
            patch_retrieval(patched.encode())


if __name__=="__main__":
    unittest.main()
