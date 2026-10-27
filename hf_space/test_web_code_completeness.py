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
 def test_run_instructions_do_not_replace_html_language_or_invent_shell_files(self):
  from project_archive import parse_project_files
  source=('```html file=index.html\n<html><script src="app.js"></script></html>\n```\n\n'
          '```javascript file=app.js\nconst ready=true;\n```\n\n'
          'To run this code, use Python\'s HTTP server:\n\n```sh\npython -m http.server 8000\n```')
  prompt='Create a complete HTML page.'
  state=programming_intent(prompt,[],[])
  check=candidate_contract_gate(source,state,[])
  self.assertEqual(check['status'],'PASS',check)
  self.assertNotIn('bash',check['detectedLanguages'])
  self.assertEqual([item['path'] for item in parse_project_files(source)],['index.html','app.js'])
  for name in ('qwen_coder_engine','lfm2_700m_engine'):
   engine=load_engine(name)
   class Response(FakeModel):
    def create_chat_completion(self,**kwargs):
     self.calls.append(kwargs)
     yield {'choices':[{'delta':{'content':source},'finish_reason':'stop'}]}
   model=Response()
   with patch.object(engine,'load',return_value=model):
    events=list(engine.generate_events({'prompt':prompt,'history':[]}))
   self.assertEqual(''.join(event.get('text','') for event in events if event['type']=='DELTA'),source)
   self.assertEqual(len(model.calls),1)
   self.assertTrue(any(event['type']=='COMPLETED' for event in events))
  named=source.replace('```sh\n','```sh file=serve.sh\n')
  self.assertIn('language-contract-mismatch:bash',candidate_contract_gate(named,state,[])['reasons'])
  commented=source.replace('python -m http.server 8000','\n# TODO: implement serving\npython -m http.server 8000')
  self.assertEqual(candidate_contract_gate(commented,state,[])['status'],'REJECT')

 def test_project_header_attributes_inside_source_are_rejected_without_rewriting(self):
  from brain_programming import _source_delivery_gaps
  for language,body in [('javascript','\nfile="src/my editor.js" project=editor\r\nexport const ready=true;'),
                        ('css','path=styles.css group=editor\nbody { color: green; }')]:
   source='```'+language+'\n'+body+'\n```'
   gaps=_source_delivery_gaps(source,'Create a software project',{})
   self.assertTrue(any(reason.startswith('misplaced-project-file-metadata:') for reason in gaps),gaps)
   self.assertIn(body,source)
  for language,body in [('javascript','file="editor.js";\nconst project="editor";'),
                        ('javascript','// file=editor.js project=editor\nconst ready=true;'),
                        ('bash','file=output.txt project=editor\nprintf "%s" "$file"'),
                        ('html','file=output.txt project=editor\n<html></html>'),
                        ('markdown','file=editor.js project=editor\nThese are example attributes.')]:
   gaps=_source_delivery_gaps('```'+language+'\n'+body+'\n```','Create a software project',{})
   self.assertFalse(any(reason.startswith('misplaced-project-file-metadata:') for reason in gaps),gaps)

 def test_ordinary_3d_web_request_gets_an_optional_verified_library_reference(self):
  p=programming_intent('Create an HTML 3D model viewer with drag orbit and wheel zoom.',[],[])
  self.assertIn('0.160.0',programming_library_context(p))
  for request in ('Create an HTML page with three buttons.',
                  'Create an offline HTML 3D model viewer.',
                  'Create an HTML 3D viewer without libraries.',
                  'Create an HTML 3D viewer with no third-party libraries.',
                  'Create an HTML 3D viewer without external JS libraries.',
                  'Create an HTML 3D viewer using raw WebGL.',
                  'Create an HTML 3D viewer using Babylon.js.'):
   with self.subTest(request=request):
    self.assertEqual(programming_library_context(programming_intent(request,[],[])),'')

 def test_repair_retains_reference_for_confirmed_pinned_source(self):
  p=programming_intent('Create an HTML 3D viewer.',[],[])
  p.update({'artifactContinuation':True,'failureEvidence':{'repairSource':'import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js";'}})
  self.assertIn('OrbitControls',programming_library_context(p))
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
  self.assertEqual(model.calls[0]['max_tokens'],engine.WEB_PAGE_OUTPUT_TOKENS)
  context=next(e for e in events if e['type']=='CONTEXT')
  self.assertEqual(context['reservedOutputTokens'],engine.WEB_PAGE_OUTPUT_TOKENS)
  self.assertLessEqual(context['estimatedInputTokens']+engine.WEB_PAGE_OUTPUT_TOKENS+engine.CONTEXT_SAFETY_TOKENS,engine.CONTEXT_TOKENS)
  with self.assertRaisesRegex(ValueError,'was not truncated'):
   engine._fit_messages(model,'system',[],'source '*engine.CONTEXT_TOKENS,engine.WEB_PAGE_OUTPUT_TOKENS)

if __name__=='__main__':unittest.main()
