#!/usr/bin/env python3
"""
Tests for ACE query parsing functionality
"""

import unittest
import sys
import os

from src.ace_prolog_parser import ACEToPrologParser
from src.QueryType import QueryType


class TestQueryParsing(unittest.TestCase):
    """Test ACE query parsing to Prolog conversion"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.parser = ACEToPrologParser()

    def test_is_x_y_queries(self):
        """Test 'Is X Y?' query pattern parsing"""
        test_cases = [
            ("Is John happy?", "happy(john)"),
            ("Is Mary tall?", "tall(mary)"),
            ("Is Bob smart?", "smart(bob)"),
            ("Is Alice kind?", "kind(alice)"),
            ("Is the-dog friendly?", "friendly(the_dog)"),
        ]

        for ace_query, expected_prolog in test_cases:
            with self.subTest(ace_query=ace_query):
                result = self.parser.ace_to_prolog_query(ace_query)
                self.assertEqual(result, expected_prolog)

    def test_who_is_x_queries(self):
        """Test 'Who is X?' query pattern parsing"""
        test_cases = [
            ("Who is happy?", "happy(X)"),
            ("Who is tall?", "tall(X)"),
            ("Who is smart?", "smart(X)"),
            ("Who is kind?", "kind(X)"),
            ("Who is friendly?", "friendly(X)"),
        ]

        for ace_query, expected_prolog in test_cases:
            with self.subTest(ace_query=ace_query):
                result = self.parser.ace_to_prolog_query(ace_query)
                self.assertEqual(result, expected_prolog)

    def test_what_does_x_like_queries(self):
        """Test 'What does X like?' query pattern parsing"""
        test_cases = [
            ("What does John like?", "likes(john, X)"),
            ("What does Mary like?", "likes(mary, X)"),
            ("What does Bob like?", "likes(bob, X)"),
            ("What does Alice like?", "likes(alice, X)"),
            ("What does the-cat like?", "likes(the_cat, X)"),
        ]

        for ace_query, expected_prolog in test_cases:
            with self.subTest(ace_query=ace_query):
                result = self.parser.ace_to_prolog_query(ace_query)
                self.assertEqual(result, expected_prolog)

    def test_query_type_detection(self):
        """Test query type detection"""
        test_cases = [
            ("Is John happy?", QueryType.IS_X_Y),
            ("Who is happy?", QueryType.WHO_IS_X),
            ("What does John like?", QueryType.WHAT_DOES_X_LIKE),
        ]

        for ace_query, expected_type in test_cases:
            with self.subTest(ace_query=ace_query):
                result = self.parser.parse_query_type(ace_query)
                self.assertEqual(result, expected_type)

    def test_unsupported_query_types(self):
        """Test that unsupported query types return None"""
        unsupported_queries = [
            "Where is John?",
            "When did Mary arrive?",
            "Why is Bob happy?",
            "How does Alice work?",
            "Can John swim?",
            "Does Mary like chocolate?",
            "Random question without proper structure?",
        ]

        for ace_query in unsupported_queries:
            with self.subTest(ace_query=ace_query):
                query_type = self.parser.parse_query_type(ace_query)
                self.assertIsNone(query_type)

                prolog_query = self.parser.ace_to_prolog_query(ace_query)
                self.assertIsNone(prolog_query)

    def test_case_sensitivity(self):
        """Test case handling in queries"""
        test_cases = [
            ("is john happy?", "happy(john)"),  # lowercase 'is'
            ("who is happy?", "happy(X)"),  # lowercase 'who'
            ("what does john like?", "likes(john, X)"),  # lowercase 'what does'
        ]

        for ace_query, expected_prolog in test_cases:
            with self.subTest(ace_query=ace_query):
                result = self.parser.ace_to_prolog_query(ace_query)
                self.assertEqual(result, expected_prolog)

    def test_entity_normalization_in_queries(self):
        """Test entity name normalization in queries"""
        test_cases = [
            ("Is John-Smith happy?", "happy(john_smith)"),
            ("Who is ice-cream-lover?", "ice_cream_lover(X)"),
            ("What does Mary Jane like?", "likes(mary_jane, X)"),
            ("Is Computer-1 working?", "working(computer_1)"),
        ]

        for ace_query, expected_prolog in test_cases:
            with self.subTest(ace_query=ace_query):
                result = self.parser.ace_to_prolog_query(ace_query)
                self.assertEqual(result, expected_prolog)

    def test_whitespace_handling(self):
        """Test handling of various whitespace scenarios in queries"""
        test_cases = [
            ("  Is John happy?  ", "happy(john)"),
            ("\tWho is happy?\t", "happy(X)"),
            ("What  does  John  like?", "likes(john, X)"),
        ]

        for ace_query, expected_prolog in test_cases:
            with self.subTest(ace_query=ace_query):
                result = self.parser.ace_to_prolog_query(ace_query)
                self.assertEqual(result, expected_prolog)

    def test_without_question_mark(self):
        """Test queries without question mark (should still work)"""
        test_cases = [
            ("Is John happy", "happy(john)"),
            ("Who is happy", "happy(X)"),
            ("What does John like", "likes(john, X)"),
        ]

        for ace_query, expected_prolog in test_cases:
            with self.subTest(ace_query=ace_query):
                result = self.parser.ace_to_prolog_query(ace_query)
                self.assertEqual(result, expected_prolog)

    def test_malformed_queries(self):
        """Test handling of malformed queries"""
        malformed_queries = [
            "Is?",  # Missing content
            "Who is?",  # Missing property
            "What does like?",  # Missing entity
            "Is John?",  # Missing property
            "",  # Empty query
        ]

        for ace_query in malformed_queries:
            with self.subTest(ace_query=ace_query):
                result = self.parser.ace_to_prolog_query(ace_query)
                self.assertIsNone(result)

    def test_complex_property_names(self):
        """Test queries with complex property names"""
        test_cases = [
            ("Is John very-happy?", "very_happy(john)"),
            ("Who is extremely-tall?", "extremely_tall(X)"),
            ("Is Alice super-smart?", "super_smart(alice)"),
        ]

        for ace_query, expected_prolog in test_cases:
            with self.subTest(ace_query=ace_query):
                result = self.parser.ace_to_prolog_query(ace_query)
                self.assertEqual(result, expected_prolog)


if __name__ == '__main__':
    unittest.main()