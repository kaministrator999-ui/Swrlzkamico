"""Real engine loops with deterministic model doubles; no model-quality claims."""
import unittest
from unittest.mock import patch

from programming_telemetry import buffered_chat_completion, completion_validation, candidate_attempt_receipt
from programming_repair_context import build_compact_repair_context, fresh_project_history, project_delivery_policy
from brain_programming import _code_fingerprint
from test_github_change_model_context import load_engine, FakeModel


COMPLETE='```html\n<!DOCTYPE html><html><head><title>Page</title></head><body><h1>Ready</h1></body></html>\n```'
PARTIAL='```html\n<!DOCTYPE html><html><body><div class'


class Responses(FakeModel):
    def __init__(self, outputs):
        super().__init__()
        self.outputs=outputs

    def create_chat_completion(self, **kwargs):
        self.calls.append(kwargs)
        text,reason=self.outputs[min(len(self.calls)-1,len(self.outputs)-1)]
        yield {'choices':[{'delta':{'content':text},'finish_reason':None}]}
        yield {'choices':[{'delta':{},'finish_reason':reason}],
               'usage':{'prompt_tokens':12,'completion_tokens':34,'total_tokens':46,'private':'never retained'}}


class CompletionBudgetTest(unittest.TestCase):
    def engines(self):
        return [load_engine(name) for name in ('qwen_coder_engine','lfm2_700m_engine')]

    def generate(self, engine, payload, outputs):
        model=Responses(outputs)
        with patch.object(engine,'load',return_value=model):
            events=list(engine.generate_events(payload))
        return model,events

    def test_actual_finish_reason_and_safe_usage_are_retained(self):
        model=Responses([(PARTIAL,'length')])
        text,timing=buffered_chat_completion(model,[{'role':'user','content':'Create a page'}],30,.3)
        self.assertEqual(text,PARTIAL)
        self.assertEqual(timing['finishReason'],'length')
        self.assertEqual(timing['requestedMaxTokens'],30)
        self.assertEqual(timing['usage'],{'prompt_tokens':12,'completion_tokens':34,'total_tokens':46})
        check=completion_validation({'status':'PASS','reasons':[],'executionVerified':False},timing)
        self.assertEqual(check['status'],'REJECT')
        self.assertIn('model-output-token-limit',check['reasons'])
        self.assertFalse(check['generationComplete'])
        self.assertFalse(check['executionVerified'])

    def test_missing_provider_finish_reason_is_unknown_not_invented_stop(self):
        model=FakeModel()
        _,timing=buffered_chat_completion(model,[],512,.3)
        self.assertIsNone(timing['finishReason'])
        self.assertIsNone(completion_validation({'status':'PASS'},timing)['generationComplete'])

    def test_a_special_worker_cannot_record_a_length_stopped_attempt_as_accepted(self):
        receipt=candidate_attempt_receipt(1,'buffered-worker',
            {'finishReason':'length','requestedMaxTokens':112},
            {'status':'PASS','reasons':[]},'source-fingerprint')
        self.assertEqual(receipt['validationStatus'],'REJECT')
        self.assertFalse(receipt['accepted'])
        self.assertIn('model-output-token-limit',receipt['validationReasons'])

    def test_truncated_coding_attempt_is_withheld_and_corrected_before_delivery(self):
        for engine in self.engines():
            with self.subTest(engine=engine.__name__):
                model,events=self.generate(engine,{'prompt':'Create a complete HTML page.','history':[]},
                                           [(PARTIAL,'length'),(COMPLETE,'stop')])
                self.assertEqual(len(model.calls),2)
                delivered=''.join(e.get('text','') for e in events if e['type']=='DELTA')
                self.assertEqual(delivered,COMPLETE)
                attempts=[e['attempt'] for e in events if e['type']=='CANDIDATE_ATTEMPT']
                self.assertIn('model-output-token-limit',attempts[0]['validationReasons'])
                self.assertEqual(attempts[0]['finishReason'],'length')
                self.assertEqual(attempts[1]['finishReason'],'stop')
                self.assertEqual(events[-1]['type'],'COMPLETED')
                self.assertFalse(any(e['type']=='FAILED' for e in events))

    def test_final_coding_length_stop_never_returns_a_complete_artifact(self):
        for engine in self.engines():
            with self.subTest(engine=engine.__name__):
                _,events=self.generate(engine,{'prompt':'Create a complete HTML page.','history':[]},[(PARTIAL,'length')])
                self.assertEqual(events[-1]['type'],'FAILED')
                self.assertEqual(events[-1]['phase'],'FAILED')
                self.assertEqual(events[-1]['reason'],'OUTPUT_TOKEN_LIMIT')
                self.assertFalse(any(e['type']=='COMPLETED' for e in events))
                self.assertNotIn(PARTIAL,''.join(e.get('text','') for e in events if e['type']=='DELTA'))
                self.assertEqual(next(e['validation'] for e in events if e['type']=='CANDIDATE_VALIDATION')['status'],'REJECT')

    def test_invalid_review_then_repeated_code_retains_outstanding_failure(self):
        from test_project_review import REQUEST, BAD, report
        invalid=report(quote='')  # Full coverage, but no literal evidence for positive requirements.
        for engine in self.engines():
            with self.subTest(engine=engine.__name__):
                model,events=self.generate(engine,{'prompt':REQUEST,'history':[]},
                    [(BAD,'stop'),(invalid,'stop'),(BAD,'stop'),(BAD,'stop')])
                self.assertEqual(len(model.calls),4)
                self.assertEqual(events[-1]['type'],'FAILED')
                self.assertEqual(events[-1]['reason'],'PROJECT_SOURCE_REVIEW_UNRESOLVED')
                self.assertFalse(any(e['type']=='COMPLETED' for e in events))
                self.assertNotIn(BAD,''.join(e.get('text','') for e in events if e['type']=='DELTA'))
                check=next(e['validation'] for e in events if e['type']=='CANDIDATE_VALIDATION')
                self.assertEqual(check['status'],'REJECT')
                self.assertIn('strategy-repeat-previous-attempt',check['reasons'])
                self.assertIn('model-project-review-outstanding',check['reasons'])
                review=check['projectReview']
                self.assertEqual(review['status'],'OUTSTANDING')
                self.assertEqual(review['auditsUsed'],1)
                self.assertEqual(review['currentCandidateReview'],'NOT_RUN_CANDIDATE_REJECTED')
                self.assertEqual(review['lastReviewedCandidate']['status'],'INCONCLUSIVE')
                self.assertNotIn('sourceSha256',review)
                self.assertIn('sourceSha256',review['lastReviewedCandidate'])
                self.assertFalse(review['executionVerified'])
                self.assertIn('MODEL SOURCE REVIEW ADVISORY',model.calls[-1]['messages'][-1]['content'])

    def test_changed_but_invalid_source_cannot_erase_an_unresolved_review(self):
        from test_project_review import REQUEST, BAD
        broken=BAD.replace('</head>','<link rel="stylesheet" href="missing.css"></head>')
        changed=broken.replace('<h1>Tasks</h1>','<h1>Updated tasks</h1>')
        for engine in self.engines():
            with self.subTest(engine=engine.__name__):
                model,events=self.generate(engine,{'prompt':REQUEST,'history':[]},
                    [(BAD,'stop'),('{"assessments":[]}','stop'),(broken,'stop'),(changed,'stop')])
                self.assertEqual(len(model.calls),4)  # Only the first candidate received an audit.
                self.assertEqual(events[-1]['reason'],'PROJECT_SOURCE_REVIEW_UNRESOLVED')
                check=next(e['validation'] for e in events if e['type']=='CANDIDATE_VALIDATION')
                self.assertIn('model-project-review-outstanding',check['reasons'])
                self.assertTrue(any('missing' in reason for reason in check['reasons']))
                self.assertEqual(check['projectReview']['auditsUsed'],1)
                self.assertEqual(check['projectReview']['lastReviewedCandidate']['status'],'INCONCLUSIVE')
                self.assertFalse(any(e['type']=='COMPLETED' for e in events))
                delivered=''.join(e.get('text','') for e in events if e['type']=='DELTA')
                self.assertNotIn('<html>',delivered)

    def test_a_valid_new_candidate_and_review_clear_the_outstanding_failure(self):
        from test_project_review import REQUEST, BAD, GOOD, report
        for engine in self.engines():
            with self.subTest(engine=engine.__name__):
                model,events=self.generate(engine,{'prompt':REQUEST,'history':[]},
                    [(BAD,'stop'),('{"assessments":[]}','stop'),(GOOD,'stop'),(report(),'stop')])
                self.assertEqual(len(model.calls),4)
                self.assertEqual(events[-1]['type'],'COMPLETED')
                self.assertFalse(any(e['type']=='FAILED' for e in events))
                self.assertEqual(''.join(e.get('text','') for e in events if e['type']=='DELTA'),GOOD)
                check=next(e['validation'] for e in events if e['type']=='CANDIDATE_VALIDATION')
                self.assertEqual(check['status'],'PASS')
                self.assertNotIn('model-project-review-outstanding',check['reasons'])
                self.assertEqual(check['projectReview']['status'],'SOURCE_ASSESSED_NO_GAPS')
                self.assertEqual(check['projectReview']['auditsUsed'],2)

    def test_final_length_stop_keeps_output_limit_reason_with_prior_review_failure(self):
        from test_project_review import REQUEST, BAD
        for engine in self.engines():
            with self.subTest(engine=engine.__name__):
                _,events=self.generate(engine,{'prompt':REQUEST,'history':[]},
                    [(BAD,'stop'),('{"assessments":[]}','stop'),(BAD,'stop'),(BAD,'length')])
                self.assertEqual(events[-1]['type'],'FAILED')
                self.assertEqual(events[-1]['reason'],'OUTPUT_TOKEN_LIMIT')
                self.assertFalse(any(e['type']=='COMPLETED' for e in events))
                check=next(e['validation'] for e in events if e['type']=='CANDIDATE_VALIDATION')
                self.assertIn('model-project-review-outstanding',check['reasons'])
                self.assertEqual(check['projectReview']['status'],'OUTSTANDING')

    def test_exhausted_ordinary_programming_rejections_are_failed(self):
        wrong='```python\nprint("Wrong language")\n```'
        for engine in self.engines():
            with self.subTest(engine=engine.__name__):
                model,events=self.generate(engine,{'prompt':'Create a complete HTML page.','history':[]},
                    [(wrong,'stop')])
                self.assertEqual(len(model.calls),3)
                self.assertEqual(events[-1]['type'],'FAILED')
                self.assertEqual(events[-1]['reason'],'PROGRAMMING_CONTRACT_UNRESOLVED')
                self.assertFalse(any(e['type']=='COMPLETED' for e in events))
                self.assertNotIn(wrong,''.join(e.get('text','') for e in events if e['type']=='DELTA'))

    def test_ordinary_non_coding_reply_keeps_its_success_terminal(self):
        answer='The lake is quiet.'
        for engine in self.engines():
            with self.subTest(engine=engine.__name__):
                model,events=self.generate(engine,{'prompt':'Describe a lake briefly.','history':[]},
                    [(answer,'stop')])
                self.assertEqual(len(model.calls),1)
                self.assertEqual(events[-1]['type'],'COMPLETED')
                self.assertFalse(any(e['type']=='FAILED' for e in events))
                self.assertEqual(''.join(e.get('text','') for e in events if e['type']=='DELTA'),answer)

    def test_non_coding_length_stop_is_failed_and_normal_budget_is_larger(self):
        for engine in self.engines():
            with self.subTest(engine=engine.__name__):
                model,events=self.generate(engine,{'prompt':'Describe a quiet lakeside sunrise.','history':[]},[('The water glows','length')])
                self.assertEqual(model.calls[0]['max_tokens'],4096)
                self.assertEqual(events[-1]['type'],'FAILED')
                self.assertEqual(events[-1]['reason'],'OUTPUT_TOKEN_LIMIT')
                self.assertFalse(any(e['type']=='COMPLETED' for e in events))
                self.assertEqual(next(e['attempt'] for e in events if e['type']=='CANDIDATE_ATTEMPT')['finishReason'],'length')

    def test_output_is_reserved_before_history_and_mandatory_text_is_preserved(self):
        for engine in self.engines():
            with self.subTest(engine=engine.__name__):
                model=FakeModel()
                history=[{'role':'assistant','content':'old message '+str(i)+'x'*24000} for i in range(8)]
                fitted,dropped,used,reserved=engine._fit_messages(model,'authoritative system',history,'exact current goal',6144)
                self.assertGreater(dropped,0)
                self.assertEqual(reserved,6144)
                self.assertEqual(fitted[0]['content'],'authoritative system')
                self.assertEqual(fitted[-1]['content'],'exact current goal')
                self.assertLessEqual(used+reserved+engine.CONTEXT_SAFETY_TOKENS,engine.CONTEXT_TOKENS)

    def test_latest_source_under_edit_is_not_silently_dropped_to_make_room(self):
        for engine in self.engines():
            with self.subTest(engine=engine.__name__):
                model=FakeModel();source='```html\n'+('x'*(engine.CONTEXT_TOKENS*4))+'\n```'
                with self.assertRaisesRegex(ValueError,'was not truncated'):
                    engine._fit_messages(model,'system',[{'role':'assistant','content':source}],'Preserve this page',6144,preserve_latest_code=True)

    def test_tilde_fenced_source_is_also_protected_and_not_a_reusable_preference(self):
        for engine in self.engines():
            with self.subTest(engine=engine.__name__):
                source='~~~html\n'+('x'*(engine.CONTEXT_TOKENS*4))+'\n~~~'
                with self.assertRaisesRegex(ValueError,'was not truncated'):
                    engine._fit_messages(FakeModel(),'system',[{'role':'assistant','content':source}],
                                         'Preserve this page',6144,preserve_latest_code=True)
        preference_with_code={'role':'user','content':'By default use this old project.\n~~~html\n<h1>Old project</h1>\n~~~'}
        self.assertEqual(fresh_project_history([preference_with_code],{'newProject':True}),[])

    def test_optional_history_after_protected_source_can_be_trimmed(self):
        for engine in self.engines():
            with self.subTest(engine=engine.__name__):
                source={'role':'assistant','content':COMPLETE}
                optional={'role':'user','content':'old log '+('x'*(engine.CONTEXT_TOKENS*4))}
                messages,dropped,_,reserved=engine._fit_messages(FakeModel(),'system',
                    [source,optional],'Keep the page and fix the current issue.',6144,preserve_latest_code=True)
                self.assertEqual(dropped,1)
                self.assertIn(source,messages)
                self.assertNotIn(optional,messages)
                self.assertEqual(reserved,6144)

    def test_repair_source_and_current_prompt_are_not_sliced(self):
        source='start source\n'+'x'*12000+'\nend source'
        system,_,telemetry=build_compact_repair_context({'codingTask':True,'failureEvidence':{'repairSource':source}},'Fix it','CODE-DELIVERY')
        self.assertIn(source,system)
        self.assertEqual(telemetry['sourceChars'],len(source))
        for engine in self.engines():
            with self.subTest(engine=engine.__name__):
                current='start request '+'x'*(engine.CONTEXT_TOKENS*4)+' end request'
                messages,_,_,reserved,fitted_prompt=engine._fit_repair_messages(FakeModel(),'canonical source',[],current,6144)
                self.assertEqual(reserved,0)
                self.assertEqual(fitted_prompt,current)
                self.assertEqual(messages[-1]['content'],current)

    def test_late_original_requirements_and_repair_directions_reach_the_budget_fitter(self):
        original='Build the project. '+'feature detail '*250+'Preserve the final export requirement.'
        direction='Repair the selected object. '+'diagnostic detail '*180+'Keep the final requested keyboard shortcut.'
        system,prompt,_=build_compact_repair_context({
            'codingTask':True,'intentContract':{'originalRequest':original},
            'repairDirection':direction,'failureEvidence':{'repairSource':'canonical complete source'},
        },direction,'CODE-DELIVERY')
        self.assertIn(original,system)
        self.assertIn(direction,system)
        self.assertEqual(prompt,direction)

    def test_new_project_retains_reusable_preference_but_discards_old_project(self):
        history=[{'role':'user','content':'I prefer accessible dark themes for future projects.'},
                 {'role':'user','content':'Add the old viewer heading'},
                 {'role':'assistant','content':'```html\n<h1>Old viewer heading</h1>\n```'}]
        self.assertEqual(fresh_project_history(history,{'newProject':True}),history[:1])
        self.assertIs(fresh_project_history(history,{'newProject':False}),history)

    def test_explicit_project_budget_and_file_protocol_reach_real_engine_calls(self):
        files=('```html file=index.html project=demo\n<!DOCTYPE html><html><head><link rel="stylesheet" href="styles.css"></head><body><h1>Ready</h1><script src="src/app.js"></script></body></html>\n```\n'
               '```css file=styles.css project=demo\nbody{margin:0;}\n```\n'
               '```javascript file=src/app.js project=demo\ndocument.body.dataset.ready="true";\n```')
        for engine in self.engines():
            with self.subTest(engine=engine.__name__):
                model,events=self.generate(engine,{'prompt':'Create a complete HTML project in separate files and provide a ZIP archive.','history':[]},[(files,'stop')])
                self.assertEqual(model.calls[0]['max_tokens'],8192)
                self.assertIn('file=index.html project=my-project',model.calls[0]['messages'][0]['content'])
                self.assertIn('application creates the actual ZIP/download',model.calls[0]['messages'][0]['content'])
                context=next(e for e in events if e['type']=='CONTEXT')
                self.assertEqual(context['contextWindowTokens'],32768)
                self.assertEqual(context['reservedOutputTokens'],8192)
                self.assertEqual(events[-1]['type'],'COMPLETED')

    def test_project_file_policy_survives_the_compact_repair_system_rebuild(self):
        original=('```html file=index.html project=demo\n<!DOCTYPE html><html><head></head>'
                  '<body><h1>Old title</h1></body></html>\n```')
        programming={
            'codingTask':True,'changeClass':'fix','canonicalCarry':True,
            'intentContract':{
                'originalRequest':'Create a complete HTML project in separate files and provide a ZIP archive.',
                'languageContract':{'explicit':True,'requiredLanguages':['html'],
                    'allowedLanguages':['html','css','javascript'],'artifactType':'web-page'},
            },
            'failureEvidence':{'repairSource':original,'evidence':'Expected Ready, actual Old title.',
                'receiptSemantics':{'categories':['assertion'],'expectedActual':['Expected Ready, actual Old title.']}},
        }
        for engine in self.engines():
            with self.subTest(engine=engine.__name__):
                model,events=self.generate(engine,
                    {'prompt':'Repair the title while preserving the project.','history':[],
                     'programmingIntent':programming},[(COMPLETE,'stop')])
                system=model.calls[0]['messages'][0]['content']
                self.assertIn('PROJECT FILE DELIVERY:',system)
                self.assertIn('application creates the actual ZIP/download',system)
                self.assertIn(original,system)
                self.assertTrue(next(e for e in events if e['type']=='CONTEXT')['repairTurn'])

    def test_later_project_file_repairs_change_every_source_fingerprint_owner(self):
        project=('```html file=index.html\n<html><body><script src="src/app.js"></script></body></html>\n```\n'
                 '```css file=styles.css\n#viewer { width:100%; }\n```\n'
                 '```javascript file=src/app.js\nconst selected = "first";\n```')
        css_repair=project.replace('width:100%','width:90%')
        js_repair=project.replace('"first"','"second"')
        owners=[_code_fingerprint]+[engine._candidate_fingerprint for engine in self.engines()]
        baseline=owners[0](project)
        for owner in owners:
            with self.subTest(owner=owner.__module__):
                self.assertEqual(owner(project),baseline)
                self.assertNotEqual(owner(css_repair),baseline)
                self.assertNotEqual(owner(js_repair),baseline)

    def test_readme_edits_do_not_hide_unchanged_code_and_nested_fences_are_preserved(self):
        code="```javascript file=src/app.js\nconst marker = '```';\nconst value = 1;\n```"
        readme='````markdown file=README.md\nFirst instructions.\n```bash\nnode src/app.js\n```\n````'
        owners=[_code_fingerprint]+[engine._candidate_fingerprint for engine in self.engines()]
        for owner in owners:
            with self.subTest(owner=owner.__module__):
                baseline=owner(code)
                project=readme+'\n'+code
                self.assertEqual(owner(project),baseline)
                self.assertEqual(owner(project.replace('First instructions.','Other instructions.')),baseline)
                self.assertNotEqual(owner(project.replace('value = 1','value = 2')),baseline)

    def test_legacy_first_file_repair_fingerprint_is_recomputed_from_complete_source(self):
        project=('```html file=index.html\n<html><body>Project</body></html>\n```\n'
                 '```javascript file=src/app.js\nconst value = 1;\n```')
        for engine in self.engines():
            with self.subTest(engine=engine.__name__):
                diagnostic=engine._repair_diagnostic({'failureEvidence':{
                    'repairSource':project,'repairSourceFingerprint':'legacy-first-file-only'}},[])
                self.assertEqual(diagnostic['repairSourceFingerprint'],engine._candidate_fingerprint(project))
                self.assertNotEqual(diagnostic['repairSourceFingerprint'],'legacy-first-file-only')

    def test_explicit_artifact_edit_uses_full_stored_revision_and_can_drop_stale_code_history(self):
        source=COMPLETE.replace('Ready','Canonical stored revision')
        programming={'codingTask':True,'changeClass':'feature','artifactContinuation':True,
            'artifactMutationRequested':True,'artifactTargetId':'artifact-revision',
            'artifactEditSource':source,'intentContract':{'originalRequest':'Create a complete HTML page.',
                'languageContract':{'explicit':True,'requiredLanguages':['html'],
                    'allowedLanguages':['html','css','javascript'],'artifactType':'web-page'}}}
        for engine in self.engines():
            with self.subTest(engine=engine.__name__):
                stale='```html\n'+'x'*(engine.CONTEXT_TOKENS*4)+'\n```'
                model,events=self.generate(engine,{'prompt':'Update this page heading to Ready.',
                    'programmingIntent':programming,'history':[{'role':'assistant','text':stale}]},[(COMPLETE,'stop')])
                system=model.calls[0]['messages'][0]['content']
                self.assertIn('CANONICAL PROJECT SOURCE UNDER EDIT',system)
                self.assertIn(source,system)
                self.assertNotIn(stale,str(model.calls[0]['messages']))
                self.assertEqual(next(e for e in events if e['type']=='CONTEXT')['historyMessagesDropped'],1)
        self.assertNotIn(source,project_delivery_policy({**programming,'newProject':True},'Make a separate app.'))


if __name__=='__main__':unittest.main()
