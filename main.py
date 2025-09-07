#!/usr/bin/env python3
"""
ACE Logical Inference Calculator - Fixed Version
A redesigned desktop application with calculator-like interface for logical reasoning
Combines free-form text input with tagged template insertion
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import csv
import json
import re
from typing import List, Dict, Tuple, Set, Optional
from dataclasses import dataclass
from pathlib import Path

from ace_prolog_parser import ACEToPrologParser

try:
    import janus_swi as janus

    PROLOG_AVAILABLE = True
except ImportError:
    PROLOG_AVAILABLE = False


@dataclass
class ACEStatement:
    """Represents an ACE statement with its type and content"""
    content: str
    statement_type: str  # 'fact', 'rule', 'query'

    def __str__(self):
        return self.content

class ACEParser:
    """Enhanced ACE parser for logical statements"""

    def __init__(self):
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


class SimplePrologEngine:
    """Improved Prolog engine with better error handling"""

    def __init__(self):
        self.prolog_available = PROLOG_AVAILABLE
        self.facts = []
        self.rules = []
        self.parser = ACEToPrologParser() if PROLOG_AVAILABLE else None

        if self.prolog_available:
            try:
                # Test Prolog availability
                list(janus.query("true"))
                print("Prolog engine initialized successfully")
            except Exception as e:
                print(f"Error initializing Prolog: {e}")
                self.prolog_available = False

    def clear(self):
        """Clear all knowledge"""
        self.facts = []
        self.rules = []

        if self.prolog_available:
            try:
                # Clear all dynamic predicates
                predicates_to_clear = [
                    "person(_)", "likes(_, _)", "happy(_)", "has_property(_, _, _)",
                    "sad(_)", "tall(_)", "smart(_)", "young(_)", "old(_)"
                ]
                for pred in predicates_to_clear:
                    try:
                        list(janus.query(f"retractall({pred})"))
                    except:
                        pass
            except Exception as e:
                print(f"Error clearing Prolog knowledge: {e}")

    def add_fact(self, ace_fact: str):
        """Add a fact to the Prolog knowledge base"""
        self.facts.append(ace_fact)
        if not self.prolog_available:
            return

        prolog_fact = self.parser.ace_to_prolog_fact(ace_fact)
        if prolog_fact:
            try:
                # Use query instead of query_once for better error handling
                list(janus.query(f"assertz({prolog_fact})"))
                print(f"Added fact: {prolog_fact}")
            except Exception as e:
                print(f"Error adding fact {prolog_fact}: {e}")

    def add_rule(self, ace_rule: str):
        """Add a rule to the Prolog knowledge base"""
        self.rules.append(ace_rule)
        if not self.prolog_available:
            return

        prolog_rule = self.parser.ace_to_prolog_rule(ace_rule)
        if prolog_rule:
            try:
                # Use query and proper rule syntax
                list(janus.query(f"assertz(({prolog_rule}))"))
                print(f"Added rule: {prolog_rule}")
            except Exception as e:
                print(f"Error adding rule {prolog_rule}: {e}")

    def query(self, ace_query: str) -> str:
        """Query the Prolog knowledge base"""
        if not self.prolog_available:
            return "Prolog not available"

        ace_query = ace_query.strip().rstrip('?')

        try:
            # Is X Y? queries
            if ace_query.lower().startswith('is '):
                query_content = ace_query[3:].strip()

                # Pattern: is X happy
                if re.match(r'^([a-zA-Z][a-zA-Z0-9_]*) ([a-zA-Z][a-zA-Z0-9_]*)', query_content):
                    match = re.match(r'^([a-zA-Z][a-zA-Z0-9_]*) ([a-zA-Z][a-zA-Z0-9_]*)', query_content)
                    entity = self.parser.normalize_entity(match.group(1))
                    property_name = self.parser.normalize_entity(match.group(2))

                    results = list(janus.query(f"{property_name}({entity})"))
                    return "Yes" if results else "No"

            # Who is X? queries
            elif ace_query.lower().startswith('who is '):
                property_name = ace_query[7:].strip().lower()
                property_name = self.parser.normalize_entity(property_name)

                try:
                    results = list(janus.query(f"{property_name}(X)"))
                    if results:
                        entities = [result['X'].title() for result in results]
                        return ', '.join(entities)
                    else:
                        return "No one"
                except Exception:
                    return "Cannot answer this query"

            # What does X like? queries
            elif re.match(r'^what does ([a-zA-Z][a-zA-Z0-9_]*) like', ace_query.lower()):
                match = re.match(r'^what does ([a-zA-Z][a-zA-Z0-9_]*) like', ace_query.lower())
                entity = self.parser.normalize_entity(match.group(1))

                try:
                    results = list(janus.query(f"likes({entity}, X)"))
                    if results:
                        objects = [result['X'].title() for result in results]
                        return ', '.join(objects)
                    else:
                        return "Nothing found"
                except Exception:
                    return "Cannot answer this query"

        except Exception as e:
            print(f"Query error: {e}")
            return f"Error in query: {str(e)}"

        return "Cannot answer this type of query"

    def get_all_facts(self) -> List[str]:
        """Get all derived facts from Prolog"""
        if not self.prolog_available:
            return []

        all_facts = []
        try:
            # Get persons
            for result in janus.query("person(X)"):
                all_facts.append(f"{result['X'].title()} is a person")

            # Get happy entities
            for result in janus.query("happy(X)"):
                all_facts.append(f"{result['X'].title()} is happy")

            # Get likes relationships
            for result in janus.query("likes(X, Y)"):
                all_facts.append(f"{result['X'].title()} likes {result['Y'].title()}")

            # Get properties
            for result in janus.query("has_property(X, P, V)"):
                prop = result['P'].replace('_', ' ')
                all_facts.append(f"{result['X'].title()} has {prop} {result['V']}")

            # Get other properties
            for prop in ['sad', 'tall', 'smart', 'young', 'old']:
                for result in janus.query(f"{prop}(X)"):
                    all_facts.append(f"{result['X'].title()} is {prop}")

        except Exception as e:
            print(f"Error getting facts: {e}")

        return all_facts


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
    def convert_to_ace_facts(headers: List[str], data: List[Dict[str, str]],
                             entity_prefix: str = "Entity") -> List[str]:
        """Convert CSV data to ACE facts"""
        facts = []

        for i, row in enumerate(data):
            entity_name = f"{entity_prefix}-{i + 1}"

            for header in headers:
                value = row.get(header, '').strip()
                if value:
                    clean_header = header.lower().replace(' ', '-').replace('_', '-')
                    clean_value = value.replace(' ', '-')

                    if value.isdigit():
                        fact = f"{entity_name} has {clean_header} {value}."
                    else:
                        fact = f"{entity_name} has {clean_header} {clean_value}."

                    facts.append(fact)

        return facts


class ModernACECalculator:
    """Modern calculator-style ACE interface with hybrid input approach"""

    def __init__(self, root):
        self.root = root
        self.root.title("ACE Logic Calculator - Fixed")
        self.root.geometry("900x800")
        self.root.configure(bg='#2c3e50')

        # Style configuration
        self.setup_styles()

        # Core components
        self.parser = ACEParser()
        self.inference_engine = SimplePrologEngine()

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
        """Setup the modern calculator interface"""
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Create main sections
        self.setup_results_section(main_container)
        self.setup_input_section(main_container)
        self.setup_button_section(main_container)
        self.setup_status_bar(main_container)

    def setup_input_section(self, parent):
        """Setup main text input area"""
        input_frame = tk.Frame(parent, bg=self.colors['card'], relief='raised', bd=2)
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Header
        header_frame = tk.Frame(input_frame, bg=self.colors['card'])
        header_frame.pack(fill=tk.X, padx=15, pady=(15, 10))

        ttk.Label(header_frame, text="Statements", style='Subtitle.TLabel').pack(side=tk.LEFT)

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

        # Add improved example text
        example_text = """John is a person.
Mary is a person.
John likes chocolate.
Mary likes books.
X is happy if X likes chocolate.
X is sad if X likes books.
Is John happy?
Is Mary sad?
Who is happy?
What does John like?"""

        self.text_input.insert(tk.END, example_text)

    def setup_button_section(self, parent):
        """Setup calculator-style button panel"""
        button_panel = tk.Frame(parent, bg=self.colors['card'], relief='raised', bd=2)
        button_panel.pack(fill=tk.X, pady=(0, 15))

        # Button grid container
        grid_container = tk.Frame(button_panel, bg=self.colors['card'])
        grid_container.pack(padx=15, pady=(15, 15))

        # Row 1: Statement types
        self.create_calc_button(grid_container, "FACT",
                                lambda: self.insert_template("<SUBJECT> is <PROPERTY>.\n"),
                                '#27ae60', 0, 0)
        self.create_calc_button(grid_container, "RULE",
                                lambda: self.insert_template("<SUBJECT> is <CONCLUSION> if <CONDITION>.\n"),
                                '#3498db', 0, 1)
        self.create_calc_button(grid_container, "QUERY",
                                lambda: self.insert_template("Is <SUBJECT> <PROPERTY>?\n"),
                                '#f39c12', 0, 2)

        # Row 2: Question templates
        self.create_calc_button(grid_container, "WHO IS ...?",
                                lambda: self.insert_template("Who is <PROPERTY>?\n"),
                                '#e67e22', 1, 0)
        self.create_calc_button(grid_container, "WHAT LIKES ...?",
                                lambda: self.insert_template("What does <SUBJECT> like?\n"),
                                '#e67e22', 1, 1)
        self.create_calc_button(grid_container, "IS ... HAPPY?",
                                lambda: self.insert_template("Is <SUBJECT> happy?\n"),
                                '#e67e22', 1, 2)

        # Row 3: Actions
        self.create_calc_button(grid_container, "EXECUTE ALL", self.execute_statements, '#27ae60', 0, 3, width=15)
        self.create_calc_button(grid_container, "CLEAR", self.clear_all, '#e74c3c', 1, 3, width=15)

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

    def setup_results_section(self, parent):
        """Setup results display"""
        results_frame = tk.Frame(parent, bg=self.colors['card'], relief='raised', bd=2)
        results_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(results_frame, text="Results", style='Subtitle.TLabel').pack(pady=(15, 10))

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

    def setup_status_bar(self, parent):
        """Setup status bar"""
        status_frame = tk.Frame(parent, bg=self.colors['card'], relief='raised', bd=2)
        status_frame.pack(fill=tk.X, pady=(15, 0))

        self.status_var = tk.StringVar()
        status_text = "Ready - Prolog Available" if PROLOG_AVAILABLE else "Ready - Prolog NOT Available"
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

    def execute_statements(self):
        """Execute all statements in the text box"""
        text_content = self.text_input.get(1.0, tk.END)

        try:
            statements = self.parser.parse_text(text_content)

            # Clear previous knowledge
            self.inference_engine.clear()

            # Process statements
            facts_count = 0
            rules_count = 0
            queries = []

            for stmt in statements:
                if stmt.statement_type == 'fact':
                    self.inference_engine.add_fact(stmt.content)
                    facts_count += 1
                elif stmt.statement_type == 'rule':
                    self.inference_engine.add_rule(stmt.content)
                    rules_count += 1
                elif stmt.statement_type == 'query':
                    queries.append(stmt)

            # Prepare results
            results = []
            results.append(f"Processed {facts_count} facts and {rules_count} rules\n")

            # Answer queries
            if queries:
                results.append("Query Results:")
                results.append("-" * 40)
                for query in queries:
                    answer = self.inference_engine.query(query.content)
                    results.append(f"Q: {query.content}")
                    results.append(f"A: {answer}")
                    results.append("")

            # Show all current facts
            all_facts = self.inference_engine.get_all_facts()
            if all_facts:
                results.append("Current Knowledge Base:")
                results.append("-" * 40)
                for fact in all_facts:
                    results.append(f"  • {fact}")
                results.append("")

            # Display results
            self.results_display.config(state=tk.NORMAL)
            self.results_display.delete(1.0, tk.END)
            self.results_display.insert(tk.END, "\n".join(results))
            self.results_display.config(state=tk.DISABLED)

            self.status_var.set(f"Executed {len(statements)} statements successfully")

        except Exception as e:
            messagebox.showerror("Error", f"Error executing statements: {str(e)}")
            self.status_var.set(f"Error: {str(e)}")

    def clear_all(self):
        """Clear everything"""
        self.inference_engine.clear()
        self.results_display.config(state=tk.NORMAL)
        self.results_display.delete(1.0, tk.END)
        self.results_display.config(state=tk.DISABLED)
        self.status_var.set("All data cleared")

    def clear_text(self):
        """Clear only the text input"""
        self.text_input.delete(1.0, tk.END)
        self.status_var.set("Text cleared")

    def load_csv(self):
        """Load CSV file and convert to ACE facts"""
        file_path = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if file_path:
            try:
                headers, data = CSVProcessor.load_csv(file_path)
                facts = CSVProcessor.convert_to_ace_facts(headers, data)

                # Add facts to text area
                current_text = self.text_input.get(1.0, tk.END)
                if current_text.strip():
                    self.text_input.insert(tk.END, "\n\n# CSV Facts\n")
                else:
                    self.text_input.insert(tk.END, "# CSV Facts\n")

                for fact in facts:
                    self.text_input.insert(tk.END, fact + "\n")

                self.status_var.set(f"Loaded {len(facts)} facts from CSV")

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

    app = ModernACECalculator(root)

    # Show startup message if Prolog is not available
    if not PROLOG_AVAILABLE:
        root.after(1000, lambda: messagebox.showinfo(
            "Setup Required",
            "For full functionality, please install:\n\n"
            "1. SWI-Prolog (https://www.swi-prolog.org/)\n"
            "2. janus_swi: pip install janus_swi"
        ))

    root.mainloop()


if __name__ == "__main__":
    main()