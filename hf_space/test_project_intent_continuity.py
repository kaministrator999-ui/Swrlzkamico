"""Follow-up project features retain original requirements across source languages."""
import unittest

from brain_programming import programming_intent
from project_archive import project_markdown


def saved_history(request, language, path, content):
    return [{"role":"user","text":request},
            {"id":"saved-project-message","role":"assistant","text":"Saved project files.",
             "meta":{"codeArtifactId":"owned-project","artifactRevision":1,
                     "artifactSourceHash":"a"*64,
                     "artifactSourceSnapshot":project_markdown([
                         {"path":path,"language":language,"content":content}])}}]


class ProjectIntentContinuity(unittest.TestCase):
    def test_non_web_feature_preserves_original_requirements_and_latest_instruction(self):
        cases=[("Python","python","tasks.py","tasks = []\n"),
               ("Kotlin","kotlin","Main.kt","fun main() { println(\"Tasks\") }\n")]
        for name,language,path,content in cases:
            with self.subTest(language=name):
                original=f"Build a {name} task project. It must reject empty task names. Keep task data in memory. Do not add networking."
                prior=programming_intent(original,[],[])
                history=saved_history(original,language,path,content)
                followup=f"Now update this project in {path} to list the tasks."
                intent=programming_intent(followup,history,[],prior)
                contract=intent['intentContract']
                self.assertTrue(intent['artifactMutationRequested'])
                self.assertEqual(intent['artifactTargetId'],'owned-project')
                self.assertEqual(contract['originalRequest'],original)
                self.assertEqual(contract['currentInstruction'],followup)
                self.assertTrue(any('reject empty task names' in item for item in contract['must']))
                self.assertTrue(any('in memory' in item for item in contract['preserve']))
                self.assertTrue(any('networking' in item for item in contract['mustNot']))

    def test_next_saved_revision_retains_both_initial_and_added_feature_requirements(self):
        original='Build a Python task project. It must reject empty names. Keep data in memory.'
        history=saved_history(original,'python','tasks.py','tasks = []\n')
        prior=programming_intent(original,[],[])
        feature='Now add a list command to this project in tasks.py.'
        prior=programming_intent(feature,history,[],prior)
        history.extend([{'role':'user','text':feature},
                        {**history[1], 'meta':{**history[1]['meta'],'artifactRevision':2,'artifactSourceHash':'b'*64}}])
        intent=programming_intent('Now update tasks.py in this project to support sorting tasks.',history,[],prior)
        self.assertEqual(intent['intentContract']['originalRequest'],original)
        self.assertTrue(any('list command' in item for item in intent['intentContract']['must']))
        self.assertTrue(any('sorting tasks' in item for item in intent['intentContract']['must']))

    def test_explicit_new_project_discards_previous_constraints_and_target(self):
        original='Build a Python task project. It must reject empty task names. Keep data in memory.'
        history=saved_history(original,'python','tasks.py','tasks = []\n')
        prior=programming_intent(original,[],[])
        request='Create a separate Kotlin project that prints a greeting.'
        intent=programming_intent(request,history,[],prior)
        self.assertTrue(intent['newProject'])
        self.assertFalse(intent['artifactMutationRequested'])
        self.assertEqual(intent['intentContract']['originalRequest'],request)
        self.assertFalse(any('task names' in item for item in intent['intentContract']['must']))

    def test_information_only_followup_does_not_mutate_owned_project(self):
        original='Build a Python task project. It must reject empty names.'
        intent=programming_intent('Explain this project.',
            saved_history(original,'python','tasks.py','tasks = []\n'),[],
            programming_intent(original,[],[]))
        self.assertEqual(intent['changeClass'],'explain')
        self.assertFalse(intent['artifactMutationRequested'])

    def test_switching_saved_projects_cannot_inherit_other_projects_contract(self):
        for explicit_prior_target in (False,True):
            with self.subTest(explicitPriorTarget=explicit_prior_target):
                original='Build a Python task project. Keep all task data in memory.'
                prior=programming_intent(original,[],[])
                if explicit_prior_target:
                    prior['artifactTargetId']='owned-project'
                prior['behaviorLedger']={'sourceFingerprint':'old-project-fingerprint'}
                history=saved_history(original,'python','tasks.py','tasks = []\n')
                pins=[{'artifactId':'project-b','artifactRevision':2,'artifactSourceHash':'b'*64,
                       'files':[{'path':'Main.kt'}],
                       'text':project_markdown([{'path':'Main.kt','language':'kotlin',
                                                'content':'fun main() { println("Hello") }\n'}])}]
                request='Update Main.kt in Kotlin project-b to print Goodbye. Keep its filename.'
                intent=programming_intent(request,history,pins,prior)
                self.assertEqual(intent['artifactTargetId'],'project-b')
                self.assertEqual(intent['intentContract']['originalRequest'],request)
                self.assertNotIn('python',intent['intentContract']['languageContract']['requiredLanguages'])
                self.assertFalse(any('task data' in item for item in intent['intentContract']['preserve']))
                self.assertFalse(intent['canonicalCarry'])

    def test_selected_native_source_does_not_inherit_latest_html_medium(self):
        original='Create an HTML website. Keep its blue theme.'
        history=saved_history(original,'html','index.html','<html><body>Hello</body></html>\n')
        pins=[{'artifactId':'project-b','artifactRevision':1,'artifactSourceHash':'b'*64,
               'files':[{'path':'Main.kt'}],
               'text':project_markdown([{'path':'Main.kt','language':'kotlin',
                                        'content':'fun main() { println("Hello") }\n'}])}]
        intent=programming_intent('Update Main.kt in project-b to print Goodbye.',history,pins,
                                  programming_intent(original,[],[]))
        self.assertEqual(intent['artifactTargetId'],'project-b')
        self.assertNotEqual(intent['intentContract']['languageContract']['artifactType'],'web-page')
        self.assertNotIn('html',intent['intentContract']['languageContract']['requiredLanguages'])

    def test_vague_failure_stays_on_explicitly_selected_project_without_mutation(self):
        original='Build a Python task project. Keep data in memory.'
        history=saved_history(original,'python','tasks.py','tasks = []\n')
        pins=[{'artifactId':'project-b','artifactRevision':2,'artifactSourceHash':'b'*64,
               'files':[{'path':'Main.kt'}],
               'text':project_markdown([{'path':'Main.kt','language':'kotlin',
                                        'content':'fun main() { println("Hello") }\n'}])}]
        for prompt in ('Fix project-b, it is broken.', 'Project-b still does not work.'):
            with self.subTest(prompt=prompt):
                intent=programming_intent(prompt,history,pins,programming_intent(original,[],[]))
                self.assertEqual(intent['artifactTargetId'],'project-b')
                self.assertTrue(intent['needsFailureEvidence'])
                self.assertFalse(intent['artifactMutationRequested'])


if __name__=='__main__':
    unittest.main()
