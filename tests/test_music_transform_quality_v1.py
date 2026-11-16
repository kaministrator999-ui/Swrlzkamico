"""Regression checks for §C creative transforms, not copyrighted song text."""
from __future__ import annotations
import unittest
from scripts.music_transform_quality_v1 import (
    quality_review, transformation_contract, transformation_directive,
    repair_directive, music_feedback_followup,
)

def verse(label,lines):
    return "["+label+"]\n"+"\n".join(lines)

V1=["Clock hands blink across the station","Paper moons outlast the rain",
    "Lanterns map a broken nation","Copper tracks remember names",
    "Every gate has got a warning","Every warning picks a side",
    "Even dusk can hear the morning","When the final train arrives"]
V2=["Violet ink across the window","Moths are tracing out a sign",
    "When the conductor drops the signal","All the clocks reverse their time",
    "Under bridges names are written","Above rooftops bells awake",
    "Someone turns the ending different","Every promise starts to break"]
HOOK=["Light the lamp and find the road","Turn the page and share the load",
      "Light the lamp and find the road","Turn the page and share the load"]

class MusicTransformTests(unittest.TestCase):
    def test_modes_and_scope(self):
        items={
            "Write a parody song of this track":"parody",
            "Can you remix those lyrics?":"remix",
            "Remaster my song, keep its chorus":"remaster",
            "Create a mashup of these two tracks":"mashup",
            "Rewrite the rap with a different scene":"paraphrase",
            "Adapt the song into a folk ballad":"adaptation",
            "Write a new cover song":"cover",
            "Please flip this track":"remix",
        }
        for prompt,want in items.items():
            with self.subTest(prompt=prompt):
                observed=transformation_contract(prompt)
                self.assertIsNotNone(observed)
                self.assertEqual(observed["mode"],want)
                self.assertIn("SONG TRANSFORMATION CONTRACT",transformation_directive(observed))
        self.assertIsNone(transformation_contract("Explain how music remixes work"))
        self.assertIsNone(transformation_contract("Please look up Roll Call lyrics"))
        self.assertIsNone(transformation_contract("Remix the HTML styling"))
        self.assertIsNotNone(transformation_contract("Remix this",reference_available=True))

    def test_duplicate_verse_detected_even_with_different_performer_labels(self):
        song="\n\n".join([verse("Verse 1: Singer A",V1),
             verse("Chorus",HOOK),verse("Verse 2: Singer B",V2),
             verse("Chorus",HOOK),verse("Verse 3: Singer C",V1)])
        check=quality_review(song)
        self.assertEqual(check["status"],"REJECT")
        self.assertIn("duplicated-nonchorus-verse",check["reasons"])

    def test_nearly_identical_verse_detected(self):
        almost=V1[:7]+["The final train has left the line"]
        song=verse("Verse 1",V1)+"\n\n"+verse("Verse 2",almost)
        self.assertIn("near-duplicate-nonchorus-verses",quality_review(song)["reasons"])

    def test_legitimate_repeated_hook_is_not_bad(self):
        song="\n".join([verse("Verse 1",V1),verse("Chorus",HOOK),
                        verse("Verse 2",V2),verse("Chorus",HOOK)])
        self.assertEqual(quality_review(song)["status"],"PASS")

    def test_repeated_padding_is_rejected_outside_chorus(self):
        song=verse("Verse 1",["I wrote a line"]*7+["A fresh one"])
        self.assertIn("repetitive-nonchorus-padding",quality_review(song)["reasons"])

    def test_intentional_blues_aab_can_opt_out(self):
        song=verse("Verse 1",["A train bell rings"]*3+["And morning comes"]*3)
        self.assertIn("repetitive-nonchorus-padding",quality_review(song)["reasons"])
        self.assertNotIn("repetitive-nonchorus-padding",quality_review(song,allow_aab=True)["reasons"])

    def test_preamble_outro_are_detected(self):
        song="Alright, Kami! Here's a remix!\n"+verse("Verse 1",V1)+"\nHope you like it!"
        faults=quality_review(song)["reasons"]
        self.assertIn("assistant-preface-in-song",faults)
        self.assertIn("assistant-outro-in-song",faults)

    def test_feedback_followup_is_not_lyrics_lookup(self):
        h=[{"role":"assistant","content":"[Verse 1]\\nA sample original rap\\n[Chorus]"}]
        self.assertTrue(music_feedback_followup(
            "I was saying that's what I seen wrong with your remix version",h))
        self.assertTrue(music_feedback_followup(
            "Your remix repeated the verses; that was the issue",[]))
        self.assertFalse(music_feedback_followup(
            "Please look up the lyrics to the song again",h))
        self.assertTrue(music_feedback_followup(
            "Don't look up the lyrics, the problems were in your remix",h))

    def test_repair_is_directed_at_actual_faults(self):
        self.assertIn("duplicated-nonchorus-verse",
                      repair_directive(["duplicated-nonchorus-verse"],"parody"))

if __name__=="__main__":
    unittest.main()
