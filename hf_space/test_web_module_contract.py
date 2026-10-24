"""Standalone module graphs and actual engine rejection-feedback delivery."""
import unittest
from unittest.mock import patch
from web_module_contract import module_dependency_gaps
from brain_programming import programming_intent,candidate_contract_gate
from test_github_change_model_context import load_engine,FakeModel

CORE='https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js'
ORBIT='https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/controls/OrbitControls.js'
BAD='<html><script type="module">import {OrbitControls} from "'+ORBIT+'";</script></html>'
GOOD='<html><script type="importmap">{"imports":{"three":"'+CORE+'"}}</script><script type="module">import {OrbitControls} from "'+ORBIT+'";</script></html>'

class WebModuleContract(unittest.TestCase):
 def test_known_external_module_requires_its_bare_dependency(self):
  self.assertEqual(module_dependency_gaps(BAD),['unresolved-browser-module:three (required by OrbitControls.js)'])
  self.assertEqual(module_dependency_gaps(GOOD),[])

 def test_direct_bare_import_is_not_browser_resolved_without_a_map(self):
  source='<html><script type="module">import * as THREE from "three";</script></html>'
  self.assertEqual(module_dependency_gaps(source),['unresolved-browser-module:three'])

 def test_prefix_and_scoped_maps_resolve_real_dependency_context(self):
  prefix='<script type="importmap">{"imports":{"three":"'+CORE+'","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script><script type="module">import {OrbitControls} from "three/addons/controls/OrbitControls.js";</script>'
  scoped='<script type="importmap">{"scopes":{"https://cdn.jsdelivr.net/npm/three@0.160.0/":{"three":"'+CORE+'"}}}</script>'+BAD
  self.assertEqual(module_dependency_gaps(prefix),[])
  self.assertEqual(module_dependency_gaps(scoped),[])

 def test_comments_strings_and_templates_are_not_import_statements(self):
  source='''<script type="module">
// import * as X from 'missing';
/* import('missing'); */
const text="import example from 'missing'";
const template=`import('missing')`;
const pattern=/import x from 'missing'/;
const object={import:()=>0};object.import('missing');
</script>'''
  self.assertEqual(module_dependency_gaps(source),[])

 def test_malformed_map_is_rejected_but_declared_build_context_is_preserved(self):
  self.assertEqual(module_dependency_gaps('<script type="importmap">{bad json}</script>'),['invalid-browser-import-map'])
  p=programming_intent('Create an HTML 3D viewer in our Vite project.',[],[])
  self.assertEqual(candidate_contract_gate(BAD,p,[])['status'],'PASS')

 def test_actual_source_reason_reaches_both_model_retry_prompts(self):
  for name in ('qwen_coder_engine','lfm2_700m_engine'):
   with self.subTest(engine=name):
    engine=load_engine(name)
    class Responses(FakeModel):
     def create_chat_completion(self,**kwargs):
      self.calls.append(kwargs)
      text=BAD if len(self.calls)==1 else GOOD
      yield {'choices':[{'delta':{'content':'```html\n'+text+'\n```'}}]}
    model=Responses()
    with patch.object(engine,'load',return_value=model):
     events=list(engine.generate_events({'prompt':'Create a complete standalone HTML 3D model viewer.','history':[]}))
    self.assertEqual(len(model.calls),2)
    self.assertIn('unresolved-browser-module:three',model.calls[1]['messages'][-1]['content'])
    self.assertIn('no execution',model.calls[1]['messages'][-1]['content'])
    receipt=next(e['validation'] for e in events if e['type']=='CANDIDATE_VALIDATION')
    self.assertEqual(receipt['status'],'PASS');self.assertFalse(receipt['executionVerified'])
    for call in model.calls:
     self.assertLessEqual(engine._token_count(model,call['messages'])+call['max_tokens']+engine.CONTEXT_SAFETY_TOKENS,engine.CONTEXT_TOKENS)

if __name__=='__main__':unittest.main()
