"""Local deterministic grader regressions for §C anonymous Chromium round 2."""
import unittest

from scripts.eval_chat_research_lyrics_conversations import CASES, ORIGINAL_TEST_LINES, check, failure_types


def fails(kind, body, prev=None):
    return [x["check"] for x in check(kind,body,prev)["checks"] if not x["pass"]]


class BroadGuestGraderTests(unittest.TestCase):
    def test_all_batches_have_unique_multi_turn_scenarios(self):
        self.assertEqual(set(CASES), {"research","songwriting","conversation","transformations","reasoning"})
        ids=[c["id"] for batch in CASES.values() for c in batch]
        self.assertEqual(len(ids),len(set(ids)))
        for cases in CASES.values():
            for case in cases:
                self.assertGreaterEqual(len(case["turns"]),2)
                for turn in case["turns"]:
                    self.assertTrue(turn["kind"] and turn["prompt"])

    def test_expansion_covers_31_distinct_scenarios_and_64_turns(self):
        self.assertEqual(31,sum(len(v) for v in CASES.values()))
        self.assertEqual(64,sum(len(c["turns"]) for batch in CASES.values() for c in batch))
        self.assertEqual(7,len(CASES["research"]))
        self.assertEqual(5,len(CASES["songwriting"]))
        self.assertEqual(8,len(CASES["conversation"]))
        self.assertEqual(5,len(CASES["transformations"]))
        self.assertEqual(6,len(CASES["reasoning"]))
        ui_cases=[c for batch in CASES.values() for c in batch if c.get("lane")=="ui"]
        self.assertEqual(3,len(ui_cases))
        self.assertTrue(all(not t.get("online") for c in ui_cases for t in c["turns"]))

    def test_reasoning_direction_and_calibration_checkers(self):
        good = {
            "handoff_forward": "CLIENT → SERVER",
            "handoff_reverse": "SERVER → CLIENT",
            "conflicting_sources": "ALPHA has 120 units and BETA has 145 units. Cannot determine a combined unique figure from different datasets.",
            "corrected_sources": "ALPHA has 135 and BETA has 145; overlap is unknown, so a combined unique count cannot be determined.",
            "guest_constraints": "Test the phone and VR headset browser joins, guest access, and cross-device interactions. No download or account is required.",
            "guest_constraints_update": "Include the desktop browser as a third device, preserve guest access, and verify browser networking without a download.",
            "unverified_tests": "Two tests fail and one passes. Inspect the failures and rerun; no fix has been verified.",
            "tests_vs_deploy": "Three tests pass, but the build is not deployed and is not live.",
            "benchmark_confounded": "A measured 140 ms and B 180 ms on different hosts. We cannot claim causality without controlled same-host testing.",
            "benchmark_controlled": "A was faster by 25 ms in this test: A 140 ms versus B 165 ms. A single benchmark is not universal.",
            "task_list": "1. Fix Stop button\n2. Improve lyric formatting\n3. Change the logo",
            "task_list_revision": "1. Fix Stop button\n2. Improve lyric formatting\n3. Design a dark-theme icon",
        }
        for kind, answer in good.items():
            with self.subTest(kind=kind):
                self.assertEqual([],fails(kind,answer))

    def test_reasoning_rejects_confident_invention_and_scope_drift(self):
        bad = {
            "handoff_forward": ("SERVER → CLIENT", "request_client_to_server"),
            "handoff_reverse": ("CLIENT → SERVER", "reply_server_to_client"),
            "conflicting_sources": ("ALPHA is 120, BETA is 145, so combined is 265", "uncertain_combined"),
            "corrected_sources": ("ALPHA is 120 and BETA is 145, with no overlap", "alpha_135"),
            "guest_constraints": ("You must install the mobile app, register and sign in", "no_forced_install"),
            "guest_constraints_update": ("Desktop joins only after you install and log in", "no_forced_install"),
            "unverified_tests": ("I fixed both failed tests and deployed the build", "no_fake_fix"),
            "tests_vs_deploy": ("Three tests pass and are now live", "not_deployed"),
            "benchmark_confounded": ("140 ms versus 180 ms proves the code change caused this improvement", "not_causal_claim"),
            "benchmark_controlled": ("A is faster by 5 ms in this test. A 140, B 165", "difference_25ms"),
            "task_list": ("I fixed Stop and completed the logo task", "not_completed_claim"),
            "task_list_revision": ("1. Fix Stop\n2. Improve lyric formatting\n3. Change the logo\n4. Deploy", "new_icon_task"),
        }
        for kind,(answer,missing) in bad.items():
            with self.subTest(kind=kind):
                self.assertIn(missing,fails(kind,answer))

    def test_lyric_verification_hijack_is_never_accepted(self):
        message=("I found search results for the lyrics, but I couldn't verify "
                 "the requested lyric text from fetched evidence, so I won't reconstruct it.")
        self.assertIn("no_lyrics_lookup_hijack",fails("pop_rewrite",message))
        self.assertIn("no_lyrics_lookup_hijack",fails("song_structure_research",message))

    def test_user_authored_verse_weather_hijack_is_never_accepted(self):
        message="I need a city/region or an explicitly shared location before I can check live weather."
        self.assertIn("no_weather_lookup_hijack",fails("source_ack",message))

    def test_inference_failure_is_never_an_original_song(self):
        message="Local Qwen inference failed after a retry. Your message was saved; please try again."
        self.assertIn("no_local_inference_failure",fails("rap_original",message))

    def test_network_phases_are_observable_not_masked_by_fluent_text(self):
        grade=check("source_ack","Acknowledged, I have your original lines.",
                    phases=["SEARCH_STARTED","SEARCH_PROVIDER_VISIT"])
        self.assertIn("no_unrequested_web_tool",
                      [x["check"] for x in grade["checks"] if not x["pass"]])
        okay=check("source_ack","Acknowledged, I have your original lines.",
                   phases=["GENERATING","COMPLETE"])
        self.assertEqual("PASS_EVIDENCE",okay["status"])

    def test_code_draft_status_is_not_valid_plain_language_or_song_response(self):
        reply=("The source has been generated but did not pass code validation. "
               "Send Continue code to retry repairing the saved source.")
        for kind in ("debugging","pop_adaptation","remaster_original","feedback_only"):
            with self.subTest(kind=kind):
                self.assertIn("no_code_generator_hijack",fails(kind,reply))
        benign=check("source_ack","Understood; these are your original authored lines.",
                     phases=["GENERATING","COMPLETE"])
        self.assertEqual("PASS_EVIDENCE",benign["status"])
        code_phase=check("source_ack","Understood; these are your original authored lines.",
                         phases=["CODE_DRAFT_STREAMING"])
        self.assertIn("no_code_generator_hijack",
                      [t["check"] for t in code_phase["checks"] if not t["pass"]])

    def test_failure_family_classification_uses_observed_evidence(self):
        sample={"outcome":"REVIEW","turns":[{"evaluation":{"checks":[
            {"check":"no_code_generator_hijack","pass":False},
            {"check":"no_unrequested_web_tool","pass":False},
            {"check":"verse1","pass":False}
        ]}}]}
        self.assertEqual(["CODE_ROUTE","CONTENT_OR_FORMAT_REVIEW",
                          "UNREQUESTED_RESEARCH"],failure_types(sample))
        blocked={"outcome":"BLOCKED","error":"TimeoutError: no reply","turns":[]}
        self.assertEqual(["TURN_TIMEOUT"],failure_types(blocked))
        good={"outcome":"PASS_EVIDENCE","turns":[{"evaluation":{
            "checks":[{"check":"no_code_generator_hijack","pass":True}]}}]}
        self.assertEqual([],failure_types(good))

    def test_weather_title_does_not_require_a_forecast(self):
        fictional=("Rain Glass Lantern\nVerse 1: rain in the window.\n"
                   "Chorus: shine on\nVerse 2: turns back toward town.\n"
                   "Bridge: chooses the road home.\n"*5)
        self.assertEqual([],fails("weather_safe_song",fictional))

    def test_adaptation_does_not_preserve_aab_verse_repetition(self):
        copied=("\nVerse 1\nWait for the midnight train\n"
                "Wait for the midnight train\nThen walk toward the lights.\n"
                "Pre-Chorus\nA soft signal\nChorus\nHome again\n"
                "Verse 2\nThe river is cold.\nBridge\nI turn.\n"
                "Final Chorus\nHome again\n" + "Another lyric line\n"*12)
        self.assertIn("no_blues_aab_copied_into_pop_verses",
                      fails("pop_adaptation",copied))

    def test_remix_recycles_too_many_source_images(self):
        song=("[Verse 1]\nA paper key unlocks the station clock\n"
              "The quiet roads become a purple noon\n[Chorus]\nA new bright song\n"
              "[Verse 2]\nAnother visitor arrives\n[Bridge]\nThey choose the open road\n"
              +"Independent new lyric line. "*30)
        self.assertIn("limited_recycled_source_imagery",fails("original_remix",song))

    def test_metaphorical_glitch_is_an_acceptable_joke(self):
        reply=("It sounds like a glitchy layout, not a literal creature. "
               "Let's inspect what triggers the UI issue.")
        self.assertEqual([],fails("metaphor",reply))

    def test_500_does_not_count_as_a_song(self):
        self.assertIn("no_generation_or_router_error",
                      fails("pop_song","Generation failed: HTTP Error 500: Internal Server Error"))

    def test_original_remix_rejects_copied_source_even_with_valid_sections(self):
        song=("[Verse 1]\n"+ORIGINAL_TEST_LINES[0]+"\nNoon sparks hurry round the dome\n"
              "[Chorus]\nCarry me out, carry me home\n"
              "[Verse 2]\nFresh feet cross a neon floor\n"
              "[Chorus]\nCarry me out, carry me home\n"
              "[Bridge]\nI choose the open door\n"+"New words keep moving. "*30)
        bad=fails("original_remix",song)
        self.assertIn("no_verbatim_source_line_1",bad)
        self.assertNotIn("distinct_verses",bad)

    def test_distinguishes_feedback_from_new_lyric(self):
        text="I can compare whether Verse 2 introduces a new event, but actual vocal flow needs a human performance check."
        self.assertEqual([],fails("feedback_only",text))
        self.assertIn("no_new_song",fails("feedback_only","[Verse 1]\nNew words\n[Verse 2]\nMore words"))

    def test_invalid_browser_listener_method_is_rejected(self):
        reply="On mobile, inspect click listeners using buttonElement.getEventListeners(). Check touch overlap and console events."
        self.assertIn("valid_dom_debugging_api",fails("debugging",reply))
        valid="On mobile, inspect the browser console, reproduce the tap, and inspect overlay pointer-events."
        self.assertEqual([],fails("debugging",valid))

    def test_staff_must_not_appear_out_of_nowhere(self):
        fabricated="Rae has 8 minutes; an extra cook arrived to help. Label containers."
        self.assertIn("no_invented_helpers",fails("staffing_followup",fabricated))

    def test_markdown_aab_verses_with_labeled_lines_are_valid(self):
        lyrics=("### Verse 1\n**A:** The steam hisses loud against the glass\n"
                "**A:** The steam hisses loud against the glass\n"
                "**B:** The last engine carries me into the past\n\n"
                "### Verse 2\n**A:** The ticket agent waves a tired hand\n"
                "**A:** The ticket agent waves a tired hand\n"
                "**B:** I leave my footprints on the sand\n\n"
                "**A quick note on the structure:** A lyric line is not a bar.")
        self.assertEqual([],fails("blues_lyrics",lyrics))

    def test_four_sung_lines_cannot_count_as_aab(self):
        lyrics=("[Verse 1]\nA line\nA line\nB line\nAn extra sung line\n"
                "[Verse 2]\nAnother line\nAnother line\nA closing line\n"
                "The station platform is empty")
        self.assertIn("two_complete_aab_verses",fails("blues_lyrics",lyrics))

    def test_not_every_new_moon_is_not_a_false_science_failure(self):
        answer=("Not every new moon causes a solar eclipse because "
                "the Moon's orbit is tilted to the ecliptic.")
        self.assertNotIn("no_invented_facts",fails("science_followup",answer))
        wrong=("Every new moon causes a total solar eclipse when "
               "the orbital tilt produces shadow alignment.")
        self.assertIn("no_invented_facts",fails("science_followup",wrong))

    def test_science_answer_checks_actual_contrast(self):
        good=("The Moon and Sun must align with Earth. Totality is smaller than the partial eclipse region. "
              "Not every new moon has a total eclipse because of orbital inclination. "
              "See https://science.nasa.gov/eclipses")
        self.assertEqual([],fails("public_science",good))


if __name__=="__main__":
    unittest.main()
