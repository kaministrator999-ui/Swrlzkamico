"""Controlled review/repair protocol tests; never model or UI acceptance."""
import copy
import json
import unittest
from unittest.mock import patch

from brain_programming import programming_intent
from project_archive import project_markdown
from project_review import (new_review_state, review_project_candidate,
                            review_requested, review_retry_instruction)
from test_generation_completion_budget import Responses
from test_github_change_model_context import load_engine

REQUEST = 'Build a polished HTML starter project. Include a persistent visible label for the task input.'
BAD = ('```html file=index.html\n<!doctype html><html><head><title>Tasks</title></head>'
       '<body><h1>Tasks</h1><input id="title" placeholder="Task title"></body></html>\n```')
GOOD = BAD.replace('<input id="title"', '<label for="title">Task title</label><input id="title"')
ISSUES = json.dumps({'issues':[{'requirementId':0,'observation':'The task input has a placeholder but no persistent label.',
                               'sourceQuote':'<input id="title" placeholder="Task title">'}]})
CLEAR = '{"issues":[]}'


def intent():
    return programming_intent(REQUEST,[],[])


def review(output, candidate=BAD, programming=None, state=None, finish='stop', count=lambda _:5):
    model=Responses([(output,finish)])
    result=review_project_candidate(model,candidate,programming or intent(),
        {'status':'PASS','reasons':[],'executionVerified':False},state or new_review_state(),count)
    return model,result


class ProjectReviewTest(unittest.TestCase):
    def test_only_explicit_polished_authored_projects_are_scoped(self):
        self.assertTrue(review_requested(intent()))
        for prompt in ('Create a tiny HTML page.', 'Build an HTML starter project.',
                       'Build a professional Python project.', 'Review this polished HTML project.',
                       'Build a professional HTML skeleton with placeholders.',
                       'Build a bare HTML starter project with professional wording.'):
            with self.subTest(prompt=prompt):
                self.assertFalse(review_requested(programming_intent(prompt,[],[])))

    def test_valid_criticism_is_advisory_with_private_feedback_and_bound_ids(self):
        state=new_review_state();model,result=review(ISSUES,state=state)
        self.assertEqual(result['status'],'REJECT')
        self.assertIn('model-project-review-issues',result['reasons'])
        self.assertEqual(result['projectReview']['status'],'ISSUES')
        self.assertFalse(result['executionVerified'])
        self.assertNotIn('observation',json.dumps(result))
        self.assertIn('placeholder',review_retry_instruction(state))
        self.assertEqual(model.calls[0]['max_tokens'],512)
        response=model.calls[0]['response_format']
        self.assertEqual(response['type'],'json_object')
        self.assertFalse(response['schema']['additionalProperties'])
        items=response['schema']['properties']['issues']['items']
        self.assertEqual(response['schema']['properties']['issues']['maxItems'],3)
        self.assertEqual(items['properties']['requirementId']['enum'],list(range(len(
            json.loads(model.calls[0]['messages'][1]['content'])['requirements']))))
        self.assertEqual(items['properties']['observation']['maxLength'],180)
        self.assertEqual(model.calls[0]['temperature'],0.0)

    def test_clear_review_is_not_execution_or_professional_appearance_acceptance(self):
        _,result=review(CLEAR)
        self.assertEqual(result['status'],'PASS')
        self.assertEqual(result['projectReview']['status'],'NO_CONCRETE_ISSUES')
        self.assertEqual(result['projectReview']['verification'],'MODEL_SOURCE_REVIEW_ONLY')
        self.assertFalse(result['executionVerified'])

    def test_invalid_json_invented_ids_and_quotes_cannot_be_accepted(self):
        values=['not JSON', '{"issues":[],"passed":true}',
                json.dumps({'issues':[{'requirementId':999,'observation':'Missing thing','sourceQuote':''}]}),
                json.dumps({'issues':[{'requirementId':True,'observation':'Missing thing','sourceQuote':''}]}),
                ISSUES.replace('<input id=', '<missing id=')]
        for value in values:
            with self.subTest(value=value):
                _,result=review(value)
                self.assertEqual(result['status'],'REJECT')
                self.assertEqual(result['projectReview']['status'],'INCONCLUSIVE')

    def test_length_and_unknown_finish_reject_even_complete_looking_json(self):
        for finish in ('length',None):
            with self.subTest(finish=finish):
                _,result=review(CLEAR,finish=finish)
                self.assertEqual(result['status'],'REJECT')
                self.assertEqual(result['projectReview']['finishReason'],finish)

    def test_owned_delta_reviews_the_composed_tree_without_changing_bytes(self):
        files=[{'path':'index.html','language':'html','content':'<html><head><link rel="stylesheet" href="styles.css"></head><body>Tasks<script src="src/app.js"></script></body></html>'},
               {'path':'styles.css','language':'css','content':'body { color: blue; }'},
               {'path':'src/app.js','language':'javascript','content':'let count=0;'}]
        programming=intent();programming.update(artifactMutationRequested=True,
            artifactContinuation=True,artifactTargetId='owned',baseRevision=1,baseSourceHash='a'*64,
            artifactEditSource=project_markdown(files),newProject=False)
        original=copy.deepcopy(programming)
        candidate='```javascript file=src/app.js\nlet count=1;\n```'
        model,result=review(CLEAR,candidate=candidate,programming=programming)
        payload=json.loads(model.calls[0]['messages'][1]['content'])
        self.assertIn('body { color: blue; }',payload['completeProjectSource'])
        self.assertIn('let count=1;',payload['completeProjectSource'])
        self.assertNotIn('let count=0;',payload['completeProjectSource'])
        self.assertEqual(payload['previousProjectSource'],original['artifactEditSource'])
        self.assertIn('let count=0;',payload['previousProjectSource'])
        self.assertEqual(result['projectReview']['sourceFileCount'],3)
        self.assertTrue(result['projectReview']['previousProjectSourceProvided'])
        self.assertEqual(programming,original)

    def test_new_user_changes_keep_precedence_over_old_style_requirements(self):
        programming=intent()
        programming['intentContract']['currentInstruction']='Redesign this project in red and replace the old title.'
        model,result=review(CLEAR,programming=programming)
        self.assertEqual(result['status'],'PASS')
        self.assertIn('currentInstruction overrides superseded original requirements',model.calls[0]['messages'][0]['content'])
        self.assertEqual(json.loads(model.calls[0]['messages'][1]['content'])['currentInstruction'],
                         programming['intentContract']['currentInstruction'])

    def test_continuation_edit_scope_does_not_demand_unrelated_preexisting_repairs(self):
        programming=intent();programming.update(artifactMutationRequested=True,
            artifactTargetId='owned',artifactEditSource=BAD,newProject=False)
        instruction='Only change index.html to rename the heading; preserve all other behavior.'
        programming['intentContract']['currentInstruction']=instruction
        model,result=review(CLEAR,candidate=GOOD,programming=programming)
        self.assertEqual(result['status'],'PASS')
        messages=model.calls[0]['messages'];payload=json.loads(messages[1]['content'])
        self.assertEqual(payload['currentInstruction'],instruction)
        self.assertIn('do not demand repairs to unrelated pre-existing defects',messages[0]['content'])
        self.assertIn('expand an only-change-file boundary',messages[0]['content'])
        self.assertEqual(payload['previousProjectSource'],BAD)

    def test_combined_previous_and_composed_source_limit_skips_without_truncation(self):
        programming=intent();programming.update(artifactMutationRequested=True,
            artifactTargetId='owned',artifactEditSource=BAD.replace('Tasks</h1>','x'*34000+'</h1>'),newProject=False)
        candidate=GOOD.replace('Tasks</h1>','y'*34000+'</h1>')
        model,result=review(CLEAR,candidate=candidate,programming=programming)
        self.assertEqual(result['status'],'PASS')
        self.assertEqual(result['projectReview']['status'],'NOT_RUN_CONTEXT_LIMIT')
        self.assertTrue(result['projectReview']['previousProjectSourceProvided'])
        self.assertEqual(model.calls,[])

    def test_oversized_source_and_context_are_truthful_not_run_without_truncation(self):
        for candidate,count in ((BAD.replace('Tasks</h1>','x'*66000+'</h1>'),lambda _:5),
                                (BAD,lambda _:33000)):
            model,result=review(CLEAR,candidate=candidate,count=count)
            self.assertEqual(result['status'],'PASS')
            self.assertEqual(result['projectReview']['status'],'NOT_RUN_CONTEXT_LIMIT')
            self.assertEqual(model.calls,[])
            self.assertEqual(result['projectReview']['auditsUsed'],0)

    def test_known_issues_cannot_be_bypassed_by_growing_source_or_context(self):
        for candidate,count in ((BAD.replace('Tasks</h1>','x'*66000+'</h1>'),lambda _:5),
                                (GOOD,lambda _:33000)):
            state=new_review_state()
            _,first=review(ISSUES,state=state)
            self.assertEqual(first['status'],'REJECT')
            model,result=review(CLEAR,candidate=candidate,count=count,state=state)
            self.assertEqual(result['status'],'REJECT')
            self.assertEqual(result['projectReview']['status'],'INCONCLUSIVE')
            self.assertIn('model-project-review-context-limit',result['reasons'])
            self.assertEqual(model.calls,[])

    def test_backend_review_failure_is_inconclusive_without_private_error_text(self):
        class Broken:
            def create_chat_completion(self,**kwargs):
                raise RuntimeError('sensitive backend detail')
        result=review_project_candidate(Broken(),BAD,intent(),
            {'status':'PASS','reasons':[],'executionVerified':False},new_review_state(),lambda _:5)
        self.assertEqual(result['status'],'REJECT')
        self.assertEqual(result['projectReview']['status'],'INCONCLUSIVE')
        self.assertNotIn('sensitive',json.dumps(result))

    def test_both_actual_engines_withhold_review_rejection_then_deliver_repaired_source(self):
        for name in ('qwen_coder_engine','lfm2_700m_engine'):
            with self.subTest(engine=name):
                engine=load_engine(name);model=Responses([(BAD,'stop'),(ISSUES,'stop'),(GOOD,'stop'),(CLEAR,'stop')])
                with patch.object(engine,'load',return_value=model):
                    events=list(engine.generate_events({'prompt':REQUEST,'history':[]}))
                self.assertEqual(events[-1]['type'],'COMPLETED')
                self.assertEqual(len(model.calls),4)
                self.assertEqual(''.join(e.get('text','') for e in events if e['type']=='DELTA'),GOOD)
                self.assertIn('MODEL SOURCE REVIEW ADVISORY',model.calls[2]['messages'][-1]['content'])
                self.assertNotIn('first candidate violated the deterministic',model.calls[2]['messages'][-1]['content'])
                check=next(e['validation'] for e in events if e['type']=='CANDIDATE_VALIDATION')
                self.assertFalse(check['executionVerified'])
                self.assertEqual(check['projectReview']['auditsUsed'],2)

    def test_unresolved_or_invalid_second_audit_cannot_escape_the_bound(self):
        for name in ('qwen_coder_engine','lfm2_700m_engine'):
            for second in (ISSUES,'not JSON'):
                with self.subTest(engine=name,second=second):
                    engine=load_engine(name)
                    model=Responses([(BAD,'stop'),(ISSUES,'stop'),(GOOD,'stop'),(second,'stop')])
                    with patch.object(engine,'load',return_value=model):
                        events=list(engine.generate_events({'prompt':REQUEST,'history':[]}))
                    self.assertEqual(events[-1]['type'],'FAILED')
                    self.assertEqual(len(model.calls),4)
                    visible=''.join(e.get('text','') for e in events if e['type']=='DELTA')
                    self.assertNotIn('<html>',visible)

    def test_ordinary_and_internal_json_generation_make_no_audit_calls(self):
        for name in ('qwen_coder_engine','lfm2_700m_engine'):
            engine=load_engine(name)
            for payload,output in (({'prompt':'Create a plain HTML page.','history':[]},BAD),
                                   ({'prompt':REQUEST,'history':[],'githubSourceChangeTask':'plan'},'{"summary":"checked"}')):
                with self.subTest(engine=name,payload=payload):
                    model=Responses([(output,'stop')])
                    with patch.object(engine,'load',return_value=model):
                        events=list(engine.generate_events(payload))
                    self.assertEqual(events[-1]['type'],'COMPLETED')
                    self.assertEqual(len(model.calls),1)


if __name__=='__main__':
    unittest.main()
