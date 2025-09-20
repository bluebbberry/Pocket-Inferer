#!/usr/bin/env python3
"""
ACE Logical Inference Calculator - Enhanced with APE HTTP API Integration
A desktop application for logical reasoning using Attempto Controlled English
Now uses the official APE (Attempto Parsing Engine) via HTTP API for robust parsing
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog, simpledialog
import csv
import re
import os
import requests
import threading
import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import urllib.parse


@dataclass
class ProjectFile:
    """Represents a project file"""
    name: str
    path: str
    content: str = ""
    is_modified: bool = False


@dataclass
class APEResult:
    """Represents APE parsing result"""
    text: str
    syntax_valid: bool = False
    drs: str = ""
    owl_output: str = ""
    paraphrase: str = ""
    error_messages: List[str] = None

    def __post_init__(self):
        if self.error_messages is None:
            self.error_messages = []


class APEReasoningClient:
    """Enhanced APE client with reasoning capabilities"""

    def __init__(self, server_url: str = "http://localhost:8001"):
        self.server_url = server_url.rstrip('/')
        self.available = False
        self.check_availability()

    def check_availability(self):
        """Check if APE server is available"""
        try:
            response = requests.get(f"{self.server_url}/?text=Test.", timeout=3)
            self.available = response.status_code == 200
            return self.available
        except Exception as e:
            print(f"APE server not available: {e}")
            self.available = False
            return False

    def parse_text(self, text: str, output_format: str = "drspp") -> APEResult:
        """Parse ACE text using APE server"""
        if not self.available:
            return APEResult(text, error_messages=["APE server not available"])

        try:
            # Prepare parameters
            params = {
                'text': text.strip(),
                'solo': output_format
            }

            # Make request
            response = requests.get(f"{self.server_url}/", params=params, timeout=15)

            if response.status_code == 200:
                result_text = response.text.strip()

                # Check for parsing errors
                if "error" in result_text.lower() or "syntax error" in result_text.lower():
                    return APEResult(text, syntax_valid=False, error_messages=[result_text])

                # Successful parse
                result = APEResult(text, syntax_valid=True)

                if output_format == "drspp":
                    result.drs = result_text
                elif output_format == "paraphrase":
                    result.paraphrase = result_text
                elif output_format == "owlfss":
                    result.owl_output = result_text

                return result
            else:
                return APEResult(text, error_messages=[f"HTTP {response.status_code}: {response.text}"])

        except Exception as e:
            return APEResult(text, error_messages=[f"Request failed: {str(e)}"])

    def reason_with_query(self, knowledge_base: List[str], query: str) -> str:
        """Perform reasoning with knowledge base and query"""
        if not self.available:
            return "APE server not available for reasoning"

        # Combine knowledge base with query
        all_statements = knowledge_base + [query]
        complete_text = '\n'.join(all_statements)

        try:
            # Try to get proof or reasoning trace
            # APE can sometimes detect inconsistencies or provide reasoning info

            # First, parse everything together
            combined_result = self.parse_text(complete_text, "drspp")

            if not combined_result.syntax_valid:
                return f"Reasoning failed: {', '.join(combined_result.error_messages)}"

            # Parse knowledge base alone to compare
            kb_text = '\n'.join(knowledge_base)
            kb_result = self.parse_text(kb_text, "drspp")

            if not kb_result.syntax_valid:
                return "Knowledge base has syntax errors"

            # Simple reasoning: compare DRS structures
            return self._compare_drs_for_reasoning(query, kb_result.drs, combined_result.drs)

        except Exception as e:
            return f"Reasoning error: {str(e)}"

    def _compare_drs_for_reasoning(self, query: str, kb_drs: str, combined_drs: str) -> str:
        """Compare DRS structures to infer reasoning result"""
        query_lower = query.lower()

        # For "Is X Y?" questions
        if query_lower.startswith('is '):
            # Check if the combined DRS has additional information
            # If parsing the KB+Query together succeeds without contradiction,
            # and the query mentions entities that appear in KB, it's likely consistent

            match = re.match(r'is ([a-zA-Z]+) (?:a )?([a-zA-Z]+)\?', query_lower)
            if match:
                subject = match.group(1)
                predicate = match.group(2)

                # Check if both subject and predicate appear in the knowledge base DRS
                subject_in_kb = f"named({subject.capitalize()})" in kb_drs
                predicate_in_kb = predicate.lower() in kb_drs.lower()

                if subject_in_kb and predicate_in_kb:
                    # If both appear and there's no contradiction, likely true
                    if "INCONSISTENT" not in combined_drs.upper():
                        return "Yes"
                    else:
                        return "No (contradiction detected)"
                elif subject_in_kb:
                    # Subject exists but predicate not directly found
                    # Check for inheritance via rules
                    if self._check_inheritance(subject, predicate, kb_drs):
                        return "Yes (by inference)"
                    else:
                        return "Unknown (insufficient information)"
                else:
                    return "No (subject not found in knowledge base)"

        # For "Who is X?" questions
        elif query_lower.startswith('who is '):
            match = re.match(r'who is (?:a )?([a-zA-Z]+)\?', query_lower)
            if match:
                predicate = match.group(1).lower()

                # Extract all named entities that might have this predicate
                entities = []
                lines = kb_drs.split('\n')
                current_entity = None

                for line in lines:
                    # Look for named entities
                    name_match = re.search(r'named\(([A-Za-z]+)\)', line)
                    if name_match:
                        current_entity = name_match.group(1)

                    # Check if this line mentions the predicate and we have a current entity
                    if current_entity and predicate in line.lower():
                        if current_entity not in entities:
                            entities.append(current_entity)

                if entities:
                    return ", ".join(entities)
                else:
                    return "No one"

        return "Cannot determine answer from DRS analysis"

    def _check_inheritance(self, subject: str, predicate: str, kb_drs: str) -> bool:
        """Check for property inheritance through rules"""
        # Look for implication patterns in DRS that might connect subject to predicate
        lines = kb_drs.split('\n')

        # Very simplified inheritance check
        # In a real system, this would be much more sophisticated
        subject_lower = subject.lower()
        predicate_lower = predicate.lower()

        # Look for patterns that suggest inheritance
        # For example: if subject is "man" and predicate is "person"
        # and there's a rule "every man is a person"

        for line in lines:
            if subject_lower in line.lower() and predicate_lower in line.lower():
                # If both appear in the same context, might indicate relationship
                if "=>" in line:  # Implication arrow in DRS
                    return True

        return False


class SimpleOllamaTranslator:
    """Simple Ollama translator for natural language to ACE"""

    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "mistral:latest"):
        self.ollama_url = ollama_url.rstrip('/')
        self.model = model
        self.available = self._check_availability()

        self.system_prompt = """Convert this natural language to ACE (Attempto Controlled English) format.

ACE Rules:
- Facts: "John is happy." or "Mary likes chocolate."
- Rules: "X is happy if X likes chocolate." (use X, Y variables)
- Questions: "Is John happy?" or "Who is happy?"

Examples:
"John is a happy person" → "John is happy."
"If someone likes chocolate they become happy" → "X is happy if X likes chocolate."
"Who is happy" → "Who is happy?"

Convert to ACE format (output only the ACE sentence):"""

    def _check_availability(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=3)
            return response.status_code == 200
        except:
            return False

    def translate(self, text: str) -> Optional[str]:
        """Translate natural language to ACE"""
        if not self.available:
            return self._simple_fallback(text)

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"{self.system_prompt}\n\n{text}",
                    "stream": False,
                    "options": {"temperature": 0.1, "max_tokens": 100}
                },
                timeout=15
            )

            if response.status_code == 200:
                result = response.json()['response'].strip()
                return self._clean_result(result)

        except Exception as e:
            print(f"Ollama error: {e}")

        return self._simple_fallback(text)

    def _clean_result(self, result: str) -> str:
        """Clean Ollama output"""
        for line in result.split('\n'):
            line = line.strip().strip('"\'')
            if line and (line.endswith('.') or line.endswith('?')):
                return self._capitalize_names(line)

        first_line = result.split('\n')[0].strip().strip('"\'')
        if not first_line.endswith(('.', '?')):
            first_line += '.'
        return self._capitalize_names(first_line)

    def _capitalize_names(self, text: str) -> str:
        """Capitalize proper names"""
        words = text.split()
        common_words = {'is', 'are', 'has', 'have', 'likes', 'like', 'if', 'then', 'who', 'what', 'does'}

        result = []
        for i, word in enumerate(words):
            if word.upper() in ['X', 'Y']:
                result.append(word.upper())
            elif i == 0 or (word.lower() not in common_words and word.isalpha()):
                result.append(word.capitalize())
            else:
                result.append(word.lower())

        return ' '.join(result)

    def _simple_fallback(self, text: str) -> str:
        """Simple pattern-based fallback"""
        text = text.strip().lower()

        if re.match(r'(.+) is (.+)', text):
            match = re.match(r'(.+) is (.+)', text)
            return f"{match.group(1).capitalize()} is {match.group(2)}."
        elif re.match(r'(.+) likes? (.+)', text):
            match = re.match(r'(.+) likes? (.+)', text)
            return f"{match.group(1).capitalize()} likes {match.group(2)}."
        elif text.startswith('who'):
            return f"{text.capitalize()}?"
        elif text.startswith('is '):
            return f"{text.capitalize()}?"
        else:
            return f"{text.capitalize()}."


class ACEKnowledgeBase:
    """Knowledge base for storing and reasoning with ACE statements"""

    def __init__(self, ape_client: APEReasoningClient):
        self.ape_client = ape_client
        self.facts = []
        self.rules = []
        self.parsed_results = {}  # text -> APEResult

    def clear(self):
        """Clear all knowledge"""
        self.facts = []
        self.rules = []
        self.parsed_results = {}

    def add_statement(self, statement: str) -> APEResult:
        """Add a statement to the knowledge base"""
        result = self.ape_client.parse_multiple_outputs(statement)

        if result.syntax_valid:
            self.parsed_results[statement] = result

            # Classify statement type based on content
            if self._is_fact(statement):
                self.facts.append(statement)
            elif self._is_rule(statement):
                self.rules.append(statement)

        return result

    def _is_fact(self, statement: str) -> bool:
        """Determine if statement is a fact"""
        statement = statement.strip()
        return (not '?' in statement and
                not ' if ' in statement.lower() and
                statement.endswith('.') and
                not statement.startswith('X ') and
                not statement.startswith('Y '))

    def _is_rule(self, statement: str) -> bool:
        """Determine if statement is a rule"""
        return (' if ' in statement.lower() or
                statement.strip().startswith('X ') or
                statement.strip().startswith('Y '))

    def query(self, question: str) -> str:
        """Process a query using APE's reasoning capabilities"""
        if not question.strip().endswith('?'):
            question = question.strip() + '?'

        if not self.ape_client.available:
            return "APE server not available for reasoning"

        # Build complete knowledge base text with the question
        knowledge_text_parts = []

        # Add all facts and rules
        for fact in self.facts:
            knowledge_text_parts.append(fact)
        for rule in self.rules:
            knowledge_text_parts.append(rule)

        # Add the question
        knowledge_text_parts.append(question)

        complete_text = '\n'.join(knowledge_text_parts)

        # Parse the complete knowledge + query with APE
        try:
            # First, let's try to get OWL output which might show inconsistencies
            owl_result = self.ape_client.parse_text(complete_text, "owlfss")

            if owl_result.syntax_valid and owl_result.owl_output:
                # Check if the OWL output indicates the query can be answered
                # This is a simplified approach - in a full system, you'd use an OWL reasoner
                return self._analyze_owl_for_answer(question, owl_result.owl_output)

            # Fallback: try to reason from DRS
            drs_result = self.ape_client.parse_text(complete_text, "drspp")
            if drs_result.syntax_valid:
                return self._analyze_drs_for_answer(question, drs_result.drs)
            else:
                return f"Reasoning failed: {', '.join(drs_result.error_messages)}"

        except Exception as e:
            return f"Error during reasoning: {str(e)}"

    def _analyze_owl_for_answer(self, question: str, owl_output: str) -> str:
        """Analyze OWL output to determine query answer"""
        # This is a simplified analysis - a full implementation would use an OWL reasoner
        question_lower = question.lower()

        if question_lower.startswith('is '):
            # Extract subject and predicate from question
            match = re.match(r'is ([a-zA-Z]+) (?:a )?([a-zA-Z]+)\?', question_lower)
            if match:
                subject = match.group(1)
                predicate = match.group(2)

                # Look for subsumption or classification in OWL
                if f"'{subject}'" in owl_output and f"'{predicate}'" in owl_output:
                    # Simple heuristic: if both entities appear in OWL output, likely related
                    if "SubClassOf" in owl_output or "ClassAssertion" in owl_output:
                        return "Yes (based on OWL reasoning)"

        return "Cannot determine from OWL output"

    def _analyze_drs_for_answer(self, question: str, drs_output: str) -> str:
        """Analyze DRS output to determine query answer"""
        # Look for consistency or inconsistency markers in DRS
        question_lower = question.lower()

        if question_lower.startswith('is '):
            # For "Is X Y?" questions, try to find the entities in DRS
            match = re.match(r'is ([a-zA-Z]+) (?:a )?([a-zA-Z]+)\?', question_lower)
            if match:
                subject = match.group(1).lower()
                predicate = match.group(2).lower()

                # Check if DRS shows the relationship
                if f"named({subject.capitalize()})" in drs_output:
                    if predicate in drs_output.lower():
                        # Simple heuristic: if both subject and predicate appear in DRS context
                        return "Yes (inferred from DRS)"
                    else:
                        return "No (not found in DRS)"

        elif question_lower.startswith('who is '):
            # For "Who is X?" questions
            predicate_match = re.match(r'who is (?:a )?([a-zA-Z]+)\?', question_lower)
            if predicate_match:
                predicate = predicate_match.group(1).lower()

                # Extract named entities from DRS that have the predicate
                entities = []
                lines = drs_output.split('\n')
                for line in lines:
                    if f"named(" in line and predicate in line.lower():
                        # Extract name from named(X) pattern
                        name_match = re.search(r'named\(([A-Za-z]+)\)', line)
                        if name_match:
                            entities.append(name_match.group(1))

                if entities:
                    return ", ".join(entities)
                else:
                    return "No one (from DRS analysis)"


class ACEKnowledgeBase:
    """Knowledge base for storing and reasoning with ACE statements"""

    def __init__(self, ape_client):
        self.ape_client = ape_client
        self.facts = []
        self.rules = []
        self.parsed_results = {}  # text -> APEResult

    def clear(self):
        """Clear all knowledge"""
        self.facts = []
        self.rules = []
        self.parsed_results = {}

    def add_statement(self, statement: str) -> APEResult:
        """Add a statement to the knowledge base"""
        result = self.ape_client.parse_text(statement, "drspp")

        # Also get paraphrase for better user feedback
        if result.syntax_valid:
            para_result = self.ape_client.parse_text(statement, "paraphrase")
            if para_result.syntax_valid:
                result.paraphrase = para_result.paraphrase

        if result.syntax_valid:
            self.parsed_results[statement] = result

            # Classify statement type based on content
            if self._is_fact(statement):
                self.facts.append(statement)
            elif self._is_rule(statement):
                self.rules.append(statement)

        return result

    def _is_fact(self, statement: str) -> bool:
        """Determine if statement is a fact"""
        statement = statement.strip()
        return (not '?' in statement and
                not ' if ' in statement.lower() and
                statement.endswith('.') and
                not statement.startswith('X ') and
                not statement.startswith('Y '))

    def _is_rule(self, statement: str) -> bool:
        """Determine if statement is a rule"""
        return (' if ' in statement.lower() or
                statement.strip().startswith('X ') or
                statement.strip().startswith('Y ') or
                statement.lower().startswith('every') or
                statement.lower().startswith('if '))

    def query(self, question: str) -> str:
        """Process a query using APE's reasoning capabilities"""
        if not question.strip().endswith('?'):
            question = question.strip() + '?'

        if not self.ape_client.available:
            return "APE server not available for reasoning"

        # Use the enhanced reasoning method
        all_knowledge = self.facts + self.rules
        return self.ape_client.reason_with_query(all_knowledge, question)

    def get_all_statements(self) -> List[str]:
        """Get all statements in the knowledge base"""
        return self.facts + self.rules

    def _answer_is_question(self, question: str) -> str:
        """Answer 'Is X Y?' questions"""
        # Extract the subject and predicate
        match = re.match(r'is ([a-zA-Z]+) ([a-zA-Z]+)\?', question.lower())
        if not match:
            return "Cannot parse question"

        subject = match.group(1).capitalize()
        predicate = match.group(2).lower()

        # Check direct facts
        for fact in self.facts:
            if f"{subject} is {predicate}" in fact.lower():
                return "Yes"

        # Apply rules (simplified)
        for rule in self.rules:
            if self._can_derive_from_rule(subject, predicate, rule):
                return "Yes"

        return "No (or cannot determine)"

    def _answer_who_question(self, question: str) -> str:
        """Answer 'Who is X?' questions"""
        match = re.match(r'who is ([a-zA-Z]+)\?', question.lower())
        if not match:
            return "Cannot parse question"

        predicate = match.group(1).lower()
        subjects = []

        # Check direct facts
        for fact in self.facts:
            fact_match = re.search(r'([A-Z][a-zA-Z]+) is ' + predicate, fact)
            if fact_match:
                subjects.append(fact_match.group(1))

        # Apply rules (simplified)
        for fact in self.facts:
            for rule in self.rules:
                derived_subject = self._derive_who_from_rule(predicate, fact, rule)
                if derived_subject and derived_subject not in subjects:
                    subjects.append(derived_subject)

        return ', '.join(subjects) if subjects else "No one (or cannot determine)"

    def _answer_what_does_question(self, question: str) -> str:
        """Answer 'What does X like?' questions"""
        match = re.match(r'what does ([a-zA-Z]+) like\?', question.lower())
        if not match:
            return "Cannot parse question"

        subject = match.group(1).capitalize()
        objects = []

        # Check direct facts
        for fact in self.facts:
            fact_match = re.search(f'{subject} likes ([a-zA-Z]+)', fact)
            if fact_match:
                objects.append(fact_match.group(1))

        return ', '.join(objects) if objects else "Nothing found"

    def _can_derive_from_rule(self, subject: str, predicate: str, rule: str) -> bool:
        """Check if we can derive a fact from a rule"""
        # Very simplified rule matching
        rule_lower = rule.lower()
        if f"x is {predicate} if" in rule_lower:
            # Extract condition
            condition_match = re.search(r'if (.+)\.', rule_lower)
            if condition_match:
                condition = condition_match.group(1)
                condition_with_subject = condition.replace('x', subject.lower())

                # Check if condition is satisfied by facts
                for fact in self.facts:
                    if condition_with_subject in fact.lower():
                        return True
        return False

    def _derive_who_from_rule(self, predicate: str, fact: str, rule: str) -> Optional[str]:
        """Derive who satisfies a predicate using rules"""
        rule_lower = rule.lower()
        if f"x is {predicate} if" in rule_lower:
            condition_match = re.search(r'if (.+)\.', rule_lower)
            if condition_match:
                condition = condition_match.group(1)

                # Extract subject from fact and check if it satisfies condition
                for subject_match in re.finditer(r'([A-Z][a-zA-Z]+)', fact):
                    subject = subject_match.group(1)
                    condition_with_subject = condition.replace('x', subject.lower())

                    if condition_with_subject in fact.lower():
                        return subject
        return None

    def get_all_statements(self) -> List[str]:
        """Get all statements in the knowledge base"""
        return self.facts + self.rules


class CSVMappingDialog:
    """Dialog for editing LLM-generated CSV to ACE mapping"""

    def __init__(self, parent, headers, sample_row, ai_translator):
        self.parent = parent
        self.headers = headers
        self.sample_row = sample_row
        self.ai_translator = ai_translator
        self.result = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("CSV to ACE Mapping")
        self.dialog.geometry("900x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.setup_ui()
        self.generate_initial_mapping()

    def setup_ui(self):
        """Setup the mapping dialog UI"""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Title
        title_label = ttk.Label(main_frame, text="CSV to ACE Logic Mapping",
                                font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 15))

        # Sample data display
        sample_frame = ttk.LabelFrame(main_frame, text="Sample CSV Row", padding=10)
        sample_frame.pack(fill='x', pady=(0, 15))

        sample_display = tk.Text(sample_frame, height=2, font=('Consolas', 9),
                                 state='disabled', bg='#f8f9fa')
        sample_display.pack(fill='x')

        # Display sample data
        sample_display.config(state='normal')
        sample_content = " | ".join([f"{h}: {v}" for h, v in zip(self.headers, self.sample_row)])
        sample_display.insert('1.0', sample_content)
        sample_display.config(state='disabled')

        # Main mapping section - two columns
        mapping_frame = ttk.LabelFrame(main_frame, text="Row Mapping", padding=15)
        mapping_frame.pack(fill='both', expand=True, pady=(0, 15))

        # Create two-column layout
        columns_container = ttk.Frame(mapping_frame)
        columns_container.pack(fill='both', expand=True)

        # Left column - Column names
        left_column = ttk.Frame(columns_container)
        left_column.pack(side='left', fill='both', expand=True, padx=(0, 10))

        ttk.Label(left_column, text="CSV Columns:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(0, 5))

        self.columns_display = tk.Text(left_column, font=('Consolas', 10),
                                       state='disabled', bg='#f8f9fa', width=35)
        self.columns_display.pack(fill='both', expand=True)

        # Right column - ACE template
        right_column = ttk.Frame(columns_container)
        right_column.pack(side='right', fill='both', expand=True, padx=(10, 0))

        ttk.Label(right_column, text="ACE Statements (use <column_name> tags):",
                  font=('Arial', 11, 'bold')).pack(anchor='w', pady=(0, 5))

        self.ace_template = scrolledtext.ScrolledText(right_column, font=('Consolas', 10),
                                                      wrap='word', width=50)
        self.ace_template.pack(fill='both', expand=True)

        # Fill columns display
        self.populate_columns_display()

        # Preview section
        preview_frame = ttk.LabelFrame(main_frame, text="Preview (Applied to Sample Row)", padding=10)
        preview_frame.pack(fill='x', pady=(0, 15))

        self.preview_text = scrolledtext.ScrolledText(preview_frame, height=4,
                                                      font=('Consolas', 10), state='disabled',
                                                      bg='#f0f8ff')
        self.preview_text.pack(fill='x')

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')

        ttk.Button(button_frame, text="Generate AI Mapping",
                   command=self.generate_initial_mapping).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Update Preview",
                   command=self.update_preview).pack(side='left', padx=(0, 10))

        ttk.Button(button_frame, text="Cancel",
                   command=self.cancel).pack(side='right', padx=(10, 0))
        ttk.Button(button_frame, text="Apply Mapping",
                   command=self.apply_mapping).pack(side='right', padx=(10, 0))

        # Bind template changes to preview update
        self.ace_template.bind('<KeyRelease>', lambda e: self.root.after(1000, self.update_preview))

    def populate_columns_display(self):
        """Fill the columns display with CSV column names and sample values"""
        self.columns_display.config(state='normal')
        self.columns_display.delete('1.0', 'end')

        content = []
        for i, (header, value) in enumerate(zip(self.headers, self.sample_row), 1):
            content.append(f"{i:2d}. {header}")
            content.append(f"    Sample: {value}")
            content.append("")

        self.columns_display.insert('1.0', '\n'.join(content))
        self.columns_display.config(state='disabled')

    def generate_initial_mapping(self):
        """Generate initial mapping using AI"""
        if not self.ai_translator.available:
            self.generate_fallback_mapping()
            return

        headers_text = ", ".join(self.headers)
        sample_text = " | ".join([f"{h}={v}" for h, v in zip(self.headers, self.sample_row)])

        prompt = f"""Convert this CSV structure to ACE (Attempto Controlled English) statements.

CSV Columns: {headers_text}
Sample Row: {sample_text}

Generate ACE statements using <column_name> tags for substitution.

Example:
For columns: name, age, city
ACE output: <name> is a person. <name> has age <age>. <name> lives in <city>.

Generate concise ACE statements for these columns:"""

        try:
            response = self.generate_mapping_with_ai(prompt)
            if response:
                self.parse_ai_response(response)
            else:
                self.generate_fallback_mapping()
        except:
            self.generate_fallback_mapping()

    def generate_mapping_with_ai(self, prompt):
        """Generate mapping using AI translator"""
        try:
            response = requests.post(
                f"{self.ai_translator.ollama_url}/api/generate",
                json={
                    "model": self.ai_translator.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.2, "max_tokens": 150}
                },
                timeout=15
            )

            if response.status_code == 200:
                return response.json()['response'].strip()
        except:
            pass
        return None

    def parse_ai_response(self, response):
        """Parse AI response and extract ACE statements"""
        lines = response.split('\n')
        ace_statements = []

        for line in lines:
            line = line.strip()
            # Look for lines that contain angle bracket tags and look like ACE statements
            if '<' in line and '>' in line and (line.endswith('.') or line.endswith('?')):
                ace_statements.append(line)

        # If no proper statements found, try to extract any line with angle brackets
        if not ace_statements:
            for line in lines:
                line = line.strip()
                if '<' in line and '>' in line and line:
                    # Ensure it ends with proper punctuation
                    if not line.endswith(('.', '?', '!')):
                        line += '.'
                    ace_statements.append(line)

        # Set the template
        if ace_statements:
            self.ace_template.delete('1.0', 'end')
            self.ace_template.insert('1.0', '\n'.join(ace_statements))
        else:
            self.generate_fallback_mapping()

        self.update_preview()

    def generate_fallback_mapping(self):
        """Generate simple fallback mapping when AI fails"""
        statements = []

        if len(self.headers) >= 1:
            first_col = self.headers[0]

            # For remaining columns, create has/property statements
            for header in self.headers[1:]:
                clean_prop = header.lower().replace('_', ' ').replace('-', ' ')
                statements.append(f"<{first_col}> has {clean_prop} <{header}>.")

        self.ace_template.delete('1.0', 'end')
        self.ace_template.insert('1.0', '\n'.join(statements))
        self.update_preview()

    def update_preview(self):
        """Update preview with sample data applied to template"""
        template_text = self.ace_template.get('1.0', 'end-1c').strip()

        if not template_text:
            self.preview_text.config(state='normal')
            self.preview_text.delete('1.0', 'end')
            self.preview_text.insert('1.0', "No template defined")
            self.preview_text.config(state='disabled')
            return

        # Create substitution dictionary
        substitutions = {}
        for header, value in zip(self.headers, self.sample_row):
            substitutions[header] = value

        preview_lines = []

        try:
            # Apply substitutions to each line
            for line in template_text.split('\n'):
                line = line.strip()
                if line:
                    # Replace <column_name> tags with actual values
                    result_line = line
                    for header, value in substitutions.items():
                        tag = f"<{header}>"
                        if tag in result_line:
                            result_line = result_line.replace(tag, value)

                    preview_lines.append(result_line)

            # Update preview display
            self.preview_text.config(state='normal')
            self.preview_text.delete('1.0', 'end')
            self.preview_text.insert('1.0', '\n'.join(preview_lines))
            self.preview_text.config(state='disabled')

        except Exception as e:
            self.preview_text.config(state='normal')
            self.preview_text.delete('1.0', 'end')
            self.preview_text.insert('1.0', f"Preview error: {str(e)}")
            self.preview_text.config(state='disabled')

    def apply_mapping(self):
        """Apply the mapping and close dialog"""
        template_text = self.ace_template.get('1.0', 'end-1c').strip()

        if not template_text:
            messagebox.showwarning("Warning", "Please define ACE template statements")
            return

        self.result = template_text
        self.dialog.destroy()

    def cancel(self):
        """Cancel the dialog"""
        self.result = None
        self.dialog.destroy()


class CSVProcessor:
    """Process CSV files and convert to ACE facts"""

    @staticmethod
    def load_csv(file_path: str) -> Tuple[List[str], List[Dict[str, str]]]:
        """Load CSV file and return headers and data"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                headers = reader.fieldnames
                data = list(reader)
                return headers, data
        except Exception as e:
            raise Exception(f"Error loading CSV: {str(e)}")

    @staticmethod
    def convert_to_ace_facts_with_template(headers: List[str], data: List[Dict[str, str]],
                                           ace_template: str) -> List[str]:
        """Convert CSV data to ACE facts using template with <column_name> tags"""
        facts = []

        for i, row in enumerate(data):
            # Process each line of the template
            for line in ace_template.split('\n'):
                line = line.strip()
                if line:
                    # Replace <column_name> tags with actual values
                    result_line = line
                    for header in headers:
                        tag = f"<{header}>"
                        if tag in result_line:
                            value = row.get(header, '').strip()
                            result_line = result_line.replace(tag, value)

                    # Only add if all tags were replaced (no < > remaining)
                    if '<' not in result_line or '>' not in result_line:
                        if not result_line.endswith('.') and not result_line.endswith('?'):
                            result_line += '.'
                        facts.append(result_line)

        return facts


class FileExplorer:
    """File explorer widget for IDE mode"""

    def __init__(self, parent, callback):
        self.callback = callback
        self.current_directory = os.getcwd() + "/programming_mode_home"
        self.open_files = {}  # path -> ProjectFile

        # Create main frame
        self.frame = ttk.Frame(parent)

        # Toolbar
        toolbar = ttk.Frame(self.frame)
        toolbar.pack(fill='x', padx=5, pady=5)

        ttk.Button(toolbar, text="📁", command=self.open_folder, width=3).pack(side='left', padx=2)
        ttk.Button(toolbar, text="📄", command=self.new_file, width=3).pack(side='left', padx=2)
        ttk.Button(toolbar, text="💾", command=self.save_current, width=3).pack(side='left', padx=2)

        # Directory path
        self.path_var = tk.StringVar(value=self.current_directory)
        path_frame = ttk.Frame(self.frame)
        path_frame.pack(fill='x', padx=5, pady=2)
        ttk.Label(path_frame, text="Path:").pack(side='left')
        ttk.Entry(path_frame, textvariable=self.path_var, state='readonly').pack(side='left', fill='x', expand=True,
                                                                                 padx=5)

        # File tree
        tree_frame = ttk.Frame(self.frame)
        tree_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.tree = ttk.Treeview(tree_frame, show='tree')
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Bind events
        self.tree.bind('<Double-1>', self.on_double_click)

        # Populate tree
        self.refresh_tree()

    def refresh_tree(self):
        """Refresh the file tree"""
        self.tree.delete(*self.tree.get_children())

        try:
            for item in sorted(os.listdir(self.current_directory)):
                item_path = os.path.join(self.current_directory, item)
                if os.path.isdir(item_path):
                    self.tree.insert('', 'end', text=f"📁 {item}", values=[item_path])
                elif item.endswith(('.ace', '.txt', '.pl', '.py')):
                    icon = "📄" if item not in [os.path.basename(f) for f in self.open_files.keys()] else "📝"
                    self.tree.insert('', 'end', text=f"{icon} {item}", values=[item_path])
        except PermissionError:
            pass

    def on_double_click(self, event):
        """Handle double click on tree item"""
        item = self.tree.selection()[0]
        path = self.tree.item(item)['values'][0]

        if os.path.isdir(path):
            self.current_directory = path
            self.path_var.set(path)
            self.refresh_tree()
        else:
            self.open_file(path)

    def open_file(self, path):
        """Open a file for editing"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            file_obj = ProjectFile(
                name=os.path.basename(path),
                path=path,
                content=content
            )

            self.open_files[path] = file_obj
            self.callback('open_file', file_obj)
            self.refresh_tree()

        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {str(e)}")

    def open_folder(self):
        """Open folder dialog"""
        folder = filedialog.askdirectory(initialdir=self.current_directory)
        if folder:
            self.current_directory = folder
            self.path_var.set(folder)
            self.refresh_tree()

    def new_file(self):
        """Create new file"""
        filename = simpledialog.askstring("New File", "Enter filename:", initialvalue="untitled.ace")
        if filename:
            path = os.path.join(self.current_directory, filename)
            file_obj = ProjectFile(
                name=filename,
                path=path,
                content="# New ACE Logic File\n\n",
                is_modified=True
            )
            self.open_files[path] = file_obj
            self.callback('open_file', file_obj)
            self.refresh_tree()

    def save_current(self):
        """Save current file"""
        self.callback('save_file', None)


class CodeEditor:
    """Enhanced code editor with syntax highlighting and line numbers"""

    def __init__(self, parent):
        self.frame = ttk.Frame(parent)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill='both', expand=True)

        self.open_tabs = {}  # file_path -> tab_frame
        self.current_file = None

        # Bind tab change event
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_change)

    def open_file(self, file_obj: ProjectFile):
        """Open file in new tab"""
        if file_obj.path in self.open_tabs:
            # Switch to existing tab
            tab_frame = self.open_tabs[file_obj.path]
            self.notebook.select(tab_frame)
            return

        # Create new tab
        tab_frame = ttk.Frame(self.notebook)

        # Add line numbers frame
        numbers_frame = tk.Frame(tab_frame, width=50, bg='#f0f0f0')
        numbers_frame.pack(side='left', fill='y')

        line_numbers = tk.Text(
            numbers_frame,
            width=4,
            padx=3,
            takefocus=0,
            border=0,
            state='disabled',
            bg='#f0f0f0',
            font=('Consolas', 10)
        )
        line_numbers.pack(fill='y', expand=True)

        # Create text widget
        text_widget = scrolledtext.ScrolledText(
            tab_frame,
            font=('Consolas', 11),
            wrap='none',
            undo=True,
            maxundo=-1
        )
        text_widget.pack(side='right', fill='both', expand=True)

        # Insert content
        text_widget.insert('1.0', file_obj.content)

        # Configure tags for syntax highlighting
        self.setup_syntax_highlighting(text_widget)

        # Bind events
        text_widget.bind('<KeyRelease>', lambda e: self.update_line_numbers(text_widget, line_numbers))
        text_widget.bind('<Button-1>', lambda e: self.update_line_numbers(text_widget, line_numbers))
        text_widget.bind('<MouseWheel>', lambda e: self.sync_scroll(text_widget, line_numbers, e))

        # Store references
        tab_frame.text_widget = text_widget
        tab_frame.file_obj = file_obj
        tab_frame.line_numbers = line_numbers

        # Add tab to notebook
        tab_name = file_obj.name + ("*" if file_obj.is_modified else "")
        self.notebook.add(tab_frame, text=tab_name)
        self.open_tabs[file_obj.path] = tab_frame

        # Select the new tab
        self.notebook.select(tab_frame)
        self.current_file = file_obj

        # Update line numbers
        self.update_line_numbers(text_widget, line_numbers)

    def setup_syntax_highlighting(self, text_widget):
        """Setup basic syntax highlighting for ACE"""
        # Configure tags
        text_widget.tag_configure('keyword', foreground='blue', font=('Consolas', 11, 'bold'))
        text_widget.tag_configure('string', foreground='green')
        text_widget.tag_configure('comment', foreground='gray', font=('Consolas', 11, 'italic'))
        text_widget.tag_configure('entity', foreground='purple', font=('Consolas', 11, 'bold'))

        def highlight_syntax(event=None):
            content = text_widget.get('1.0', 'end')

            # Clear existing tags
            for tag in ['keyword', 'string', 'comment', 'entity']:
                text_widget.tag_remove(tag, '1.0', 'end')

            # Highlight keywords
            keywords = ['is', 'are', 'if', 'then', 'who', 'what', 'does', 'like', 'has', 'have', 'every', 'all', 'some',
                        'no']
            for keyword in keywords:
                start = '1.0'
                while True:
                    pos = text_widget.search(f'\\b{keyword}\\b', start, 'end', regexp=True, nocase=True)
                    if not pos:
                        break
                    end_pos = f"{pos}+{len(keyword)}c"
                    text_widget.tag_add('keyword', pos, end_pos)
                    start = end_pos

            # Highlight comments
            start = '1.0'
            while True:
                pos = text_widget.search('#.*', start, 'end', regexp=True)
                if not pos:
                    break
                line_end = f"{pos} lineend"
                text_widget.tag_add('comment', pos, line_end)
                start = f"{pos} linestart +1line"

            # Highlight entities (capitalized words)
            start = '1.0'
            while True:
                pos = text_widget.search('[A-Z][a-zA-Z0-9_-]*', start, 'end', regexp=True)
                if not pos:
                    break
                end_pos = text_widget.index(f"{pos} wordend")
                text_widget.tag_add('entity', pos, end_pos)
                start = end_pos

        # Bind highlighting
        text_widget.bind('<KeyRelease>', highlight_syntax)
        text_widget.after(100, highlight_syntax)

    def update_line_numbers(self, text_widget, line_numbers):
        """Update line numbers"""
        line_count = int(text_widget.index('end').split('.')[0])

        line_numbers.config(state='normal')
        line_numbers.delete('1.0', 'end')

        for i in range(1, line_count):
            line_numbers.insert('end', f"{i:>3}\n")

        line_numbers.config(state='disabled')

    def sync_scroll(self, text_widget, line_numbers, event):
        """Sync scrolling between text and line numbers"""
        line_numbers.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_tab_change(self, event):
        """Handle tab change"""
        selected_tab = self.notebook.select()
        if selected_tab:
            tab_frame = self.notebook.nametowidget(selected_tab)
            if hasattr(tab_frame, 'file_obj'):
                self.current_file = tab_frame.file_obj

    def get_current_content(self):
        """Get content of current tab"""
        selected_tab = self.notebook.select()
        if selected_tab:
            tab_frame = self.notebook.nametowidget(selected_tab)
            if hasattr(tab_frame, 'text_widget'):
                return tab_frame.text_widget.get('1.0', 'end-1c')
        return ""

    def save_current_file(self):
        """Save current file"""
        selected_tab = self.notebook.select()
        if selected_tab:
            tab_frame = self.notebook.nametowidget(selected_tab)
            if hasattr(tab_frame, 'file_obj') and hasattr(tab_frame, 'text_widget'):
                content = tab_frame.text_widget.get('1.0', 'end-1c')
                try:
                    with open(tab_frame.file_obj.path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    tab_frame.file_obj.is_modified = False
                    # Update tab title
                    tab_index = self.notebook.index(selected_tab)
                    self.notebook.tab(tab_index, text=tab_frame.file_obj.name)
                    return True
                except Exception as e:
                    messagebox.showerror("Error", f"Could not save file: {str(e)}")
        return False


class EnhancedACECalculator:
    """Enhanced ACE Calculator with APE HTTP API integration"""

    def __init__(self, root):
        self.root = root
        self.root.title("ACE Logic Calculator with APE Integration")
        self.root.geometry("1200x900")
        self.root.configure(bg='#2c3e50')

        # Mode state
        self.is_ide_mode = False

        # Style configuration
        self.setup_styles()

        # Core components
        self.ape_client = APEReasoningClient()
        self.knowledge_base = ACEKnowledgeBase(self.ape_client)

        # AI Assistant
        self.ai_translator = SimpleOllamaTranslator()

        # UI components
        self.setup_ui()

    def setup_styles(self):
        """Setup modern styling"""
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Color scheme
        self.colors = {
            'bg': '#2c3e50',
            'card': '#34495e',
            'accent': '#3498db',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'text': '#ecf0f1',
            'text_dark': '#2c3e50'
        }

        # Configure styles
        self.style.configure('Card.TFrame', background=self.colors['card'], relief='flat')
        self.style.configure('Title.TLabel', background=self.colors['bg'], foreground=self.colors['text'],
                             font=('Arial', 18, 'bold'))
        self.style.configure('Subtitle.TLabel', background=self.colors['card'], foreground=self.colors['text'],
                             font=('Arial', 11, 'bold'))

    def setup_ui(self):
        """Setup the main interface"""
        # Main container
        self.main_container = tk.Frame(self.root, bg=self.colors['bg'])
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Create calculator mode UI
        self.setup_calculator_mode()

    def setup_calculator_mode(self):
        """Setup calculator-like interface"""
        # Mode switcher
        mode_frame = tk.Frame(self.main_container, bg=self.colors['bg'])
        mode_frame.pack(fill='x', pady=(0, 15))

        self.mode_button = tk.Button(
            mode_frame,
            text="Programming Mode",
            command=self.toggle_mode,
            bg=self.colors['warning'],
            fg='white',
            font=('Arial', 10, 'bold'),
            relief='raised',
            bd=2,
            padx=20,
            pady=5
        )
        self.mode_button.pack(side='right')

        # Title with APE status
        title_text = "ACE Logic Calculator with APE"
        if not self.ape_client.available:
            title_text += " (APE Server Offline)"

        title_label = ttk.Label(mode_frame, text=title_text, style='Title.TLabel')
        title_label.pack(side='left')

        # Create calculator sections
        self.calc_container = tk.Frame(self.main_container, bg=self.colors['bg'])
        self.calc_container.pack(fill=tk.BOTH, expand=True)

        self.setup_calc_results_section(self.calc_container)
        self.setup_calc_input_section(self.calc_container)
        self.setup_calc_button_section(self.calc_container)
        self.setup_calc_status_bar(self.calc_container)

    def setup_ide_mode(self):
        """Setup IDE-like interface"""
        # Mode switcher (update)
        mode_frame = tk.Frame(self.main_container, bg=self.colors['bg'])
        mode_frame.pack(fill='x', pady=(0, 15))

        self.mode_button = tk.Button(
            mode_frame,
            text="Exit Programming Mode",
            command=self.toggle_mode,
            bg=self.colors['accent'],
            fg='white',
            font=('Arial', 10, 'bold'),
            relief='raised',
            bd=2,
            padx=20,
            pady=5
        )
        self.mode_button.pack(side='right')

        # Title
        title_label = ttk.Label(mode_frame, text="Programming Mode with APE", style='Title.TLabel')
        title_label.pack(side='left')

        # Create IDE layout
        self.ide_container = tk.Frame(self.main_container, bg=self.colors['bg'])
        self.ide_container.pack(fill=tk.BOTH, expand=True)

        # Main paned window
        main_paned = ttk.PanedWindow(self.ide_container, orient='horizontal')
        main_paned.pack(fill='both', expand=True)

        # Left panel (File Explorer)
        left_panel = ttk.Frame(main_paned, width=300)
        main_paned.add(left_panel, weight=1)

        # File explorer
        explorer_label = ttk.Label(left_panel, text="Files", style='Subtitle.TLabel')
        explorer_label.pack(pady=(10, 5))

        self.file_explorer = FileExplorer(left_panel, self.handle_file_action)
        self.file_explorer.frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Right panel
        right_panel = ttk.PanedWindow(main_paned, orient='vertical')
        main_paned.add(right_panel, weight=3)

        # Code editor area
        editor_frame = ttk.Frame(right_panel)
        right_panel.add(editor_frame, weight=2)

        editor_label = ttk.Label(editor_frame, text="Editor", style='Subtitle.TLabel')
        editor_label.pack(pady=(10, 5))

        self.code_editor = CodeEditor(editor_frame)
        self.code_editor.frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Results panel
        results_frame = ttk.Frame(right_panel, height=250)
        right_panel.add(results_frame, weight=1)

        results_label = ttk.Label(results_frame, text="APE Analysis & Results", style='Subtitle.TLabel')
        results_label.pack(pady=(10, 5))

        # Control buttons
        control_frame = tk.Frame(results_frame, bg=self.colors['card'])
        control_frame.pack(fill='x', padx=10, pady=5)

        tk.Button(control_frame, text="Parse with APE", command=self.parse_ide_code,
                  bg=self.colors['success'], fg='white', font=('Arial', 9, 'bold'),
                  padx=15, pady=5).pack(side='left', padx=5)

        tk.Button(control_frame, text="Save", command=self.save_current_file,
                  bg=self.colors['accent'], fg='white', font=('Arial', 9, 'bold'),
                  padx=15, pady=5).pack(side='left', padx=5)

        tk.Button(control_frame, text="Clear Results", command=self.clear_ide_results,
                  bg=self.colors['danger'], fg='white', font=('Arial', 9, 'bold'),
                  padx=15, pady=5).pack(side='left', padx=5)

        # Results display
        self.ide_results_display = scrolledtext.ScrolledText(
            results_frame,
            height=10,
            font=('Consolas', 10),
            state=tk.DISABLED,
            bg='#ecf0f1',
            fg=self.colors['text_dark'],
            wrap=tk.WORD
        )
        self.ide_results_display.pack(fill='both', expand=True, padx=10, pady=(5, 10))

        # Status bar for IDE
        self.setup_ide_status_bar(self.ide_container)

    def handle_file_action(self, action, file_obj):
        """Handle file explorer actions"""
        if action == 'open_file':
            self.code_editor.open_file(file_obj)
        elif action == 'save_file':
            self.save_current_file()

    def toggle_mode(self):
        """Toggle between calculator and IDE mode"""
        # Clear current interface
        for widget in self.main_container.winfo_children():
            widget.destroy()

        self.is_ide_mode = not self.is_ide_mode

        if self.is_ide_mode:
            self.setup_ide_mode()
            self.root.title("ACE Logic Calculator - Programming Mode with APE")
        else:
            self.setup_calculator_mode()
            self.root.title("ACE Logic Calculator with APE Integration")

    def parse_ide_code(self):
        """Parse code from IDE editor using APE"""
        content = self.code_editor.get_current_content()
        if not content.strip():
            messagebox.showwarning("Warning", "No code to parse")
            return

        if not self.ape_client.available:
            messagebox.showerror("Error", "APE server is not available. Please start the APE HTTP server.")
            return

        try:
            # Clear previous knowledge
            self.knowledge_base.clear()

            # Parse statements line by line
            statements = [line.strip() for line in content.split('\n')
                          if line.strip() and not line.strip().startswith('#')]

            results = []
            results.append("=== APE Parsing Results ===")
            results.append(f"Processing {len(statements)} statements\n")

            queries = []
            facts_and_rules = []

            for i, statement in enumerate(statements, 1):
                result = self.knowledge_base.add_statement(statement)

                if result.syntax_valid:
                    results.append(f"✓ Statement {i}: {statement}")

                    if statement.strip().endswith('?'):
                        queries.append(statement)
                    else:
                        facts_and_rules.append(statement)

                    if result.drs:
                        results.append(f"  DRS: {result.drs[:100]}{'...' if len(result.drs) > 100 else ''}")
                    if result.paraphrase:
                        results.append(f"  Paraphrase: {result.paraphrase}")
                    results.append("")
                else:
                    results.append(f"✗ Statement {i}: {statement}")
                    results.append(f"  Errors: {', '.join(result.error_messages)}")
                    results.append("")

            # Process queries
            if queries:
                results.append("Query Results:")
                results.append("-" * 40)
                for query in queries:
                    answer = self.knowledge_base.query(query)
                    results.append(f"Q: {query}")
                    results.append(f"A: {answer}")
                    results.append("")

            # Show knowledge base summary
            all_statements = self.knowledge_base.get_all_statements()
            if all_statements:
                results.append("Knowledge Base Summary:")
                results.append("-" * 40)
                results.append(f"Facts: {len(self.knowledge_base.facts)}")
                results.append(f"Rules: {len(self.knowledge_base.rules)}")
                results.append("")
                for stmt in all_statements[:10]:  # Show first 10
                    results.append(f"  • {stmt}")
                if len(all_statements) > 10:
                    results.append(f"  ... and {len(all_statements) - 10} more")

            # Display results
            self.ide_results_display.config(state=tk.NORMAL)
            self.ide_results_display.delete(1.0, tk.END)
            self.ide_results_display.insert(tk.END, "\n".join(results))
            self.ide_results_display.config(state=tk.DISABLED)

            # Update status
            if hasattr(self, 'ide_status_var'):
                self.ide_status_var.set(f"Parsed {len(statements)} statements with APE")

        except Exception as e:
            messagebox.showerror("Error", f"Error parsing with APE: {str(e)}")
            if hasattr(self, 'ide_status_var'):
                self.ide_status_var.set(f"Error: {str(e)}")

    def save_current_file(self):
        """Save current file in IDE"""
        if self.code_editor.save_current_file():
            if hasattr(self, 'ide_status_var'):
                self.ide_status_var.set("File saved successfully")
        else:
            if hasattr(self, 'ide_status_var'):
                self.ide_status_var.set("No file to save or error occurred")

    def clear_ide_results(self):
        """Clear IDE results"""
        self.ide_results_display.config(state=tk.NORMAL)
        self.ide_results_display.delete(1.0, tk.END)
        self.ide_results_display.config(state=tk.DISABLED)
        if hasattr(self, 'ide_status_var'):
            self.ide_status_var.set("Results cleared")

    def setup_ide_status_bar(self, parent):
        """Setup status bar for IDE mode"""
        status_frame = tk.Frame(parent, bg=self.colors['card'], relief='raised', bd=2)
        status_frame.pack(fill=tk.X, pady=(15, 0))

        self.ide_status_var = tk.StringVar()
        status_text = "Programming Mode Ready - APE Available" if self.ape_client.available else "Programming Mode - APE Server Offline"
        self.ide_status_var.set(status_text)

        status_label = tk.Label(status_frame, textvariable=self.ide_status_var,
                                bg=self.colors['card'], fg=self.colors['text'],
                                font=('Arial', 9), anchor='w')
        status_label.pack(fill=tk.X, padx=10, pady=5)

    def setup_calc_input_section(self, parent):
        """Setup main text input area for calculator mode"""
        input_frame = tk.Frame(parent, bg=self.colors['card'], relief='raised', bd=2)
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Header
        header_frame = tk.Frame(input_frame, bg=self.colors['card'])
        header_frame.pack(fill=tk.X, padx=15, pady=(15, 10))

        ttk.Label(header_frame, text="ACE Statements", style='Subtitle.TLabel').pack(side=tk.LEFT)

        # File operations
        file_frame = tk.Frame(header_frame, bg=self.colors['card'])
        file_frame.pack(side=tk.RIGHT)

        self.create_small_button(file_frame, "Load CSV", self.load_csv, '#9b59b6')
        self.create_small_button(file_frame, "Import", self.import_file, '#9b59b6')
        self.create_small_button(file_frame, "Export", self.export_file, '#9b59b6')

        # Main text area
        text_frame = tk.Frame(input_frame, bg=self.colors['card'])
        text_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        self.text_input = scrolledtext.ScrolledText(
            text_frame,
            height=12,
            font=('Consolas', 11),
            bg='#ecf0f1',
            fg=self.colors['text_dark'],
            relief='flat',
            bd=5,
            wrap=tk.WORD,
            insertbackground='#2c3e50'
        )
        self.text_input.pack(fill=tk.BOTH, expand=True)

        # Add exciting ACE examples
        example_text = """# Logical Reasoning Examples

# Simple Facts
Every man is a person.
John is a man.
Mary is a woman.
Every woman is a person.

# Properties and Relations  
John likes Mary.
Mary likes chocolate.
Every person that likes chocolate is happy.

# Complex Rules
If a person X likes a person Y and Y likes chocolate then X is jealous.
Every jealous person is unhappy.

# Queries to test reasoning
Is John a person?
Is Mary happy?
Who is happy?
Who is jealous?
What does John like?

# Advanced Example: Family Relations
John is the father of Mary.
Mary is the mother of Peter.
If X is the father of Y then X is a parent of Y.
If X is the mother of Y then X is a parent of Y.
If X is a parent of Y and Y is a parent of Z then X is a grandparent of Z.

Who is a parent of Mary?
Who is a grandparent of Peter?"""

        self.text_input.insert(tk.END, example_text)

    def setup_calc_button_section(self, parent):
        """Setup calculator-style button panel"""
        button_panel = tk.Frame(parent, bg=self.colors['card'], relief='raised', bd=2)
        button_panel.pack(fill=tk.X, pady=(0, 15))

        # Button grid container
        grid_container = tk.Frame(button_panel, bg=self.colors['card'])
        grid_container.pack(padx=15, pady=(15, 15))

        # Row 1: Statement types
        self.create_calc_button(grid_container, "FACT",
                                lambda: self.insert_template("<ENTITY> is <PROPERTY>.\n"),
                                '#27ae60', 0, 0)
        self.create_calc_button(grid_container, "RULE",
                                lambda: self.insert_template("If <CONDITION> then <CONCLUSION>.\n"),
                                '#3498db', 0, 1)
        self.create_calc_button(grid_container, "QUERY",
                                lambda: self.insert_template("Is <ENTITY> <PROPERTY>?\n"),
                                '#f39c12', 0, 2)

        # Row 2: Question templates
        self.create_calc_button(grid_container, "WHO IS ...?",
                                lambda: self.insert_template("Who is <PROPERTY>?\n"),
                                '#e67e22', 1, 0)
        self.create_calc_button(grid_container, "WHAT LIKES ...?",
                                lambda: self.insert_template("What does <ENTITY> like?\n"),
                                '#e67e22', 1, 1)
        self.create_calc_button(grid_container, "UNIVERSAL",
                                lambda: self.insert_template("Every <CLASS> is <PROPERTY>.\n"),
                                '#8e44ad', 1, 2)

        # Row 3: Actions
        self.create_calc_button(grid_container, "PARSE WITH APE", self.parse_statements, '#27ae60', 0, 3, width=15)
        self.create_calc_button(grid_container, "AI ASSIST", lambda: self.show_ai_assist(), '#e74c3c', 1, 3, width=15)

    def create_calc_button(self, parent, text, command, color, row, col, width=12):
        """Create a calculator-style button"""
        btn = tk.Button(parent, text=text, command=command,
                        bg=color, fg='white', font=('Arial', 9, 'bold'),
                        relief='raised', bd=2, width=width, pady=8,
                        activebackground=color, activeforeground='white')
        btn.grid(row=row, column=col, padx=5, pady=3, sticky='ew')
        parent.columnconfigure(col, weight=1)

    def create_small_button(self, parent, text, command, color):
        """Create a small button for file operations"""
        btn = tk.Button(parent, text=text, command=command,
                        bg=color, fg='white', font=('Arial', 8, 'bold'),
                        relief='raised', bd=1, padx=10, pady=2,
                        activebackground=color, activeforeground='white')
        btn.pack(side=tk.LEFT, padx=2)

    def setup_calc_results_section(self, parent):
        """Setup results display for calculator mode"""
        results_frame = tk.Frame(parent, bg=self.colors['card'], relief='raised', bd=2)
        results_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(results_frame, text="APE Analysis & Results", style='Subtitle.TLabel').pack(pady=(15, 10))

        # Results text area
        self.results_display = scrolledtext.ScrolledText(
            results_frame,
            height=10,
            font=('Consolas', 10),
            state=tk.DISABLED,
            bg='#ecf0f1',
            fg=self.colors['text_dark']
        )
        self.results_display.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

    def setup_calc_status_bar(self, parent):
        """Setup status bar for calculator mode"""
        status_frame = tk.Frame(parent, bg=self.colors['card'], relief='raised', bd=2)
        status_frame.pack(fill=tk.X, pady=(15, 0))

        self.status_var = tk.StringVar()
        status_text = "Ready - APE Available" if self.ape_client.available else "Ready - APE Server Offline"
        self.status_var.set(status_text)

        status_label = tk.Label(status_frame, textvariable=self.status_var,
                                bg=self.colors['card'], fg=self.colors['text'],
                                font=('Arial', 9), anchor='w')
        status_label.pack(fill=tk.X, padx=10, pady=5)

    def insert_template(self, template):
        """Insert template at current cursor position"""
        cursor_pos = self.text_input.index(tk.INSERT)
        self.text_input.insert(cursor_pos, template)
        self.text_input.focus_set()

        # Move cursor to first placeholder
        if '<' in template:
            start_pos = self.text_input.search('<', cursor_pos)
            if start_pos:
                end_pos = self.text_input.search('>', start_pos)
                if end_pos:
                    # Select the placeholder text
                    self.text_input.tag_add(tk.SEL, start_pos, f"{end_pos}+1c")
                    self.text_input.mark_set(tk.INSERT, start_pos)

        self.status_var.set(f"Template inserted: {template.strip()}")

    def parse_statements(self):
        """Parse all statements in the text box using APE"""
        if not self.ape_client.available:
            messagebox.showerror("Error",
                                 "APE server is not available. Please start the APE HTTP server at http://localhost:8001")
            return

        text_content = self.text_input.get(1.0, tk.END)

        try:
            # Clear previous knowledge
            self.knowledge_base.clear()

            # Parse statements line by line
            statements = [line.strip() for line in text_content.split('\n')
                          if line.strip() and not line.strip().startswith('#')]

            if not statements:
                messagebox.showwarning("Warning", "No statements to parse")
                return

            results = []
            results.append("=== APE Parsing Results ===")
            results.append(f"Processing {len(statements)} statements\n")

            queries = []
            facts_and_rules = []

            # Progress tracking
            self.status_var.set("Parsing with APE...")
            self.root.update()

            for i, statement in enumerate(statements, 1):
                self.status_var.set(f"Parsing statement {i}/{len(statements)}...")
                self.root.update()

                result = self.knowledge_base.add_statement(statement)

                if result.syntax_valid:
                    results.append(f"✓ Statement {i}: {statement}")

                    if statement.strip().endswith('?'):
                        queries.append(statement)
                    else:
                        facts_and_rules.append(statement)

                    if result.drs:
                        results.append(f"  DRS: {result.drs[:150]}{'...' if len(result.drs) > 150 else ''}")
                    if result.paraphrase:
                        results.append(f"  Paraphrase: {result.paraphrase}")
                    results.append("")
                else:
                    results.append(f"✗ Statement {i}: {statement}")
                    results.append(f"  Errors: {', '.join(result.error_messages)}")
                    results.append("")

            # Process queries
            if queries:
                results.append("Query Results:")
                results.append("-" * 50)
                self.status_var.set("Processing queries...")
                self.root.update()

                for query in queries:
                    answer = self.knowledge_base.query(query)
                    results.append(f"Q: {query}")
                    results.append(f"A: {answer}")
                    results.append("")

            # Show knowledge base summary
            all_statements = self.knowledge_base.get_all_statements()
            if all_statements:
                results.append("Knowledge Base Summary:")
                results.append("-" * 50)
                results.append(f"Total Facts: {len(self.knowledge_base.facts)}")
                results.append(f"Total Rules: {len(self.knowledge_base.rules)}")
                results.append(f"Total Queries: {len(queries)}")
                results.append("")

                if self.knowledge_base.facts:
                    results.append("Sample Facts:")
                    for fact in self.knowledge_base.facts[:5]:
                        results.append(f"  • {fact}")
                    if len(self.knowledge_base.facts) > 5:
                        results.append(f"  ... and {len(self.knowledge_base.facts) - 5} more facts")
                    results.append("")

                if self.knowledge_base.rules:
                    results.append("Sample Rules:")
                    for rule in self.knowledge_base.rules[:3]:
                        results.append(f"  • {rule}")
                    if len(self.knowledge_base.rules) > 3:
                        results.append(f"  ... and {len(self.knowledge_base.rules) - 3} more rules")

            # Display results
            self.results_display.config(state=tk.NORMAL)
            self.results_display.delete(1.0, tk.END)
            self.results_display.insert(tk.END, "\n".join(results))
            self.results_display.config(state=tk.DISABLED)

            self.status_var.set(f"Parsed {len(statements)} statements successfully with APE")

        except Exception as e:
            messagebox.showerror("Error", f"Error parsing with APE: {str(e)}")
            self.status_var.set(f"Error: {str(e)}")

    def show_ai_assist(self):
        """Show AI assist dialog"""
        user_input = simpledialog.askstring(
            "AI Assistant",
            "Enter natural language statement:\n\n"
            "Examples:\n"
            "• 'Every person who likes chocolate is happy'\n"
            "• 'John is a tall person who likes Mary'\n"
            "• 'If someone is a parent then they are responsible'\n"
            "• 'Who is happy?'"
        )

        if user_input and user_input.strip():
            # Show progress
            self.status_var.set("AI translating...")
            self.root.update()

            def do_translation():
                try:
                    ace_result = self.ai_translator.translate(user_input.strip())
                    if ace_result:
                        # Add to text area
                        self.root.after(0, lambda: self.add_translated_text(ace_result))
                    else:
                        self.root.after(0, lambda: self.status_var.set("Translation failed - try rephrasing"))
                except Exception as e:
                    self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))

            # Run in thread to avoid blocking
            threading.Thread(target=do_translation, daemon=True).start()

    def add_translated_text(self, ace_text):
        """Add translated ACE text to the main text area"""
        # Insert at current cursor position
        current_pos = self.text_input.index(tk.INSERT)

        # Add newline if not at start of line
        if self.text_input.get(f"{current_pos} linestart", current_pos).strip():
            self.text_input.insert(current_pos, "\n")

        # Insert the translated text
        self.text_input.insert(tk.INSERT, ace_text + "\n")

        # Update status
        self.status_var.set(f"Added: {ace_text}")

    def load_csv(self):
        """Load CSV file and convert to ACE facts with LLM-powered mapping"""
        file_path = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if file_path:
            try:
                headers, data = CSVProcessor.load_csv(file_path)

                if not data:
                    messagebox.showwarning("Warning", "CSV file is empty")
                    return

                # Show mapping dialog with sample row
                sample_row = [data[0].get(header, '') for header in headers]

                # Create and show mapping dialog
                mapping_dialog = CSVMappingDialog(self.root, headers, sample_row, self.ai_translator)
                self.root.wait_window(mapping_dialog.dialog)

                # Check if user applied mapping
                if mapping_dialog.result:
                    # Convert using template
                    facts = CSVProcessor.convert_to_ace_facts_with_template(
                        headers, data, mapping_dialog.result
                    )

                    # Add facts to text area
                    current_text = self.text_input.get(1.0, tk.END)
                    if current_text.strip():
                        self.text_input.insert(tk.END, "\n\n# CSV Facts (Template Mapping)\n")
                    else:
                        self.text_input.insert(tk.END, "# CSV Facts (Template Mapping)\n")

                    for fact in facts:
                        self.text_input.insert(tk.END, fact + "\n")

                    self.status_var.set(f"Loaded {len(facts)} facts from CSV with template mapping")
                else:
                    self.status_var.set("CSV import cancelled")

            except Exception as e:
                messagebox.showerror("Error", f"Error loading CSV: {str(e)}")

    def export_file(self):
        """Export current text to file"""
        file_path = filedialog.asksaveasfilename(
            title="Export Statements",
            defaultextension=".ace",
            filetypes=[("ACE files", "*.ace"), ("Text files", "*.txt"), ("All files", "*.*")]
        )

        if file_path:
            try:
                content = self.text_input.get(1.0, tk.END)
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.status_var.set("File exported successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Error exporting: {str(e)}")

    def import_file(self):
        """Import statements from file"""
        file_path = filedialog.askopenfilename(
            title="Import Statements",
            filetypes=[("ACE files", "*.ace"), ("Text files", "*.txt"), ("All files", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

                self.text_input.delete(1.0, tk.END)
                self.text_input.insert(tk.END, content)
                self.status_var.set("File imported successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Error importing: {str(e)}")


def main():
    """Main application entry point"""
    root = tk.Tk()
    root.resizable(True, True)

    app = EnhancedACECalculator(root)

    # Show startup message about APE server
    def show_startup_info():
        if not app.ape_client.available:
            messagebox.showinfo(
                "APE Server Setup Required",
                "The APE (Attempto Parsing Engine) server is not running.\n\n"
                "To enable full functionality:\n"
                "1. Download and compile APE from http://attempto.ifi.uzh.ch\n"
                "2. Start the HTTP server: ./ape.exe -httpserver\n"
                "3. The server will run at http://localhost:8001\n\n"
                "For AI translation assistance, also ensure Ollama is running."
            )

    root.after(1000, show_startup_info)
    root.mainloop()


if __name__ == "__main__":
    main()