"""Human behavior requirements reach real engine model messages; no quality claim."""
import unittest
from unittest.mock import patch

from brain_programming import programming_intent
from programming_repair_context import project_delivery_policy, contract_rejection_context
from test_github_change_model_context import load_engine
from test_generation_completion_budget import Responses


REQUEST='Now can you make a 3d model editor page'
# An intentionally insufficient source response. Tests inspect policy delivery,
# not accepted runtime behavior; no editor implementation is supplied as input.
NO_EDITOR='```html\n<!doctype html><html><head><title>Editor</title></head><body><p>Editor</p></body></html>\n```'


class ApplicationDeliveryPolicy(unittest.TestCase):
    def test_default_contract_becomes_operational_behavior(self):
        policy=project_delivery_policy(programming_intent(REQUEST,[],[]),REQUEST)
        self.assertIn('APPLICATION ACCEPTANCE:',policy)
        for text in ['actual editable objects to the 3D scene at runtime',
                     'choose which existing scene object is selected',
                     'Newly created objects must also be selectable',
                     'change its position','change its orientation','change its size',
                     'on the selected scene object only',
                     'remove only the selected scene object',
                     'Other objects must remain available',
                     'camera movement alone cannot satisfy']:
            self.assertIn(text,policy)
        # Behavioral requirements contain no prepared editor algorithm or API.
        for implementation in ['Raycaster','TransformControls','scene.add(','.attach(','.position.x']:
            self.assertNotIn(implementation,policy)

    def test_explicit_narrowing_does_not_reintroduce_excluded_features(self):
        for phrase, included, excluded in [
            ('with selection only.',['Object selection:'],
                ['Object creation:','Selected-object transformation:','Selected-object deletion:']),
            ('only moving objects.',['Object selection:','change its position'],
                ['Object creation:','change its orientation','change its size','Selected-object deletion:']),
            ('only rotate and scale objects.',['Object selection:','change its orientation','change its size'],
                ['Object creation:','change its position','Selected-object deletion:']),
        ]:
            prompt='Make a 3D scene editor HTML page '+phrase
            policy=project_delivery_policy(programming_intent(prompt,[],[]),prompt)
            with self.subTest(prompt=prompt):
                for text in included:self.assertIn(text,policy)
                for text in excluded:self.assertNotIn(text,policy)

    def test_source_repair_feedback_translates_only_observed_missing_operations(self):
        context=contract_rejection_context({'reasons':[
            'missing-editor-source-capability:select',
            'missing-editor-source-capability:transform',
            'missing-editor-source-transform:rotate',
            'missing-editor-source-capability:delete']})
        self.assertIn('APPLICATION ACCEPTANCE — SOURCE REPAIR:',context)
        for text in ['choose which existing scene object is selected','change its orientation',
                     'remove only the selected scene object','not an execution receipt']:
            self.assertIn(text,context)
        for text in ['Object creation:','change its position','change its size']:
            self.assertNotIn(text,context)
        mode_only=contract_rejection_context({'reasons':['missing-editor-source-transform:scale']})
        self.assertIn('change its size',mode_only)
        self.assertNotIn('Object selection:',mode_only)
        ignored=contract_rejection_context({'reasons':['missing-editor-source-capability:invented']})
        self.assertNotIn('APPLICATION ACCEPTANCE',ignored)

    def test_other_application_types_and_review_do_not_gain_editor_requirements(self):
        for prompt in ['Create a 3D viewer HTML page.','Create a text editor HTML page.']:
            self.assertNotIn('APPLICATION ACCEPTANCE',project_delivery_policy(programming_intent(prompt,[],[]),prompt))
        state=programming_intent(REQUEST,[],[])
        self.assertEqual(project_delivery_policy({**state,'changeClass':'review'},'Review it.'),'')

    def test_file_metadata_is_explicitly_on_the_opening_line_for_all_source_stacks(self):
        for prompt in ['Create an HTML project in separate files.',
                       'Create a Kotlin Android project in separate files.']:
            with self.subTest(prompt=prompt):
                policy=project_delivery_policy(programming_intent(prompt,[],[]),prompt)
                for text in ['SAME physical line as the opening backticks',
                             '"```html file=index.html project=my-project"',
                             'NEXT line begins the actual HTML file contents',
                             'including non-web source/config files',
                             'Never put bare file=',
                             'inside the file body',
                             'becomes literal source']:
                    self.assertIn(text,policy)

    def test_missing_module_feedback_explains_filename_protocol_without_inventing_source(self):
        feedback=contract_rejection_context({'reasons':['missing-project-module:editor.js']})
        for text in ['PROJECT FILE PROTOCOL CORRECTION:',
                     'exact resolved relative path',
                     'same physical line as the opening backticks',
                     'The next line is actual source code',
                     'does not remove those lines, invent a missing module or repair the code',
                     'not a runtime or build result']:
            self.assertIn(text,feedback)
        self.assertIn('missing-project-module:editor.js',feedback)
        self.assertNotIn('scene.add(',feedback)
        self.assertNotIn('PROJECT FILE PROTOCOL CORRECTION:',
                         contract_rejection_context({'reasons':['missing-required-language:html']}))

    def test_module_filename_protocol_repair_reaches_both_real_engine_calls(self):
        prompt='Create a small HTML project in separate files with src/app.js.'
        bad=('```html file=index.html\n<!doctype html><html><body>'
             '<script type="module" src="src/app.js"></script></body></html>\n```')
        good=bad+'\n```javascript file=src/app.js\ndocument.body.dataset.ready="true";\n```'
        for name in ['qwen_coder_engine','lfm2_700m_engine']:
            engine=load_engine(name)
            model=Responses([(bad,'stop'),(good,'stop')])
            with self.subTest(engine=name),patch.object(engine,'load',return_value=model):
                events=list(engine.generate_events({'prompt':prompt,'history':[]}))
            self.assertGreaterEqual(len(model.calls),2)
            self.assertIn('SAME physical line as the opening backticks',
                          model.calls[0]['messages'][0]['content'])
            self.assertIn('PROJECT FILE PROTOCOL CORRECTION:',
                          model.calls[1]['messages'][-1]['content'])
            self.assertIn('missing-project-module:src/app.js',
                          model.calls[1]['messages'][-1]['content'])
            self.assertEqual(events[-1]['type'],'COMPLETED')

    def test_both_real_engine_message_builders_deliver_default_and_narrow_policy(self):
        for name in ['qwen_coder_engine','lfm2_700m_engine']:
            engine=load_engine(name)
            for prompt,narrow in [(REQUEST,False),('Make a 3D model editor HTML page only moving objects.',True)]:
                model=Responses([(NO_EDITOR,'stop')])
                with self.subTest(engine=name,prompt=prompt),patch.object(engine,'load',return_value=model):
                    events=list(engine.generate_events({'prompt':prompt,'history':[]}))
                self.assertTrue(model.calls)
                initial=model.calls[0]['messages'][0]['content']
                self.assertIn('APPLICATION ACCEPTANCE:',initial)
                self.assertIn('choose which existing scene object is selected',initial)
                self.assertIn('change its position',initial)
                if narrow:
                    self.assertNotIn('Object creation:',initial)
                    self.assertNotIn('change its orientation',initial)
                    self.assertNotIn('Selected-object deletion:',initial)
                else:
                    self.assertIn('Object creation:',initial)
                    self.assertIn('Selected-object deletion:',initial)
                # Actual source rejection also reaches subsequent model calls.
                self.assertGreater(len(model.calls),1)
                retry=model.calls[1]['messages'][-1]['content']
                self.assertIn('APPLICATION ACCEPTANCE — SOURCE REPAIR:',retry)
                self.assertEqual(next(e['validation'] for e in events if e['type']=='CANDIDATE_VALIDATION')['status'],'REJECT')


if __name__=='__main__':unittest.main()
