"""File-based software projects keep code routing, contracts and source guards.

Model/weight generation is doubled; Station, routing, engine message creation,
source gating and artifact/ZIP boundaries are real. No editor quality claim.
"""
import copy
import io
from pathlib import Path
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch
import zipfile

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from brain_programming import programming_intent,candidate_contract_gate
from response_cognition import classify_response_cognition,requests_web_source,requests_source_project
from programming_repair_context import response_budget,fresh_project_history
from test_generation_completion_budget import Responses
from test_github_change_model_context import load_engine
import model_router
import station
import test_project_archive as archive_tests

PROJECT_REQUEST=('Create a separate 3D model editor project with index.html, styles.css, editor.js and README.md. '
    'Include adding cubes and spheres, object selection, position/rotation/scale editing of the selected object, '
    'deletion, and orbit/zoom. Make the interface usable on mobile. '
    'Return complete source files for a working small prototype.')
NATIVE_REQUEST='Create a separate Android 3D model editor project in Kotlin with MainActivity.kt.'
VIEWER='```html file=index.html\n<!doctype html><html><head><title>Viewer</title></head><body><h1>Old heading</h1><canvas></canvas><script>window.viewer=true;</script></body></html>\n```'
HISTORY=[{'role':'user','text':'Create a 3D viewer HTML page.'},
    {'role':'assistant','text':VIEWER,'meta':{'codeArtifactId':'artifact-viewer',
        'artifactRevision':1,'artifactSourceHash':'a'*64,'artifactSourceSnapshot':VIEWER}}]

# These tiny object-data handlers test source evidence and byte transport only.
# They are not a renderer, a working editor or input supplied to a real model.
PROJECT_FILES=[
    {'path':'index.html','language':'html','content':'<!doctype html><html><head><title>Fixture</title><link rel="stylesheet" href="styles.css"></head><body><canvas></canvas><script src="editor.js"></script></body></html>\n'},
    {'path':'styles.css','language':'css','content':'body{margin:0}\n'},
    {'path':'editor.js','language':'javascript','content':'''let selected=null;const objects=[];
function addObject(){const object={position:{x:0},rotation:{x:0},scale:{x:1}};objects.push(object);selected=object;}
addButton.onclick=addObject;
canvas.onclick=()=>{selected=objects[0];};
deleteButton.onclick=()=>{objects.splice(objects.indexOf(selected),1);};
x.oninput=()=>{selected.position.x=1;};
r.oninput=()=>{selected.rotation.x=1;};
s.oninput=()=>{selected.scale.x=2;};
'''},
    {'path':'README.md','language':'markdown','content':'Deterministic transport fixture; not browser acceptance.\n'},
]
PROJECT_SOURCE='\n'.join('```'+item['language']+' file='+item['path']+'\n'+item['content']+'```' for item in PROJECT_FILES)


class SourceProjectRouting(unittest.TestCase):
    def test_actual_four_file_request_is_guarded_fresh_web_code_without_history_leak(self):
        prior=programming_intent(HISTORY[0]['text'],[],[])
        prior['intentContract']['literalUiText']=[{'target':'heading','text':'Old heading'}]
        prior['intentContract']['must']+=['Preserve only the old viewer project.']
        for history,state in (([],{}),(HISTORY,prior)):
            with self.subTest(history=bool(history)):
                intent=programming_intent(PROJECT_REQUEST,history,[],state)
                self.assertTrue(requests_source_project(PROJECT_REQUEST));self.assertTrue(requests_web_source(PROJECT_REQUEST))
                self.assertEqual(classify_response_cognition(PROJECT_REQUEST)['deliverable'],'code')
                self.assertTrue(intent['codingTask']);self.assertTrue(intent['newProject'])
                self.assertEqual(intent['projectContext'],'new');self.assertEqual(intent['changeClass'],'create')
                self.assertFalse(intent['artifactMutationRequested']);self.assertEqual(intent['artifactTargetId'],'')
                contract=intent['intentContract'];language=contract['languageContract']
                self.assertFalse(language['explicit']);self.assertEqual(language['requiredLanguages'],['html'])
                self.assertEqual(language['artifactType'],'web-page')
                self.assertEqual(contract['applicationCapabilities']['required'],['create','select','transform','delete'])
                self.assertFalse(contract['literalUiText']);self.assertNotIn('old viewer project',str(contract))
                self.assertEqual(fresh_project_history(history,intent),[])
                self.assertEqual(response_budget(intent,PROJECT_REQUEST)['tokens'],8192)
                self.assertEqual(candidate_contract_gate(VIEWER,intent,[])['status'],'REJECT')
                self.assertEqual(candidate_contract_gate(PROJECT_SOURCE,intent,[])['status'],'PASS')

    def test_native_editor_project_is_code_and_fresh_without_inferred_html(self):
        prior=programming_intent(HISTORY[0]['text'],[],[])
        prior['intentContract']['literalUiText']=[{'target':'heading','text':'Old heading'}]
        intent=programming_intent(NATIVE_REQUEST,HISTORY,[],prior)
        self.assertEqual(classify_response_cognition(NATIVE_REQUEST)['deliverable'],'code')
        self.assertTrue(intent['codingTask']);self.assertTrue(intent['newProject'])
        self.assertFalse(requests_web_source(NATIVE_REQUEST))
        language=intent['intentContract']['languageContract']
        self.assertEqual(language['requiredLanguages'],['kotlin']);self.assertNotEqual(language['artifactType'],'web-page')
        self.assertFalse(intent['intentContract']['literalUiText']);self.assertEqual(fresh_project_history(HISTORY,intent),[])
        check=candidate_contract_gate('```kotlin file=MainActivity.kt\nfun main(){println("Native source fixture")}\n```',intent,[])
        self.assertEqual(check['status'],'PASS');self.assertFalse(check['executionVerified'])

    def test_assets_destinations_and_nonsoftware_projects_do_not_become_code(self):
        for prompt in ('Create a 3D mesh for viewer/index.html.',
                       'Create a rigged 3D character for an editor project with index.html.',
                       'Create a 3D sculpture project.',
                       'Create a mesh project with index.html.',
                       'Create a wedding planning project.',
                       'Create a school science project.'):
            with self.subTest(prompt=prompt):
                self.assertFalse(requests_source_project(prompt));self.assertFalse(requests_web_source(prompt))
                self.assertFalse(programming_intent(prompt,[],[])['codingTask'])
        for prompt in ('Create a project with index.html and app.js.',
                       'Build a 3D editor software project.',
                       'Build a Kotlin 3D project with MainActivity.kt.'):
            with self.subTest(prompt=prompt):
                self.assertTrue(requests_source_project(prompt));self.assertTrue(programming_intent(prompt,[],[])['codingTask'])

    def test_both_real_engines_route_project_contract_into_model_and_withhold_viewer(self):
        for name in ('qwen_coder_engine','lfm2_700m_engine'):
            engine=load_engine(name);model=Responses([(VIEWER,'stop'),(PROJECT_SOURCE,'stop')])
            with self.subTest(engine=name),patch.object(engine,'load',return_value=model):
                events=list(engine.generate_events({'prompt':PROJECT_REQUEST,'history':HISTORY}))
            self.assertEqual(len(model.calls),2);self.assertEqual(model.calls[0]['max_tokens'],8192)
            policy=model.calls[0]['messages'][0]['content']
            self.assertIn('3D scene editor prototype:',policy);self.assertIn('APPLICATION ACCEPTANCE:',policy)
            self.assertIn('PROJECT FILE DELIVERY:',policy);self.assertNotIn('Old heading',str(model.calls[0]['messages']))
            attempts=[event['attempt'] for event in events if event['type']=='CANDIDATE_ATTEMPT']
            self.assertEqual(attempts[0]['validationStatus'],'REJECT');self.assertEqual(attempts[-1]['validationStatus'],'PASS')
            self.assertEqual(events[-1]['type'],'COMPLETED')
            self.assertEqual(''.join(e.get('text','') for e in events if e['type']=='DELTA'),PROJECT_SOURCE)


class SourceProjectStation(unittest.TestCase):
    def setUp(self):
        archive_tests.ProjectArchiveHTTP.setUp(self)

    def test_real_station_and_router_700m_to_coder_create_separate_four_file_archive(self):
        thread=self.sessions['owner-cookie']['threads'][0]
        before=copy.deepcopy(thread['codeArtifacts'][0])
        thread['messages']=copy.deepcopy(HISTORY)
        engine=load_engine('qwen_coder_engine');model=Responses([(PROJECT_SOURCE,'stop')])
        captured=[]
        def forbidden(_payload):
            raise AssertionError('Non-coder generator must not run for the source project.')
        def dispatch(model_id,payload,*_generators):
            events=list(model_router.dispatch(model_id,payload,forbidden,
                stock_generate=forbidden,large_generate=forbidden,coder_generate=engine.generate_events))
            captured.extend(events)
            return iter(events)
        with patch.object(station,'routes',return_value=[SimpleNamespace(model_id='700m',available=True)]), \
             patch.object(station,'dispatch',side_effect=dispatch), \
             patch.object(station,'persist_runtime_diagnostic',return_value=None), \
             patch.object(station._pool,'submit',side_effect=lambda fn,*args:fn(*args)), \
             patch.object(engine,'load',return_value=model):
            sent=self.client.post('/api/lalm_station/send',json={'modelId':'700m','prompt':PROJECT_REQUEST,
                'threadId':'thread-owned','requestId':'source-project-request','assistantMessageId':'source-project-answer'})
        self.assertEqual(sent.status_code,202)
        self.assertTrue(any(e.get('phase')=='CODER_AUTO_ROUTE' and e.get('selectedModelId')=='coder' for e in captured))
        snapshot=self.client.get('/api/lalm_station/sync').json()
        generation=snapshot['activeGeneration']
        self.assertEqual(generation['requestedModelId'],'700m');self.assertEqual(generation['selectedModelId'],'coder')
        self.assertTrue(generation['programmingIntent']['newProject'])
        self.assertEqual(generation['candidateValidation']['status'],'PASS')
        artifacts=snapshot['currentThread']['codeArtifacts']
        self.assertEqual(len(artifacts),2);self.assertEqual(artifacts[0],before)
        delivered=artifacts[1]
        self.assertEqual([item['path'] for item in delivered['files']],[item['path'] for item in PROJECT_FILES])
        self.assertEqual(delivered['currentRevision'],1)
        download=self.client.get('/api/lalm_station/artifacts/thread-owned/'+delivered['id']+'/download?revision=1')
        self.assertEqual(download.status_code,200)
        with zipfile.ZipFile(io.BytesIO(download.content)) as archive:
            for item in PROJECT_FILES:
                self.assertEqual(archive.read(item['path']),item['content'].encode())


if __name__=='__main__':
    unittest.main()
