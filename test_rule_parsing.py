#!/usr/bin/env python3
"""
Tests for ACE rule parsing functionality
"""

import unittest

from src.ace_prolog_parser import ACEToPrologParser


class TestRuleParsing(unittest.TestCase):
    """Test ACE rule parsing to Prolog conversion"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.parser = ACEToPrologParser()

    def test_simple_if_rule_x_is_happy_if_x_likes_chocolate(self):
        """Test simple 'X is happy if X likes chocolate' rule"""
        ace_rule = "X is happy if X likes chocolate."
        expected_prolog = "happy(X) :- likes(X, chocolate)"
        result = self.parser.ace_to_prolog_rule(ace_rule)
        self.assertEqual(result, expected_prolog)

    def test_simple_if_rule_x_is_smart_if_x_is_student(self):
        """Test simple 'X is smart if X is student' rule"""
        ace_rule = "X is smart if X is student."
        expected_prolog = "smart(X) :- student(X)"
        result = self.parser.ace_to_prolog_rule(ace_rule)
        self.assertEqual(result, expected_prolog)

    def test_simple_if_rule_x_is_tired_if_x_is_busy(self):
        """Test simple 'X is tired if X is busy' rule"""
        ace_rule = "X is tired if X is busy."
        expected_prolog = "tired(X) :- busy(X)"
        result = self.parser.ace_to_prolog_rule(ace_rule)
        self.assertEqual(result, expected_prolog)

    def test_simple_if_rule_y_is_successful_if_y_is_hardworking(self):
        """Test simple 'Y is successful if Y is hardworking' rule"""
        ace_rule = "Y is successful if Y is hardworking."
        expected_prolog = "successful(Y) :- hardworking(Y)"
        result = self.parser.ace_to_prolog_rule(ace_rule)
        self.assertEqual(result, expected_prolog)

    def test_specific_entity_x_is_happy_if_x_likes_ice_cream(self):
        """Test rule with specific entity - ice cream"""
        ace_rule = "X is happy if X likes ice-cream."
        expected_prolog = "happy(X) :- likes(X, ice_cream)"
        result = self.parser.ace_to_prolog_rule(ace_rule)
        self.assertEqual(result, expected_prolog)

    def test_specific_entity_x_is_satisfied_if_x_likes_chocolate(self):
        """Test rule with specific entity - satisfied and chocolate"""
        ace_rule = "X is satisfied if X likes chocolate."
        expected_prolog = "satisfied(X) :- likes(X, chocolate)"
        result = self.parser.ace_to_prolog_rule(ace_rule)
        self.assertEqual(result, expected_prolog)

    def test_specific_entity_y_is_content_if_y_likes_music(self):
        """Test rule with specific entity - content and music"""
        ace_rule = "Y is content if Y likes music."
        expected_prolog = "content(Y) :- likes(Y, music)"
        result = self.parser.ace_to_prolog_rule(ace_rule)
        self.assertEqual(result, expected_prolog)

    def test_case_insensitive_if_lowercase(self):
        """Test case insensitive 'if' - lowercase"""
        ace_rule = "X is happy if X likes chocolate."
        expected_prolog = "happy(X) :- likes(X, chocolate)"
        result = self.parser.ace_to_prolog_rule(ace_rule)
        self.assertEqual(result, expected_prolog)

    def test_case_insensitive_if_uppercase(self):
        """Test case insensitive 'if' - uppercase"""
        ace_rule = "X is happy IF X likes chocolate."
        expected_prolog = "happy(X) :- likes(X, chocolate)"
        result = self.parser.ace_to_prolog_rule(ace_rule)
        self.assertEqual(result, expected_prolog)

    def test_case_insensitive_if_title_case(self):
        """Test case insensitive 'if' - title case"""
        ace_rule = "X is happy If X likes chocolate."
        expected_prolog = "happy(X) :- likes(X, chocolate)"
        result = self.parser.ace_to_prolog_rule(ace_rule)
        self.assertEqual(result, expected_prolog)

    def test_case_insensitive_if_mixed_case(self):
        """Test case insensitive 'if' - mixed case"""
        ace_rule = "X is happy iF X likes chocolate."
        expected_prolog = "happy(X) :- likes(X, chocolate)"
        result = self.parser.ace_to_prolog_rule(ace_rule)
        self.assertEqual(result, expected_prolog)

    def test_variable_name_a(self):
        """Test rule with variable name A"""
        ace_rule = "A is happy if A likes chocolate."
        expected_prolog = "happy(A) :- likes(A, chocolate)"
        result = self.parser.ace_to_prolog_rule(ace_rule)
        self.assertEqual(result, expected_prolog)

    def test_variable_name_person(self):
        """Test rule with variable name Person"""
        ace_rule = "Person is happy if Person likes chocolate."
        expected_prolog = "happy(PERSON) :- likes(PERSON, chocolate)"
        result = self.parser.ace_to_prolog_rule(ace_rule)
        self.assertEqual(result, expected_prolog)

    def test_variable_name_someone(self):
        """Test rule with variable name Someone"""
        ace_rule = "Someone is happy if Someone likes chocolate."
        expected_prolog = "happy(SOMEONE) :- likes(SOMEONE, chocolate)"
        result = self.parser.ace_to_prolog_rule(ace_rule)
        self.assertEqual(result, expected_prolog)

    def test_condition_parsing_x_likes_chocolate(self):
        """Test condition parsing for 'X likes chocolate'"""
        condition = "X likes chocolate"
        var_name = "X"
        expected = "likes(X, chocolate)"
        result = self.parser._parse_condition(condition, var_name)
        self.assertEqual(result, expected)

    def test_condition_parsing_john_likes_music(self):
        """Test condition parsing for 'John likes music'"""
        condition = "John likes music"
        var_name = "X"
        expected = "likes(john, music)"
        result = self.parser._parse_condition(condition, var_name)
        self.assertEqual(result, expected)

    def test_condition_parsing_y_likes_ice_cream(self):
        """Test condition parsing for 'Y likes ice-cream'"""
        condition = "Y likes ice-cream"
        var_name = "Y"
        expected = "likes(Y, ice_cream)"
        result = self.parser._parse_condition(condition, var_name)
        self.assertEqual(result, expected)

    def test_condition_parsing_x_is_student(self):
        """Test condition parsing for 'X is student'"""
        condition = "X is student"
        var_name = "X"
        expected = "student(X)"
        result = self.parser._parse_condition(condition, var_name)
        self.assertEqual(result, expected)

    def test_condition_parsing_mary_is_teacher(self):
        """Test condition parsing for 'Mary is teacher'"""
        condition = "Mary is teacher"
        var_name = "X"
        expected = "teacher(mary)"
        result = self.parser._parse_condition(condition, var_name)
        self.assertEqual(result, expected)

    def test_condition_parsing_y_is_happy(self):
        """Test condition parsing for 'Y is happy'"""
        condition = "Y is happy"
        var_name = "Y"
        expected = "happy(Y)"
        result = self.parser._parse_condition(condition, var_name)
        self.assertEqual(result, expected)

    # def test_unsupported_rule_multiple_conditions_and(self):
    #     """Test unsupported rule with multiple conditions using 'and'"""
    #     ace_rule = "X is happy and Y is sad if Z likes music."
    #     result = self.parser.ace_to_prolog_rule(ace_rule)
    #     self.assertIsNone(result)

    def test_unsupported_rule_if_then_format(self):
        """Test unsupported rule with if-then format"""
        ace_rule = "If X and Y then Z."
        result = self.parser.ace_to_prolog_rule(ace_rule)
        self.assertIsNone(result)

    def test_unsupported_rule_complex_multiple_conditions(self):
        """Test unsupported complex rule with multiple conditions"""
        ace_rule = "Complex rule with multiple conditions."
        result = self.parser.ace_to_prolog_rule(ace_rule)
        self.assertIsNone(result)

    def test_unsupported_rule_not_a_rule(self):
        """Test unsupported text that is not a rule"""
        ace_rule = "Not a rule at all."
        result = self.parser.ace_to_prolog_rule(ace_rule)
        self.assertIsNone(result)

    def test_unsupported_rule_empty_string(self):
        """Test unsupported empty string"""
        ace_rule = ""
        result = self.parser.ace_to_prolog_rule(ace_rule)
        self.assertIsNone(result)

    def test_malformed_rule_missing_conclusion(self):
        """Test malformed rule with missing conclusion"""
        ace_rule = "X is if Y likes chocolate."
        result = self.parser.ace_to_prolog_rule(ace_rule)
        self.assertIsNone(result)

    def test_malformed_rule_missing_condition(self):
        """Test malformed rule with missing condition"""
        ace_rule = "X is happy if."
        result = self.parser.ace_to_prolog_rule(ace_rule)
        self.assertIsNone(result)

    def test_malformed_rule_missing_conclusion_entirely(self):
        """Test malformed rule missing conclusion entirely"""
        ace_rule = "if X likes chocolate."
        result = self.parser.ace_to_prolog_rule(ace_rule)
        self.assertIsNone(result)

    def test_malformed_rule_incomplete_condition(self):
        """Test malformed rule with incomplete condition"""
        ace_rule = "X is happy if Y."
        result = self.parser.ace_to_prolog_rule(ace_rule)
        self.assertIsNone(result)

    def test_whitespace_leading_trailing_spaces(self):
        """Test handling of leading and trailing spaces"""
        ace_rule = "  X is happy if X likes chocolate.  "
        expected_prolog = "happy(X) :- likes(X, chocolate)"
        result = self.parser.ace_to_prolog_rule(ace_rule)
        self.assertEqual(result, expected_prolog)

    def test_whitespace_leading_trailing_tabs(self):
        """Test handling of leading and trailing tabs"""
        ace_rule = "\tX is happy if X likes chocolate.\t"
        expected_prolog = "happy(X) :- likes(X, chocolate)"
        result = self.parser.ace_to_prolog_rule(ace_rule)
        self.assertEqual(result, expected_prolog)

    # def test_whitespace_multiple_spaces_between_words(self):
    #     """Test handling of multiple spaces between words"""
    #     ace_rule = "X  is  happy  if  X  likes  chocolate."
    #     expected_prolog = "happy(X) :- likes(X, chocolate)"
    #     result = self.parser.ace_to_prolog_rule(ace_rule)
    #     self.assertEqual(result, expected_prolog)

    def test_without_period_x_is_happy(self):
        """Test rule without trailing period - happy case"""
        ace_rule = "X is happy if X likes chocolate"
        expected_prolog = "happy(X) :- likes(X, chocolate)"
        result = self.parser.ace_to_prolog_rule(ace_rule)
        self.assertEqual(result, expected_prolog)

    def test_without_period_y_is_smart(self):
        """Test rule without trailing period - smart case"""
        ace_rule = "Y is smart if Y is student"
        expected_prolog = "smart(Y) :- student(Y)"
        result = self.parser.ace_to_prolog_rule(ace_rule)
        self.assertEqual(result, expected_prolog)


if __name__ == '__main__':
    unittest.main()