#!/usr/bin/env python3
"""
Tests for ACE rule parsing functionality
"""

import unittest
import sys
import os

from src.ace_prolog_parser import ACEToPrologParser


class TestRuleParsing(unittest.TestCase):
    """Test ACE rule parsing to Prolog conversion"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.parser = ACEToPrologParser()

    def test_simple_if_rules(self):
        """Test simple 'X is Y if Z' rules"""
        test_cases = [
            ("X is happy if X likes chocolate.", "happy(X) :- likes(X, chocolate)"),
            ("X is smart if X is student.", "smart(X) :- student(X)"),
            ("X is tired if X is busy.", "tired(X) :- busy(X)"),
            ("Y is successful if Y is hardworking.", "successful(Y) :- hardworking(Y)"),
        ]

        for ace_rule, expected_prolog in test_cases:
            with self.subTest(ace_rule=ace_rule):
                result = self.parser.ace_to_prolog_rule(ace_rule)
                self.assertEqual(result, expected_prolog)

    def test_specific_entity_in_condition(self):
        """Test rules with specific entities in conditions"""
        test_cases = [
            ("X is happy if X likes ice-cream.", "happy(X) :- likes(X, ice_cream)"),
            ("X is satisfied if X likes chocolate.", "happy(X) :- likes(X, chocolate)"),  # Note: This might need fixing
            ("Y is content if Y likes music.", "content(Y) :- likes(Y, music)"),
        ]

        for ace_rule, expected_prolog in test_cases:
            with self.subTest(ace_rule=ace_rule):
                result = self.parser.ace_to_prolog_rule(ace_rule)
                # Note: The second test case shows a potential bug - "satisfied" becomes "happy"
                # This test documents current behavior, but the bug should be fixed
                if "satisfied" in ace_rule:
                    expected_prolog = "satisfied(X) :- likes(X, chocolate)"
                self.assertEqual(result, expected_prolog)

    def test_case_insensitive_if(self):
        """Test that 'if' matching is case insensitive"""
        test_cases = [
            ("X is happy if X likes chocolate.", "happy(X) :- likes(X, chocolate)"),
            ("X is happy IF X likes chocolate.", "happy(X) :- likes(X, chocolate)"),
            ("X is happy If X likes chocolate.", "happy(X) :- likes(X, chocolate)"),
            ("X is happy iF X likes chocolate.", "happy(X) :- likes(X, chocolate)"),
        ]

        for ace_rule, expected_prolog in test_cases:
            with self.subTest(ace_rule=ace_rule):
                result = self.parser.ace_to_prolog_rule(ace_rule)
                self.assertEqual(result, expected_prolog)

    def test_different_variable_names(self):
        """Test rules with different variable names"""
        test_cases = [
            ("A is happy if A likes chocolate.", "happy(A) :- likes(A, chocolate)"),
            ("Person is happy if Person likes chocolate.", "happy(PERSON) :- likes(PERSON, chocolate)"),
            ("Someone is happy if Someone likes chocolate.", "happy(SOMEONE) :- likes(SOMEONE, chocolate)"),
        ]

        for ace_rule, expected_prolog in test_cases:
            with self.subTest(ace_rule=ace_rule):
                result = self.parser.ace_to_prolog_rule(ace_rule)
                self.assertEqual(result, expected_prolog)

    def test_condition_parsing_likes(self):
        """Test condition parsing for 'likes' patterns"""
        # Test the _parse_condition method directly
        test_cases = [
            ("X likes chocolate", "X", "likes(X, chocolate)"),
            ("John likes music", "X", "likes(john, music)"),
            ("Y likes ice-cream", "Y", "likes(Y, ice_cream)"),
        ]

        for condition, var_name, expected in test_cases:
            with self.subTest(condition=condition, var_name=var_name):
                result = self.parser._parse_condition(condition, var_name)
                self.assertEqual(result, expected)

    def test_condition_parsing_is(self):
        """Test condition parsing for 'is' patterns"""
        test_cases = [
            ("X is student", "X", "student(X)"),
            ("Mary is teacher", "X", "teacher(mary)"),
            ("Y is happy", "Y", "happy(Y)"),
        ]

        for condition, var_name, expected in test_cases:
            with self.subTest(condition=condition, var_name=var_name):
                result = self.parser._parse_condition(condition, var_name)
                self.assertEqual(result, expected)

    def test_unsupported_rule_patterns(self):
        """Test that unsupported rule patterns return None"""
        unsupported_rules = [
            "X is happy and Y is sad if Z likes music.",
            "If X and Y then Z.",
            "Complex rule with multiple conditions.",
            "Not a rule at all.",
            "",
        ]

        for ace_rule in unsupported_rules:
            with self.subTest(ace_rule=ace_rule):
                result = self.parser.ace_to_prolog_rule(ace_rule)
                self.assertIsNone(result)

    def test_malformed_rules(self):
        """Test handling of malformed rules"""
        malformed_rules = [
            "X is if Y likes chocolate.",  # Missing conclusion
            "X is happy if.",  # Missing condition
            "if X likes chocolate.",  # Missing conclusion entirely
            "X is happy if Y.",  # Incomplete condition
        ]

        for ace_rule in malformed_rules:
            with self.subTest(ace_rule=ace_rule):
                result = self.parser.ace_to_prolog_rule(ace_rule)
                self.assertIsNone(result)

    def test_whitespace_handling(self):
        """Test handling of various whitespace scenarios in rules"""
        test_cases = [
            ("  X is happy if X likes chocolate.  ", "happy(X) :- likes(X, chocolate)"),
            ("\tX is happy if X likes chocolate.\t", "happy(X) :- likes(X, chocolate)"),
            ("X  is  happy  if  X  likes  chocolate.", "happy(X) :- likes(X, chocolate)"),
        ]

        for ace_rule, expected_prolog in test_cases:
            with self.subTest(ace_rule=ace_rule):
                result = self.parser.ace_to_prolog_rule(ace_rule)
                self.assertEqual(result, expected_prolog)

    def test_without_period(self):
        """Test rules without trailing period"""
        test_cases = [
            ("X is happy if X likes chocolate", "happy(X) :- likes(X, chocolate)"),
            ("Y is smart if Y is student", "smart(Y) :- student(Y)"),
        ]

        for ace_rule, expected_prolog in test_cases:
            with self.subTest(ace_rule=ace_rule):
                result = self.parser.ace_to_prolog_rule(ace_rule)
                self.assertEqual(result, expected_prolog)


if __name__ == '__main__':
    unittest.main()