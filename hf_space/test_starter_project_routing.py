"""Concrete starter projects route to code without swallowing prose or assets."""
import unittest

from brain_programming import programming_intent
from response_cognition import requests_source_project, requests_web_source


class StarterProjectRouting(unittest.TestCase):
    def test_named_stack_and_application_starters_are_code(self):
        for request in ('Build a React starter project.',
                        'Build a polished starter task manager project.',
                        'Create a Vue project.',
                        'Create a Next.js starter project.',
                        'Build a Django starter project.',
                        'Create a Flutter starter project.'):
            with self.subTest(request=request):
                self.assertTrue(requests_source_project(request))
                self.assertTrue(programming_intent(request,[],[])['codingTask'])

    def test_frontend_stack_stays_frontend_without_inventing_html_file_requirement(self):
        intent=programming_intent('Build a React starter project.',[],[])
        language=intent['intentContract']['languageContract']
        self.assertEqual(language['artifactType'],'web-page')
        self.assertNotIn('html',language['requiredLanguages'])
        self.assertTrue(requests_web_source('Create a Vue starter project.'))

    def test_native_and_backend_project_stacks_do_not_become_html(self):
        for request in ('Build a React Native starter project.',
                        'Create a Flutter starter project.',
                        'Create a Django starter project.'):
            with self.subTest(request=request):
                self.assertFalse(requests_web_source(request))
                self.assertNotEqual(programming_intent(request,[],[])['intentContract']['languageContract']['artifactType'],'web-page')

    def test_purpose_clause_text_and_media_never_gain_software_authority(self):
        for request in ('Write a React project proposal.',
                        'Create a wedding project plan.',
                        'Build my next project.',
                        'Create a next project for school.',
                        'Write a story about a task manager project.',
                        'Create a logo for a React starter project.',
                        'Create a 3D mesh for a task board project.'):
            with self.subTest(request=request):
                self.assertFalse(requests_source_project(request))
                self.assertFalse(programming_intent(request,[],[])['codingTask'])


if __name__=='__main__':
    unittest.main()
