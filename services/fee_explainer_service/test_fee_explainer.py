import os
import sys
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from services.fee_explainer_service.service import FeeExplainerService
import unittest

class TestFeeExplainer(unittest.TestCase):
    def setUp(self):
        self.service = FeeExplainerService()

    def test_single_scenario(self):
        result = self.service.generate_explanation("exit_load")
        self.assertIsNotNone(result)
        self.assertEqual(result["type"], "exit_load")
        self.assertLessEqual(len(result["bullets"]), 6)
        self.assertEqual(len(result["links"]), 2)
        print("✓ Single Scenario Test Passed")

    def test_multiple_scenarios(self):
        types = ["exit_load", "brokerage"]
        results = self.service.explain_multiple(types)
        self.assertEqual(len(results), 2)
        for r in results:
            self.assertLessEqual(len(r["bullets"]), 6)
            self.assertEqual(len(r["links"]), 2)
        print("✓ Multiple Scenarios Test Passed")

if __name__ == "__main__":
    unittest.main()
