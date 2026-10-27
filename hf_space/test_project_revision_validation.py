"""Changed-file model replies are checked against the complete saved project."""
import unittest
from unittest.mock import patch

from brain_programming import candidate_contract_gate, programming_intent
from project_archive import project_markdown
from test_generation_completion_budget import Responses
from test_github_change_model_context import load_engine


FILES = [
    {"path":"index.html","language":"html","content":'<html><head><link rel="stylesheet" href="styles.css"></head><body><button id="count">0</button><script type="module" src="src/app.js"></script></body></html>\n'},
    {"path":"styles.css","language":"css","content":"button { color: green; }\n"},
    {"path":"src/app.js","language":"javascript","content":"let count=0; document.getElementById('count').onclick=()=>count++;\n"},
    {"path":"README.md","language":"markdown","content":"# Counter\nServe the project root locally.\n"},
]
DELTA="```javascript file=src/app.js\nlet count=2; document.getElementById('count').onclick=()=>count++;\n```"


def state(files=FILES):
    result=programming_intent('Create an HTML page with CSS and JavaScript for a counter.',[],[])
    result.update({"artifactMutationRequested":True,"artifactContinuation":True,
        "artifactTargetId":"owned-project","artifactEditSource":project_markdown(files),
        "baseRevision":1,"baseSourceHash":"a"*64,"newProject":False,"projectContext":"existing"})
    return result


class ProjectRevisionValidation(unittest.TestCase):
    def test_ordinary_project_edit_verbs_resolve_saved_history_without_a_manual_pin(self):
        history=[{'role':'user','text':'Create an HTML project with CSS and JavaScript.'},
            {'id':'saved-message','role':'assistant','text':'The project files are saved.',
             'meta':{'codeArtifactId':'owned-project','artifactRevision':1,
                     'artifactSourceHash':'a'*64,'artifactSourceSnapshot':project_markdown(FILES)}}]
        for verb in ('update','edit','change','modify','revise','continue'):
            with self.subTest(verb=verb):
                result=programming_intent('Now '+verb+' src/app.js in this project so count starts at2.',history,[])
                self.assertEqual(result['changeClass'],'feature',result)
                self.assertTrue(result['artifactMutationRequested'],result)
                self.assertEqual(result['artifactTargetId'],'owned-project')
        result=programming_intent('Explain how to edit this project.',history,[])
        self.assertEqual(result['changeClass'],'explain',result)
        self.assertFalse(result['artifactMutationRequested'])

    def test_named_javascript_only_update_preserves_html_language_and_module_contract(self):
        check=candidate_contract_gate(DELTA,state(),[])
        self.assertEqual(check["status"],"PASS",check)
        self.assertEqual(check["projectRevisionFileCount"],4)
        self.assertIn("html",check["detectedLanguages"])
        self.assertFalse(check["executionVerified"])

    def test_missing_dependency_in_changed_module_is_checked_in_final_file_tree(self):
        delta=DELTA.replace('let count=2;',"import {value} from './missing.js'; let count=value;")
        check=candidate_contract_gate(delta,state(),[])
        self.assertEqual(check["status"],"REJECT")
        self.assertTrue(any(reason.startswith('missing-project-module:') for reason in check["reasons"]),check)

    def test_ambiguous_filenames_and_unfinished_raw_fences_cannot_be_hidden_by_merge(self):
        for delta in (DELTA.replace(' file=src/app.js',''),DELTA.rsplit('```',1)[0]):
            check=candidate_contract_gate(delta,state(),[])
            self.assertEqual(check["status"],"REJECT",check)
            self.assertTrue(any(reason.startswith(('invalid-project-revision:','unclosed-code-fence')) for reason in check["reasons"]),check)

    def test_preserved_old_comment_is_not_a_new_placeholder_but_new_stub_is_rejected(self):
        prior=[dict(item) for item in FILES]
        prior[1]['content']='/* TODO: unrelated legacy theme work */\n'+prior[1]['content']
        self.assertEqual(candidate_contract_gate(DELTA,state(prior),[])["status"],"PASS")
        check=candidate_contract_gate(DELTA.replace('let count=2;','// TODO: implement counter\nlet count=2;'),state(prior),[])
        self.assertIn('unfinished-implementation-placeholder',check['reasons'])

    def test_new_project_never_borrows_the_previous_project_files(self):
        check=candidate_contract_gate(DELTA,{**state(),"newProject":True},[])
        self.assertIsNone(check['projectRevisionFileCount'])
        self.assertIn('missing-required-language:html',check['reasons'])

    def test_both_actual_engine_loops_accept_one_complete_changed_file(self):
        for name in ('lfm2_700m_engine','qwen_coder_engine'):
            engine=load_engine(name)
            model=Responses([(DELTA,'stop')])
            with self.subTest(engine=name),patch.object(engine,'load',return_value=model):
                events=list(engine.generate_events({'prompt':'Update src/app.js in this project so count starts at2.',
                    'history':[],'programmingIntent':state()}))
            self.assertEqual(len(model.calls),1)
            self.assertEqual(events[-1]['type'],'COMPLETED')
            self.assertEqual(next(event['validation'] for event in events if event['type']=='CANDIDATE_VALIDATION')['status'],'PASS')
            self.assertEqual(''.join(event.get('text','') for event in events if event['type']=='DELTA'),DELTA)


if __name__=='__main__':
    unittest.main()
