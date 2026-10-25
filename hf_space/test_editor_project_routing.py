"""Owner-export regressions for routing, project boundaries and source checks.

These deterministic checks do not prove model/editor runtime competence.
"""
import copy
import unittest

from brain_programming import (
    _code_fingerprint, _literal_ui_text, candidate_contract_gate,
    programming_intent, programming_library_context,
)
from response_cognition import classify_response_cognition, requests_web_source

VIEWER_REQUEST = 'Can you do a 3d model viewer html page for me'
HEADING_REQUEST = 'Now can you add text to the top saying §wyrlz of that 3d model viewer'
EDITOR_REQUEST = 'Now can you make a 3d model editor page'
HTML = '<!DOCTYPE html><html><head><title>Viewer</title></head><body><canvas></canvas><script>window.ready=true;</script></body></html>'
FENCED = '```html file=index.html\n'+HTML+'\n```'
HASH = 'a'*64


def owned_history(source=FENCED):
    return [{'id':'user-viewer','role':'user','text':VIEWER_REQUEST},
            {'id':'assistant-viewer','role':'assistant','text':source,
             'meta':{'codeArtifactId':'artifact-viewer','artifactRevision':1,
                     'artifactSourceHash':HASH,'artifactSourceSnapshot':source}}]


def heading_state():
    history=owned_history()
    prior=programming_intent(VIEWER_REQUEST,[],[])
    return programming_intent(HEADING_REQUEST,history,[],prior)


class EditorProjectRouting(unittest.TestCase):
    def test_exact_export_sequence_routes_editor_to_new_guardable_web_project(self):
        history=owned_history();viewer=programming_intent(VIEWER_REQUEST,[],[])
        heading=programming_intent(HEADING_REQUEST,history,[],viewer)
        self.assertTrue(heading['codingTask'])
        self.assertEqual(heading['intentContract']['languageContract']['requiredLanguages'],['html'])
        self.assertEqual(heading['intentContract']['literalUiText'],[
            {'text':'§wyrlz','target':'heading','source':'locator-bounded'}])
        history += [{'role':'user','text':HEADING_REQUEST},
                    {'id':'assistant-heading','role':'assistant','text':'Updated the heading.',
                     'meta':{'codeArtifactId':'artifact-viewer','artifactRevision':2,
                             'artifactSourceHash':'b'*64,'artifactSourceSnapshot':FENCED}}]
        editor=programming_intent(EDITOR_REQUEST,history,[],heading)
        self.assertTrue(editor['codingTask']);self.assertTrue(editor['newProject'])
        self.assertEqual(editor['changeClass'],'create');self.assertEqual(editor['projectContext'],'new')
        self.assertEqual(editor['intentContract']['originalRequest'],EDITOR_REQUEST)
        self.assertEqual(editor['intentContract']['languageContract']['requiredLanguages'],['html'])
        self.assertFalse(editor['intentContract']['languageContract']['explicit'])
        self.assertEqual(editor['intentContract']['literalUiText'],[])
        self.assertFalse(editor['artifactMutationRequested']);self.assertFalse(editor['artifactContinuation'])
        self.assertEqual(editor.get('artifactEditSource',''),'');self.assertEqual(editor['artifactTargetId'],'')
        cognition=classify_response_cognition(EDITOR_REQUEST,history,editor)
        self.assertEqual(cognition['deliverable'],'code');self.assertEqual(cognition['relation'],'standalone')
        self.assertIn('TransformControls',programming_library_context(editor))

    def test_heading_updates_owned_viewer_without_manual_pin(self):
        state=heading_state()
        self.assertTrue(state['artifactContinuation']);self.assertTrue(state['artifactMutationRequested'])
        self.assertEqual(state['artifactTargetId'],'artifact-viewer')
        self.assertEqual(state['baseRevision'],1);self.assertEqual(state['baseSourceHash'],HASH)
        self.assertEqual(state['artifactEditSource'],FENCED)
        self.assertEqual(state['intentContract']['originalRequest'],VIEWER_REQUEST)
        self.assertEqual(state['intentContract']['currentInstruction'],HEADING_REQUEST)

    def test_raw_code_history_does_not_invent_persistent_mutation_identity(self):
        history=[{'role':'user','text':VIEWER_REQUEST},{'role':'assistant','text':FENCED}]
        state=programming_intent(HEADING_REQUEST,history,[],programming_intent(VIEWER_REQUEST,[],[]))
        self.assertTrue(state['codingTask']);self.assertFalse(state['artifactMutationRequested'])
        self.assertEqual(state['artifactTargetId'],'')
        for incomplete in ({'codeArtifactId':'artifact-viewer'},
                           {'codeArtifactId':'artifact-viewer','artifactRevision':1,'artifactSourceHash':'bad'}):
            bad=owned_history();bad[1]['meta']=incomplete
            self.assertEqual(programming_intent(HEADING_REQUEST,bad,[])['artifactTargetId'],'')

    def test_explicit_conversion_is_an_edit_but_new_goal_with_reference_is_separate(self):
        for prompt in ('Turn this viewer into a 3d model editor page',
                       'Now can you make this viewer into a 3d editor page'):
            with self.subTest(prompt=prompt):
                state=programming_intent(prompt,owned_history(),[],heading_state())
                self.assertFalse(state['newProject']);self.assertTrue(state['artifactMutationRequested'])
                self.assertEqual(state['artifactTargetId'],'artifact-viewer')
        state=programming_intent('Create another editor page using that viewer colors.',owned_history(),[],heading_state())
        self.assertTrue(state['newProject']);self.assertEqual(state['artifactTargetId'],'')

    def test_new_project_does_not_inherit_repair_or_pinned_project_constraints(self):
        old=heading_state();old['failureEvidence']={'kind':'execution-failure'}
        old['failureHistory']=[{'categories':['dependency-error']}]
        old['repairConstraints']={'unavailableDependencies':['old-library']}
        old['behaviorLedger']={'knownPassingCases':['viewer-only-feature']}
        pin={'artifactType':'code','artifactId':'artifact-viewer','artifactRevision':1,
             'artifactSourceHash':HASH,'text':FENCED}
        state=programming_intent(EDITOR_REQUEST,owned_history(),[pin],old)
        self.assertIsNone(state['failureEvidence']);self.assertEqual(state['failureHistory'],[])
        self.assertEqual(state['repairConstraints']['unavailableDependencies'],[])
        self.assertNotIn('viewer-only-feature',str(state['behaviorLedger']))
        self.assertEqual(state['intentContract']['literalUiText'],[])

    def test_application_page_nouns_do_not_require_html_but_media_stays_media(self):
        for prompt in ('Create a 3D editor page','Make a model viewer page','Build a calculator page',
                       'Create a page to edit models','Can you do a model editor page'):
            with self.subTest(prompt=prompt):
                state=programming_intent(prompt,[],[])
                self.assertTrue(state['codingTask']);self.assertTrue(requests_web_source(prompt))
                self.assertEqual(state['intentContract']['languageContract']['requiredLanguages'],['html'])
        for prompt,medium in (
                ('Create a 3D mesh for an editor page','3d-asset'),
                ('Create a rigged 3D character model for a viewer page','3d-asset'),
                ('Create a music track for my editor page','audio'),
                ('Write a page about a 3D editor','text'),
                ('Write a poem about HTML','text')):
            with self.subTest(prompt=prompt):
                self.assertFalse(requests_web_source(prompt))
                self.assertEqual(classify_response_cognition(prompt)['deliverable'],medium)
                self.assertFalse(programming_intent(prompt,[],[])['codingTask'])

    def test_chosen_framework_is_not_replaced_by_inferred_html(self):
        state=programming_intent('Build a React 3D editor page in TypeScript',[],[])
        self.assertEqual(state['intentContract']['languageContract']['requiredLanguages'],['typescript'])
        self.assertNotIn('html',state['intentContract']['languageContract']['requiredLanguages'])
        for text in ('Create an offline 3D editor page','Create a 3D editor page using Babylon.js',
                     'Create a 3D editor page with no external libraries'):
            self.assertEqual(programming_library_context(programming_intent(text,[],[])),'')

    def test_full_mandatory_request_and_artifact_source_are_not_clipped(self):
        prompt='Create an HTML page. '+('Preserve the supplied behavior. '*160)+' Keep the final requirement.'
        state=programming_intent(prompt,[],[])
        self.assertEqual(state['intentContract']['originalRequest'],prompt)
        source=FENCED.replace('</body>','<!--'+'x'*13000+'--></body>')
        state=programming_intent(HEADING_REQUEST,owned_history(source),[],state)
        self.assertEqual(state['artifactEditSource'],source)


class CompleteProjectGate(unittest.TestCase):
    def test_inferred_html_requirement_rejects_js_substitution(self):
        state=programming_intent(EDITOR_REQUEST,[],[])
        result=candidate_contract_gate('```javascript\nconsole.log("editor");\n```',state,[])
        self.assertIn('missing-required-language:html',result['reasons'])
        self.assertEqual(result['status'],'REJECT');self.assertFalse(result['executionVerified'])

    def test_actual_export_partial_and_unclosed_or_unsafe_files_reject(self):
        state=programming_intent(EDITOR_REQUEST,[],[])
        for source,reason in (
                ('```html\n<html><body><div class','unclosed-code-fence'),
                ('```html\n<html><body><div class\n```','unfinished-html-token'),
                ('```html file=../index.html\n'+HTML+'\n```','invalid-project-files:'),
                ('```html\n<html><body><div></body></html>\n```','unclosed-html-element:div')):
            with self.subTest(reason=reason):
                result=candidate_contract_gate(source,state,[])
                self.assertEqual(result['status'],'REJECT')
                self.assertTrue(any(item.startswith(reason) for item in result['reasons']),result)

    def test_multifile_html_entry_after_docs_and_css_with_json_support(self):
        state=programming_intent('Create an editor page project in separate HTML, CSS and JavaScript files.',[],[])
        source=('````markdown file=README.md\nRun locally.\n```sh\npython -m http.server\n```\n````\n'
                '```css file=styles.css\nbody{margin:0}\n```\n'
                '```json file=scene.json\n{"objects":[]}\n```\n'
                '```html file=index.html\n'+HTML.replace('window.ready=true;','window.ready=true; const marker="```";')+'\n```\n'
                '```javascript file=src/editor.js\nconst objects=[];\n```')
        result=candidate_contract_gate(source,state,[])
        self.assertEqual(result['status'],'PASS',result)
        self.assertFalse(result['executionVerified'])
        changed=source.replace('const objects=[];','const objects=[1];')
        self.assertNotEqual(_code_fingerprint(source),_code_fingerprint(changed))
        self.assertEqual(_code_fingerprint(source),_code_fingerprint(source.replace('Run locally.','Run in a browser.')))

    def test_corrupt_json_and_explicit_single_file_constraints_reject(self):
        source=FENCED+'\n```json file=scene.json\n{\n```'
        result=candidate_contract_gate(source,programming_intent('Create an editor page project.',[],[]),[])
        self.assertIn('invalid-json-project-file:scene.json',result['reasons'])
        result=candidate_contract_gate(FENCED+'\n```css file=styles.css\nbody{}\n```',
                                       programming_intent('Create a single-file HTML editor page.',[],[]),[])
        self.assertIn('single-file-request-has-multiple-files',result['reasons'])

    def test_requested_literal_heading_is_exact_and_location_is_not_text(self):
        state=heading_state()
        good=FENCED.replace('<canvas>','<h1>§wyrlz</h1><canvas>')
        self.assertEqual(candidate_contract_gate(good,state,[])['status'],'PASS')
        for bad in (good.replace('<h1>§wyrlz</h1>','<h1>§wyrlz of that 3d model viewer</h1>'),
                    good.replace('<h1>§wyrlz</h1>','<h1>Swyrlz</h1>'),
                    good.replace('<title>Viewer</title>','<title>§wyrlz</title>').replace('<h1>§wyrlz</h1>','<h1>Wrong</h1>')):
            self.assertIn('literal-ui-text-mismatch:§wyrlz',candidate_contract_gate(bad,state,[])['reasons'])

    def test_exact_literal_is_an_early_actionable_model_requirement_and_retry(self):
        from programming_repair_context import build_compact_repair_context,contract_rejection_context
        state=heading_state()
        requirement=state['intentContract']['must'][0]
        self.assertIn('heading must display exactly "§wyrlz"',requirement)
        self.assertNotIn('of that 3d model viewer',requirement)
        system,_,_=build_compact_repair_context(state,HEADING_REQUEST,'CODE-DELIVERY')
        self.assertIn('heading must display exactly',system)
        bad=FENCED.replace('<canvas>','<h1>§wyrlz of that 3d model viewer</h1><canvas>')
        validation=candidate_contract_gate(bad,state,[])
        retry=contract_rejection_context(validation)
        self.assertIn('replace the entire visible text',retry)
        self.assertIn('"text":"§wyrlz"',retry)
        self.assertIn('Do not append words',retry)

    def test_both_engine_model_messages_receive_exact_literal_not_only_ambiguous_prompt(self):
        from unittest.mock import patch
        from test_github_change_model_context import load_engine
        from test_generation_completion_budget import Responses
        source=FENCED.replace('<canvas>','<h1>§wyrlz</h1><canvas>')
        payload={'prompt':HEADING_REQUEST,'history':owned_history()}
        for name in ('qwen_coder_engine','lfm2_700m_engine'):
            engine=load_engine(name);model=Responses([(source,'stop')])
            with self.subTest(engine=name),patch.object(engine,'load',return_value=model):
                events=list(engine.generate_events(payload))
                self.assertEqual(events[-1]['type'],'COMPLETED')
                policy=model.calls[0]['messages'][0]['content']
                self.assertIn('Exact visible UI text: heading must display exactly',policy)
                self.assertIn('Do not append wording outside this literal',policy)

    def test_quoted_literals_keep_phrase_case_and_unrelated_target_requirements(self):
        prompt='Add heading text saying "Go on that viewer" to the top.'
        self.assertEqual(_literal_ui_text(prompt)[0]['text'],'Go on that viewer')
        state=programming_intent('Add button text saying "Save" to that viewer.',owned_history(),[],heading_state())
        values={(item['target'],item['text']) for item in state['intentContract']['literalUiText']}
        self.assertIn(('heading','§wyrlz'),values);self.assertIn(('button','Save'),values)

    def test_literal_in_comments_or_readme_does_not_satisfy_visible_heading(self):
        state=heading_state()
        bad=FENCED.replace('window.ready=true;',"// el.textContent='§wyrlz';\nwindow.ready=true;")
        self.assertIn('literal-ui-text-mismatch:§wyrlz',candidate_contract_gate(bad,state,[])['reasons'])
        bad += '\n```markdown file=README.md\n<h1>§wyrlz</h1>\n```'
        self.assertIn('literal-ui-text-mismatch:§wyrlz',candidate_contract_gate(bad,state,[])['reasons'])
        dynamic=FENCED.replace('window.ready=true;',"document.body.textContent='§wyrlz';")
        self.assertEqual(candidate_contract_gate(dynamic,state,[])['status'],'PASS')


if __name__=='__main__':
    unittest.main()
