"""Real repair-context regressions: passing checks cannot diagnose failures."""
import json
import unittest
from brain_programming import _receipt_semantics


class StructuredReceiptScope(unittest.TestCase):
    def test_passed_dependency_and_error_names_do_not_become_failures(self):
        receipt={"cases":[
            {"name":"responsive-mobile-canvas","passed":False,"expected":"right edge <=390","actual":{"left":8,"width":390,"right":398}},
            {"name":"dependency-loads","passed":True},
            {"name":"no-TypeError-browser-errors","passed":True},
        ]}
        result=_receipt_semantics(json.dumps(receipt))
        self.assertNotIn('dependency',result['categories'])
        self.assertNotIn('type',result['categories'])
        self.assertEqual(result['failingTests'],['responsive-mobile-canvas'])
        self.assertIn('398',' '.join(result['expectedActual']))
        self.assertEqual(len(result['behaviorCases']),3)

    def test_actual_failed_dependency_and_plain_error_are_retained(self):
        receipt={"cases":[{"name":"module-load","passed":False,"message":"ModuleNotFoundError: No module named example"}]}
        result=_receipt_semantics('TypeError: separate plain diagnostic\n'+json.dumps(receipt))
        self.assertIn('dependency',result['categories'])
        self.assertIn('type',result['categories'])

    def test_passing_nested_result_does_not_supply_extra_failed_cases(self):
        result=_receipt_semantics(json.dumps({"cases":[{"name":"response-shape","passed":True,"actual":{"ok":False}},{"name":"counter","passed":False,"expected":2,"actual":1}]}))
        self.assertEqual(result['structuredReceipt']['caseCount'],2)
        self.assertEqual(result['failingTests'],['counter'])

    def test_successful_transport_does_not_hide_failed_child_tests(self):
        result=_receipt_semantics(json.dumps({'ok':True,'cases':[{'name':'counter','passed':False,'expected':2,'actual':1}]}))
        self.assertEqual(result['failingTests'],['counter'])
        self.assertIn('behavior-mismatch',result['categories'])

if __name__=='__main__':unittest.main()
