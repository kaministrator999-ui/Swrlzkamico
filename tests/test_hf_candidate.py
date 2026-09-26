"""Offline structural and contract checks; never misreport these as live model inference."""
import ast,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Candidate(unittest.TestCase):
 def test_source_contract(self):
  src=(ROOT/"hf_space/app.py").read_text(encoding="utf-8")
  tree=ast.parse(src)
  self.assertIn("generate_events",src)
  self.assertIn('kind=="DELTA"',src)
  self.assertIn('kind=="FAILED"',src)
  self.assertNotIn("torch.hub",src)
 def test_model_provenance(self):
  p=json.loads((ROOT/"hf_space/MODEL_PROVENANCE.json").read_text(encoding="utf-8"))
  m=json.loads((ROOT/"hf_space/lalm§wyrlz.transport.json").read_text(encoding="utf-8"))
  self.assertEqual(p["transportSha256"],m["sha256"])
  self.assertEqual(p["transportChunks"],54)
  self.assertEqual(p["rawSha256"],"65e4b5d730f66024c44da25aec27730db27aa0019df0df26c0997d17ce58bdee")
 def test_canonical_source(self):
  for rel in ("accepted_runtime/lalm/r39_engine.py","swyrlz/r39_inference.py","swyrlz/backend.py","chat/§wyrlz/index.html"):
   self.assertEqual((ROOT/rel).read_bytes(),(ROOT/"hf_space"/rel).read_bytes())
  self.assertIn("SWRLZ_LALM_STATION",(ROOT/"api/lalm_station.py").read_text(encoding="utf-8"))
 def test_no_secret_or_billing_code(self):
  app=(ROOT/"hf_space/app.py").read_text(encoding="utf-8")
  for term in ("HF_TOKEN","request_space_hardware","add_space_secret","billing"):
   self.assertNotIn(term,app)
if __name__=="__main__":unittest.main()
