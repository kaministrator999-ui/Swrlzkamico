"""Selection identity and corrupt-artifact rejection without loading weights."""
import hashlib
import os
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import patch

PATH=Path(__file__).with_name('coder_model_config.py')

class CoderModelSelection(unittest.TestCase):
    def configured(self, **values):
        with patch.dict(os.environ, values, clear=True):
            return runpy.run_path(str(PATH))

    def test_default_and_explicit_variants_have_matching_labels_and_pins(self):
        for size in ('1.5B','3B','7B'):
            with self.subTest(size=size):
                repo='Qwen/Qwen2.5-Coder-'+size+'-Instruct-GGUF'
                config=self.configured(SWRLZ_CODER_MODEL_REPO=repo)
                options=config['download_arguments']()
                self.assertEqual(options['repo_id'],repo)
                self.assertEqual(options['revision'],config['KNOWN_MODELS'][repo]['revision'])
                self.assertEqual(options['filename'],config['KNOWN_MODELS'][repo]['file'])
                self.assertIn(size,config['MODEL_LABEL'])
                self.assertIn(options['revision'],config['MODEL_CHECKPOINT'])
        self.assertIn('7B',self.configured()['MODEL_REPO'])

    def test_unknown_explicit_selection_does_not_claim_an_official_pin(self):
        config=self.configured(SWRLZ_CODER_MODEL_REPO='example/custom',SWRLZ_CODER_MODEL_FILE='custom.gguf')
        self.assertIsNone(config['MODEL_REVISION'])
        self.assertNotIn('revision',config['download_arguments']())
        self.assertEqual(config['MODEL_CHECKPOINT'],'example/custom/custom.gguf')

    def test_corrupt_same_length_artifact_is_rejected_before_native_load(self):
        config=self.configured();verify=config['verify_artifact']
        valid=b'valid';verify.__globals__['_SELECTED']={'bytes':len(valid),'sha256':hashlib.sha256(valid).hexdigest()}
        with tempfile.TemporaryDirectory() as folder:
            artifact=Path(folder)/'model.gguf';artifact.write_bytes(valid);verify(artifact)
            artifact.write_bytes(b'wrong')
            with self.assertRaisesRegex(ValueError,'checksum'):verify(artifact)
            artifact.write_bytes(b'shorter')
            with self.assertRaisesRegex(ValueError,'length'):verify(artifact)

if __name__=='__main__':unittest.main()
