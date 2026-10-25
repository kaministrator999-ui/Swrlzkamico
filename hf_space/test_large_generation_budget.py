"""Bounded long-form requests, real engine reservation, and imported-source safety."""
import unittest
from unittest.mock import patch

from brain_programming import programming_intent
from programming_repair_context import response_budget, long_delivery_policy, preserve_existing_source, source_sized_budget
from test_generation_completion_budget import COMPLETE, Responses
from test_github_change_model_context import load_engine, FakeModel


class LargeGenerationPolicy(unittest.TestCase):
    def test_explicit_large_outputs_receive_substantial_room(self):
        cases=[
            ({'codingTask':True},'Build a huge coding project with lots of code.'),
            ({'codingTask':True},'Create a comprehensive HTML application project.'),
            ({},'Write a long document about ocean currents.'),
            ({},'Produce a substantial report on renewable energy.'),
            ({},'Write a 3,000-word explanation of orbital mechanics.'),
            ({},'Draft a 10-page specification for our workshop.'),
            ({},'Explain the source in a detailed report.'),
        ]
        for state,prompt in cases:
            with self.subTest(prompt=prompt):
                budget=response_budget(state,prompt)
                self.assertEqual((budget['tier'],budget['tokens']),('large',16384))
                self.assertIn('remaining work',long_delivery_policy(budget))

    def test_existing_project_and_ordinary_document_tiers(self):
        for state,prompt in [({'codingTask':True},'Create a 3D model editor page.'),
                             ({'codingTask':True},'Build a multi-file project.'),
                             ({},'Write a 1,200-word explanation of ocean currents.')]:
            with self.subTest(prompt=prompt):
                self.assertEqual(response_budget(state,prompt)['tokens'],8192)
        for prompt in ['How big is a large language model?', 'What is a comprehensive document?',
                       'Describe a quiet lakeside sunrise.', 'The large project broke yesterday.']:
            with self.subTest(prompt=prompt):
                self.assertEqual(response_budget({},prompt)['tokens'],4096)

    def test_current_shortening_wins_over_carried_large_contract(self):
        state={'codingTask':True,'intentContract':{'originalRequest':'Create a comprehensive application project.'}}
        for prompt in ['Keep it concise.', 'Briefly explain the architecture.',
                       'Only a tiny fix please.', 'Respond in one sentence.',
                       'Explain it in under 100 words.']:
            with self.subTest(prompt=prompt):
                self.assertEqual(response_budget(state,prompt)['tokens'],4096)

    def test_existing_raw_source_is_protected_without_invented_artifact_identity(self):
        prompt='Now can you add text to the top saying §wyrlz of that 3d model viewer'
        source='```html\n<!doctype html><html><body>'+'x'*160000+'</body></html>\n```'
        history=[{'role':'user','text':'Create a viewer HTML page'},
                 {'role':'assistant','text':source}]
        state=programming_intent(prompt,history,[])
        self.assertEqual(state['projectContext'],'existing')
        self.assertFalse(state['artifactContinuation'])
        self.assertFalse(state['artifactMutationRequested'])
        self.assertTrue(preserve_existing_source(state))
        projected=[{'role':m['role'],'content':m['text']} for m in history]
        for name in ('qwen_coder_engine','lfm2_700m_engine'):
            engine=load_engine(name)
            with self.subTest(engine=name),self.assertRaisesRegex(ValueError,'was not truncated'):
                engine._fit_messages(FakeModel(),'policy',projected,prompt,4096,
                    preserve_latest_code=preserve_existing_source(state))
        self.assertFalse(state['artifactTargetId'])
        self.assertFalse(preserve_existing_source({**state,'newProject':True}))

    def test_short_edit_still_reserves_complete_source_delivery(self):
        state={'codingTask':True,'projectContext':'existing','changeClass':'feature',
            'artifactEditSource':'```html\n'+'x'*24000+'\n```'}
        initial=response_budget(state,'Only a tiny fix please.')
        self.assertEqual(initial['tokens'],4096)
        actual=source_sized_budget(FakeModel(),state,[],initial)
        self.assertGreater(actual['tokens'],4096)
        self.assertEqual(actual['tier'],'source-complete')
        self.assertLessEqual(actual['tokens'],16384)
        for name in ('qwen_coder_engine','lfm2_700m_engine'):
            engine=load_engine(name)
            fitted,_,used,reserved=engine._fit_messages(FakeModel(),'policy\n'+state['artifactEditSource'],[],
                'Only a tiny fix please.',actual['tokens'])
            self.assertEqual(reserved,actual['tokens'])
            self.assertIn(state['artifactEditSource'],fitted[0]['content'])
            self.assertLessEqual(used+reserved+engine.CONTEXT_SAFETY_TOKENS,engine.CONTEXT_TOKENS)
        too_big={**state,'artifactEditSource':'```html\n'+'x'*100000+'\n```'}
        with self.assertRaisesRegex(ValueError,'bounded output maximum.*16384'):
            source_sized_budget(FakeModel(),too_big,[],initial)
        self.assertEqual(source_sized_budget(FakeModel(),{**too_big,'changeClass':'review'},[],initial),initial)

    def test_imported_heading_edit_engine_uses_source_sized_output_floor(self):
        before='```html\n<!doctype html><html><head><title>Viewer</title></head><body><h1>Viewer</h1>'+('x'*24000)+'</body></html>\n```'
        after=before.replace('<h1>Viewer</h1>','<h1>§wyrlz</h1>')
        payload={'prompt':'Now can you add text to the top saying §wyrlz of that 3d model viewer',
            'history':[{'role':'user','text':'Create a viewer HTML page'},
                       {'role':'assistant','text':before}]}
        for name in ('qwen_coder_engine','lfm2_700m_engine'):
            engine=load_engine(name);model=Responses([(after,'stop')])
            with self.subTest(engine=name),patch.object(engine,'load',return_value=model):
                events=list(engine.generate_events(payload))
                self.assertGreater(model.calls[0]['max_tokens'],4096)
                self.assertEqual(next(e for e in events if e['type']=='CONTEXT')['responseBudgetTier'],'source-complete')
                self.assertTrue(any(before in message['content'] for message in model.calls[0]['messages']))
                self.assertEqual(events[-1]['type'],'COMPLETED')

    def test_both_engines_reserve_long_output_before_optional_history(self):
        for name in ('qwen_coder_engine','lfm2_700m_engine'):
            engine=load_engine(name)
            self.assertEqual(engine.CONTEXT_TOKENS,32768)
            model=Responses([('Ocean circulation redistributes heat.','stop')])
            payload={'prompt':'Write a comprehensive report on ocean currents.',
                'history':[{'role':'assistant','text':'old irrelevant context '+'x'*80000}]}
            with self.subTest(engine=name),patch.object(engine,'load',return_value=model):
                events=list(engine.generate_events(payload))
                self.assertEqual(model.calls[0]['max_tokens'],16384)
                context=next(e for e in events if e['type']=='CONTEXT')
                self.assertEqual(context['responseBudgetTier'],'large')
                self.assertEqual(context['reservedOutputTokens'],16384)
                self.assertGreater(context['historyMessagesDropped'],0)
                self.assertLessEqual(context['estimatedInputTokens']+16384+engine.CONTEXT_SAFETY_TOKENS,32768)
                self.assertEqual(events[-1]['type'],'COMPLETED')

    def test_large_code_uses_same_reservation_and_length_failure_remains_truthful(self):
        for name in ('qwen_coder_engine','lfm2_700m_engine'):
            engine=load_engine(name)
            model=Responses([(COMPLETE,'length')])
            with self.subTest(engine=name),patch.object(engine,'load',return_value=model):
                events=list(engine.generate_events({'prompt':'Create a comprehensive HTML project.', 'history':[]}))
                self.assertEqual(model.calls[0]['max_tokens'],16384)
                self.assertEqual(events[-1]['type'],'FAILED')
                self.assertEqual(events[-1]['reason'],'OUTPUT_TOKEN_LIMIT')
                self.assertFalse(any(e['type']=='COMPLETED' for e in events))

    def test_identity_and_exact_steps_keep_special_decode_caps(self):
        for name in ('qwen_coder_engine','lfm2_700m_engine'):
            engine=load_engine(name)
            for prompt in ['What is your name?', 'Explain a huge project in 3 numbered steps.']:
                model=Responses([('1. Inspect.\n2. Build.\n3. Verify.','stop')])
                with self.subTest(engine=name,prompt=prompt),patch.object(engine,'load',return_value=model):
                    list(engine.generate_events({'prompt':prompt,'history':[]}))
                    for call in model.calls:self.assertLessEqual(call['max_tokens'],512)


if __name__=='__main__':unittest.main()
