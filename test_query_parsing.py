#!/usr/bin/env python3
"""
Tests for ACE query parsing functionality
"""

import unittest

from src.ace_prolog_parser import ACEToPrologParser
from src.QueryType import QueryType


class TestQueryParsing(unittest.TestCase):
    """Test ACE query parsing to Prolog conversion"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.parser = ACEToPrologParser()

    def test_is_john_happy_query(self):
        """Test 'Is John happy?' query pattern parsing"""
        ace_query = "Is John happy?"
        expected_prolog = "happy(john)"
        result = self.parser.ace_to_prolog_query(ace_query)
        self.assertEqual(result, expected_prolog)

    def test_is_mary_tall_query(self):
        """Test 'Is Mary tall?' query pattern parsing"""
        ace_query = "Is Mary tall?"
        expected_prolog = "tall(mary)"
        result = self.parser.ace_to_prolog_query(ace_query)
        self.assertEqual(result, expected_prolog)

    def test_is_bob_smart_query(self):
        """Test 'Is Bob smart?' query pattern parsing"""
        ace_query = "Is Bob smart?"
        expected_prolog = "smart(bob)"
        result = self.parser.ace_to_prolog_query(ace_query)
        self.assertEqual(result, expected_prolog)

    def test_is_alice_kind_query(self):
        """Test 'Is Alice kind?' query pattern parsing"""
        ace_query = "Is Alice kind?"
        expected_prolog = "kind(alice)"
        result = self.parser.ace_to_prolog_query(ace_query)
        self.assertEqual(result, expected_prolog)

    # def test_is_the_dog_friendly_query(self):
    #     """Test 'Is the-dog friendly?' query pattern parsing"""
    #     ace_query = "Is the-dog friendly?"
    #     expected_prolog = "friendly(the_dog)"
    #     result = self.parser.ace_to_prolog_query(ace_query)
    #     self.assertEqual(result, expected_prolog)

    def test_who_is_happy_query(self):
        """Test 'Who is happy?' query pattern parsing"""
        ace_query = "Who is happy?"
        expected_prolog = "happy(X)"
        result = self.parser.ace_to_prolog_query(ace_query)
        self.assertEqual(result, expected_prolog)

    def test_who_is_tall_query(self):
        """Test 'Who is tall?' query pattern parsing"""
        ace_query = "Who is tall?"
        expected_prolog = "tall(X)"
        result = self.parser.ace_to_prolog_query(ace_query)
        self.assertEqual(result, expected_prolog)

    def test_who_is_smart_query(self):
        """Test 'Who is smart?' query pattern parsing"""
        ace_query = "Who is smart?"
        expected_prolog = "smart(X)"
        result = self.parser.ace_to_prolog_query(ace_query)
        self.assertEqual(result, expected_prolog)

    def test_who_is_kind_query(self):
        """Test 'Who is kind?' query pattern parsing"""
        ace_query = "Who is kind?"
        expected_prolog = "kind(X)"
        result = self.parser.ace_to_prolog_query(ace_query)
        self.assertEqual(result, expected_prolog)

    def test_who_is_friendly_query(self):
        """Test 'Who is friendly?' query pattern parsing"""
        ace_query = "Who is friendly?"
        expected_prolog = "friendly(X)"
        result = self.parser.ace_to_prolog_query(ace_query)
        self.assertEqual(result, expected_prolog)

    def test_what_does_john_like_query(self):
        """Test 'What does John like?' query pattern parsing"""
        ace_query = "What does John like?"
        expected_prolog = "likes(john, X)"
        result = self.parser.ace_to_prolog_query(ace_query)
        self.assertEqual(result, expected_prolog)

    def test_what_does_mary_like_query(self):
        """Test 'What does Mary like?' query pattern parsing"""
        ace_query = "What does Mary like?"
        expected_prolog = "likes(mary, X)"
        result = self.parser.ace_to_prolog_query(ace_query)
        self.assertEqual(result, expected_prolog)

    def test_what_does_bob_like_query(self):
        """Test 'What does Bob like?' query pattern parsing"""
        ace_query = "What does Bob like?"
        expected_prolog = "likes(bob, X)"
        result = self.parser.ace_to_prolog_query(ace_query)
        self.assertEqual(result, expected_prolog)

    def test_what_does_alice_like_query(self):
        """Test 'What does Alice like?' query pattern parsing"""
        ace_query = "What does Alice like?"
        expected_prolog = "likes(alice, X)"
        result = self.parser.ace_to_prolog_query(ace_query)
        self.assertEqual(result, expected_prolog)

    # def test_what_does_the_cat_like_query(self):
    #     """Test 'What does the-cat like?' query pattern parsing"""
    #     ace_query = "What does the-cat like?"
    #     expected_prolog = "likes(the_cat, X)"
    #     result = self.parser.ace_to_prolog_query(ace_query)
    #     self.assertEqual(result, expected_prolog)

    def test_query_type_detection_is_john_happy(self):
        """Test query type detection for 'Is John happy?'"""
        ace_query = "Is John happy?"
        expected_type = QueryType.IS_X_Y
        result = self.parser.parse_query_type(ace_query)
        self.assertEqual(result, expected_type)

    def test_query_type_detection_who_is_happy(self):
        """Test query type detection for 'Who is happy?'"""
        ace_query = "Who is happy?"
        expected_type = QueryType.WHO_IS_X
        result = self.parser.parse_query_type(ace_query)
        self.assertEqual(result, expected_type)

    def test_query_type_detection_what_does_john_like(self):
        """Test query type detection for 'What does John like?'"""
        ace_query = "What does John like?"
        expected_type = QueryType.WHAT_DOES_X_LIKE
        result = self.parser.parse_query_type(ace_query)
        self.assertEqual(result, expected_type)

    def test_unsupported_query_where_is_john(self):
        """Test unsupported query: Where is John?"""
        ace_query = "Where is John?"
        query_type = self.parser.parse_query_type(ace_query)
        self.assertIsNone(query_type)
        prolog_query = self.parser.ace_to_prolog_query(ace_query)
        self.assertIsNone(prolog_query)

    def test_unsupported_query_when_did_mary_arrive(self):
        """Test unsupported query: When did Mary arrive?"""
        ace_query = "When did Mary arrive?"
        query_type = self.parser.parse_query_type(ace_query)
        self.assertIsNone(query_type)
        prolog_query = self.parser.ace_to_prolog_query(ace_query)
        self.assertIsNone(prolog_query)

    def test_unsupported_query_why_is_bob_happy(self):
        """Test unsupported query: Why is Bob happy?"""
        ace_query = "Why is Bob happy?"
        query_type = self.parser.parse_query_type(ace_query)
        self.assertIsNone(query_type)
        prolog_query = self.parser.ace_to_prolog_query(ace_query)
        self.assertIsNone(prolog_query)

    def test_unsupported_query_how_does_alice_work(self):
        """Test unsupported query: How does Alice work?"""
        ace_query = "How does Alice work?"
        query_type = self.parser.parse_query_type(ace_query)
        self.assertIsNone(query_type)
        prolog_query = self.parser.ace_to_prolog_query(ace_query)
        self.assertIsNone(prolog_query)

    def test_unsupported_query_can_john_swim(self):
        """Test unsupported query: Can John swim?"""
        ace_query = "Can John swim?"
        query_type = self.parser.parse_query_type(ace_query)
        self.assertIsNone(query_type)
        prolog_query = self.parser.ace_to_prolog_query(ace_query)
        self.assertIsNone(prolog_query)

    def test_unsupported_query_does_mary_like_chocolate(self):
        """Test unsupported query: Does Mary like chocolate?"""
        ace_query = "Does Mary like chocolate?"
        query_type = self.parser.parse_query_type(ace_query)
        self.assertIsNone(query_type)
        prolog_query = self.parser.ace_to_prolog_query(ace_query)
        self.assertIsNone(prolog_query)

    def test_unsupported_query_random_question(self):
        """Test unsupported query: Random question without proper structure?"""
        ace_query = "Random question without proper structure?"
        query_type = self.parser.parse_query_type(ace_query)
        self.assertIsNone(query_type)
        prolog_query = self.parser.ace_to_prolog_query(ace_query)
        self.assertIsNone(prolog_query)

    def test_case_insensitive_is_john_happy(self):
        """Test case handling: is john happy?"""
        ace_query = "is john happy?"
        expected_prolog = "happy(john)"
        result = self.parser.ace_to_prolog_query(ace_query)
        self.assertEqual(result, expected_prolog)

    def test_case_insensitive_who_is_happy(self):
        """Test case handling: who is happy?"""
        ace_query = "who is happy?"
        expected_prolog = "happy(X)"
        result = self.parser.ace_to_prolog_query(ace_query)
        self.assertEqual(result, expected_prolog)

    def test_case_insensitive_what_does_john_like(self):
        """Test case handling: what does john like?"""
        ace_query = "what does john like?"
        expected_prolog = "likes(john, X)"
        result = self.parser.ace_to_prolog_query(ace_query)
        self.assertEqual(result, expected_prolog)

    # def test_entity_normalization_john_smith_happy(self):
    #     """Test entity normalization: Is John-Smith happy?"""
    #     ace_query = "Is John-Smith happy?"
    #     expected_prolog = "happy(john_smith)"
    #     result = self.parser.ace_to_prolog_query(ace_query)
    #     self.assertEqual(result, expected_prolog)

    def test_entity_normalization_who_is_ice_cream_lover(self):
        """Test entity normalization: Who is ice-cream-lover?"""
        ace_query = "Who is ice-cream-lover?"
        expected_prolog = "ice_cream_lover(X)"
        result = self.parser.ace_to_prolog_query(ace_query)
        self.assertEqual(result, expected_prolog)

    # def test_entity_normalization_mary_jane_likes(self):
    #     """Test entity normalization: What does Mary Jane like?"""
    #     ace_query = "What does Mary Jane like?"
    #     expected_prolog = "likes(mary_jane, X)"
    #     result = self.parser.ace_to_prolog_query(ace_query)
    #     self.assertEqual(result, expected_prolog)

    # def test_entity_normalization_computer_1_working(self):
    #     """Test entity normalization: Is Computer-1 working?"""
    #     ace_query = "Is Computer-1 working?"
    #     expected_prolog = "working(computer_1)"
    #     result = self.parser.ace_to_prolog_query(ace_query)
    #     self.assertEqual(result, expected_prolog)

    def test_whitespace_handling_is_john_happy(self):
        """Test whitespace handling: '  Is John happy?  '"""
        ace_query = "  Is John happy?  "
        expected_prolog = "happy(john)"
        result = self.parser.ace_to_prolog_query(ace_query)
        self.assertEqual(result, expected_prolog)

    def test_whitespace_handling_who_is_happy(self):
        """Test whitespace handling: '\\tWho is happy?\\t'"""
        ace_query = "\tWho is happy?\t"
        expected_prolog = "happy(X)"
        result = self.parser.ace_to_prolog_query(ace_query)
        self.assertEqual(result, expected_prolog)

    # def test_whitespace_handling_what_does_john_like(self):
    #     """Test whitespace handling: 'What  does  John  like?'"""
    #     ace_query = "What  does  John  like?"
    #     expected_prolog = "likes(john, X)"
    #     result = self.parser.ace_to_prolog_query(ace_query)
    #     self.assertEqual(result, expected_prolog)

    def test_without_question_mark_is_john_happy(self):
        """Test query without question mark: 'Is John happy'"""
        ace_query = "Is John happy"
        expected_prolog = "happy(john)"
        result = self.parser.ace_to_prolog_query(ace_query)
        self.assertEqual(result, expected_prolog)

    def test_without_question_mark_who_is_happy(self):
        """Test query without question mark: 'Who is happy'"""
        ace_query = "Who is happy"
        expected_prolog = "happy(X)"
        result = self.parser.ace_to_prolog_query(ace_query)
        self.assertEqual(result, expected_prolog)

    def test_without_question_mark_what_does_john_like(self):
        """Test query without question mark: 'What does John like'"""
        ace_query = "What does John like"
        expected_prolog = "likes(john, X)"
        result = self.parser.ace_to_prolog_query(ace_query)
        self.assertEqual(result, expected_prolog)

    def test_malformed_query_is_missing_content(self):
        """Test malformed query: 'Is?'"""
        ace_query = "Is?"
        result = self.parser.ace_to_prolog_query(ace_query)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()