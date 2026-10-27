"""User default requires implemented code; explanatory comments remain allowed."""
import unittest

from brain_programming import candidate_contract_gate, programming_intent
from programming_repair_context import build_compact_repair_context


def gate(prompt, source):
    state=programming_intent(prompt,[],[])
    return state,candidate_contract_gate(source,state,[])


class ImplementationCompleteness(unittest.TestCase):
    def test_default_survives_initial_and_compact_contracts(self):
        state=programming_intent('Create a Python sum function.',[],[])
        contract=state['intentContract']
        self.assertEqual(contract['implementationPolicy'],'complete-source')
        self.assertIn('complete usable code',contract['must'][0])
        self.assertIn('pseudocode',contract['mustNot'][0])
        context,_,_=build_compact_repair_context(state,'Fix it.','')
        self.assertIn('commented placeholders',context)

    def test_python_function_stubs_are_rejected_but_real_code_is_allowed(self):
        for body in ('pass','...','raise NotImplementedError','raise NotImplementedError("later")'):
            with self.subTest(body=body):
                _,result=gate('Create a Python sum function.','```python\ndef total(values):\n    """Sum the values."""\n    '+body+'\n```')
                self.assertIn('unfinished-function-stub:total',result['reasons'])
                self.assertFalse(result['executionVerified'])
        for code in ('def total(values):\n    # Sum implemented below.\n    return sum(values)',
                     'from abc import abstractmethod\nclass Base:\n    @abstractmethod\n    def work(self):\n        pass\nclass Child(Base):\n    def work(self):\n        return 1',
                     'def read(path):\n    try:\n        return open(path).read()\n    except FileNotFoundError:\n        pass\n    return ""'):
            with self.subTest(code=code):
                self.assertEqual(gate('Create Python code.','```python\n'+code+'\n```')[1]['status'],'PASS')

    def test_valid_protocol_and_explicit_noop_or_exception_are_allowed(self):
        for prompt, code in (
            ('Create Python interface code.', 'from typing import Protocol\nclass Reader(Protocol):\n    def read(self) -> str: ...'),
            ('Create a Python no-op callback.', 'def callback():\n    pass'),
            ('Create a Python function that raises NotImplementedError.', 'def unsupported():\n    raise NotImplementedError("unsupported")'),
        ):
            with self.subTest(prompt=prompt):
                self.assertEqual(gate(prompt,'```python\n'+code+'\n```')[1]['status'],'PASS')

    def test_javascript_and_html_placeholder_comments_reject(self):
        for code in ('// TODO\nfunction start() {}','/* FIXME: implement later */\nfunction start() {}',
                     '// Add your code here\nfunction start() {}',
                     'function start() { throw new Error("not implemented"); }'):
            with self.subTest(code=code):
                _,result=gate('Create JavaScript code.','```javascript\n'+code+'\n```')
                self.assertEqual(result['status'],'REJECT')
        _,result=gate('Create an HTML page.','```html\n<!doctype html><html><body><!-- Insert your implementation here --></body></html>\n```')
        self.assertIn('unfinished-implementation-placeholder',result['reasons'])

    def test_explanatory_comments_literals_and_readme_are_not_placeholders(self):
        source=('```javascript file=app.js\n'
                '// Render the current selection.\n'
                'const label="TODO: this is literal user data";\n'
                'const url="https://example.test/path";\n'
                'function total(values){return values.reduce((a,b)=>a+b,0);}\n```\n'
                '```markdown file=README.md\nThis example explains TODO markers in a separate document.\n```')
        result=gate('Create JavaScript code.',source)[1]
        self.assertEqual(result['status'],'PASS',result)
        python='```python\nvalue = "TODO: literal data"\n# Return the supplied value.\ndef identity(value):\n    return value\n```'
        self.assertEqual(gate('Create Python code.',python)[1]['status'],'PASS')

    def test_explicit_scaffold_opt_in_preserves_user_intent(self):
        for prompt,source in (
            ('Create a Python skeleton with TODO placeholders.','```python\ndef total(values):\n    # TODO implement\n    pass\n```'),
            ('Create a 3D model editor HTML scaffold with TODO placeholders.','```html\n<!doctype html><html><body><!-- Add your implementation here --></body></html>\n```'),
        ):
            with self.subTest(prompt=prompt):
                state,result=gate(prompt,source)
                self.assertEqual(state['intentContract']['implementationPolicy'],'explicit-scaffold')
                self.assertNotIn('applicationCapabilities',state['intentContract'])
                self.assertEqual(result['status'],'PASS',result)

    def test_leading_todo_filename_metadata_is_allowed_only_for_its_actual_path(self):
        for label,path,language,body,prompt in (
            ('// todo.js','todo.js','javascript','const ready=true;','Create JavaScript code.'),
            ('// TODO-app.js','src/TODO-app.js','javascript','const ready=true;','Create JavaScript code.'),
            ('# TODO.py','src/TODO.py','python','def answer():\n    return 42','Create Python code.'),
            ('/* FIXME.css */','FIXME.css','css','body{margin:0}','Create CSS code.'),
        ):
            with self.subTest(label=label):
                source='```'+language+' file='+path+'\n'+label+'\n'+body+'\n```'
                self.assertEqual(gate(prompt,source)[1]['status'],'PASS')
        # The shared metadata parser can also infer the first file's path.
        self.assertEqual(gate('Create JavaScript code.','```javascript\n// todo.js\nconst ready=true;\n```')[1]['status'],'PASS')

    def test_filename_exemption_does_not_hide_real_todo_or_later_comments(self):
        for path,body in (
            ('todo.js','// todo.js\n// TODO: implement behavior\nconst ready=true;'),
            ('todo.js','// todo.js\nconst ready=true;\n// todo.js'),
            ('todo.js','const ready=true;\n// todo.js'),
            ('todo.js','// todo.js implement later\nconst ready=true;'),
            ('app.js','// todo.js\nconst ready=true;'),
            ('todo.js','// TODO.js\nconst ready=true;'),
        ):
            with self.subTest(path=path,body=body):
                _,result=gate('Create JavaScript code.','```javascript file='+path+'\n'+body+'\n```')
                self.assertIn('unfinished-implementation-placeholder',result['reasons'])

    def test_negative_scaffold_request_does_not_disable_gate(self):
        for prompt in ('Create Python code, no pseudocode or placeholders.',
                       'Create Python code. Do not return a skeleton.',
                       'Create complete working Python code with no TODO stubs.'):
            with self.subTest(prompt=prompt):
                state,result=gate(prompt,'```python\ndef work():\n    pass\n```')
                self.assertEqual(state['intentContract']['implementationPolicy'],'complete-source')
                self.assertEqual(result['status'],'REJECT')

    def test_pseudocode_fence_is_not_code_implementation(self):
        _,result=gate('Create a Python function.','```pseudocode\nBEGIN\n  ADD each value\nEND\n```')
        self.assertIn('pseudocode-instead-of-implementation',result['reasons'])


if __name__=='__main__':
    unittest.main()
