#!/usr/bin/env python3
"""
Test runner for ACE to Prolog Parser tests
Run all tests or specific test categories
"""

import unittest
import sys
import os
from io import StringIO

# Import test modules
from test_fact_parsing import TestFactParsing
from test_rule_parsing import TestRuleParsing
from test_query_parsing import TestQueryParsing
from test_statement_classification import TestStatementClassification
from test_integration import TestACEToPrologIntegration


def run_specific_tests(test_categories=None):
    """
    Run specific test categories

    Args:
        test_categories: List of test category names to run.
                        Options: ['facts', 'rules', 'queries', 'classification', 'integration']
                        If None, runs all tests.
    """

    # Map category names to test classes
    category_map = {
        'facts': TestFactParsing,
        'rules': TestRuleParsing,
        'queries': TestQueryParsing,
        'classification': TestStatementClassification,
        'integration': TestACEToPrologIntegration
    }

    # Create test suite
    suite = unittest.TestSuite()

    if test_categories is None:
        # Run all tests
        test_categories = list(category_map.keys())

    for category in test_categories:
        if category in category_map:
            # Add all tests from the test class
            tests = unittest.TestLoader().loadTestsFromTestCase(category_map[category])
            suite.addTests(tests)
            print(f"Added {category} tests")
        else:
            print(f"Warning: Unknown test category '{category}'")

    return suite


def run_tests_with_detailed_output(suite):
    """Run tests with detailed output"""

    # Custom test result class for more detailed output
    class DetailedTestResult(unittest.TextTestResult):
        def addSuccess(self, test):
            super().addSuccess(test)
            if self.verbosity > 1:
                self.stream.write(f"✓ {test._testMethodName} ")
                self.stream.write(f"({test.__class__.__name__})\n")

        def addError(self, test, err):
            super().addError(test, err)
            self.stream.write(f"✗ ERROR: {test._testMethodName} ")
            self.stream.write(f"({test.__class__.__name__})\n")

        def addFailure(self, test, err):
            super().addFailure(test, err)
            self.stream.write(f"✗ FAIL: {test._testMethodName} ")
            self.stream.write(f"({test.__class__.__name__})\n")

    # Create custom test runner
    class DetailedTestRunner(unittest.TextTestRunner):
        resultclass = DetailedTestResult

    # Run tests
    runner = DetailedTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)

    return result


def print_test_summary(result):
    """Print a summary of test results"""
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    successes = total_tests - failures - errors

    print(f"Total tests run: {total_tests}")
    print(f"Successes: {successes}")
    print(f"Failures: {failures}")
    print(f"Errors: {errors}")

    if failures > 0:
        print(f"\nFAILURES ({failures}):")
        for test, traceback in result.failures:
            print(f"  - {test}")

    if errors > 0:
        print(f"\nERRORS ({errors}):")
        for test, traceback in result.errors:
            print(f"  - {test}")

    success_rate = (successes / total_tests) * 100 if total_tests > 0 else 0
    print(f"\nSuccess rate: {success_rate:.1f}%")

    if success_rate == 100.0:
        print("🎉 All tests passed!")
    elif success_rate >= 90.0:
        print("✅ Most tests passed - minor issues detected")
    elif success_rate >= 70.0:
        print("⚠️  Several tests failed - attention needed")
    else:
        print("❌ Many tests failed - major issues detected")


def main():
    """Main test runner function"""
    import argparse

    parser = argparse.ArgumentParser(description="Run ACE to Prolog Parser tests")
    parser.add_argument(
        '--categories',
        nargs='+',
        choices=['facts', 'rules', 'queries', 'classification', 'integration', 'all'],
        default=['all'],
        help='Test categories to run (default: all)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--failfast', '-f',
        action='store_true',
        help='Stop on first failure'
    )

    args = parser.parse_args()

    # Handle 'all' category
    if 'all' in args.categories:
        categories = None
    else:
        categories = args.categories

    print("ACE to Prolog Parser Test Suite")
    print("=" * 40)

    if categories:
        print(f"Running test categories: {', '.join(categories)}")
    else:
        print("Running all test categories")

    print()

    # Create and run test suite
    suite = run_specific_tests(categories)
    result = run_tests_with_detailed_output(suite)

    # Print summary
    print_test_summary(result)

    # Exit with appropriate code
    if result.wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()