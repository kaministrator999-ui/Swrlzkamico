"""Routing safety regression: external GitHub text writes are not code generation."""
import ast
from pathlib import Path
import re
import unittest

ROUTER = Path(__file__).resolve().parent / "model_router.py"

class ExternalCreateRoutingTest(unittest.TestCase):
    def test_word_boundaries_and_variants(self):
        source=ROUTER.read_text(encoding="utf-8")
        tree=ast.parse(source)
        dispatch=next(x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name=="dispatch")
        assignment=next(x for x in ast.walk(dispatch) if isinstance(x, ast.Assign) and any(isinstance(y, ast.Name) and y.id=="repository_file_creation" for y in x.targets))
        # Inspect only the source-defined pattern literals, avoiding optional model/HTTP dependencies.
        call=assignment.value.args[0]
        pattern="".join(ast.literal_eval(part) for part in (call.values if isinstance(call, ast.JoinedStr) else [call])) if isinstance(call, ast.Constant) else None
        if pattern is None:
            # The production expression is a Python re.search with adjacent strings.
            pattern=ast.literal_eval(call)
        positive=[
            "Can you make a txt file in the repo for me",
            "Please create a text file in the GitHub repository",
            "in github please add a text file",
            "save a txt file in my repo",
        ]
        negative=[
            "Write Python code that creates a text file in the repo",
            "Explain how GitHub creates files",
            "Can you make a webpage?",
            "Read the repo's existing txt file",
        ]
        for text in positive:
            with self.subTest(text=text):
                self.assertTrue(re.search(pattern,text.lower()),text)
        # These checks protect the simple external-action discrimination, not full
        # semantic language understanding.
        for text in negative[1:]:
            with self.subTest(text=text):
                self.assertFalse(re.search(pattern,text.lower()),text)


if __name__ == "__main__":
    unittest.main()
