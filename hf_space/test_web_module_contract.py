"""Standalone module graphs and actual engine rejection-feedback delivery."""
import unittest
import json
import re
from pathlib import Path
from unittest.mock import patch
from web_module_contract import module_dependency_gaps
from brain_programming import programming_intent,candidate_contract_gate,_code_fingerprint
from programming_repair_context import candidate_retry_messages,contract_rejection_context
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

 def test_native_core_only_map_does_not_resolve_addon_subpaths(self):
  # Exact module graph from the rejected native viewer: its core map was
  # present, but its addon import used an undeclared package subpath.
  native=GOOD.replace(ORBIT,'three/examples/jsm/controls/OrbitControls.js')
  self.assertEqual(module_dependency_gaps(native),['unresolved-browser-module:three/examples/jsm/controls/OrbitControls.js'])
  facts=json.loads((Path(__file__).with_name('programming_references')/'three-0.160.0.json').read_text())
  prose='\n'.join(facts['facts'])
  mapping=re.search(r'<script type="importmap">\s*\{[\s\S]*?</script>',prose).group()
  standard=mapping+'<script type="module">import {OrbitControls} from "three/addons/controls/OrbitControls.js";</script>'
  self.assertEqual(module_dependency_gaps(standard),[])
  self.assertIn('does not map three/examples/jsm/controls/OrbitControls.js',prose)

 def test_browser_resolution_feedback_does_not_invent_dependency_unavailability(self):
  reason='unresolved-browser-module:three/examples/jsm/controls/OrbitControls.js'
  feedback=contract_rejection_context({'reasons':[reason]})
  self.assertIn(reason,feedback)
  self.assertIn('exact key resolves only that name',feedback)
  self.assertIn('trailing-slash prefix key and URL',feedback)
  self.assertIn('does not prove the dependency is unavailable',feedback)
  self.assertNotIn('BROWSER MODULE RESOLUTION',contract_rejection_context({'reasons':['missing-required-language:html']}))

 def test_css_id_rule_repairs_change_brain_and_both_engine_fingerprints(self):
  engines=[load_engine(name) for name in ('qwen_coder_engine','lfm2_700m_engine')]
  fingerprints=[_code_fingerprint]+[engine._candidate_fingerprint for engine in engines]
  sources=[
   '```html\n<html><style>\n#viewer { margin: 0; }\n</style></html>\n```',
   '```css\n#viewer { margin: 0; }\n```',
   '#viewer {\n margin: 0;\n}',
  ]
  for source in sources:
   changed=source.replace('margin: 0','margin: 10px')
   with self.subTest(source=source):
    before=[fingerprint(source) for fingerprint in fingerprints]
    after=[fingerprint(changed) for fingerprint in fingerprints]
    self.assertEqual(len(set(before)),1)
    self.assertEqual(len(set(after)),1)
    self.assertTrue(all(a!=b for a,b in zip(before,after)))

 def test_comment_only_python_and_javascript_edits_keep_source_fingerprints(self):
  fingerprints=[_code_fingerprint]+[load_engine(name)._candidate_fingerprint for name in ('qwen_coder_engine','lfm2_700m_engine')]
  for source,changed in [
   ('```python\n# old comment\ndef answer():\n return 42\n```','```python\n# new comment\ndef answer():\n return 42\n```'),
   ('```javascript\n// old comment\nconst answer=42;\n```','```javascript\n// new comment\nconst answer=42;\n```'),
  ]:
   for fingerprint in fingerprints:
    with self.subTest(source=source,owner=fingerprint.__module__):
     self.assertEqual(fingerprint(source),fingerprint(changed))

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
    self.assertEqual(model.calls[1]['messages'][-2],{'role':'assistant','content':'```html\n'+BAD+'\n```'})
    receipt=next(e['validation'] for e in events if e['type']=='CANDIDATE_VALIDATION')
    self.assertEqual(receipt['status'],'PASS');self.assertFalse(receipt['executionVerified'])
    for call in model.calls:
     self.assertLessEqual(engine._token_count(model,call['messages'])+call['max_tokens']+engine.CONTEXT_SAFETY_TOKENS,engine.CONTEXT_TOKENS)

 def test_final_retry_replaces_failed_draft_and_retains_original_goal(self):
  goal='Create a complete standalone HTML 3D model viewer. Preserve the visible wireframe control.'
  second=BAD.replace('<html>','<html><h1>Latest failed draft</h1>')
  for name in ('qwen_coder_engine','lfm2_700m_engine'):
   with self.subTest(engine=name):
    engine=load_engine(name)
    class Responses(FakeModel):
     def create_chat_completion(self,**kwargs):
      self.calls.append(kwargs)
      yield {'choices':[{'delta':{'content':'```html\n'+[BAD,second,GOOD][len(self.calls)-1]+'\n```'}}]}
    model=Responses()
    with patch.object(engine,'load',return_value=model):
     events=list(engine.generate_events({'prompt':goal,'history':[]}))
    self.assertEqual(len(model.calls),3)
    original=model.calls[0]['messages']
    for call,draft in zip(model.calls[1:],[BAD,second]):
     self.assertEqual(call['messages'][:-2],original)
     self.assertEqual(call['messages'][-2],{'role':'assistant','content':'```html\n'+draft+'\n```'})
     self.assertIn('unresolved-browser-module:three (required by OrbitControls.js)',call['messages'][-1]['content'])
     self.assertIn(goal,str(call['messages'][:-2]))
     self.assertLessEqual(engine._token_count(model,call['messages'])+call['max_tokens']+engine.CONTEXT_SAFETY_TOKENS,engine.CONTEXT_TOKENS)
    self.assertEqual(next(e['validation'] for e in events if e['type']=='CANDIDATE_VALIDATION')['status'],'PASS')

 def test_fresh_project_repeated_draft_gets_causal_strategy_change(self):
  goal='Build a complete standalone HTML 3D viewer with a working wireframe control.'
  bad=GOOD.replace(ORBIT,'three/examples/jsm/controls/OrbitControls.js')
  for name in ('qwen_coder_engine','lfm2_700m_engine'):
   with self.subTest(engine=name):
    engine=load_engine(name)
    class Responses(FakeModel):
     def create_chat_completion(self,**kwargs):
      self.calls.append(kwargs)
      yield {'choices':[{'delta':{'content':'```html\n'+(bad if len(self.calls)<=2 else GOOD)+'\n```'}}]}
    model=Responses()
    with patch.object(engine,'load',return_value=model):
     events=list(engine.generate_events({'prompt':goal,'history':[]}))
    self.assertEqual(len(model.calls),3)
    last=model.calls[-1]['messages']
    self.assertEqual(last[:-2],model.calls[0]['messages'])
    self.assertIn(goal,str(last[:-2]))
    self.assertEqual(last[-2]['content'],'```html\n'+bad+'\n```')
    self.assertIn('strategy-repeat-previous-attempt',last[-1]['content'])
    self.assertIn('Do not reuse the same executable fingerprint',last[-1]['content'])
    self.assertIn('Change the unresolved executable import path',last[-1]['content'])
    self.assertNotIn('Replace the unavailable dependency boundary',last[-1]['content'])
    self.assertEqual(next(e['validation'] for e in events if e['type']=='CANDIDATE_VALIDATION')['status'],'PASS')
    for call in model.calls:
     self.assertLessEqual(engine._token_count(model,call['messages'])+call['max_tokens']+engine.CONTEXT_SAFETY_TOKENS,engine.CONTEXT_TOKENS)

 def test_retry_context_keeps_canonical_source_and_all_of_latest_draft(self):
  original=[{'role':'system','content':'Canonical source under repair: original source and MUST contract.'},
            {'role':'user','content':'Keep the working behavior and repair only the failed dependency.'}]
  draft='begin failed source\n'+'x'*12000+'\nend failed source'
  retry=candidate_retry_messages(original,draft,'actual-source-failure')
  self.assertEqual(retry[:-2],original)
  self.assertEqual(retry[-2]['content'],draft)
  self.assertIn('actual-source-failure',retry[-1]['content'])
  retry[0]['content']='changed copy'
  self.assertIn('Canonical source',original[0]['content'])

 def test_large_source_is_checked_and_oversized_source_is_rejected(self):
  from project_archive import MAX_FILE_BYTES
  padded='<!--'+'x'*70000+'-->'+BAD
  self.assertTrue(any(reason.startswith('unresolved-browser-module:') for reason in module_dependency_gaps(padded)))
  self.assertEqual(module_dependency_gaps('x'*(MAX_FILE_BYTES+1)), ['browser-module-source-exceeds-validation-limit'])

 def test_retry_output_budget_counts_complete_failed_source(self):
  for name in ('qwen_coder_engine','lfm2_700m_engine'):
   with self.subTest(engine=name):
    engine=load_engine(name)
    large=BAD.replace('<html>','<html><!--'+'x'*(engine.CONTEXT_TOKENS*3)+'-->')
    class Responses(FakeModel):
     def create_chat_completion(self,**kwargs):
      self.calls.append(kwargs)
      yield {'choices':[{'delta':{'content':'```html\n'+(large if len(self.calls)==1 else GOOD)+'\n```'}}]}
    model=Responses()
    with patch.object(engine,'load',return_value=model):
     list(engine.generate_events({'prompt':'Create a complete standalone HTML 3D viewer.','history':[{'role':'user','text':'Project context: '+'existing context '*375}]}))
    self.assertEqual(len(model.calls),2)
    self.assertLess(model.calls[1]['max_tokens'],model.calls[0]['max_tokens'])
    self.assertEqual(model.calls[1]['messages'][-2]['content'],'```html\n'+large+'\n```')
    for call in model.calls:
     self.assertLessEqual(engine._token_count(model,call['messages'])+call['max_tokens']+engine.CONTEXT_SAFETY_TOKENS,engine.CONTEXT_TOKENS)

 def test_oversized_failed_source_rejects_without_silent_truncation(self):
  for name in ('qwen_coder_engine','lfm2_700m_engine'):
   with self.subTest(engine=name):
    engine=load_engine(name)
    oversized=BAD.replace('<html>','<html><!--'+'x'*(engine.CONTEXT_TOKENS*4-3000)+'-->')
    class Responses(FakeModel):
     def create_chat_completion(self,**kwargs):
      self.calls.append(kwargs)
      yield {'choices':[{'delta':{'content':'```html\n'+oversized+'\n```'}}]}
    model=Responses()
    with patch.object(engine,'load',return_value=model),self.assertRaisesRegex(ValueError,'Insufficient context'):
     list(engine.generate_events({'prompt':'Create a complete standalone HTML 3D viewer.','history':[]}))
    self.assertEqual(len(model.calls),1)

 def test_known_pinned_transform_controls_update_is_rejected_on_bound_instance(self):
  source=(GOOD.replace('OrbitControls','TransformControls')
      .replace('</script></html>', 'const gizmo=new TransformControls(camera,canvas);scene.add(gizmo);gizmo.update();</script></html>'))
  reasons=module_dependency_gaps(source)
  self.assertEqual(len(reasons),1)
  self.assertTrue(reasons[0].startswith('unsupported-three-r160-api:TransformControls.update()'))
  self.assertIn('retain editor controls',reasons[0])
  contract=programming_intent('Create a complete standalone HTML 3D viewer.',[],[])
  receipt=candidate_contract_gate('```html\n'+source+'\n```',contract,[])
  self.assertEqual(receipt['status'],'REJECT');self.assertFalse(receipt['executionVerified'])
  self.assertIn(reasons[0],receipt['reasons'])

 def test_pinned_transform_binding_aliases_and_namespace_are_checked(self):
  prefix='<script type="importmap">{"imports":{"three":"'+CORE+'","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>'
  for imported,constructor in (
   ('import {TransformControls} from "three/addons/controls/TransformControls.js";','TransformControls'),
   ('import {TransformControls as EditorGizmo} from "three/addons/controls/TransformControls.js";','EditorGizmo'),
   ('import * as EditAPI from "three/addons/controls/TransformControls.js";','EditAPI.TransformControls'),
  ):
   with self.subTest(imported=imported):
    source=prefix+'<script type="module">'+imported+'const handle=new '+constructor+'(camera,canvas);handle.update();</script>'
    self.assertTrue(any(r.startswith('unsupported-three-r160-api:') for r in module_dependency_gaps(source)))

 def test_unrelated_versions_updates_and_text_are_not_rejected_as_transform_api(self):
  fixed=GOOD.replace('OrbitControls','TransformControls').replace('</script></html>','const gizmo=new TransformControls(camera,canvas);gizmo.updateMatrixWorld();</script></html>')
  for source in (
   fixed,
   GOOD.replace('</script></html>','const orbit=new OrbitControls(camera,canvas);orbit.update();</script></html>'),
   fixed.replace('gizmo.updateMatrixWorld();','const example="gizmo.update()"; // gizmo.update()\n/* gizmo.update() */'),
   fixed.replace('0.160.0','0.161.0').replace('gizmo.updateMatrixWorld();','gizmo.update();'),
   '<script type="module">class TransformControls{update(){}}const gizmo=new TransformControls();gizmo.update();</script>',
  ):
   with self.subTest(source=source):self.assertFalse(any(r.startswith('unsupported-three-r160-api:') for r in module_dependency_gaps(source)))

 def test_rebinding_shadowing_and_explicit_update_extension_remain_ungraded(self):
  source=GOOD.replace('OrbitControls','TransformControls').replace('</script></html>','const gizmo=new TransformControls(camera,canvas);BODY</script></html>')
  for body in (
   'gizmo.update=()=>0;gizmo.update();',
   'gizmo["update"]=()=>0;gizmo.update();',
   'Object.defineProperty(gizmo,"update",{value:()=>0});gizmo.update();',
   'gizmo=new OtherControls();gizmo.update();',
   'function custom(gizmo){gizmo.update();}',
   'function custom(camera,gizmo){gizmo.update();}',
   'const custom=(gizmo)=>gizmo.update();',
   'const custom=gizmo=>gizmo.update();',
   'Object.assign(gizmo,{update(){return 0;}});gizmo.update();',
  ):
   with self.subTest(body=body):
    self.assertEqual(module_dependency_gaps(source.replace('BODY',body)),[])

 def test_actual_transform_api_reason_reaches_both_model_retries(self):
  bad=GOOD.replace('OrbitControls','TransformControls').replace('</script></html>','const gizmo=new TransformControls(camera,canvas);gizmo.update();</script></html>')
  for name in ('qwen_coder_engine','lfm2_700m_engine'):
   with self.subTest(engine=name):
    engine=load_engine(name)
    class Responses(FakeModel):
     def create_chat_completion(self,**kwargs):
      self.calls.append(kwargs)
      text=bad if len(self.calls)==1 else GOOD
      yield {'choices':[{'delta':{'content':'```html\n'+text+'\n```'}}]}
    model=Responses()
    with patch.object(engine,'load',return_value=model):
     events=list(engine.generate_events({'prompt':'Create a complete standalone HTML 3D viewer.','history':[]}))
    self.assertEqual(len(model.calls),2)
    self.assertIn('unsupported-three-r160-api:TransformControls.update()',model.calls[1]['messages'][-1]['content'])
    receipt=next(e['validation'] for e in events if e['type']=='CANDIDATE_VALIDATION')
    self.assertEqual(receipt['status'],'PASS');self.assertFalse(receipt['executionVerified'])

 def test_multifile_source_gate_checks_returned_editor_module_api(self):
  from project_archive import project_markdown
  transform='https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/controls/TransformControls.js'
  files=[
   {'path':'index.html','language':'html','content':'<html><script type="importmap">{"imports":{"three":"'+CORE+'","editor-controls":"'+transform+'"}}</script><script type="module" src="src/editor.js"></script></html>'},
   {'path':'src/editor.js','language':'javascript','content':'import {TransformControls as Gizmo} from "editor-controls";const tool=new Gizmo(camera,canvas);tool.update();'},
  ]
  state=programming_intent('Create a complete standalone HTML 3D viewer project in separate files.',[],[])
  result=candidate_contract_gate(project_markdown(files),state,[])
  self.assertEqual(result['status'],'REJECT')
  self.assertTrue(any(r.startswith('unsupported-three-r160-api:') for r in result['reasons']))
  self.assertFalse(result['executionVerified'])
  files[1]['content']=files[1]['content'].replace('tool.update();','tool.updateMatrixWorld();')
  self.assertEqual(candidate_contract_gate(project_markdown(files),state,[])['status'],'PASS')

 def test_multifile_nested_module_graph_resolves_actual_parent_scope(self):
  transform='https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/controls/TransformControls.js'
  files=[
   {'path':'pages/index.html','language':'html','content':'<html><script type="importmap">{"imports":{"three":"'+CORE+'"},"scopes":{"../src/editor/":{"editor-controls":"'+transform+'"}}}</script><script type="module" src="../src/app.js"></script></html>'},
   {'path':'src/app.js','language':'javascript','content':'import "./editor/my controls.js";'},
   {'path':'src/editor/my controls.js','language':'javascript','content':'import {TransformControls as Gizmo} from "editor-controls";const tool=new Gizmo(camera,canvas);tool.updateMatrixWorld();'},
   {'path':'server.js','language':'javascript','content':'import fs from "node-fs-not-a-browser-module";'},
  ]
  self.assertEqual(module_dependency_gaps(files[0]['content'],files),[])
  files[2]['content']=files[2]['content'].replace('tool.updateMatrixWorld();','tool.update();')
  self.assertTrue(any(r.startswith('unsupported-three-r160-api:') for r in module_dependency_gaps(files[0]['content'],files)))
  files[2]['content']='import {TransformControls} from "unmapped-controls";'
  self.assertIn('unresolved-browser-module:unmapped-controls',module_dependency_gaps(files[0]['content'],files))

 def test_multifile_missing_relative_modules_and_document_maps_stay_separate(self):
  files=[
   {'path':'a/index.html','language':'html','content':'<html><script type="importmap">{"imports":{"utility":"https://example.invalid/utility.js"}}</script><script type="module" src="app.js?v=1"></script></html>'},
   {'path':'a/app.js','language':'javascript','content':'import "utility";'},
   {'path':'b/index.html','language':'html','content':'<html><script type="module" src="app.js"></script></html>'},
   {'path':'b/app.js','language':'javascript','content':'import "utility";'},
  ]
  self.assertIn('unresolved-browser-module:utility',module_dependency_gaps('',files))
  files[3]['content']='import "./missing.js";'
  self.assertEqual(module_dependency_gaps('',files),['missing-project-module:b/missing.js'])

 def test_source_declared_vite_react_tsx_graph_requires_build_verification(self):
  files=[
   {'path':'index.html','language':'html','content':'<html><script type="module" src="src/main.tsx"></script></html>'},
   {'path':'src/main.tsx','language':'typescript','content':'import React from "react";import App from "./App";'},
   {'path':'package.json','language':'json','content':json.dumps({'dependencies':{'react':'^18.3.0'},'devDependencies':{'vite':'^5.4.0'},'scripts':{'build':'vite build','dev':'vite'}})},
  ]
  self.assertEqual(module_dependency_gaps('',files),[])
  # A compiler-driven dist entry is also source awaiting a build, not evidence
  # that the absent generated file was successfully emitted or executed.
  files[0]['content']='<html><script type="module" src="dist/main.js"></script></html>'
  for package_name,script in (('vite','vite build'),('webpack','webpack --mode production'),('esbuild','esbuild src/main.tsx --bundle --outdir=dist'),('typescript','tsc')):
   with self.subTest(package=package_name):
    files[2]['content']=json.dumps({'devDependencies':{package_name:'^1.0.0'},'scripts':{'build':script}})
    self.assertEqual(module_dependency_gaps('',files),[])

 def test_arbitrary_package_metadata_and_script_text_do_not_bypass_browser_checks(self):
  for package in (
   {'name':'vite','scripts':{'build':'vite build'}},
   {'devDependencies':{'vite':'^5.0.0'},'scripts':{'build':'mybuild'}},
   {'devDependencies':{'vite':'^5.0.0'},'scripts':{'mybuild':'vite build'}},
   {'devDependencies':{'vite':'^5.0.0'},'scripts':{'build':'echo vite build'}},
   {'devDependencies':{'vite':'^5.0.0'},'scripts':{'build':'vite --version'}},
   {'devDependencies':{'typescript':'^5.0.0'},'scripts':{'build':'tsc --noEmit'}},
   {'devDependencies':{'vite':'^5.0.0'},'scripts':{'build':'node -e \'console.log("vite build")\''}},
   {'devDependencies':{'typescript':'^5.0.0'},'scripts':{}},
  ):
   with self.subTest(package=package):
    files=[{'path':'index.html','language':'html','content':'<html><script type="module" src="src/main.tsx"></script></html>'},
           {'path':'src/main.tsx','language':'typescript','content':'import React from "react";'},
           {'path':'package.json','language':'json','content':json.dumps(package)}]
    self.assertIn('unresolved-browser-module:react',module_dependency_gaps('',files))

 def test_build_evidence_belongs_to_nearest_html_package(self):
  built=json.dumps({'devDependencies':{'vite':'^5.0.0'},'scripts':{'build':'vite build'}})
  files=[{'path':'web/index.html','language':'html','content':'<html><script type="module" src="main.js"></script></html>'},
         {'path':'web/main.js','language':'javascript','content':'import "unmapped";'},
         {'path':'tools/package.json','language':'json','content':built}]
  self.assertIn('unresolved-browser-module:unmapped',module_dependency_gaps('',files))
  files[2]['path']='package.json'
  self.assertEqual(module_dependency_gaps('',files),[])
  files.append({'path':'web/package.json','language':'json','content':'{"name":"plain-browser-project"}'})
  self.assertIn('unresolved-browser-module:unmapped',module_dependency_gaps('',files))

 def test_matching_build_command_is_recognized_in_actual_shell_position(self):
  for script in ('NODE_ENV=production vite build','npx --no-install vite build','npm exec vite -- build','echo preparing && vite build'):
   with self.subTest(script=script):
    files=[{'path':'index.html','language':'html','content':'<html><script type="module" src="dist/main.js"></script></html>'},
           {'path':'package.json','language':'json','content':json.dumps({'devDependencies':{'vite':'^5.0.0'},'scripts':{'build':script}})}]
    self.assertEqual(module_dependency_gaps('',files),[])

if __name__=='__main__':unittest.main()
