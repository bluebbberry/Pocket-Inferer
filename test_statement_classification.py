#!/usr/bin/env python3
"""
Tests for ACE statement classification functionality
"""

import unittest

from src.ace_prolog_parser import ACEToPrologParser


class TestStatementClassification(unittest.TestCase):
    """Test ACE statement type classification"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.parser = ACEToPrologParser()

    def test_fact_classification_john_is_person(self):
        """Test fact classification for 'John is a person'"""
        statement = "John is a person."
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'fact')
        self.assertEqual(result.content, statement)

    def test_fact_classification_mary_is_happy(self):
        """Test fact classification for 'Mary is happy'"""
        statement = "Mary is happy."
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'fact')
        self.assertEqual(result.content, statement)

    def test_fact_classification_bob_likes_chocolate(self):
        """Test fact classification for 'Bob likes chocolate'"""
        statement = "Bob likes chocolate."
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'fact')
        self.assertEqual(result.content, statement)

    def test_fact_classification_alice_has_age(self):
        """Test fact classification for 'Alice has age 25'"""
        statement = "Alice has age 25."
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'fact')
        self.assertEqual(result.content, statement)

    def test_fact_classification_cat_is_sleeping(self):
        """Test fact classification for 'The-cat is sleeping'"""
        statement = "The-cat is sleeping."
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'fact')
        self.assertEqual(result.content, statement)

    def test_fact_classification_computer_runs_software(self):
        """Test fact classification for 'Computer-1 runs software'"""
        statement = "Computer-1 runs software."
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'fact')
        self.assertEqual(result.content, statement)

    def test_rule_classification_x_is_happy_if_likes_chocolate(self):
        """Test rule classification for 'X is happy if X likes chocolate'"""
        statement = "X is happy if X likes chocolate."
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'rule')
        self.assertEqual(result.content, statement)

    def test_rule_classification_if_student_then_young(self):
        """Test rule classification for 'If X is a student then X is young'"""
        statement = "If X is a student then X is young."
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'rule')
        self.assertEqual(result.content, statement)

    def test_rule_classification_y_is_tired_if_works_hard(self):
        """Test rule classification for 'Y is tired if Y works hard'"""
        statement = "Y is tired if Y works hard."
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'rule')
        self.assertEqual(result.content, statement)

    def test_rule_classification_if_has_age_then_person(self):
        """Test rule classification for 'If A has age B then A is person'"""
        statement = "If A has age B then A is person."
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'rule')
        self.assertEqual(result.content, statement)

    def test_rule_classification_someone_successful_if_works_hard(self):
        """Test rule classification for 'Someone is successful if someone works hard'"""
        statement = "Someone is successful if someone works hard."
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'rule')
        self.assertEqual(result.content, statement)

    def test_query_classification_is_john_happy(self):
        """Test query classification for 'Is John happy?'"""
        statement = "Is John happy?"
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'query')
        self.assertEqual(result.content, statement)

    def test_query_classification_who_is_tall(self):
        """Test query classification for 'Who is tall?'"""
        statement = "Who is tall?"
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'query')
        self.assertEqual(result.content, statement)

    def test_query_classification_what_does_mary_like(self):
        """Test query classification for 'What does Mary like?'"""
        statement = "What does Mary like?"
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'query')
        self.assertEqual(result.content, statement)

    def test_query_classification_are_students_young(self):
        """Test query classification for 'Are students young?'"""
        statement = "Are students young?"
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'query')
        self.assertEqual(result.content, statement)

    def test_query_classification_does_bob_like_chocolate(self):
        """Test query classification for 'Does Bob like chocolate?'"""
        statement = "Does Bob like chocolate?"
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'query')
        self.assertEqual(result.content, statement)

    def test_query_classification_where_is_alice(self):
        """Test query classification for 'Where is Alice?'"""
        statement = "Where is Alice?"
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'query')
        self.assertEqual(result.content, statement)

    def test_query_classification_when_did_john_arrive(self):
        """Test query classification for 'When did John arrive?'"""
        statement = "When did John arrive?"
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'query')
        self.assertEqual(result.content, statement)

    def test_query_classification_why_is_mary_sad(self):
        """Test query classification for 'Why is Mary sad?'"""
        statement = "Why is Mary sad?"
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'query')
        self.assertEqual(result.content, statement)

    def test_query_classification_how_does_system_work(self):
        """Test query classification for 'How does the system work?'"""
        statement = "How does the system work?"
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'query')
        self.assertEqual(result.content, statement)

    def test_auto_period_addition_john_is_person(self):
        """Test automatic period addition for 'John is a person'"""
        input_statement = "John is a person"
        expected_text = "John is a person."
        result = self.parser.parse_statement(input_statement)
        self.assertEqual(result.statement_type, 'fact')
        self.assertEqual(result.content, expected_text)

    def test_auto_period_addition_mary_is_happy(self):
        """Test automatic period addition for 'Mary is happy'"""
        input_statement = "Mary is happy"
        expected_text = "Mary is happy."
        result = self.parser.parse_statement(input_statement)
        self.assertEqual(result.statement_type, 'fact')
        self.assertEqual(result.content, expected_text)

    def test_auto_period_addition_bob_likes_chocolate(self):
        """Test automatic period addition for 'Bob likes chocolate'"""
        input_statement = "Bob likes chocolate"
        expected_text = "Bob likes chocolate."
        result = self.parser.parse_statement(input_statement)
        self.assertEqual(result.statement_type, 'fact')
        self.assertEqual(result.content, expected_text)

    def test_case_insensitive_rule_lowercase(self):
        """Test case insensitive rule classification - lowercase"""
        statement = "x is happy if x likes chocolate."
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'rule')

    def test_case_insensitive_rule_uppercase_if_then(self):
        """Test case insensitive rule classification - uppercase IF THEN"""
        statement = "IF X is student THEN X is young."
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'rule')

    def test_case_insensitive_query_lowercase_is(self):
        """Test case insensitive query classification - lowercase 'is john happy?'"""
        statement = "is john happy?"
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'query')

    def test_case_insensitive_query_uppercase_who(self):
        """Test case insensitive query classification - uppercase 'WHO is tall?'"""
        statement = "WHO is tall?"
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'query')

    def test_case_insensitive_query_mixed_case_what(self):
        """Test case insensitive query classification - mixed case 'what DOES mary like?'"""
        statement = "what DOES mary like?"
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'query')

    def test_ambiguous_statement_complex_sentence(self):
        """Test ambiguous statement defaults to fact - complex sentence"""
        statement = "This is a complex sentence"
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'fact')
        self.assertEqual(result.content, statement + '.')

    def test_ambiguous_statement_random_text(self):
        """Test ambiguous statement defaults to fact - random text"""
        statement = "Random text without clear structure"
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'fact')
        self.assertEqual(result.content, statement + '.')

    def test_ambiguous_statement_multiple_words(self):
        """Test ambiguous statement defaults to fact - multiple words"""
        statement = "Multiple words in a sequence"
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'fact')
        self.assertEqual(result.content, statement + '.')

    def test_ambiguous_statement_numbers_and_text(self):
        """Test ambiguous statement defaults to fact - numbers and text"""
        statement = "123 numbers and text"
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'fact')
        self.assertEqual(result.content, statement + '.')

    def test_empty_statement(self):
        """Test handling of empty statement"""
        input_statement = ""
        expected_text = "."
        result = self.parser.parse_statement(input_statement)
        self.assertEqual(result.statement_type, 'fact')
        self.assertEqual(result.content, expected_text)

    def test_whitespace_only_statement_spaces(self):
        """Test handling of whitespace-only statement with spaces"""
        input_statement = "   "
        expected_text = "."
        result = self.parser.parse_statement(input_statement)
        self.assertEqual(result.statement_type, 'fact')
        self.assertEqual(result.content, expected_text)

    def test_whitespace_only_statement_tab(self):
        """Test handling of whitespace-only statement with tab"""
        input_statement = "\t"
        expected_text = "."
        result = self.parser.parse_statement(input_statement)
        self.assertEqual(result.statement_type, 'fact')
        self.assertEqual(result.content, expected_text)

    def test_whitespace_only_statement_newline(self):
        """Test handling of whitespace-only statement with newline"""
        input_statement = "\n"
        expected_text = "."
        result = self.parser.parse_statement(input_statement)
        self.assertEqual(result.statement_type, 'fact')
        self.assertEqual(result.content, expected_text)

    def test_statement_with_period_mr_john(self):
        """Test statement with period in middle - Mr. John"""
        statement = "Mr. John is a person."
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'fact')
        self.assertEqual(result.content, statement)

    def test_statement_with_period_dr_mary(self):
        """Test statement with period in middle - Dr. Mary"""
        statement = "Dr. Mary is happy."
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'fact')
        self.assertEqual(result.content, statement)

    def test_statement_with_period_version_number(self):
        """Test statement with period in middle - Version 1.0"""
        statement = "Version 1.0 is software."
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'fact')
        self.assertEqual(result.content, statement)

    def test_multiple_sentence_statements_facts(self):
        """Test multiple sentence statement treated as one fact"""
        statement = "John is happy. Mary is sad."
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'fact')

    def test_multiple_sentence_statements_queries(self):
        """Test multiple sentence statement treated as one query"""
        statement = "Is John happy? Is Mary sad?"
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'query')

    def test_special_characters_apostrophe(self):
        """Test statement with apostrophe - John's dog"""
        statement = "John's dog is happy."
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'fact')

    def test_special_characters_hyphen(self):
        """Test statement with hyphen - Mary-Jane"""
        statement = "Mary-Jane is a person."
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'fact')

    def test_special_characters_at_symbol(self):
        """Test statement with @ symbol - Computer@Home"""
        statement = "Computer@Home is running."
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'fact')

    def test_special_characters_underscore_version(self):
        """Test statement with underscore - Version_2.1"""
        statement = "Version_2.1 is software."
        result = self.parser.parse_statement(statement)
        self.assertEqual(result.statement_type, 'fact')

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
            self.assertEqual(statements[i].statement_type, expected_type)

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
            self.assertEqual(statements[i].content, expected_text)

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
        self.assertEqual(statements[0].content, "John is a person.")
        self.assertEqual(statements[1].content, "Mary is happy.")

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
        self.assertEqual(statements[0].content, "John is a person.")
        self.assertEqual(statements[1].content, "Mary is happy.")


if __name__ == '__main__':
    unittest.main()
