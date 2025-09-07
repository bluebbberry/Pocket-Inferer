#!/usr/bin/env python3
"""
ACE to Prolog Parser - Separate parser class for converting ACE statements to Prolog format
"""

import re
from typing import Optional


class ACEToPrologParser:
    """
    Converts Attempto Controlled English (ACE) statements to Prolog format.

    This parser handles facts, rules, and queries, converting them from natural
    language ACE syntax to formal Prolog predicates.
    """

    def __init__(self):
        """Initialize the parser with regex patterns for different ACE constructs."""
        # Fact patterns for basic statements
        self.fact_patterns = {
            'is_a': r'^([A-Za-z][a-zA-Z0-9_]*) is a ([a-zA-Z][a-zA-Z0-9_]*)$',
            'is': r'^([A-Za-z][a-zA-Z0-9_]*) is ([a-zA-Z][a-zA-Z0-9_]*)$',
            'likes': r'^([A-Za-z][a-zA-Z0-9_]*) likes ([a-zA-Z][a-zA-Z0-9_]*)$',
            'has_property': r'^([A-Za-z][a-zA-Z0-9_]*) has ([a-zA-Z][a-zA-Z0-9_-]*) ([a-zA-Z0-9_-]+)$'
        }

        # Expression patterns for variables and entities
        self.expression_patterns = {
            'var_is': r'^([A-Za-z]) is ([a-zA-Z][a-zA-Z0-9_]*)$',
            'var_likes': r'^([A-Za-z]) likes ([a-zA-Z][a-zA-Z0-9_]*)$',
            'entity_is': r'^([A-Za-z][a-zA-Z0-9_]*) is ([a-zA-Z][a-zA-Z0-9_]*)$',
            'entity_likes': r'^([A-Za-z][a-zA-Z0-9_]*) likes ([a-zA-Z][a-zA-Z0-9_]*)$'
        }

    def ace_to_prolog_fact(self, ace_fact: str) -> Optional[str]:
        """
        Convert an ACE fact to Prolog format.

        Args:
            ace_fact: The ACE fact string (e.g., "John is a person.")

        Returns:
            Prolog fact string or None if conversion fails

        Examples:
            "John is a person." -> "person(john)"
            "Mary likes chocolate." -> "likes(mary, chocolate)"
            "Bob has age 25." -> "has_property(bob, age, 25)"
        """
        ace_fact = ace_fact.strip().rstrip('.')

        # Handle "X is a Y" pattern
        match = re.match(self.fact_patterns['is_a'], ace_fact, re.IGNORECASE)
        if match:
            entity, category = match.groups()
            return f"{category.lower()}({entity.lower()})"

        # Handle "X is Y" pattern (property/adjective)
        match = re.match(self.fact_patterns['is'], ace_fact, re.IGNORECASE)
        if match:
            entity, property_name = match.groups()
            return f"{property_name.lower()}({entity.lower()})"

        # Handle "X likes Y" pattern
        match = re.match(self.fact_patterns['likes'], ace_fact, re.IGNORECASE)
        if match:
            entity, object_name = match.groups()
            return f"likes({entity.lower()}, {object_name.lower()})"

        # Handle "X has Y Z" pattern (properties with values)
        match = re.match(self.fact_patterns['has_property'], ace_fact, re.IGNORECASE)
        if match:
            entity, property_name, value = match.groups()
            # Clean property name (replace hyphens with underscores)
            clean_property = property_name.lower().replace('-', '_')
            return f"has_property({entity.lower()}, {clean_property}, {value.lower()})"

        return None

    def ace_to_prolog_rule(self, ace_rule: str) -> Optional[str]:
        """
        Convert an ACE rule to Prolog format.

        Args:
            ace_rule: The ACE rule string (e.g., "X is happy if X likes chocolate.")

        Returns:
            Prolog rule string or None if conversion fails

        Examples:
            "X is happy if X likes chocolate." -> "happy(X) :- likes(X, chocolate)"
        """
        ace_rule = ace_rule.strip().rstrip('.')

        # Handle "... if ..." pattern
        if ' if ' in ace_rule.lower():
            parts = ace_rule.split(' if ', 1)
            if len(parts) != 2:
                return None

            conclusion_part = parts[0].strip()
            condition_part = parts[1].strip()

            # Convert both parts to Prolog predicates
            conclusion_prolog = self._convert_ace_expression_to_prolog(conclusion_part)
            condition_prolog = self._convert_ace_expression_to_prolog(condition_part)

            if conclusion_prolog and condition_prolog:
                return f"{conclusion_prolog} :- {condition_prolog}"

        # Handle "If ... then ..." pattern
        elif ace_rule.lower().startswith('if ') and ' then ' in ace_rule.lower():
            parts = ace_rule.split(' then ', 1)
            if len(parts) != 2:
                return None

            condition_part = parts[0][3:].strip()  # Remove "if "
            conclusion_part = parts[1].strip()

            # Convert both parts to Prolog predicates
            conclusion_prolog = self._convert_ace_expression_to_prolog(conclusion_part)
            condition_prolog = self._convert_ace_expression_to_prolog(condition_part)

            if conclusion_prolog and condition_prolog:
                return f"{conclusion_prolog} :- {condition_prolog}"

        return None

    def _convert_ace_expression_to_prolog(self, expression: str) -> Optional[str]:
        """
        Convert an ACE expression (part of a rule) to Prolog predicate.

        Args:
            expression: The ACE expression string

        Returns:
            Prolog predicate string or None if conversion fails
        """
        expression = expression.strip()

        # Handle "X is Y" pattern with variables
        match = re.match(self.expression_patterns['var_is'], expression, re.IGNORECASE)
        if match:
            var, property_name = match.groups()
            return f"{property_name.lower()}({var.upper()})"

        # Handle "X likes Y" pattern with variables
        match = re.match(self.expression_patterns['var_likes'], expression, re.IGNORECASE)
        if match:
            var, object_name = match.groups()
            return f"likes({var.upper()}, {object_name.lower()})"

        # Handle "X is Y" pattern with specific entities
        match = re.match(self.expression_patterns['entity_is'], expression, re.IGNORECASE)
        if match:
            entity, property_name = match.groups()
            return f"{property_name.lower()}({entity.lower()})"

        # Handle "X likes Y" pattern with specific entities
        match = re.match(self.expression_patterns['entity_likes'], expression, re.IGNORECASE)
        if match:
            entity, object_name = match.groups()
            return f"likes({entity.lower()}, {object_name.lower()})"

        return None

    def ace_query_to_prolog(self, ace_query: str) -> Optional[str]:
        """
        Convert an ACE query to Prolog query format.

        Args:
            ace_query: The ACE query string (e.g., "Is John happy?")

        Returns:
            Prolog query string or None if conversion fails

        Examples:
            "Is John happy?" -> "happy(john)"
            "Who is happy?" -> "happy(X)"
            "What does John like?" -> "likes(john, X)"
        """
        ace_query = ace_query.strip().rstrip('?')

        # Handle "Is X Y?" queries
        if ace_query.lower().startswith('is '):
            query_content = ace_query[3:].strip()
            return self._convert_ace_expression_to_prolog(query_content)

        # Handle "Are X Y?" queries (plural form)
        elif ace_query.lower().startswith('are '):
            query_content = ace_query[4:].strip()
            # Convert "are" to "is" for processing
            if query_content.endswith('s'):
                query_content = query_content[:-1]  # Remove plural 's'
            return self._convert_ace_expression_to_prolog(query_content)

        # Handle "Who is Y?" queries
        elif ace_query.lower().startswith('who is '):
            property_name = ace_query[7:].strip().lower()
            return f"{property_name}(X)"

        # Handle "What does X like?" queries
        elif re.match(r'^what does ([a-zA-Z][a-zA-Z0-9_]*) like$', ace_query.lower()):
            match = re.match(r'^what does ([a-zA-Z][a-zA-Z0-9_]*) like$', ace_query.lower())
            entity = match.group(1)
            return f"likes({entity.lower()}, X)"

        # Handle "Does X like Y?" queries
        elif ace_query.lower().startswith('does '):
            # Convert "Does X like Y" to "X likes Y" and process
            query_without_does = ace_query[5:].strip()
            return self._convert_ace_expression_to_prolog(query_without_does)

        return None

    def get_supported_patterns(self) -> dict:
        """
        Get information about supported ACE patterns.

        Returns:
            Dictionary describing supported patterns and examples
        """
        return {
            'facts': {
                'is_a': {
                    'pattern': 'Entity is a Category.',
                    'example': 'John is a person.',
                    'prolog': 'person(john)'
                },
                'is': {
                    'pattern': 'Entity is Property.',
                    'example': 'John is happy.',
                    'prolog': 'happy(john)'
                },
                'likes': {
                    'pattern': 'Entity likes Object.',
                    'example': 'Mary likes chocolate.',
                    'prolog': 'likes(mary, chocolate)'
                },
                'has_property': {
                    'pattern': 'Entity has Property Value.',
                    'example': 'Bob has age 25.',
                    'prolog': 'has_property(bob, age, 25)'
                }
            },
            'rules': {
                'if_then': {
                    'pattern': 'Conclusion if Condition.',
                    'example': 'X is happy if X likes chocolate.',
                    'prolog': 'happy(X) :- likes(X, chocolate)'
                },
                'then_if': {
                    'pattern': 'If Condition then Conclusion.',
                    'example': 'If X likes chocolate then X is happy.',
                    'prolog': 'happy(X) :- likes(X, chocolate)'
                }
            },
            'queries': {
                'is_question': {
                    'pattern': 'Is Entity Property?',
                    'example': 'Is John happy?',
                    'prolog': 'happy(john)'
                },
                'who_question': {
                    'pattern': 'Who is Property?',
                    'example': 'Who is happy?',
                    'prolog': 'happy(X)'
                },
                'what_likes': {
                    'pattern': 'What does Entity like?',
                    'example': 'What does John like?',
                    'prolog': 'likes(john, X)'
                }
            }
        }


if __name__ == "__main__":
    # Quick demonstration
    parser = ACEToPrologParser()

    # Test facts
    facts = [
        "John is a person.",
        "Mary is happy.",
        "Bob likes chocolate.",
        "Alice has age 25."
    ]

    print("=== Testing Facts ===")
    for fact in facts:
        prolog = parser.ace_to_prolog_fact(fact)
        print(f"ACE: {fact}")
        print(f"Prolog: {prolog}")
        print()

    # Test rules
    rules = [
        "X is happy if X likes chocolate.",
        "If X has age Y then X is adult."
    ]

    print("=== Testing Rules ===")
    for rule in rules:
        prolog = parser.ace_to_prolog_rule(rule)
        print(f"ACE: {rule}")
        print(f"Prolog: {prolog}")
        print()

    # Test queries
    queries = [
        "Is John happy?",
        "Who is happy?",
        "What does Mary like?"
    ]

    print("=== Testing Queries ===")
    for query in queries:
        prolog = parser.ace_query_to_prolog(query)
        print(f"ACE: {query}")
        print(f"Prolog: {prolog}")
        print()