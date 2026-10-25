"""Source-only editor contracts; browser behavior is independently verified.

Fixtures below are tiny lexical examples, not working editors or model prompts.
"""
import unittest

from application_capabilities import apply_application_contract, application_source_gaps, infer_application_capabilities
from brain_programming import candidate_contract_gate, programming_intent
from programming_repair_context import build_compact_repair_context

REQUEST = 'Now can you make a 3d model editor page'


def source(js, markup=''):
    return '```html file=index.html\n<!doctype html><html><head><title>Test</title></head><body>'+markup+'<script>'+js+'</script></body></html>\n```'


# This is the semantic shape of the actual pinned7B negative trial: one
# rotating cube, camera navigation and a never-attached transform control.
VIEWER_NEGATIVE = source('''
const scene = new Scene(), cube = new Mesh(); scene.add(cube);
const controls = new OrbitControls(camera, canvas);
const transformControls = new TransformControls(camera, canvas);
transformControls.addEventListener('change', () => { renderer.render(scene,camera); });
scene.add(transformControls);
function animate() { cube.rotation.x += 0.01; controls.update(); requestAnimationFrame(animate); }
animate();
window.addEventListener('resize', () => { renderer.setSize(innerWidth,innerHeight); });
''')


class ApplicationContract(unittest.TestCase):
    def test_exact_editor_contract_and_compact_model_context_have_operations(self):
        state = programming_intent(REQUEST, [], [])
        capabilities = state['intentContract']['applicationCapabilities']
        self.assertEqual(capabilities['required'], ['create','select','transform','delete'])
        self.assertEqual(capabilities['transformModes'], ['translate','rotate','scale'])
        self.assertEqual(capabilities['scope'], 'prototype-default')
        self.assertLess(len(state['intentContract']['must'][0]), 320)
        # A long list of user requirements cannot evict the derived requirement
        # from the existing compact repair-context ten-requirement bound.
        state['intentContract']['must'] += ['Other requirement '+str(i) for i in range(20)]
        system, _, _ = build_compact_repair_context(state, 'Fix the interaction.', '')
        for operation in ('create','select','transform','delete','translate','rotate','scale'):
            self.assertIn(operation, system)
        self.assertIn('3D scene editor prototype:',system)

    def test_viewer_and_unrelated_editors_do_not_gain_scene_editor_scope(self):
        for prompt in ('Make a 3D model viewer HTML page.','Create a text editor HTML page.',
                       'Create a machine learning model editor page.', 'Create a neural model editor.'):
            with self.subTest(prompt=prompt):
                self.assertIsNone(infer_application_capabilities(prompt))
                self.assertNotIn('applicationCapabilities', programming_intent(prompt,[],[]).get('intentContract',{}))

    def test_explicit_narrowing_changes_only_requested_capabilities(self):
        for phrase, required, modes in (
            ('selection only',['select'],[]),
            ('only move objects',['select','transform'],['translate']),
            ('only rotate and scale objects',['select','transform'],['rotate','scale']),
            ('without adding/deleting objects',['select','transform'],['translate','rotate','scale']),
            ('with no rotation',['create','select','transform','delete'],['translate','scale']),
            ('with no transformations',['create','select','delete'],[]),
        ):
            with self.subTest(phrase=phrase):
                cap=infer_application_capabilities('Make a 3D scene editor '+phrase+'.')
                self.assertEqual(cap['required'],required);self.assertEqual(cap['transformModes'],modes)
                self.assertEqual(cap['scope'],'explicit-narrowing')
        full=infer_application_capabilities('Make a 3D editor in HTML only with buttons.')
        self.assertEqual(full['scope'],'prototype-default')

    def test_narrow_followup_replaces_default_and_unrelated_followup_preserves_it(self):
        contract=apply_application_contract({'must':['Keep theme.']}, REQUEST)
        narrowed=apply_application_contract(contract,'Only move objects.')
        self.assertEqual(narrowed['applicationCapabilities']['required'],['select','transform'])
        self.assertEqual(narrowed['applicationCapabilities']['transformModes'],['translate'])
        self.assertNotIn('create,',narrowed['must'][0]);self.assertEqual(narrowed['must'][1], 'Keep theme.')
        self.assertEqual(apply_application_contract(narrowed,'Fix the event handler.'),narrowed)


class ApplicationSourceEvidence(unittest.TestCase):
    def setUp(self):
        self.contract=programming_intent(REQUEST, [], [])['intentContract']

    def test_actual_viewer_shape_is_not_a_successful_editor(self):
        result=candidate_contract_gate(VIEWER_NEGATIVE,programming_intent(REQUEST,[],[]),[])
        self.assertEqual(result['status'],'REJECT');self.assertFalse(result['executionVerified'])
        for key in ('create','select','transform','delete'):
            self.assertIn('missing-editor-source-capability:'+key,result['reasons'])
        self.assertIn('missing-editor-source-transform:rotate',result['reasons'])

    def test_bound_custom_engine_numeric_operations_have_source_evidence(self):
        candidate=source('''
let selected = null; const objects = [];
function addObject() { const entity = new Entity(); objects.push(entity); selected = entity; }
function selectObject() { selected = objects[0]; }
function removeObject() { objects.splice(objects.indexOf(selected),1); selected=null; }
addButton.addEventListener('click', addObject);
selectButton.onclick = selectObject;
deleteButton.addEventListener('click', () => removeObject());
x.oninput = e => { selected.position.x = Number(e.target.value); };
r.oninput = e => { selected.rotation.set(0,Number(e.target.value),0); };
s.oninput = e => { selected.scale.setScalar(Number(e.target.value)); };
''')
        self.assertEqual(application_source_gaps(candidate,self.contract),[])
        result=candidate_contract_gate(candidate,programming_intent(REQUEST,[],[]),[])
        self.assertEqual(result['status'],'PASS');self.assertFalse(result['executionVerified'])

    def test_animation_comments_ui_labels_and_dom_classes_are_not_editing(self):
        candidate=source('''
// addButton.onclick = () => { objects.push(new Mesh()); selected=objects[0]; scene.remove(selected); selected.position.x=1; selected.rotation.x=1; selected.scale.x=2; };
function animate() { selected.position.x=1; selected.rotation.x=1; selected.scale.x=2; }
button.addEventListener('click', () => { button.classList.add('active'); button.classList.remove('pending'); });
''','<button>Add Select Delete Translate Rotate Scale</button>')
        gaps=application_source_gaps(candidate,self.contract)
        for key in ('create','select','transform','delete'):
            self.assertIn('missing-editor-source-capability:'+key,gaps)

    def test_inline_handlers_and_separate_js_files_are_read(self):
        candidate=source('', '<button onclick="addObject()">Add</button>')+'\n```javascript file=editor.js\n'+'''
let selected; const objects=[];
function addObject(){objects.push({});selected=objects[0];}
canvas.addEventListener('pointerdown',()=>{selected=objects[0];});
deleteButton.onclick=()=>{objects.splice(0,1);};
x.oninput=()=>{selected.position.x=1;selected.rotation.x=1;selected.scale.x=2;};
'''+'\n```'
        self.assertEqual(application_source_gaps(candidate,self.contract),[])

    def test_attached_gizmo_modes_are_optional_alternative_to_numeric_forms(self):
        candidate=source('''
function addMesh(){scene.add(new Mesh());}
addButton.onclick=addMesh;
canvas.addEventListener('pointerdown',()=>{selected=hits[0];gizmo.attach(selected);});
deleteButton.onclick=()=>{scene.remove(selected);};
mode.onchange=()=>{gizmo.setMode(mode.value);};
''','<select><option value="translate">Move</option><option value="rotate">Rotate</option><option value="scale">Scale</option></select>')
        self.assertEqual(application_source_gaps(candidate,self.contract),[])
        candidate=candidate.replace('gizmo.attach(selected);','')
        self.assertIn('missing-editor-source-capability:transform',application_source_gaps(candidate,self.contract))

    def test_narrow_scope_is_not_forced_to_full_editor(self):
        state=programming_intent('Make a 3D model editor HTML page with selection only.',[],[])
        candidate=source("canvas.addEventListener('pointerdown',()=>{selected=objects[0];});")
        self.assertEqual(candidate_contract_gate(candidate,state,[])['status'],'PASS')
        state=programming_intent('Make a 3D model editor HTML page only moving objects.',[],[])
        candidate=source("canvas.onclick=()=>{selected=objects[0];};x.oninput=()=>{selected.position.x=1;};")
        self.assertEqual(candidate_contract_gate(candidate,state,[])['status'],'PASS')


if __name__=='__main__':
    unittest.main()
