"""Offline regression checks for §C's online song-lyric extraction.

Run with: PYTHONPATH=hf_space python -m unittest hf_space/test_online_lyric_extraction_fix.py
Tests use invented lyrics and local HTML fixtures; no external requests.
"""
from __future__ import annotations

import unittest
from unittest.mock import patch

from api import online_research
import online_tools


SUBJECT = '"Copper Lantern" by Demo Ensemble'
URL = "https://genius.com/demo-ensemble-copper-lantern-lyrics"
LYRIC_BODY = """Copper Lantern lyrics by Demo Ensemble
Lyrics
[Verse 1]
Copper lanterns guide the midnight train
We paint the window with a little rain
Follow me
Share the spark
Hey
We turn the dark into a weathered map
A quiet city has a secret clap
[Chorus]
Bring the light and hold the line
Every road can learn to shine
We cross the sky before the dawn
Our borrowed hour carries on
"""
DESCRIPTIVE_SNIPPET = (
    "Explore the music catalog, biography, concert schedule, merchandise, "
    "photographs, production credits, archives, interviews and festival appearances."
)


class OnlineLyricExtractionFixTests(unittest.TestCase):
    def test_ddg_html_accepts_href_before_class(self):
        html = (
            '<div class="result"><a href="https://example.org/song" '
            'class="result__a">Demo Ensemble Song Lyrics</a>'
            '<a class="result__snippet">Song page</a></div>'
        )
        with patch.object(online_research, "_validate_public_url", side_effect=lambda value: value):
            results, anchors = online_research._parse_ddg_html("demo song lyrics", html)
        self.assertEqual(anchors, 1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["url"], "https://example.org/song")

    def test_exact_lyric_search_retries_after_off_topic_provider(self):
        wrong=[{
            "title": "TechCrunch | Startup and Technology News",
            "url": "https://techcrunch.com/",
            "snippet": "Startup news and the latest technology reporting",
        }]
        right=[{
            "title": "Demo Ensemble - Copper Lantern Lyrics",
            "url": URL,
            "snippet": "Demo Ensemble song lyrics",
        }]
        with patch.object(online_research,"_provider_attempt",side_effect=[wrong,right]) as visit:
            results=online_research._ddg_search('"Copper Lantern" "Demo Ensemble" lyrics')
        self.assertEqual(visit.call_count,2)
        self.assertEqual([item["url"] for item in results],[URL])

    def test_generic_search_does_not_apply_song_identity_filter(self):
        unrelated=[{
            "title": "TechCrunch | Startup and Technology News",
            "url": "https://techcrunch.com/",
            "snippet": "Startup and technology news",
        }]
        with patch.object(online_research,"_provider_attempt",return_value=unrelated) as visit:
            results=online_research._ddg_search("latest startup technology news")
        self.assertEqual(visit.call_count,1)
        self.assertEqual(results,unrelated)

    def test_dom_lyric_container_preserves_lines_without_chrome(self):
        page = """<html><body>
        <nav>Privacy Policy Subscribe To Updates</nav>
        <script>const stolen = 'not a lyric';</script>
        <div data-lyrics-container="true"><span>[Verse 1]</span><br>
          Copper lanterns guide the midnight train<br>Follow me<br>Hey<br>
          We paint the window with a little rain<br>
        </div>
        <div class="lyrics"><span>[Chorus]</span><br>
          Bring the light and hold the line<br>Share the spark<br>
          Every road can learn to shine<br>Our borrowed hour carries on<br>
        </div>
        <footer>Related songs and comments</footer></body></html>"""
        result = online_research._lyric_dom_text(page)
        self.assertRegex(result, r"\[Verse 1\]\s*\n\s*Copper lanterns guide")
        self.assertIn("\nHey\n", result)
        self.assertRegex(result, r"\[Chorus\]\s*\n\s*Bring the light")
        self.assertNotIn("Privacy Policy", result)
        self.assertNotIn("Related songs", result)
        self.assertNotIn("const stolen", result)
        self.assertEqual(online_research._lyric_dom_text("<div>Only site navigation</div>"), "")

    def test_lyric_verifier_preserves_short_and_natural_lines(self):
        analysis = online_tools._lyrics_extract_analysis(LYRIC_BODY, "full-lyrics", SUBJECT)
        self.assertEqual(analysis["diagnostics"]["decision"], "ACCEPTED", analysis["diagnostics"])
        lyric = analysis["text"]
        for phrase in ("Follow me", "Share the spark", "Hey", "[Verse 1]", "[Chorus]"):
            if phrase.startswith("["):
                self.assertNotIn(phrase, lyric)
            else:
                self.assertIn(phrase, lyric)
        self.assertGreaterEqual(len(lyric.splitlines()), 10)

    def test_lyric_page_feedback_and_recommendations_are_not_verses(self):
        page = (
            "Copper Lantern Lyrics by Demo Ensemble\nLyrics\n"
            "Copper lanterns guide the midnight train\n"
            "We paint the window with a little rain\n"
            "I carry the light past the gate\n"
            "The train comes in a little late\n"
            "The road is quiet in the dawn\n"
            "We keep the lantern burning on\n"
            "The morning lights the other shore\n"
            "The lantern shines a little more\n"
            "Are these lyrics accurate?\nLooks right\nNeeds a fix\n"
            "Previous track\nAnother song\nAnother artist\n"
        )
        analysis = online_tools._lyrics_extract_analysis(page, "full-lyrics", SUBJECT)
        lyric = analysis["text"]
        self.assertNotIn("Looks right", lyric, analysis["diagnostics"])
        self.assertNotIn("Previous track", lyric, analysis["diagnostics"])
        self.assertNotIn("Are these lyrics accurate?", lyric)
        self.assertEqual(analysis["diagnostics"]["terminalBoundaryKind"], "HARD_BOUNDARY")

    def _bundle(self, *, page_title: str, url: str):
        return {
            "provider": "offline-fixture",
            "researchId": "research:lyrics-fix-test",
            "errors": [],
            "candidatePool": [],
            "fetchFailures": [],
            "evidence": [{
                "evidenceId": "e1",
                "title": page_title,
                "pageTitle": page_title,
                "url": url,
                "finalUrl": url,
                "snippet": DESCRIPTIVE_SNIPPET,
                "extract": LYRIC_BODY,
                "fetchedAt": 1793650000000,
                "status": 200,
                "source": "genius.com",
                "query": "Copper Lantern Demo Ensemble lyrics",
                "rank": 1,
            }],
        }

    def _lookup(self, title: str, url: str):
        plan = {
            "query": "Copper Lantern Demo Ensemble lyrics",
            "contentMode": "lyrics-verification",
            "requestedScope": "full-lyrics",
            "subject": SUBJECT,
        }
        bundle = self._bundle(page_title=title, url=url)
        with (
            patch.object(online_tools, "run_online_research", return_value=bundle),
            patch.object(online_tools.canonical_online_research, "search_public", return_value=[]),
        ):
            return online_tools._search_bundle(plan)

    def test_verified_song_body_not_rejected_by_unrelated_metadata_snippet(self):
        result = self._lookup(
            "Copper Lantern Lyrics by Demo Ensemble",
            URL,
        )
        context = result["modelContext"]
        self.assertIsNotNone(context.get("verifiedLyrics"), context.get("lyricsSourceAttempts"))
        self.assertEqual(context["lyricsSourceAttempts"][0]["outcome"], "VERIFIED")

    def test_primary_lyric_research_quotes_song_and_artist(self):
        plan={
            "query": "who do I catch tech n9ne lyrics",
            "contentMode": "lyrics-verification",
            "requestedScope": "full-lyrics",
            "subject": '"Who Do I Catch" by Tech N9ne',
        }
        with (
            patch.object(online_tools,"run_online_research",return_value={
                "provider": "offline-fixture", "evidence": [],
                "candidatePool": [], "fetchFailures": [], "errors": [],
            }) as research,
            patch.object(online_tools.canonical_online_research,"search_public",return_value=[]),
        ):
            online_tools._search_bundle(plan)
        payload=research.call_args.args[0]
        self.assertIn('"Who Do I Catch"',payload["prompt"])
        self.assertIn('"Tech N9ne"',payload["prompt"])
        self.assertEqual(payload["researchQueries"],[payload["prompt"]])

    def test_unrelated_result_never_shown_as_lyric_source(self):
        bundle=self._bundle(
            page_title="TechCrunch | Startup and Technology News",
            url="https://techcrunch.com/",
        )
        plan={
            "query": "Copper Lantern Demo Ensemble lyrics",
            "contentMode": "lyrics-verification",
            "requestedScope": "full-lyrics",
            "subject": SUBJECT,
        }
        with (
            patch.object(online_tools,"run_online_research",return_value=bundle),
            patch.object(online_tools.canonical_online_research,"search_public",return_value=[]),
        ):
            result=online_tools._search_bundle(plan)
        self.assertEqual(result["status"],"NO_RESULTS")
        self.assertEqual(result["resultCount"],0)
        self.assertEqual(result["widgets"],[])
        self.assertEqual(result["sources"],[])
        self.assertEqual(result["modelContext"]["evidence"],[])
        self.assertEqual(result["modelContext"]["unrelatedSearchResultsExcluded"],1)

    def test_wrong_song_stays_rejected_even_with_structured_verse(self):
        result = self._lookup(
            "Another Tune Lyrics by Different Performer",
            "https://example.org/different-performer-another-tune-lyrics",
        )
        self.assertIsNone(result["modelContext"].get("verifiedLyrics"))
        attempts = result["modelContext"].get("lyricsSourceAttempts") or []
        self.assertTrue(attempts)
        self.assertEqual(attempts[0]["outcome"], "REJECTED")


if __name__ == "__main__":
    unittest.main()
