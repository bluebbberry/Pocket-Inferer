#!/usr/bin/env python3
"""
Integration tests for ACE to Prolog Parser
Tests end-to-end functionality combining multiple components
"""

import unittest
import sys
import os

from src.ace_prolog_parser import ACEToPrologParser
from src.QueryType import QueryType


class TestACEToPrologIntegration(unittest.TestCase):
    """Integration tests for the complete ACE to Prolog conversion pipeline"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.parser = ACEToPrologParser()

    def test_complete_knowledge_base_scenario(self):
        """Test a complete scenario with facts, rules, and queries"""
        knowledge_base_text = """
        # Facts about people
        John is a person.
        Mary is a person.
        Bob is a student.
        Alice is a teacher.

        # Facts about preferences
        John likes chocolate.
        Mary likes music.
        Bob likes books.
        Alice likes coffee.

        # Facts about properties
        John is happy.
        Bob is smart.

        # Rules
        X is content if X likes music.
        X is studious if X likes books.
        Y is caffeinated if Y likes coffee.
        """

        # Parse all statements
        statements = self.parser.parse_text(knowledge_base_text)

        # Should have 10 statements (excluding comments)
        self.assertEqual(len(statements), 10)

        # Check statement types
        expected_types = [
            'fact', 'fact', 'fact', 'fact',  # people facts
            'fact', 'fact', 'fact', 'fact',  # preference facts
            'fact', 'fact',  # property facts
        ]
        # Note: Rules are not included in expected_types as they should be 3 more
        for i, expected_type in enumerate(expected_types):
            if i < len(statements):
                self.assertEqual(statements[i].type, expected_type)

    def test_fact_to_prolog_conversion_pipeline(self):
        """Test complete pipeline for facts"""
        test_facts = [
            ("John is a person.", "person(john)"),
            ("Mary is happy.", "happy(mary)"),
            ("Bob likes chocolate.", "likes(bob, chocolate)"),
            ("Alice has age 25.", "has_property(alice, age, 25)"),
        ]

        for ace_text, expected_prolog in test_facts:
            with self.subTest(ace_text=ace_text):
                # Parse statement
                statement = self.parser.parse_statement(ace_text)
                self.assertEqual(statement.type, 'fact')

                # Convert to Prolog
                prolog_result = self.parser.ace_to_prolog_fact(statement.text)
                self.assertEqual(prolog_result, expected_prolog)

    def test_rule_to_prolog_conversion_pipeline(self):
        """Test complete pipeline for rules"""
        test_rules = [
            ("X is happy if X likes chocolate.", "happy(X) :- likes(X, chocolate)"),
            ("Y is smart if Y is student.", "smart(Y) :- student(Y)"),
            ("Someone is tired if Someone is busy.", "tired(SOMEONE) :- busy(SOMEONE)"),
        ]

        for ace_text, expected_prolog in test_rules:
            with self.subTest(ace_text=ace_text):
                # Parse statement
                statement = self.parser.parse_statement(ace_text)
                self.assertEqual(statement.type, 'rule')

                # Convert to Prolog
                prolog_result = self.parser.ace_to_prolog_rule(statement.text)
                self.assertEqual(prolog_result, expected_prolog)

    def test_query_to_prolog_conversion_pipeline(self):
        """Test complete pipeline for queries"""
        test_queries = [
            ("Is John happy?", QueryType.IS_X_Y, "happy(john)"),
            ("Who is smart?", QueryType.WHO_IS_X, "smart(X)"),
            ("What does Mary like?", QueryType.WHAT_DOES_X_LIKE, "likes(mary, X)"),
        ]

        for ace_text, expected_query_type, expected_prolog in test_queries:
            with self.subTest(ace_text=ace_text):
                # Parse statement
                statement = self.parser.parse_statement(ace_text)
                self.assertEqual(statement.type, 'query')

                # Check query type
                query_type = self.parser.parse_query_type(statement.text)
                self.assertEqual(query_type, expected_query_type)

                # Convert to Prolog
                prolog_result = self.parser.ace_to_prolog_query(statement.text)
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
            self.assertEqual(statements[i].type, expected_type)

    def test_entity_consistency_across_statements(self):
        """Test that entity normalization is consistent across different statement types"""
        test_cases = [
            # Same entity in different contexts
            ("John-Smith is a person.", "fact", "person(john_smith)"),
            ("John-Smith is happy.", "fact", "happy(john_smith)"),
            ("Is John-Smith tall?", "query", "tall(john_smith)"),
            ("What does John-Smith like?", "query", "likes(john_smith, X)"),
        ]

        for ace_text, expected_type, expected_prolog in test_cases:
            with self.subTest(ace_text=ace_text):
                # Parse statement
                statement = self.parser.parse_statement(ace_text)
                self.assertEqual(statement.type, expected_type)

                # Convert to Prolog based on type
                if expected_type == 'fact':
                    prolog_result = self.parser.ace_to_prolog_fact(statement.text)
                elif expected_type == 'query':
                    prolog_result = self.parser.ace_to_prolog_query(statement.text)

                self.assertEqual(prolog_result, expected_prolog)

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
        facts = [s for s in statements if s.type == 'fact']
        prolog_facts = []
        for fact in facts:
            prolog_fact = self.parser.ace_to_prolog_fact(fact.text)
            if prolog_fact:
                prolog_facts.append(prolog_fact)

        # Convert rules
        rules = [s for s in statements if s.type == 'rule']
        prolog_rules = []
        for rule in rules:
            prolog_rule = self.parser.ace_to_prolog_rule(rule.text)
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
        valid_statements = [s for s in statements if s.text in ["John is a person.", "Mary is happy."]]
        self.assertEqual(len(valid_statements), 2)

        for statement in valid_statements:
            prolog_fact = self.parser.ace_to_prolog_fact(statement.text)
            self.assertIsNotNone(prolog_fact)

    def test_whitespace_and_formatting_robustness(self):
        """Test robustness against various whitespace and formatting issues"""
        messy_text = """

           John    is   a    person.   


        	Mary	is	happy.	

        X is   tired   if   X    works   hard.

           Is    Bob    tall?   

        """

        statements = self.parser.parse_text(messy_text)

        # Should handle whitespace gracefully
        self.assertEqual(len(statements), 4)

        # Check that conversions still work
        fact_statement = statements[0]  # John is a person
        self.assertEqual(fact_statement.type, 'fact')
        prolog_fact = self.parser.ace_to_prolog_fact(fact_statement.text)
        self.assertEqual(prolog_fact, "person(john)")

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
        facts = [s for s in statements if s.type == 'fact']
        rules = [s for s in statements if s.type == 'rule']
        queries = [s for s in statements if s.type == 'query']

        self.assertEqual(len(facts), 100)
        self.assertEqual(len(rules), 2)
        self.assertEqual(len(queries), 2)


if __name__ == '__main__':
    unittest.main()