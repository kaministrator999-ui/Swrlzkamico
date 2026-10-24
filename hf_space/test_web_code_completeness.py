"""Incomplete-web regression supplied by the owner; no behavioral PASS inferred."""
from pathlib import Path
import sys,unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
from brain_programming import programming_intent,candidate_contract_gate,programming_library_context
from test_github_change_model_context import load_engine,FakeModel

SCAFFOLD='''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>3D Modeling Engine Page</title>
<style>/* Add your 3D modeling styles here */
#3dModel { width: 100%; height: 500px; border: 1px solid #000; }</style></head>
<body><h1>3D Modeling Engine Page</h1><div id="3dModel"></div><script>
// Add your 3D modeling JavaScript here
// Use a library like Three.js to create the 3D model
// Example:
// const scene = new THREE.Scene();
// const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
// const renderer = new THREE.WebGLRenderer();
// renderer.setSize(window.innerWidth, window.innerHeight);
// document.body.appendChild(renderer.domElement);
// const geometry = new THREE.BoxGeometry();
// const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
// const cube = new THREE.Mesh(geometry, material);
// scene.add(cube);
// camera.position.z = 5;
// renderer.render(scene, camera);
</script></body></html>'''

class WebCompleteness(unittest.TestCase):
 def test_requested_behaviors_survive_without_modal_must_wording(self):
  request='Create an HTML model viewer. Show a cube with drag orbit and wheel zoom. Use a pinned import map. Wire a wireframe checkbox. Do not claim tests ran.\n```js\n// Include an unrelated camera feature.\n```'
  contract=programming_intent(request,[],[])['intentContract']
  for clause in ['Show a cube with drag orbit and wheel zoom.','Use a pinned import map.','Wire a wireframe checkbox.']:
   self.assertIn(clause,contract['must'])
  self.assertIn('Do not claim tests ran.',contract['mustNot'])
  self.assertNotIn('unrelated camera',' '.join(contract['must']))
 def test_library_evidence_is_version_scoped_and_not_for_unrelated_turns(self):
  p=programming_intent('Create an HTML 3D model viewer using Three.js 0.160.0',[],[])
  self.assertIn('OrbitControls',programming_library_context(p))
  p=programming_intent('Create an HTML viewer using Three.js 0.150.0',[],[])
  self.assertEqual(programming_library_context(p),'')
  p=programming_intent('Create an HTML calculator',[],[])
  self.assertEqual(programming_library_context(p),'')
  self.assertEqual(programming_library_context({'codingTask':False}),'')
 def test_html_viewer_keeps_its_embedded_runtime_languages(self):
  p=programming_intent('Create a single-file HTML 3D model viewer using Three.js with a wireframe control',[],[])
  contract=p['intentContract']['languageContract']
  self.assertEqual(contract['artifactType'],'web-page')
  self.assertCountEqual(contract['allowedLanguages'],['html','css','javascript'])
  source='```html\n<!doctype html><html><style>canvas{display:block}</style><canvas></canvas><script type="module">document.querySelector("canvas").width=300;</script></html>\n```'
  self.assertEqual(candidate_contract_gate(source,p,[])['status'],'PASS')

 def test_single_html_document_can_satisfy_explicit_css_and_javascript(self):
  p=programming_intent('Create a single HTML 3D modeling page with CSS and JavaScript',[],[])
  self.assertEqual(p['intentContract']['languageContract']['artifactType'],'web-page')
  source='```html\n<html><style>canvas{width:100%}</style><button onclick="count++">Add</button><script>let count=0;</script></html>\n```'
  result=candidate_contract_gate(source,p,[])
  self.assertEqual(result['status'],'PASS',result)
  self.assertCountEqual(result['detectedLanguages'],['html','css','javascript'])
  self.assertFalse(result['executionVerified'])
 def test_supplied_scaffold_is_not_a_completed_3d_page(self):
  p=programming_intent('Create a functional 3D modeling HTML page',[],[])
  r=candidate_contract_gate('```html\n'+SCAFFOLD+'\n```',p,[])
  self.assertEqual(r['status'],'REJECT');self.assertFalse(r['executionVerified'])
  self.assertIn('unfinished-implementation-placeholder',r['reasons'])
  self.assertIn('dynamic-page-has-no-runtime-implementation',r['reasons'])

 def test_comment_and_data_script_are_not_executable_implementation(self):
  p=programming_intent('Create an interactive HTML calculator page',[],[])
  for script in ('// example: calculate();','/* calculate(); */',''):
   r=candidate_contract_gate('<html><script>'+script+'</script></html>',p,[])
   self.assertIn('dynamic-page-has-no-runtime-implementation',r['reasons'])
  r=candidate_contract_gate('<html><script type="application/json">{"example":1}</script></html>',p,[])
  self.assertIn('dynamic-page-has-no-runtime-implementation',r['reasons'])

 def test_static_and_explicit_templates_remain_valid(self):
  p=programming_intent('Create a static HTML page with a heading',[],[])
  self.assertEqual(candidate_contract_gate('<html><h1>Hello</h1></html>',p,[])['status'],'PASS')
  p=programming_intent('Create an HTML template with placeholders',[],[])
  self.assertEqual(candidate_contract_gate(SCAFFOLD,p,[])['status'],'PASS')
  p=programming_intent('Create a working HTML editor; do not return a scaffold',[],[])
  self.assertEqual(candidate_contract_gate(SCAFFOLD,p,[])['status'],'REJECT')

 def test_active_or_loaded_script_is_shape_only_never_execution_success(self):
  p=programming_intent('Create an interactive HTML page',[],[])
  for script in ('<script>const label="https://example.org"; document.body.textContent=label;</script>',
                 '<script type="module" src="app.js"></script>'):
   r=candidate_contract_gate('<html>'+script+'</html>',p,[])
   self.assertEqual(r['status'],'PASS');self.assertFalse(r['executionVerified'])

 def test_actual_engine_shape_checks_do_not_raise_regex_error(self):
  for name in ('qwen_coder_engine','lfm2_700m_engine'):
   engine=load_engine(name)
   p=programming_intent('Create a functional 3D modeling HTML page',[],[])
   self.assertEqual(engine._candidate_structure_check('```html\n'+SCAFFOLD+'\n```',p,[])['status'],'REJECT')
   p=programming_intent('Write a Python function named add(a, b)',[],[])
   r=engine._candidate_structure_check('```python\ndef add(a,b):\n return a+b\n```',p,[])
   self.assertEqual(r['status'],'PASS',r)

 def test_structural_closing_lines_are_not_generation_loops(self):
  p=programming_intent('Create an HTML page with JavaScript',[],[])
  code='```html\n<html><script>\n'+''.join('function f'+str(i)+'() {\n  return '+str(i)+';\n}\n' for i in range(12))+'</script></html>\n```'
  for name in ('qwen_coder_engine','lfm2_700m_engine'):
   engine=load_engine(name)
   self.assertNotIn('repetition-loop',engine._candidate_structure_check(code,p,[])['reasons'])
   repeated='```html\n<html><script>\n'+('console.log("repeated without purpose");\n'*9)+'</script></html>\n```'
   self.assertIn('repetition-loop',engine._candidate_structure_check(repeated,p,[])['reasons'])

 def test_web_output_budget_grows_within_real_context_limit(self):
  engine=load_engine('qwen_coder_engine')
  class WebModel(FakeModel):
   def create_chat_completion(self,**kwargs):
    self.calls.append(kwargs)
    yield {'choices':[{'delta':{'content':'```html\n<!doctype html><html><body><h1>Demo</h1></body></html>\n```'}}]}
  model=WebModel()
  with patch.object(engine,'load',return_value=model):
   events=list(engine.generate_events({'prompt':'Create a complete static HTML page with a heading','history':[]}))
  self.assertEqual(model.calls[0]['max_tokens'],3072)
  context=next(e for e in events if e['type']=='CONTEXT')
  self.assertGreaterEqual(context['reservedOutputTokens'],3072)
  self.assertLessEqual(context['estimatedInputTokens']+3072+engine.CONTEXT_SAFETY_TOKENS,engine.CONTEXT_TOKENS)
  fitted=engine._fit_messages(model,'system',[],'source '*4000,3072)
  self.assertLess(fitted[3],3072)

if __name__=='__main__':unittest.main()
