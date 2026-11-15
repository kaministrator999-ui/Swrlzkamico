"""§C role-tagged public evidence and visible source receipts regressions."""
from __future__ import annotations

import ast
import json
import unittest

from api.research_evidence_envelope_v1 import (
    CONTRACT, _sources, build_envelope, source_trace_events,
)
from scripts.hf_chat_tagged_research_evidence_v1 import patch_engine, patch_ui, MARKER

BUNDLE={
    "contractId":"swrlz-selective-evidence-v1",
    "resultCount":3,
    "evidence":[
        {"title":"Blizzard original class FAQ",
         "url":"https://classic.battle.net/diablo2exp/faq/general.shtml",
         "excerpt":"Five original classes in Diablo II: Amazon, Barbarian, Necromancer, Paladin, Sorceress.",
         "referenceRole":"historical_original_class_roster"},
        {"title":"Blizzard expansion class retrospective",
         "url":"https://news.blizzard.com/en-us/article/example",
         "excerpt":"Two new classes in Lord of Destruction: Assassin and Druid.",
         "referenceRole":"historical_expansion_class_additions"},
        {"title":"Unverified blog speculation",
         "url":"https://example.org/research",
         "excerpt":"Questionable material not independently checked."},
    ],
    "verifiedContext":{
        "verification":"source_extracted_count_and_named_members",
        "scope":"expansion","subject":"Diablo II","total":7,
        "classes":["Amazon","Barbarian","Paladin","Necromancer",
                   "Sorceress","Assassin","Druid"],
        "evidence":[
            {"title":"Base","url":"https://classic.battle.net/diablo2exp/faq/general.shtml"},
            {"title":"Expansion","url":"https://news.blizzard.com/en-us/article/example"},
        ],
    },
}


class ResearchEnvelopeTests(unittest.TestCase):
    def test_model_packet_separates_roles_and_source_status(self):
        packet=build_envelope({
            "prompt":"What were all the classes in Diablo 2 LoD?",
            "history":[{"role":"user","text":"Secret private history is not a public source"}],
            "onlineContext":BUNDLE,
        })
        self.assertEqual(packet["schema"],CONTRACT)
        self.assertEqual(packet["current_user_request"]["role"],"user_instruction")
        self.assertEqual(packet["conversation_context"]["role"],"prior_thread_messages")
        self.assertFalse(packet["conversation_context"]["copied_private_history"])
        self.assertEqual(packet["research_results"]["role"],"untrusted_external_source_data")
        sources=packet["research_results"]["sources"]
        self.assertEqual(len(sources),3)
        self.assertEqual([card["id"] for card in sources],["S1","S2","S3"])
        self.assertEqual(sources[0]["claim_status"],"supports_checked_roster_membership")
        self.assertEqual(sources[1]["claim_status"],"supports_checked_roster_membership")
        self.assertEqual(sources[2]["claim_status"],"retrieved_not_claim_verified")
        self.assertEqual(packet["checked_findings"]["total"],7)
        self.assertNotIn("Secret private history",json.dumps(packet))

    def test_poor_evidence_is_retrieved_not_verified(self):
        item={
            "contractId":"swrlz-selective-evidence-v1",
            "evidence":BUNDLE["evidence"],
            "verifiedContext":{"verification":"guessed_by_model",
                               "evidence":BUNDLE["verifiedContext"]["evidence"]},
        }
        packet=build_envelope({"prompt":"list the classes","onlineContext":item})
        self.assertNotIn("checked_findings",packet)
        self.assertTrue(all(s["claim_status"]=="retrieved_not_claim_verified"
                            for s in packet["research_results"]["sources"]))
        events=list(source_trace_events(item))
        self.assertTrue(all(e["trace"]["phase"]=="RESEARCH_SOURCE_RETRIEVED" for e in events))

    def test_trace_events_have_public_source_urls_and_no_private_history(self):
        trace=list(source_trace_events(BUNDLE))
        self.assertEqual(len(trace),3)
        self.assertEqual(trace[0]["type"],"ONLINE_TRACE")
        self.assertEqual(trace[0]["trace"]["phase"],"RESEARCH_SOURCE_CHECKED")
        self.assertEqual(trace[-1]["trace"]["phase"],"RESEARCH_SOURCE_RETRIEVED")
        self.assertTrue(trace[0]["trace"]["url"].startswith("https://"))
        self.assertNotIn("history",json.dumps(trace).lower())
        self.assertNotIn("user_request",json.dumps(trace).lower())

    def test_external_invalid_url_is_ignored_and_size_limits_hold(self):
        sources=[
            {"url":"javascript:alert(1)","title":"Bad","excerpt":"malicious"},
            {"url":"https://user:pw@example.com/","title":"Credentials","excerpt":"bad"},
            {"url":"http://example.com/","title":"Plain text","excerpt":"not TLS"},
            {"url":"https://example.org:"+str(65530),"title":"Port","excerpt":"bad"},
        ]+[{"url":"https://example.org/"+str(n),
             "title":"Result "+str(n),"excerpt":"word "*700}
            for n in range(18)]
        bundle={"contractId":"swrlz-selective-evidence-v1","evidence":sources}
        packet=build_envelope({"prompt":"Research the options","onlineContext":bundle},
                              max_json_chars=3800)
        self.assertIsNotNone(packet)
        self.assertLessEqual(len(json.dumps(packet,ensure_ascii=False,separators=(",",":"))),3800)
        self.assertLessEqual(len(packet["research_results"]["sources"]),8)
        self.assertEqual(len(_sources(bundle)),8)
        self.assertTrue(all(item["url"].startswith("https://example.org/")
                            for item in _sources(bundle)))

    def test_empty_source_packet_is_not_invented(self):
        for payload in ({},{"prompt":"Hello"},{
            "prompt":"Research a thing","onlineContext":{
                "contractId":"other","evidence":BUNDLE["evidence"]}},{
            "prompt":"Research a thing","onlineContext":{
                "contractId":"swrlz-selective-evidence-v1","evidence":[]}}):
            self.assertIsNone(build_envelope(payload))
        self.assertEqual(list(source_trace_events(None)),[])

    def test_engine_patch_preserves_existing_model_entrypoints(self):
        base=(
            "import os\n"
            "def generate_events(payload):\n"
            "    # swrlz-selective-factual-retrieval-v1: no web search unless owner enables.\n"
            "    payload, _research_route = enrich_payload(payload,None)\n"
            "    prompt=str(payload.get(\"prompt\") or \"\").strip()\n"
            "    if not prompt: raise ValueError(\"Empty prompt\")\n"
            "    online_context=payload.get(\"onlineContext\") if isinstance(payload.get(\"onlineContext\"),dict) else {}\n"
            "    if online_context:\n"
            "        system+=(\"ONLINE EXTERNAL EVIDENCE\"+\"ONLINE EVIDENCE RULES\")\n"
            "    temporal=payload.get(\"temporalContext\") if isinstance(payload.get(\"temporalContext\"),dict) else {}\n"
            "    yield {'type':'COMPLETED'}\n"
            "# swrlz-evidence-checked-factual-response-v1\n"
            "# swrlz-verified-public-enumerations-v2\n"
            "def later(payload):\n"
            "    from api.online_research import research as _research_v2, _page_fetch as _safe_page_fetch_v2\n"
            "    try:\n"
            "        enriched,route=_enrich_public_v2(payload,_research_v2,\n"
            "                                         fetch_page=_safe_page_fetch_v2,enabled=True)\n"
            "    except Exception:\n"
            "        return\n"
            "    bundle=enriched.get(\"onlineContext\") or {}\n"
            "    yield {\"type\":\"STATUS\",\"phase\":\"RESEARCH_READY\","
            "\"reason\":\"Fetched\"}\n"
        ).encode()
        staged=patch_engine(base).decode()
        ast.parse(staged)
        self.assertIn("RESEARCH EVIDENCE PACKET",staged)
        self.assertIn("source_trace_events",staged)
        self.assertIn("RESEARCH_STARTED",staged)
        self.assertIn("source_extracted_count_and_named_members",CONTRACT+" source_extracted_count_and_named_members")
        with self.assertRaises(RuntimeError):patch_engine(staged.encode())

    def test_ui_patch_uses_dom_text_not_html_and_avoids_duplicate_trail(self):
        base=(
            ".station-activity-note{color:#abc}\n"
            "    @keyframes station-pulse-v238{0%{opacity:1}}\n"
            "const renderActivityTimelineV238=()=>{\n"
            "          normalized.push({phase,reason,atUnixMs:Number.isFinite(atUnixMs)&&atUnixMs>0?atUnixMs:0});\n"
            "          wrapper.append(header,sub,details);\n"
            "        wrapper.__activityRows=events;\n"
            "};\n"
            "const onlineEvents=(Array.isArray(g.status)?g.status:[]).filter(item=>{\n"
            "          const phase=String(item?.phase||item?.type||\"\").toUpperCase();\n"
            "          const cats=Array.isArray(item?.categories)?item.categories.map(v=>String(v).toUpperCase()):[];\n"
        ).encode()
        output=patch_ui(base).decode()
        self.assertIn("Research results (",output)
        self.assertIn("textContent=titleText",output)
        self.assertIn("safeHttpUrl(item.url)",output)
        self.assertNotIn("innerHTML",output)
        self.assertIn("return false;",output)
        with self.assertRaises(RuntimeError):patch_ui(output.encode())


if __name__=="__main__":
    unittest.main()
