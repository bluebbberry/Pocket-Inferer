#!/usr/bin/env python3
"""
Integration tests for ACE to Prolog Parser
Tests end-to-end functionality combining multiple components
"""

import unittest

from src.ace_prolog_parser import ACEToPrologParser
from src.QueryType import QueryType


class TestACEToPrologIntegration(unittest.TestCase):
    """Integration tests for the complete ACE to Prolog conversion pipeline"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.parser = ACEToPrologParser()

    # def test_complete_knowledge_base_scenario(self):
    #     """Test a complete scenario with facts, rules, and queries"""
    #     knowledge_base_text = """
    #     # Facts about people
    #     John is a person.
    #     Mary is a person.
    #     Bob is a student.
    #     Alice is a teacher.
    #
    #     # Facts about preferences
    #     John likes chocolate.
    #     Mary likes music.
    #     Bob likes books.
    #     Alice likes coffee.
    #
    #     # Facts about properties
    #     John is happy.
    #     Bob is smart.
    #
    #     # Rules
    #     X is content if X likes music.
    #     X is studious if X likes books.
    #     Y is caffeinated if Y likes coffee.
    #     """
    #
    #     # Parse all statements
    #     statements = self.parser.parse_text(knowledge_base_text)
    #
    #     # Should have 10 statements (excluding comments)
    #     self.assertEqual(len(statements), 10)
    #
    #     # Check statement types
    #     expected_types = [
    #         'fact', 'fact', 'fact', 'fact',  # people facts
    #         'fact', 'fact', 'fact', 'fact',  # preference facts
    #         'fact', 'fact',  # property facts
    #     ]
    #     # Note: Rules are not included in expected_types as they should be 3 more
    #     for i, expected_type in enumerate(expected_types):
    #         if i < len(statements):
    #             self.assertEqual(statements[i].content, expected_type)

    # def test_fact_pipeline_john_person(self):
    #     """Test complete pipeline for fact: John is a person"""
    #     ace_text = "John is a person."
    #     expected_prolog = "person(john)"
    #
    #     statement = self.parser.parse_statement(ace_text)
    #     self.assertEqual(statement.content, 'fact')
    #
    #     prolog_result = self.parser.ace_to_prolog_fact(statement.content)
    #     self.assertEqual(prolog_result, expected_prolog)

    # def test_fact_pipeline_mary_happy(self):
    #     """Test complete pipeline for fact: Mary is happy"""
    #     ace_text = "Mary is happy."
    #     expected_prolog = "happy(mary)"
    #
    #     statement = self.parser.parse_statement(ace_text)
    #     self.assertEqual(statement.content, 'fact')
    #
    #     prolog_result = self.parser.ace_to_prolog_fact(statement.content)
    #     self.assertEqual(prolog_result, expected_prolog)

    def test_fact_pipeline_bob_likes_chocolate(self):
        """Test complete pipeline for fact: Bob likes chocolate"""
        ace_text = "Bob likes chocolate."
        expected_prolog = "likes(bob, chocolate)"

        statement = self.parser.parse_statement(ace_text)
        self.assertEqual(statement.statement_type, 'fact')

        prolog_result = self.parser.ace_to_prolog_fact(statement.content)
        self.assertEqual(prolog_result, expected_prolog)

    def test_fact_pipeline_alice_has_age_25(self):
        """Test complete pipeline for fact: Alice has age 25"""
        ace_text = "Alice has age 25."
        expected_prolog = "has_property(alice, age, 25)"

        statement = self.parser.parse_statement(ace_text)
        self.assertEqual(statement.statement_type, 'fact')

        prolog_result = self.parser.ace_to_prolog_fact(statement.content)
        self.assertEqual(prolog_result, expected_prolog)

    def test_rule_pipeline_x_happy_likes_chocolate(self):
        """Test complete pipeline for rule: X is happy if X likes chocolate"""
        ace_text = "X is happy if X likes chocolate."
        expected_prolog = "happy(X) :- likes(X, chocolate)"

        statement = self.parser.parse_statement(ace_text)
        self.assertEqual(statement.statement_type, 'rule')

        prolog_result = self.parser.ace_to_prolog_rule(statement.content)
        self.assertEqual(prolog_result, expected_prolog)

    def test_rule_pipeline_y_smart_is_student(self):
        """Test complete pipeline for rule: Y is smart if Y is student"""
        ace_text = "Y is smart if Y is student."
        expected_prolog = "smart(Y) :- student(Y)"

        statement = self.parser.parse_statement(ace_text)
        self.assertEqual(statement.statement_type, 'rule')

        prolog_result = self.parser.ace_to_prolog_rule(statement.content)
        self.assertEqual(prolog_result, expected_prolog)

    def test_rule_pipeline_someone_tired_busy(self):
        """Test complete pipeline for rule: Someone is tired if Someone is busy"""
        ace_text = "Someone is tired if Someone is busy."
        expected_prolog = "tired(SOMEONE) :- busy(SOMEONE)"

        statement = self.parser.parse_statement(ace_text)
        self.assertEqual(statement.statement_type, 'rule')

        prolog_result = self.parser.ace_to_prolog_rule(statement.content)
        self.assertEqual(prolog_result, expected_prolog)

    def test_query_pipeline_is_john_happy(self):
        """Test complete pipeline for query: Is John happy?"""
        ace_text = "Is John happy?"
        expected_query_type = QueryType.IS_X_Y
        expected_prolog = "happy(john)"

        statement = self.parser.parse_statement(ace_text)
        self.assertEqual(statement.statement_type, 'query')

        query_type = self.parser.parse_query_type(statement.content)
        self.assertEqual(query_type, expected_query_type)

        prolog_result = self.parser.ace_to_prolog_query(statement.content)
        self.assertEqual(prolog_result, expected_prolog)

    def test_query_pipeline_who_is_smart(self):
        """Test complete pipeline for query: Who is smart?"""
        ace_text = "Who is smart?"
        expected_query_type = QueryType.WHO_IS_X
        expected_prolog = "smart(X)"

        statement = self.parser.parse_statement(ace_text)
        self.assertEqual(statement.statement_type, 'query')

        query_type = self.parser.parse_query_type(statement.content)
        self.assertEqual(query_type, expected_query_type)

        prolog_result = self.parser.ace_to_prolog_query(statement.content)
        self.assertEqual(prolog_result, expected_prolog)

    def test_query_pipeline_what_does_mary_like(self):
        """Test complete pipeline for query: What does Mary like?"""
        ace_text = "What does Mary like?"
        expected_query_type = QueryType.WHAT_DOES_X_LIKE
        expected_prolog = "likes(mary, X)"

        statement = self.parser.parse_statement(ace_text)
        self.assertEqual(statement.statement_type, 'query')

        query_type = self.parser.parse_query_type(statement.content)
        self.assertEqual(query_type, expected_query_type)

        prolog_result = self.parser.ace_to_prolog_query(statement.content)
        self.assertEqual(prolog_result, expected_prolog)

    def test_mixed_statement_processing(self):
        """Test processing mixed types of statements"""
        mixed_text = """
        John is a person.
        X is happy if X likes chocolate.
        Is Mary tall?
        Bob likes music.
        Who is smart?
        Y is tired if Y works hard.
        """

        statements = self.parser.parse_text(mixed_text)

        # Check we have the right number and types
        self.assertEqual(len(statements), 6)
        expected_types = ['fact', 'rule', 'query', 'fact', 'query', 'rule']

        for i, expected_type in enumerate(expected_types):
            self.assertEqual(statements[i].statement_type, expected_type)

    def test_entity_consistency_john_smith_person(self):
        """Test entity normalization consistency: John-Smith is a person"""
        ace_text = "John-Smith is a person."
        expected_prolog = "person(john_smith)"

        statement = self.parser.parse_statement(ace_text)
        self.assertEqual(statement.statement_type, 'fact')

        prolog_result = self.parser.ace_to_prolog_fact(statement.content)
        self.assertEqual(prolog_result, expected_prolog)

    def test_entity_consistency_john_smith_happy(self):
        """Test entity normalization consistency: John-Smith is happy"""
        ace_text = "John-Smith is happy."
        expected_prolog = "happy(john_smith)"

        statement = self.parser.parse_statement(ace_text)
        self.assertEqual(statement.statement_type, 'fact')

        prolog_result = self.parser.ace_to_prolog_fact(statement.content)
        self.assertEqual(prolog_result, expected_prolog)

    # def test_entity_consistency_is_john_smith_tall(self):
    #     """Test entity normalization consistency: Is John-Smith tall?"""
    #     ace_text = "Is John-Smith tall?"
    #     expected_prolog = "tall(john_smith)"
    #
    #     statement = self.parser.parse_statement(ace_text)
    #     self.assertEqual(statement.statement_type, 'query')
    #
    #     prolog_result = self.parser.ace_to_prolog_query(statement.content)
    #     self.assertEqual(prolog_result, expected_prolog)

    # def test_entity_consistency_what_does_john_smith_like(self):
    #     """Test entity normalization consistency: What does John-Smith like?"""
    #     ace_text = "What does John-Smith like?"
    #     expected_prolog = "likes(john_smith, X)"
    #
    #     statement = self.parser.parse_statement(ace_text)
    #     self.assertEqual(statement.statement_type, 'query')
    #
    #     prolog_result = self.parser.ace_to_prolog_query(statement.content)
    #     self.assertEqual(prolog_result, expected_prolog)

    def test_complex_scenario_with_rules_and_queries(self):
        """Test a complex scenario that would work in a Prolog system"""
        scenario_text = """
        # People
        John is a person.
        Mary is a person.

        # Preferences
        John likes chocolate.
        Mary likes music.

        # Rules
        X is happy if X likes chocolate.
        X is creative if X likes music.
        """

        statements = self.parser.parse_text(scenario_text)

        # Convert facts
        facts = [s for s in statements if s.statement_type == 'fact']
        prolog_facts = []
        for fact in facts:
            prolog_fact = self.parser.ace_to_prolog_fact(fact.content)
            if prolog_fact:
                prolog_facts.append(prolog_fact)

        # Convert rules
        rules = [s for s in statements if s.statement_type == 'rule']
        prolog_rules = []
        for rule in rules:
            prolog_rule = self.parser.ace_to_prolog_rule(rule.content)
            if prolog_rule:
                prolog_rules.append(prolog_rule)

        # Expected Prolog facts
        expected_facts = [
            "person(john)",
            "person(mary)",
            "likes(john, chocolate)",
            "likes(mary, music)"
        ]

        # Expected Prolog rules
        expected_rules = [
            "happy(X) :- likes(X, chocolate)",
            "creative(X) :- likes(X, music)"
        ]

        self.assertEqual(sorted(prolog_facts), sorted(expected_facts))
        self.assertEqual(sorted(prolog_rules), sorted(expected_rules))

    def test_error_handling_in_pipeline(self):
        """Test error handling throughout the pipeline"""
        problematic_text = """
        # Valid statements
        John is a person.

        # Invalid/unsupported patterns
        This is a complex sentence that doesn't match any pattern.
        X is Y if A and B and C.

        # Empty lines and comments

        # Another comment

        # Valid statement at the end
        Mary is happy.
        """

        statements = self.parser.parse_text(problematic_text)

        # Should parse all non-comment lines as statements
        # Even unsupported patterns should be classified (likely as facts)
        self.assertGreaterEqual(len(statements), 3)

        # Check that valid statements still work
        valid_statements = [s for s in statements if s.content in ["John is a person.", "Mary is happy."]]
        self.assertEqual(len(valid_statements), 2)

        for statement in valid_statements:
            prolog_fact = self.parser.ace_to_prolog_fact(statement.content)
            self.assertIsNotNone(prolog_fact)

    # def test_whitespace_and_formatting_robustness(self):
    #     """Test robustness against various whitespace and formatting issues"""
    #     messy_text = """
    #
    #        John    is   a    person.
    #
    #
    #     	Mary	is	happy.
    #
    #     X is   tired   if   X    works   hard.
    #
    #        Is    Bob    tall?
    #
    #     """
    #
    #     statements = self.parser.parse_text(messy_text)
    #
    #     # Should handle whitespace gracefully
    #     self.assertEqual(len(statements), 4)
    #
    #     # Check that conversions still work
    #     fact_statement = statements[0]  # John is a person
    #     self.assertEqual(fact_statement.statement_type, 'fact')
    #     prolog_fact = self.parser.ace_to_prolog_fact(fact_statement.content)
    #     self.assertEqual(prolog_fact, "person(john)")

    def test_large_knowledge_base_processing(self):
        """Test processing a larger knowledge base efficiently"""
        # Generate a larger knowledge base
        large_kb_lines = []

        # Add many facts
        for i in range(50):
            large_kb_lines.append(f"Person{i} is a person.")
            large_kb_lines.append(f"Person{i} likes item{i}.")

        # Add some rules
        large_kb_lines.append("X is satisfied if X likes item0.")
        large_kb_lines.append("X is content if X likes item1.")

        # Add some queries
        large_kb_lines.append("Who is satisfied?")
        large_kb_lines.append("Is Person0 content?")

        large_kb_text = "\n".join(large_kb_lines)
        statements = self.parser.parse_text(large_kb_text)

        # Should parse all statements
        self.assertEqual(len(statements), 104)  # 50*2 facts + 2 rules + 2 queries

        # Check distribution of types
        facts = [s for s in statements if s.statement_type == 'fact']
        rules = [s for s in statements if s.statement_type == 'rule']
        queries = [s for s in statements if s.statement_type == 'query']

        self.assertEqual(len(facts), 100)
        self.assertEqual(len(rules), 2)
        self.assertEqual(len(queries), 2)


if __name__ == '__main__':
    unittest.main()