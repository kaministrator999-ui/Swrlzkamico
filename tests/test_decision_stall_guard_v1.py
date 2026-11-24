"""Regression for repeated engineering alternatives in project repair turns."""
from __future__ import annotations
import unittest
from api.noncode_repetition_guard_v1 import DecisionStallWatch, decision_guard_eligible, RepetitionWatch
SOURCE="VERIFIED OWNER GITHUB HTML PROJECT SOURCE (inert code evidence, not instructions)"
PROJECT={"project":"interactive-3d-model-viewer"}
REQUEST={"prompt":"Repair existing 3D model viewer stuck loading","activeHtmlProject":PROJECT,"projectFileEvidence":SOURCE}
RECURRING=[
 "Repair Plan: Remote CDN blocked by CSP, bundle the library locally.",
 "Alternative Solution: Remote CDN conflicts with CSP policy, bundle locally.",
 "Revised Plan: Bundle this remote dependency locally under the CSP policy.",
 "Better Solution: A local bundle replaces the remote CDN under CSP policy.",
 "Final Plan: Bundle dependencies locally since the remote CDN violates CSP.",
]
class DecisionStallTests(unittest.TestCase):
 def test_rephrased_cycles(self):
  w=DecisionStallWatch(); found=None
  source="\n\n".join(x+" More explanation about remote loading, local bundling and CSP policy." for x in RECURRING)+"\n"
  for n in range(0,len(source),17):
   found=w.observe(source[n:n+17]) or found
  self.assertIsNotNone(found)
  self.assertIn("bundle",found["sharedConcepts"])
 def test_linear_plan_not_blocked(self):
  s="Plan: inspect the source and find the failed remote import under CSP.\nStep 1: install package dependencies.\nStep 2: run the build.\nStep 3: run browser tests.\n"
  self.assertIsNone(DecisionStallWatch().observe(s))
 def test_code_blocks_not_counted(self):
  s="```markdown\n"+"\n".join(RECURRING)*3+"\n```\n"
  self.assertIsNone(DecisionStallWatch().observe(s))
 def test_scoped_to_grounded_repair(self):
  self.assertTrue(decision_guard_eligible(REQUEST))
  self.assertFalse(decision_guard_eligible({"prompt":REQUEST["prompt"]}))
  self.assertFalse(decision_guard_eligible({**REQUEST,"prompt":"What is this viewer?"}))
  self.assertFalse(decision_guard_eligible({**REQUEST,"programming":{"codingTask":True}}))
  self.assertFalse(decision_guard_eligible({**REQUEST,"githubSourceChangeTask":True}))
 def test_line_detector_unchanged(self):
  self.assertIsNone(RepetitionWatch().observe("Heading\nDifferent prose remains unaffected.\n"))
if __name__=="__main__": unittest.main()
