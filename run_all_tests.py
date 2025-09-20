#!/usr/bin/env python3
"""
All tests suite - run all ACE to Prolog Parser tests
"""

import unittest

# Import all test modules
from test_fact_parsing import TestFactParsing
from test_rule_parsing import TestRuleParsing
from test_query_parsing import TestQueryParsing
from test_statement_classification import TestStatementClassification
from test_integration import TestACEToPrologIntegration


class TestAllTests(unittest.TestCase):
    """Test suite that runs all other test suites"""

    def test_run_all_tests(self):
        """Run all test suites"""
        # Create test suite
        suite = unittest.TestSuite()

        # Add all test classes
        test_classes = [
            TestFactParsing,
            TestRuleParsing,
            TestQueryParsing,
            TestStatementClassification,
            TestACEToPrologIntegration
        ]

        for test_class in test_classes:
            tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
            suite.addTests(tests)

        # Run tests
        runner = unittest.TextTestRunner(verbosity=0, stream=open('/dev/null', 'w'))
        result = runner.run(suite)

        # Assert that all tests passed
        self.assertTrue(result.wasSuccessful(),
                        f"Some tests failed: {len(result.failures)} failures, {len(result.errors)} errors")


if __name__ == '__main__':
    unittest.main()