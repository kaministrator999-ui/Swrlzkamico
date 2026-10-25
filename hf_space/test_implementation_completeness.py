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
