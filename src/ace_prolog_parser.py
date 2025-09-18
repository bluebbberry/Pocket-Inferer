#!/usr/bin/env python3
"""
ACE to Prolog Parser - Enhanced with administrative logic (drop-in replacement)
"""

import re
from typing import List

from src.ACEStatement import ACEStatement
from src.QueryType import QueryType


class ACEToPrologParser:
    """Enhanced ACE to Prolog parser with administrative logic support"""

    def __init__(self):
        self.entity_map = {}
        self.next_entity_id = 1

        self.predicates_to_clear = [
            "person(_)", "likes(_, _)", "happy(_)", "has_property(_, _, _)",
            "sad(_)", "tall(_)", "smart(_)", "young(_)", "old(_)", "residence(_, _)", "employment_status(_, _)",
            "marital_status(_, _), children_count(_, _), birth_date(_, _), income(_, _, _), eligible(_, _)"
        ]

        # Enhanced patterns for administrative logic
        self.fact_patterns = [
            # Original patterns
            r'^[A-Z][a-zA-Z0-9_-]+ (is|are|has|have) .+\.$',
            r'^[A-Z][a-zA-Z0-9_-]+ .+ [a-zA-Z0-9_-]+\.$',

            # Administrative patterns
            r'^[A-Z][a-zA-Z0-9_-]+ earns \d+(\.\d+)? euros per (month|year)\.$',
            r'^[A-Z][a-zA-Z0-9_-]+ was born on \d{4}-\d{2}-\d{2}\.$',
            r'^[A-Z][a-zA-Z0-9_-]+ lives in [A-Za-z0-9_-]+\.$',
            r'^[A-Z][a-zA-Z0-9_-]+ has \d+ (child|children)\.$',
            r'^[A-Z][a-zA-Z0-9_-]+ is (employed|unemployed|self-employed|retired)\.$',
            r'^[A-Z][a-zA-Z0-9_-]+ is (married|single|divorced|widowed)\.$',
            r'^[A-Z][a-zA-Z0-9_-]+ has (German|EU|non-EU) citizenship\.$'
        ]

        self.rule_patterns = [
            # Original patterns
            r'^.+ if .+\.$',
            r'^If .+ then .+\.$',

            # Administrative patterns
            r'^.+ is eligible for .+ if .+\.$',
            r'^.+ qualifies for .+ when .+\.$',
            r'^.+ receives .+ if .+ and .+\.$'
        ]

        self.query_patterns = [
            # Original patterns
            r'^.+\?$',
            r'^(Is|Are|Does|Do|Who|What|When|Where|Why|How) .+\?$',

            # Administrative patterns
            r'^Is .+ eligible for .+\?$',
            r'^What benefits does .+ qualify for\?$',
            r'^How much .+ does .+ receive\?$',
            r'^Which .+ are eligible for .+\?$'
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
        """Convert ACE fact to Prolog fact with administrative extensions"""
        ace_fact = ace_fact.strip().rstrip('.')

        # ========== ORIGINAL PATTERNS ==========

        # Pattern: X is a person
        if re.match(r'^(.+) is a ([a-zA-Z][a-zA-Z0-9_]*)', ace_fact):
            match = re.match(r'^(.+) is a ([a-zA-Z][a-zA-Z0-9_]*)', ace_fact)
            entity = self.normalize_entity(match.group(1))
            category = self.normalize_entity(match.group(2))
            return f"{category}({entity})"

        # Pattern: X is Y (property) - but check for administrative patterns first
        elif re.match(r'^(.+) is (employed|unemployed|self.employed|retired|married|single|divorced|widowed)',
                      ace_fact):
            match = re.match(r'^(.+) is (employed|unemployed|self.employed|retired|married|single|divorced|widowed)',
                             ace_fact)
            entity = self.normalize_entity(match.group(1))
            status = match.group(2).replace('-', '_')

            # Determine the type of status
            if status in ['employed', 'unemployed', 'self_employed', 'retired']:
                return f"employment_status({entity}, {status})"
            elif status in ['married', 'single', 'divorced', 'widowed']:
                return f"marital_status({entity}, {status})"

        # Pattern: X is Y (general property)
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

        # ========== ADMINISTRATIVE PATTERNS ==========

        # Pattern: X earns Y euros per month/year
        elif re.match(r'^(.+) earns (\d+(?:\.\d+)?) euros per (month|year)', ace_fact):
            match = re.match(r'^(.+) earns (\d+(?:\.\d+)?) euros per (month|year)', ace_fact)
            entity = self.normalize_entity(match.group(1))
            amount = match.group(2)
            period = match.group(3)
            return f"income({entity}, {amount}, {period})"

        # Pattern: X was born on YYYY-MM-DD
        elif re.match(r'^(.+) was born on (\d{4}-\d{2}-\d{2})', ace_fact):
            match = re.match(r'^(.+) was born on (\d{4}-\d{2}-\d{2})', ace_fact)
            entity = self.normalize_entity(match.group(1))
            birth_date = match.group(2)
            return f"birth_date({entity}, date({birth_date.replace('-', ', ')}))"

        # Pattern: X lives in Y
        elif re.match(r'^(.+) lives in ([A-Za-z][A-Za-z0-9_-]*)', ace_fact):
            match = re.match(r'^(.+) lives in ([A-Za-z][A-Za-z0-9_-]*)', ace_fact)
            entity = self.normalize_entity(match.group(1))
            location = self.normalize_entity(match.group(2))
            return f"residence({entity}, {location})"

        # Pattern: X has N children
        elif re.match(r'^(.+) has (\d+) (child|children)', ace_fact):
            match = re.match(r'^(.+) has (\d+) (child|children)', ace_fact)
            entity = self.normalize_entity(match.group(1))
            count = match.group(2)
            return f"children_count({entity}, {count})"

        # Pattern: X has German/EU/non-EU citizenship
        elif re.match(r'^(.+) has (German|EU|non.EU) citizenship', ace_fact):
            match = re.match(r'^(.+) has (German|EU|non.EU) citizenship', ace_fact)
            entity = self.normalize_entity(match.group(1))
            citizenship = match.group(2).replace('-', '_').lower()
            return f"citizenship({entity}, {citizenship})"

        # Pattern: X has Y Z (general - keep original)
        elif re.match(r'^(.+) has (.+) (.+)', ace_fact):
            match = re.match(r'^(.+) has (.+) (.+)', ace_fact)
            entity = self.normalize_entity(match.group(1))
            property_name = self.normalize_entity(match.group(2))
            value = self.normalize_entity(match.group(3))
            return f"has_property({entity}, {property_name}, {value})"

        return None

    def ace_to_prolog_rule(self, ace_rule: str) -> str | None:
        """Convert ACE rule to Prolog rule with administrative extensions"""
        ace_rule = ace_rule.strip().rstrip('.')

        # Pattern: X is eligible for Y if Z
        if re.match(r'^(.+) is eligible for (.+) if (.+)', ace_rule, re.IGNORECASE):
            match = re.match(r'^(.+) is eligible for (.+) if (.+)', ace_rule, re.IGNORECASE)
            entity = match.group(1).strip()
            benefit = match.group(2).strip()
            conditions = match.group(3).strip()

            var_name = entity.upper() if entity.upper() in ['X', 'Y', 'Z'] else 'X'
            benefit_norm = self.normalize_entity(benefit)

            conclusion = f"eligible({var_name}, {benefit_norm})"
            condition_prolog = self._parse_complex_conditions(conditions, var_name)

            if condition_prolog:
                return f"{conclusion} :- {condition_prolog}"

        # Original pattern: X is Y if Z
        elif ' if ' in ace_rule.lower():
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
                condition_prolog = self._parse_complex_conditions(condition, var_name)
                if condition_prolog:
                    return f"{conclusion_prolog} :- {condition_prolog}"

        return None

    def _parse_complex_conditions(self, condition: str, var_name: str) -> str | None:
        """Parse complex conditions with AND, OR, numerical comparisons"""
        # Handle AND conditions
        if ' and ' in condition.lower():
            parts = re.split(r'\s+and\s+', condition, flags=re.IGNORECASE)
            parsed_parts = []
            for part in parts:
                parsed_part = self._parse_single_condition(part.strip(), var_name)
                if parsed_part:
                    parsed_parts.append(parsed_part)
            if parsed_parts:
                return ', '.join(parsed_parts)

        # Handle OR conditions
        elif ' or ' in condition.lower():
            parts = re.split(r'\s+or\s+', condition, flags=re.IGNORECASE)
            parsed_parts = []
            for part in parts:
                parsed_part = self._parse_single_condition(part.strip(), var_name)
                if parsed_part:
                    parsed_parts.append(parsed_part)
            if parsed_parts:
                return '; '.join(parsed_parts)

        # Single condition
        else:
            return self._parse_single_condition(condition, var_name)

        return None

    def _parse_single_condition(self, condition: str, var_name: str) -> str | None:
        """Parse a single condition with administrative predicates"""

        # Has more/fewer than N children
        if re.match(r'^(.+) has (more than|fewer than|at least|exactly) (\d+) (child|children)', condition):
            match = re.match(r'^(.+) has (more than|fewer than|at least|exactly) (\d+) (child|children)', condition)
            subject = match.group(1).strip()
            comparison = match.group(2)
            count = match.group(3)

            if subject.upper() == var_name or subject.lower() == var_name.lower():
                if comparison == 'more than':
                    return f"children_count({var_name}, Count), Count > {count}"
                elif comparison == 'fewer than':
                    return f"children_count({var_name}, Count), Count < {count}"
                elif comparison == 'at least':
                    return f"children_count({var_name}, Count), Count >= {count}"
                elif comparison == 'exactly':
                    return f"children_count({var_name}, Count), Count =:= {count}"

        # Has citizenship
        elif re.match(r'^(.+) has (German|EU|non.EU) citizenship', condition):
            match = re.match(r'^(.+) has (German|EU|non.EU) citizenship', condition)
            subject = match.group(1).strip()
            citizenship_type = match.group(2).replace('-', '_').lower()

            if subject.upper() == var_name or subject.lower() == var_name.lower():
                return f"citizenship({var_name}, {citizenship_type})"

        # Lives in location
        elif re.match(r'^(.+) lives in (.+)', condition):
            match = re.match(r'^(.+) lives in (.+)', condition)
            subject = match.group(1).strip()
            location = self.normalize_entity(match.group(2))

            if subject.upper() == var_name or subject.lower() == var_name.lower():
                return f"residence({var_name}, {location})"

        # Basic property conditions
        elif re.match(r'^(.+) (is|has) (.+)', condition):
            match = re.match(r'^(.+) (is|has) (.+)', condition)
            subject = match.group(1).strip()
            verb = match.group(2)
            object_part = match.group(3).strip()

            if subject.upper() == var_name or subject.lower() == var_name.lower():
                if verb == 'is':
                    if object_part in ['employed', 'unemployed', 'self-employed', 'retired']:
                        return f"employment_status({var_name}, {object_part.replace('-', '_')})"
                    elif object_part in ['married', 'single', 'divorced', 'widowed']:
                        return f"marital_status({var_name}, {object_part})"
                    else:
                        property_name = self.normalize_entity(object_part)
                        return f"{property_name}({var_name})"

        # Fallback to original condition parsing
        return self._parse_condition(condition, var_name)

    def _parse_condition(self, condition: str, var_name: str) -> str | None:
        """Original condition parsing (unchanged for compatibility)"""
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
        """Enhanced query type parsing with administrative queries"""
        query_lower = ace_query.lower()

        # Original patterns
        if query_lower.startswith('is '):
            # Check for eligibility queries first
            if re.match(r'^is (.+) eligible for (.+)', query_lower):
                return QueryType.IS_ELIGIBLE_FOR
            return QueryType.IS_X_Y
        elif query_lower.startswith('who is '):
            return QueryType.WHO_IS_X
        elif re.match(r'^what does ([a-zA-Z][a-zA-Z0-9_]*) like', query_lower):
            return QueryType.WHAT_DOES_X_LIKE

        # New administrative patterns
        elif re.match(r'^what benefits does (.+) qualify for', query_lower):
            return QueryType.WHAT_BENEFITS
        elif re.match(r'^which (.+) are eligible for (.+)', query_lower):
            return QueryType.WHICH_ELIGIBLE
        elif re.match(r'^how much (.+) does (.+) (receive|earn)', query_lower):
            return QueryType.HOW_MUCH

        return None

    def ace_to_prolog_query(self, ace_query):
        """Enhanced query conversion with administrative query support"""
        ace_query = ace_query.strip().rstrip('?')
        prolog_query = None
        query_type = self.parse_query_type(ace_query)

        # Original query types
        if query_type is QueryType.IS_X_Y:
            query_content = ace_query[3:].strip()
            if re.match(r'^([a-zA-Z][a-zA-Z0-9_]*) ([a-zA-Z][a-zA-Z0-9_]*)', query_content):
                match = re.match(r'^([a-zA-Z][a-zA-Z0-9_]*) ([a-zA-Z][a-zA-Z0-9_]*)', query_content)
                entity = self.normalize_entity(match.group(1))
                property_name = self.normalize_entity(match.group(2))
                prolog_query = f"{property_name}({entity})"

        elif query_type is QueryType.WHO_IS_X:
            property_name = ace_query[7:].strip().lower()
            property_name = self.normalize_entity(property_name)
            prolog_query = f"{property_name}(X)"

        elif query_type is QueryType.WHAT_DOES_X_LIKE:
            match = re.match(r'^what does ([a-zA-Z][a-zA-Z0-9_]*) like', ace_query.lower())
            entity = self.normalize_entity(match.group(1))
            prolog_query = f"likes({entity}, X)"

        # New administrative query types
        elif query_type == QueryType.IS_ELIGIBLE_FOR:
            match = re.match(r'^is (.+) eligible for (.+)', ace_query.lower())
            entity = self.normalize_entity(match.group(1))
            benefit = self.normalize_entity(match.group(2))
            prolog_query = f"eligible({entity}, {benefit})"

        elif query_type == QueryType.WHAT_BENEFITS:
            match = re.match(r'^what benefits does (.+) qualify for', ace_query.lower())
            entity = self.normalize_entity(match.group(1))
            prolog_query = f"eligible({entity}, X)"

        elif query_type == QueryType.WHICH_ELIGIBLE:
            match = re.match(r'^which (.+) are eligible for (.+)', ace_query.lower())
            benefit = self.normalize_entity(match.group(2))
            prolog_query = f"eligible(X, {benefit})"

        elif query_type == QueryType.HOW_MUCH:
            match = re.match(r'^how much (.+) does (.+) (receive|earn)', ace_query.lower())
            if match:
                benefit_type = self.normalize_entity(match.group(1))
                entity = self.normalize_entity(match.group(2))
                action = match.group(3)

                if action == 'earn' and benefit_type == 'income':
                    prolog_query = f"income({entity}, X, _)"
                elif action == 'earn':
                    prolog_query = f"income({entity}, X, _)"
                else:
                    prolog_query = f"benefit_amount({entity}, {benefit_type}, X)"

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

    # Test administrative facts
    facts = [
        "Hans is a person.",
        "Hans earns 2500.50 euros per month.",
        "Hans was born on 1985-06-15.",
        "Hans lives in Germany.",
        "Hans has 2 children.",
        "Hans is married.",
        "Hans is employed.",
        "Hans has German citizenship."
    ]

    print("=== Testing Administrative Facts ===")
    for fact in facts:
        prolog = parser.ace_to_prolog_fact(fact)
        print(f"ACE: {fact}")
        print(f"Prolog: {prolog}")
        print()

    # Test administrative rules
    rules = [
        "X is eligible for Kindergeld if X has German citizenship and X has more than 0 children and X lives in Germany."
    ]

    print("=== Testing Administrative Rules ===")
    for rule in rules:
        prolog = parser.ace_to_prolog_rule(rule)
        print(f"ACE: {rule}")
        print(f"Prolog: {prolog}")
        print()

    # Test administrative queries
    queries = [
        "Is Hans eligible for Kindergeld?",
        "How much income does Hans earn?"
    ]

    print("=== Testing Administrative Queries ===")
    for query in queries:
        prolog = parser.ace_to_prolog_query(query)
        print(f"ACE: {query}")
        print(f"Prolog: {prolog}")
        print()
