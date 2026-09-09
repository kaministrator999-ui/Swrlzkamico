from __future__ import annotations

import hashlib
import os
import unittest
from datetime import datetime, timezone
from unittest import mock

from api.online_evidence import (
    DerivedQuery,
    EvidenceError,
    OnlineEvidenceService,
    SafeFetchError,
    SafeFetcher,
    SearchHit,
    TransportResponse,
    build_grounded_payload,
    configured_evidence_service,
    derive_knowledge_query,
    evidence_configuration_status,
    resolve_public_https_url,
)


FIXED_TIME = datetime(2026, 9, 9, 12, 0, 0, tzinfo=timezone.utc)


def public_resolver(hostname: str, port: int):
    address = "93.184.216.34" if hostname != "private.example" else "10.0.0.7"
    return [(2, 1, 6, "", (address, port))]


class FixtureProvider:
    provider_id = "fixture-search"

    def __init__(self, hits):
        self.hits = hits
        self.queries = []

    def search(self, query: str, limit: int):
        self.queries.append((query, limit))
        return self.hits[:limit]


class OnlineEvidenceTests(unittest.TestCase):
    def test_runtime_configuration_is_disabled_and_has_no_provider_by_default(self):
        with mock.patch.dict(os.environ, {"SWRLZ_ONLINE_EVIDENCE_ENABLED": "false", "SWRLZ_ONLINE_EVIDENCE_PROVIDER": ""}, clear=False):
            status = evidence_configuration_status()
            self.assertFalse(status["available"])
            self.assertEqual(status["defaultMode"], "OFFLINE")
            self.assertTrue(status["noSilentFallback"])
            with self.assertRaises(EvidenceError) as raised:
                configured_evidence_service()
            self.assertEqual(raised.exception.code, "ONLINE_EVIDENCE_DISABLED")

    def test_query_uses_current_prompt_and_redacts_common_secrets(self):
        query = derive_knowledge_query(
            "Find current docs for me at person@example.com using sk-abcdefghijklmnopqrstuvwxyz123456",
        )
        self.assertNotIn("person@example.com", query.text)
        self.assertNotIn("sk-abcdefghijklmnopqrstuvwxyz", query.text)
        self.assertEqual(query.redaction_count, 2)
        self.assertEqual(query.sha256, hashlib.sha256(query.text.encode()).hexdigest())

    def test_query_fails_closed_when_only_sensitive_material_remains(self):
        with self.assertRaises(EvidenceError) as raised:
            derive_knowledge_query("person@example.com")
        self.assertEqual(raised.exception.code, "ONLINE_QUERY_EMPTY_AFTER_REDACTION")

    def test_url_policy_rejects_http_credentials_ports_and_private_dns(self):
        cases = (
            "http://example.com/",
            "https://user:pass@example.com/",
            "https://example.com/private?token=secret-value",
            "https://example.com:444/",
            "https://private.example/",
        )
        for url in cases:
            with self.subTest(url=url), self.assertRaises(SafeFetchError):
                resolve_public_https_url(url, public_resolver)

    def test_redirect_target_is_resolved_and_revalidated_before_second_fetch(self):
        calls = []

        def transport(resolved, timeout, max_bytes):
            del timeout, max_bytes
            calls.append(resolved.url)
            return TransportResponse(302, {"location": "https://private.example/secret"}, b"")

        fetcher = SafeFetcher(resolver=public_resolver, transport=transport, clock=lambda: FIXED_TIME)
        with self.assertRaises(SafeFetchError) as raised:
            fetcher.fetch("https://example.com/start")
        self.assertEqual(raised.exception.code, "EVIDENCE_ADDRESS_REJECTED")
        self.assertEqual(calls, ["https://example.com/start"])

    def test_html_fetch_is_bounded_and_strips_executable_elements(self):
        body = b"<html><head><title>Fixture title</title><script>steal()</script></head><body><h1>Verified heading</h1><form>ignore me</form><p>Useful evidence.</p></body></html>"

        def transport(resolved, timeout, max_bytes):
            del resolved, timeout, max_bytes
            return TransportResponse(200, {"content-type": "text/html; charset=utf-8"}, body)

        document = SafeFetcher(
            resolver=public_resolver,
            transport=transport,
            clock=lambda: FIXED_TIME,
        ).fetch("https://example.com/evidence#fragment")
        self.assertEqual(document.url, "https://example.com/evidence")
        self.assertEqual(document.title, "Fixture title")
        self.assertIn("Verified heading", document.text)
        self.assertIn("Useful evidence.", document.text)
        self.assertNotIn("steal", document.text)
        self.assertNotIn("ignore me", document.text)
        self.assertEqual(document.content_sha256, hashlib.sha256(body).hexdigest())

    def test_service_builds_lineage_receipt_and_skips_rejected_result(self):
        provider = FixtureProvider(
            [
                SearchHit("https://example.com/a", "Search title", "result-1"),
                SearchHit("https://private.example/hidden", "Rejected", "result-2"),
            ],
        )

        def transport(resolved, timeout, max_bytes):
            del timeout, max_bytes
            body = f"<html><title>Fetched</title><body>Evidence from {resolved.url}</body></html>".encode()
            return TransportResponse(200, {"content-type": "text/html"}, body)

        fetcher = SafeFetcher(resolver=public_resolver, transport=transport, clock=lambda: FIXED_TIME)
        query = derive_knowledge_query("What changed in the current documentation?")
        bundle = OnlineEvidenceService(provider, fetcher, clock=lambda: FIXED_TIME).collect(query)
        self.assertEqual(provider.queries, [(query.text, 5)])
        self.assertEqual(len(bundle.sources), 1)
        self.assertEqual(len(bundle.skipped), 1)
        receipt = bundle.receipt()
        self.assertEqual(receipt["contractId"], "swrlz_online_evidence_v1")
        self.assertEqual(receipt["sourceCount"], 1)
        self.assertEqual(receipt["retention"], "REQUEST_SCOPED_EPHEMERAL")
        self.assertFalse(receipt["trainingEligible"])
        self.assertRegex(receipt["bundleSha256"], r"^[a-f0-9]{64}$")

        payload = {
            "prompt": "What changed?",
            "responseDirective": "unchanged stable directive",
            "history": [{"role": "USER", "text": "prior"}],
        }
        grounded = build_grounded_payload(payload, bundle)
        self.assertEqual(grounded["responseDirective"], payload["responseDirective"])
        self.assertEqual(grounded["history"][:-1], payload["history"])
        self.assertEqual(grounded["history"][-1]["role"], "SYSTEM")
        self.assertIn("UNTRUSTED REFERENCE DATA", grounded["history"][-1]["text"])
        self.assertIn(bundle.sources[0].source_id, grounded["history"][-1]["text"])
        self.assertEqual(grounded["knowledgeReceipt"], receipt)


if __name__ == "__main__":
    unittest.main()
