#!/usr/bin/env python3
"""
Tests for ACE statement classification functionality
"""

import unittest
import sys
import os

from src.ace_prolog_parser import ACEToPrologParser
from src.ACEStatement import ACEStatement


class TestStatementClassification(unittest.TestCase):
    """Test ACE statement type classification"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.parser = ACEToPrologParser()

    def test_fact_classification(self):
        """Test classification of fact statements"""
        fact_statements = [
            "John is a person.",
            "Mary is happy.",
            "Bob likes chocolate.",
            "Alice has age 25.",
            "The-cat is sleeping.",
            "Computer-1 runs software.",
        ]

        for statement in fact_statements:
            with self.subTest(statement=statement):
                result = self.parser.parse_statement(statement)
                self.assertEqual(result.type, 'fact')
                self.assertEqual(result.text, statement)

    def test_rule_classification(self):
        """Test classification of rule statements"""
        rule_statements = [
            "X is happy if X likes chocolate.",
            "If X is a student then X is young.",
            "Y is tired if Y works hard.",
            "If A has age B then A is person.",
            "Someone is successful if someone works hard.",
        ]

        for statement in rule_statements:
            with self.subTest(statement=statement):
                result = self.parser.parse_statement(statement)
                self.assertEqual(result.type, 'rule')
                self.assertEqual(result.text, statement)

    def test_query_classification(self):
        """Test classification of query statements"""
        query_statements = [
            "Is John happy?",
            "Who is tall?",
            "What does Mary like?",
            "Are students young?",
            "Does Bob like chocolate?",
            "Where is Alice?",
            "When did John arrive?",
            "Why is Mary sad?",
            "How does the system work?",
        ]

        for statement in query_statements:
            with self.subTest(statement=statement):
                result = self.parser.parse_statement(statement)
                self.assertEqual(result.type, 'query')
                self.assertEqual(result.text, statement)

    def test_auto_period_addition(self):
        """Test automatic period addition for statements without periods"""
        test_cases = [
            ("John is a person", "John is a person."),
            ("Mary is happy", "Mary is happy."),
            ("Bob likes chocolate", "Bob likes chocolate."),
        ]

        for input_statement, expected_text in test_cases:
            with self.subTest(input_statement=input_statement):
                result = self.parser.parse_statement(input_statement)
                self.assertEqual(result.type, 'fact')
                self.assertEqual(result.text, expected_text)

    def test_case_insensitive_classification(self):
        """Test case insensitive classification for rules and queries"""
        test_cases = [
            ("x is happy if x likes chocolate.", 'rule'),
            ("IF X is student THEN X is young.", 'rule'),
            ("is john happy?", 'query'),
            ("WHO is tall?", 'query'),
            ("what DOES mary like?", 'query'),
        ]

        for statement, expected_type in test_cases:
            with self.subTest(statement=statement):
                result = self.parser.parse_statement(statement)
                self.assertEqual(result.type, expected_type)

    def test_ambiguous_statements_default_to_fact(self):
        """Test that ambiguous statements default to fact classification"""
        ambiguous_statements = [
            "This is a complex sentence",
            "Random text without clear structure",
            "Multiple words in a sequence",
            "123 numbers and text",
        ]

        for statement in ambiguous_statements:
            with self.subTest(statement=statement):
                result = self.parser.parse_statement(statement)
                self.assertEqual(result.type, 'fact')
                # Should add period if not present
                expected_text = statement + '.' if not statement.endswith('.') else statement
                self.assertEqual(result.text, expected_text)

    def test_empty_and_whitespace_statements(self):
        """Test handling of empty and whitespace-only statements"""
        test_cases = [
            ("", "."),
            ("   ", "."),
            ("\t", "."),
            ("\n", "."),
        ]

        for input_statement, expected_text in test_cases:
            with self.subTest(input_statement=repr(input_statement)):
                result = self.parser.parse_statement(input_statement)
                self.assertEqual(result.type, 'fact')
                self.assertEqual(result.text, expected_text)

    def test_statement_with_periods_in_middle(self):
        """Test statements that have periods in the middle"""
        test_cases = [
            ("Mr. John is a person.", 'fact'),
            ("Dr. Mary is happy.", 'fact'),
            ("Version 1.0 is software.", 'fact'),
        ]

        for statement, expected_type in test_cases:
            with self.subTest(statement=statement):
                result = self.parser.parse_statement(statement)
                self.assertEqual(result.type, expected_type)
                self.assertEqual(result.text, statement)

    def test_multiple_sentence_statements(self):
        """Test statements with multiple sentences"""
        test_cases = [
            ("John is happy. Mary is sad.", 'fact'),  # Will be treated as one fact
            ("Is John happy? Is Mary sad?", 'query'),  # Will be treated as one query
        ]

        for statement, expected_type in test_cases:
            with self.subTest(statement=statement):
                result = self.parser.parse_statement(statement)
                self.assertEqual(result.type, expected_type)

    def test_statements_with_special_characters(self):
        """Test statements containing special characters"""
        test_cases = [
            ("John's dog is happy.", 'fact'),
            ("Mary-Jane is a person.", 'fact'),
            ("Computer@Home is running.", 'fact'),
            ("Version_2.1 is software.", 'fact'),
        ]

        for statement, expected_type in test_cases:
            with self.subTest(statement=statement):
                result = self.parser.parse_statement(statement)
                self.assertEqual(result.type, expected_type)

    def test_parse_text_multiple_statements(self):
        """Test parsing multiple statements from text"""
        text = """
        John is a person.
        Mary is happy.
        X is smart if X is student.
        Is Bob tall?
        # This is a comment and should be ignored
        Alice likes music.
        Who is kind?
        """

        statements = self.parser.parse_text(text)

        # Should have 6 statements (comment should be ignored)
        self.assertEqual(len(statements), 6)

        # Check types
        expected_types = ['fact', 'fact', 'rule', 'query', 'fact', 'query']
        for i, expected_type in enumerate(expected_types):
            self.assertEqual(statements[i].type, expected_type)

        # Check specific texts
        expected_texts = [
            "John is a person.",
            "Mary is happy.",
            "X is smart if X is student.",
            "Is Bob tall?",
            "Alice likes music.",
            "Who is kind?"
        ]
        for i, expected_text in enumerate(expected_texts):
            self.assertEqual(statements[i].text, expected_text)

    def test_parse_text_with_empty_lines(self):
        """Test parsing text with empty lines and comments"""
        text = """

        John is a person.

        # Comment line

        Mary is happy.

        """

        statements = self.parser.parse_text(text)

        # Should have 2 statements
        self.assertEqual(len(statements), 2)
        self.assertEqual(statements[0].text, "John is a person.")
        self.assertEqual(statements[1].text, "Mary is happy.")

    def test_parse_text_comment_handling(self):
        """Test that comments are properly ignored"""
        text = """
        # This is a comment
        John is a person.
        # Another comment
        # Yet another comment
        Mary is happy.
        """

        statements = self.parser.parse_text(text)

        # Should have 2 statements (comments ignored)
        self.assertEqual(len(statements), 2)
        self.assertEqual(statements[0].text, "John is a person.")
        self.assertEqual(statements[1].text, "Mary is happy.")


if __name__ == '__main__':
    unittest.main()