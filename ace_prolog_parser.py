#!/usr/bin/env python3
"""
ACE to Prolog Parser - Separate parser class for converting ACE statements to Prolog format
"""

import re
from dataclasses import dataclass
from typing import Optional, List

from ACEStatement import ACEStatement
from QueryType import QueryType


class ACEToPrologParser:
    """Enhanced ACE to Prolog parser with better rule handling"""

    def __init__(self):
        self.entity_map = {}
        self.next_entity_id = 1

        self.fact_patterns = [
            r'^[A-Z][a-zA-Z0-9_-]+ (is|are|has|have) .+\.$',
            r'^[A-Z][a-zA-Z0-9_-]+ .+ [a-zA-Z0-9_-]+\.$'
        ]
        self.rule_patterns = [
            r'^.+ if .+\.$',
            r'^If .+ then .+\.$'
        ]
        self.query_patterns = [
            r'^.+\?$',
            r'^(Is|Are|Does|Do|Who|What|When|Where|Why|How) .+\?$'
        ]

    def normalize_entity(self, entity: str) -> str:
        """Normalize entity names for Prolog"""
        entity = entity.strip().lower()
        # Replace spaces and hyphens with underscores
        entity = re.sub(r'[\s\-]+', '_', entity)
        # Ensure it starts with lowercase letter
        if entity and entity[0].isupper():
            entity = entity[0].lower() + entity[1:]
        return entity

    def ace_to_prolog_fact(self, ace_fact: str) -> str | None:
        """Convert ACE fact to Prolog fact"""
        ace_fact = ace_fact.strip().rstrip('.')

        # Pattern: X is a person
        if re.match(r'^(.+) is a ([a-zA-Z][a-zA-Z0-9_]*)', ace_fact):
            match = re.match(r'^(.+) is a ([a-zA-Z][a-zA-Z0-9_]*)', ace_fact)
            entity = self.normalize_entity(match.group(1))
            category = self.normalize_entity(match.group(2))
            return f"{category}({entity})"

        # Pattern: X is Y (property)
        elif re.match(r'^(.+) is ([a-zA-Z][a-zA-Z0-9_]*)', ace_fact):
            match = re.match(r'^(.+) is ([a-zA-Z][a-zA-Z0-9_]*)', ace_fact)
            entity = self.normalize_entity(match.group(1))
            property_name = self.normalize_entity(match.group(2))
            return f"{property_name}({entity})"

        # Pattern: X likes Y
        elif re.match(r'^(.+) likes (.+)', ace_fact):
            match = re.match(r'^(.+) likes (.+)', ace_fact)
            entity1 = self.normalize_entity(match.group(1))
            entity2 = self.normalize_entity(match.group(2))
            return f"likes({entity1}, {entity2})"

        # Pattern: X has Y Z
        elif re.match(r'^(.+) has (.+) (.+)', ace_fact):
            match = re.match(r'^(.+) has (.+) (.+)', ace_fact)
            entity = self.normalize_entity(match.group(1))
            property_name = self.normalize_entity(match.group(2))
            value = self.normalize_entity(match.group(3))
            return f"has_property({entity}, {property_name}, {value})"

        return None

    def ace_to_prolog_rule(self, ace_rule: str) -> str | None:
        """Convert ACE rule to Prolog rule"""
        ace_rule = ace_rule.strip().rstrip('.')

        # Pattern: X is Y if Z
        if ' if ' in ace_rule.lower():
            parts = re.split(r'\s+if\s+', ace_rule, flags=re.IGNORECASE)
            if len(parts) == 2:
                conclusion = parts[0].strip()
                condition = parts[1].strip()

                # Parse conclusion
                if re.match(r'^(.+) is ([a-zA-Z][a-zA-Z0-9_]*)', conclusion):
                    match = re.match(r'^(.+) is ([a-zA-Z][a-zA-Z0-9_]*)', conclusion)
                    var_name = match.group(1).upper()  # Use uppercase for variables
                    property_name = self.normalize_entity(match.group(2))
                    conclusion_prolog = f"{property_name}({var_name})"
                else:
                    return None

                # Parse condition
                condition_prolog = self._parse_condition(condition, var_name)
                if condition_prolog:
                    return f"{conclusion_prolog} :- {condition_prolog}"

        return None

    def _parse_condition(self, condition: str, var_name: str) -> str | None:
        """Parse condition part of a rule"""
        # Pattern: X likes Y
        if re.match(r'^(.+) likes (.+)', condition):
            match = re.match(r'^(.+) likes (.+)', condition)
            subject = match.group(1).strip()
            object_name = self.normalize_entity(match.group(2))

            # Replace subject with variable if it matches
            if subject.upper() == var_name:
                return f"likes({var_name}, {object_name})"
            else:
                subject_norm = self.normalize_entity(subject)
                return f"likes({subject_norm}, {object_name})"

        # Pattern: X is Y
        elif re.match(r'^(.+) is (.+)', condition):
            match = re.match(r'^(.+) is (.+)', condition)
            subject = match.group(1).strip()
            property_name = self.normalize_entity(match.group(2))

            if subject.upper() == var_name:
                return f"{property_name}({var_name})"
            else:
                subject_norm = self.normalize_entity(subject)
                return f"{property_name}({subject_norm})"

        return None

    def parse_query_type(self, ace_query):
        # Is X Y? queries
        if ace_query.lower().startswith('is '):
            return QueryType.IS_X_Y

        # Who is X? queries
        elif ace_query.lower().startswith('who is '):
            return QueryType.WHO_IS_X

        # What does X like? queries
        elif re.match(r'^what does ([a-zA-Z][a-zA-Z0-9_]*) like', ace_query.lower()):
            return QueryType.WHAT_DOES_X_LIKE
        return None

    def parse_query(self, ace_query):

        ace_query = ace_query.strip().rstrip('?')

        prolog_query = None

        query_type = self.parse_query_type(ace_query)

        # Is X Y? queries
        if query_type is QueryType.IS_X_Y:
            query_content = ace_query[3:].strip()

            # Pattern: is X happy
            if re.match(r'^([a-zA-Z][a-zA-Z0-9_]*) ([a-zA-Z][a-zA-Z0-9_]*)', query_content):
                match = re.match(r'^([a-zA-Z][a-zA-Z0-9_]*) ([a-zA-Z][a-zA-Z0-9_]*)', query_content)
                entity = self.normalize_entity(match.group(1))
                property_name = self.normalize_entity(match.group(2))

                prolog_query = f"{property_name}({entity})"

        # Who is X? queries
        elif query_type is QueryType.WHO_IS_X:
            property_name = ace_query[7:].strip().lower()
            property_name = self.normalize_entity(property_name)

            prolog_query = f"{property_name}(X)"

        # What does X like? queries
        elif query_type is QueryType.WHAT_DOES_X_LIKE:
            match = re.match(r'^what does ([a-zA-Z][a-zA-Z0-9_]*) like', ace_query.lower())
            entity = self.normalize_entity(match.group(1))

            prolog_query = f"likes({entity}, X)"

        return prolog_query

    def parse_statement(self, text: str) -> ACEStatement:
        """Parse a single ACE statement"""
        text = text.strip()

        if any(re.match(pattern, text, re.IGNORECASE) for pattern in self.query_patterns):
            return ACEStatement(text, 'query')
        elif any(re.match(pattern, text, re.IGNORECASE) for pattern in self.rule_patterns):
            return ACEStatement(text, 'rule')
        elif any(re.match(pattern, text) for pattern in self.fact_patterns) or text.endswith('.'):
            return ACEStatement(text, 'fact')
        else:
            # Default to fact if uncertain
            return ACEStatement(text + '.' if not text.endswith('.') else text, 'fact')

    def parse_text(self, text: str) -> List[ACEStatement]:
        """Parse multiple ACE statements from text"""
        statements = []
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        for line in lines:
            if line and not line.startswith('#'):  # Skip comments
                statements.append(self.parse_statement(line))

        return statements



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