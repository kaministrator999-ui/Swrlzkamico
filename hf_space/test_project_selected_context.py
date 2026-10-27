"""Owned-file context projection, complete-source budgets and real engine loops."""
import copy
import json
import unittest
from unittest.mock import patch

from brain_programming import candidate_contract_gate
from programming_repair_context import (owned_project_edit_scope, source_under_edit,
    source_sized_budget, fresh_project_history, project_delivery_policy)
from project_archive import project_markdown, parse_project_files
from test_generation_completion_budget import Responses
from test_github_change_model_context import FakeModel, load_engine


def state(files, instruction='Update src/app.js in this project.'):
    return {'codingTask':True,'projectContext':'existing','changeClass':'feature',
        'artifactContinuation':True,'artifactMutationRequested':True,
        'artifactTargetId':'owned-project','baseRevision':3,'baseSourceHash':'a'*64,
        'artifactEditSource':project_markdown(files),'newProject':False,
        'intentContract':{'originalRequest':'Create an HTML source project.',
            'currentInstruction':instruction,'implementationPolicy':'complete-source',
            'languageContract':{'explicit':True,'requiredLanguages':['html'],
                'allowedLanguages':['html','css','javascript'],'artifactType':'web-page'}}}


def files(count=3):
    return [{'path':'index.html','language':'html','content':'<html><body><h1>Fixture</h1></body></html>\n'},
            {'path':'src/app.js','language':'javascript','content':'export const value=1;\n'},
            *[{'path':f'src/module-{n}.js','language':'javascript',
                'content':f'export const value{n}="unselected-content-{n}";\n'} for n in range(count-2)]]


class ProjectSelectedContext(unittest.TestCase):
    def test_owned_selection_preserves_complete_file_and_truthful_bounded_index(self):
        original=files(2000);programming=state(original);before=copy.deepcopy(programming)
        scope=owned_project_edit_scope(programming)
        self.assertEqual(parse_project_files(scope['source']),[original[1]])
        index=json.loads(scope['pathIndex'])
        self.assertEqual(index['totalFiles'],2000)
        self.assertEqual(index['selectedPaths'],['src/app.js'])
        self.assertGreater(index['omittedOtherPathCount'],0)
        self.assertEqual(len(index['listedOtherPaths'])+index['omittedOtherPathCount'],1999)
        self.assertLessEqual(len(scope['pathIndex']),4096)
        self.assertIn('not inspected',index['scope'])
        self.assertEqual(programming,before,'canonical complete project is never mutated')

    def test_unique_basename_works_but_ambiguous_or_partial_paths_abstain(self):
        programming=state(files(),'Update app.js in this project.')
        self.assertEqual(owned_project_edit_scope(programming)['selectedPaths'],['src/app.js'])
        for instruction in ('Edit src/app.js.','Edit app.js.'):
            self.assertEqual(owned_project_edit_scope(state(files(),instruction))['selectedPaths'],['src/app.js'])
        ambiguous=files()+[{'path':'other/app.js','language':'javascript','content':'export const other=2;\n'}]
        self.assertIsNone(owned_project_edit_scope(state(ambiguous,'Update app.js in this project.')))
        self.assertEqual(owned_project_edit_scope(state(ambiguous,'Update src/app.js in this project.'))['selectedPaths'],['src/app.js'])
        for instruction in ('Update src/app.js.map.', 'Update other-src/app.js.',
                            'Change the page background.', 'Use the supplied example:\n```js\n// src/app.js\n```'):
            self.assertIsNone(owned_project_edit_scope(state(files(),instruction)),instruction)

    def test_ownership_proof_is_required_and_raw_source_is_never_scoped(self):
        original=state(files())
        for changes in ({'artifactTargetId':''},{'artifactMutationRequested':False},
                        {'baseRevision':0},{'baseRevision':True},{'baseSourceHash':'not-a-hash'}):
            candidate={**original,**changes}
            self.assertIsNone(owned_project_edit_scope(candidate))
            self.assertEqual(source_under_edit(candidate,[]),original['artifactEditSource'])
        raw={**original,'artifactTargetId':'','artifactEditSource':''}
        history=[{'role':'assistant','content':original['artifactEditSource']}]
        self.assertEqual(source_under_edit(raw,history),original['artifactEditSource'])

    def test_new_whole_project_and_repair_requests_keep_their_existing_owners(self):
        original=state(files())
        for changes in ({'newProject':True},{'failureEvidence':{'repairSource':original['artifactEditSource']}},
                        {'canonicalCarry':True},{'behaviorRepairBaseSource':original['artifactEditSource']}):
            self.assertIsNone(owned_project_edit_scope({**original,**changes}))
        for instruction in ('Update all files including src/app.js.',
                            'Update src/app.js and all remaining files.',
                            'Refactor the entire project around src/app.js.',
                            'Update src/app.js across the repository.'):
            candidate=state(files(),instruction)
            self.assertIsNone(owned_project_edit_scope(candidate))
            self.assertEqual(source_under_edit(candidate,[]),candidate['artifactEditSource'])

    def test_only_exact_current_assistant_snapshot_is_projected_in_history(self):
        programming=state(files());source=programming['artifactEditSource']
        history=[{'role':'assistant','content':source,'id':'current'},
                 {'role':'user','content':source,'id':'raw-user'},
                 {'role':'assistant','content':'Unrelated prose\n'+source,'id':'different'},
                 {'role':'assistant','content':'```js\nconst unrelated=1;\n```','id':'old'}]
        before=copy.deepcopy(history);projected=fresh_project_history(history,programming)
        self.assertEqual(projected[0]['content'],owned_project_edit_scope(programming)['source'])
        self.assertEqual(projected[1:],history[1:])
        self.assertEqual(history,before)
        unscoped=state(files(),'Update the project appearance.')
        self.assertIs(fresh_project_history(history,unscoped),history)

    def test_output_floor_uses_selected_complete_files_and_never_clips_oversized_file(self):
        original=files();original[1]['content']='// selected complete bytes\n'+'x'*24000
        programming=state(original)
        budget=source_sized_budget(FakeModel(),programming,[],{'tokens':4096,'tier':'normal'})
        self.assertGreater(budget['tokens'],4096)
        self.assertLessEqual(budget['tokens'],16384)
        self.assertIn(original[1]['content'],source_under_edit(programming,[]))
        original[1]['content']='x'*100000
        with self.assertRaisesRegex(ValueError,'source was not truncated'):
            source_sized_budget(FakeModel(),state(original),[],{'tokens':4096,'tier':'normal'})

    def test_two_thousand_file_project_edit_fits_both_real_engine_message_builders(self):
        original=files(2000);programming=state(original)
        delta='```javascript file=src/app.js\nexport const value=7;\n```'
        for name in ('qwen_coder_engine','lfm2_700m_engine'):
            engine=load_engine(name);model=Responses([(delta,'stop')])
            payload={'prompt':'Update src/app.js in this project.',
                     'programmingIntent':programming,
                     'history':[{'role':'assistant','text':programming['artifactEditSource']}]}
            with self.subTest(engine=name),patch.object(engine,'load',return_value=model):
                events=list(engine.generate_events(payload))
            self.assertEqual(len(model.calls),1)
            self.assertEqual(events[-1]['type'],'COMPLETED')
            delivered=''.join(event.get('text','') for event in events if event['type']=='DELTA')
            self.assertEqual(delivered,delta)
            messages=model.calls[0]['messages'];combined='\n'.join(message['content'] for message in messages)
            self.assertIn(original[1]['content'],combined)
            self.assertNotIn('unselected-content-0',combined)
            self.assertNotIn(programming['artifactEditSource'],combined)
            self.assertIn('BOUNDED PROJECT PATH INDEX',messages[0]['content'])
            context=next(event for event in events if event['type']=='CONTEXT')
            self.assertLessEqual(context['estimatedInputTokens']+context['reservedOutputTokens']+engine.CONTEXT_SAFETY_TOKENS,engine.CONTEXT_TOKENS)
            validation=next(event['validation'] for event in events if event['type']=='CANDIDATE_VALIDATION')
            self.assertEqual(validation['status'],'PASS')
            self.assertEqual(candidate_contract_gate(delta,programming,[])['projectRevisionFileCount'],2000)
            self.assertEqual(programming['artifactEditSource'],project_markdown(original))

    def test_unscoped_owned_policy_still_includes_all_canonical_contents(self):
        programming=state(files(),'Update the project appearance.')
        policy=project_delivery_policy(programming,'Update the project appearance.')
        self.assertIn(programming['artifactEditSource'],policy)
        self.assertNotIn('BOUNDED PROJECT PATH INDEX',policy)
        self.assertEqual(source_under_edit(programming,[]),programming['artifactEditSource'])


if __name__=='__main__':unittest.main()
