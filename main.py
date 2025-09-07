# !/usr/bin/env python3
"""
ACE Logical Inference Calculator with SWI-Prolog Backend
A desktop application implementing Attempto Controlled English for logical reasoning
Uses SWI-Prolog through janus_swi for proper logical inference

INSTALLATION AND SETUP:
1. Install SWI-Prolog:
   - Windows: Download from https://www.swi-prolog.org/download/stable
   - Ubuntu/Debian: sudo apt-get install swi-prolog
   - macOS: brew install swi-prolog

2. Install Python dependencies:
   pip install janus_swi

3. Run the program:
   python ace_calculator_prolog.py

USAGE:
- The Calculator Mode allows quick testing of ACE statements
- The Programming Mode provides a full development environment
- Use proper ACE syntax like "John is a person.", "X is happy if X likes chocolate."
- Queries should end with "?" like "Is John happy?"
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
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
    print("Warning: janus_swi not available. Install with: pip install janus_swi")
    print("Also ensure SWI-Prolog is installed on your system.")


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
    """Simplified Prolog engine using only janus_swi query methods"""

    def __init__(self):
        self.prolog_available = PROLOG_AVAILABLE
        self.facts = []
        self.rules = []
        self.parser = ACEToPrologParser()

        if self.prolog_available:
            try:
                # Test basic functionality
                test_result = list(janus.query("true"))
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
                # Retract common predicates
                predicates_to_clear = [
                    "person(_)",
                    "likes(_, _)",
                    "happy(_)",
                    "has_property(_, _, _)"
                ]

                for pred in predicates_to_clear:
                    try:
                        janus.query_once(f"retractall({pred})")
                    except:
                        pass  # Predicate might not exist

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
                janus.query_once(f"assertz({prolog_fact})")
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
                janus.query_once(f"assertz(({prolog_rule}))")
                print(f"Added rule: {prolog_rule}")
            except Exception as e:
                print(f"Error adding rule {prolog_rule}: {e}")

    def query(self, ace_query: str) -> str:
        """Query the Prolog knowledge base"""
        if not self.prolog_available:
            return "Prolog not available. Please install janus_swi and SWI-Prolog."

        ace_query = ace_query.strip().rstrip('?')

        # Handle "Is X Y?" queries
        if ace_query.lower().startswith('is '):
            query_content = ace_query[3:].strip()
            prolog_query = self.parser._convert_ace_expression_to_prolog(query_content)

            if prolog_query:
                try:
                    # Try the query and check if it succeeds
                    results = list(janus.query(prolog_query))
                    return "Yes" if results else "No"
                except Exception as e:
                    print(f"Error querying {prolog_query}: {e}")
                    return "Error in query"

        # Handle "Who is Y?" queries
        elif ace_query.lower().startswith('who is '):
            property = ace_query[7:].strip().lower()
            try:
                results = list(janus.query(f"{property}(X)"))
                if results:
                    entities = [result['X'] for result in results]
                    return ', '.join([e.title() for e in entities])
                else:
                    return "No one"
            except Exception as e:
                print(f"Error in who query: {e}")
                return "Error in query"

        # Handle "What does X like?" queries
        elif re.match(r'^what does ([a-zA-Z][a-zA-Z0-9_]*) like\??$', ace_query.lower()):
            match = re.match(r'^what does ([a-zA-Z][a-zA-Z0-9_]*) like\??$', ace_query.lower())
            entity = match.group(1)
            try:
                results = list(janus.query(f"likes({entity.lower()}, X)"))
                if results:
                    objects = [result['X'] for result in results]
                    return ', '.join([o.title() for o in objects])
                else:
                    return "Nothing found"
            except Exception as e:
                print(f"Error in what query: {e}")
                return "Error in query"

        return "Cannot answer this type of query"

    def get_all_facts(self) -> List[str]:
        """Get all derived facts from Prolog"""
        if not self.prolog_available:
            return []

        all_facts = []

        try:
            # Get all person facts
            for result in janus.query("person(X)"):
                all_facts.append(f"{result['X'].title()} is a person")

            # Get all happy facts
            for result in janus.query("happy(X)"):
                all_facts.append(f"{result['X'].title()} is happy")

            # Get all likes facts
            for result in janus.query("likes(X, Y)"):
                all_facts.append(f"{result['X'].title()} likes {result['Y']}")

            # Get all property facts
            for result in janus.query("has_property(X, P, V)"):
                all_facts.append(f"{result['X'].title()} has {result['P'].replace('_', '-')} {result['V']}")

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
                    # Clean header and value for ACE format
                    clean_header = header.lower().replace(' ', '-').replace('_', '-')
                    clean_value = value.replace(' ', '-')

                    # Create ACE fact: "Entity-1 has-age 25."
                    if value.isdigit():
                        fact = f"{entity_name} has {clean_header} {value}."
                    else:
                        fact = f"{entity_name} has {clean_header} {clean_value}."

                    facts.append(fact)

        return facts


class ACECalculatorApp:
    """Main application class for the ACE Logical Calculator with Prolog backend"""

    def __init__(self, root):
        self.root = root
        self.root.title("ACE Logical Inference Calculator (Prolog Backend)")
        self.root.geometry("1000x700")

        # Core components
        self.parser = ACEParser()
        self.inference_engine = SimplePrologEngine()

        # Application state
        self.current_facts = []
        self.current_rules = []
        self.current_queries = []

        # Setup UI
        self.setup_ui()

        # Show Prolog status
        if not PROLOG_AVAILABLE:
            messagebox.showwarning("Prolog Not Available",
                                   "janus_swi is not installed. Please install it with:\n"
                                   "pip install janus_swi\n\n"
                                   "Also ensure SWI-Prolog is installed on your system.")

    def setup_ui(self):
        """Setup the user interface"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Calculator mode tab
        self.calculator_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.calculator_frame, text="Calculator Mode")
        self.setup_calculator_ui()

        # Programming mode tab
        self.programming_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.programming_frame, text="Programming Mode")
        self.setup_programming_ui()

        # Status bar
        self.status_var = tk.StringVar()
        status_text = "Ready - Prolog Available" if PROLOG_AVAILABLE else "Ready - Prolog NOT Available"
        self.status_var.set(status_text)
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_calculator_ui(self):
        """Setup calculator mode interface"""
        # Main frame
        main_frame = ttk.Frame(self.calculator_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Input ACE Statements")
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.calc_input = scrolledtext.ScrolledText(input_frame, height=8, width=60)
        self.calc_input.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add example text
        example_text = """# Example ACE statements:
John is a person.
Mary is a person.
John likes chocolate.
X is happy if X likes chocolate.
Is John happy?
Who is happy?
What does John like?"""

        self.calc_input.insert(tk.END, example_text)

        # Buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        ttk.Button(button_frame, text="Process & Run",
                   command=self.process_and_run).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Clear All",
                   command=self.clear_all).pack(side=tk.LEFT, padx=(0, 5))

        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="Results")
        results_frame.pack(fill=tk.BOTH, expand=True)

        self.calc_results = scrolledtext.ScrolledText(results_frame, height=8, state=tk.DISABLED)
        self.calc_results.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def setup_programming_ui(self):
        """Setup programming mode interface"""
        # Main paned window
        paned = ttk.PanedWindow(self.programming_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel - Editor
        left_frame = ttk.LabelFrame(paned, text="ACE Editor")
        paned.add(left_frame, weight=2)

        # Toolbar
        toolbar = ttk.Frame(left_frame)
        toolbar.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(toolbar, text="Load CSV", command=self.load_csv).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Export", command=self.export_knowledge).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Import", command=self.import_knowledge).pack(side=tk.LEFT, padx=(0, 5))

        # Editor
        self.prog_editor = scrolledtext.ScrolledText(left_frame, height=20)
        self.prog_editor.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Right panel - Results and control
        right_frame = ttk.LabelFrame(paned, text="Results & Control")
        paned.add(right_frame, weight=1)

        # Control buttons
        control_frame = ttk.Frame(right_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(control_frame, text="Execute",
                   command=self.execute_programming_mode).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Clear",
                   command=self.clear_programming).pack(side=tk.LEFT, padx=(0, 5))

        # Results display
        self.prog_results = scrolledtext.ScrolledText(right_frame, height=15, state=tk.DISABLED)
        self.prog_results.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    def process_and_run(self):
        """Process ACE statements and run queries"""
        text = self.calc_input.get(1.0, tk.END)
        try:
            statements = self.parser.parse_text(text)

            # Clear previous knowledge
            self.inference_engine.clear()
            self.current_facts = []
            self.current_rules = []
            self.current_queries = []

            # Process statements
            for stmt in statements:
                if stmt.statement_type == 'fact':
                    self.inference_engine.add_fact(stmt.content)
                    self.current_facts.append(stmt)
                elif stmt.statement_type == 'rule':
                    self.inference_engine.add_rule(stmt.content)
                    self.current_rules.append(stmt)
                elif stmt.statement_type == 'query':
                    self.current_queries.append(stmt)

            # Run queries and display results
            results = []
            results.append("=== PROLOG INFERENCE RESULTS ===\n")

            # Show all current facts
            all_facts = self.inference_engine.get_all_facts()
            if all_facts:
                results.append("Current facts in knowledge base:")
                for fact in all_facts:
                    results.append(f"  • {fact}")
                results.append("")

            # Answer queries
            if self.current_queries:
                results.append("Query answers:")
                for query in self.current_queries:
                    answer = self.inference_engine.query(query.content)
                    results.append(f"  Q: {query.content}")
                    results.append(f"  A: {answer}")
                    results.append("")

            # Display results
            self.calc_results.config(state=tk.NORMAL)
            self.calc_results.delete(1.0, tk.END)
            self.calc_results.insert(tk.END, "\n".join(results))
            self.calc_results.config(state=tk.DISABLED)

            self.status_var.set(f"Processed {len(statements)} statements")

        except Exception as e:
            messagebox.showerror("Error", f"Error processing statements: {str(e)}")

    def execute_programming_mode(self):
        """Execute statements in programming mode"""
        text = self.prog_editor.get(1.0, tk.END)
        try:
            statements = self.parser.parse_text(text)

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
            results.append("=== EXECUTION RESULTS ===\n")
            results.append(f"Processed {facts_count} facts and {rules_count} rules\n")

            # Show all current facts
            all_facts = self.inference_engine.get_all_facts()
            if all_facts:
                results.append("Knowledge base contents:")
                for fact in all_facts:
                    results.append(f"  • {fact}")
                results.append("")

            # Answer queries
            if queries:
                results.append("Query results:")
                for query in queries:
                    answer = self.inference_engine.query(query.content)
                    results.append(f"  Q: {query.content}")
                    results.append(f"  A: {answer}")
                    results.append("")

            # Display results
            self.prog_results.config(state=tk.NORMAL)
            self.prog_results.delete(1.0, tk.END)
            self.prog_results.insert(tk.END, "\n".join(results))
            self.prog_results.config(state=tk.DISABLED)

            self.status_var.set("Execution completed")

        except Exception as e:
            messagebox.showerror("Error", f"Error executing: {str(e)}")

    def clear_all(self):
        """Clear all data in calculator mode"""
        self.inference_engine.clear()
        self.calc_results.config(state=tk.NORMAL)
        self.calc_results.delete(1.0, tk.END)
        self.calc_results.config(state=tk.DISABLED)
        self.status_var.set("Cleared all data")

    def clear_programming(self):
        """Clear programming mode"""
        self.inference_engine.clear()
        self.prog_results.config(state=tk.NORMAL)
        self.prog_results.delete(1.0, tk.END)
        self.prog_results.config(state=tk.DISABLED)
        self.status_var.set("Cleared programming mode")

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

                # Add facts to editor
                current_text = self.prog_editor.get(1.0, tk.END)
                if current_text.strip():
                    self.prog_editor.insert(tk.END, "\n\n# CSV Facts\n")
                else:
                    self.prog_editor.insert(tk.END, "# CSV Facts\n")

                for fact in facts:
                    self.prog_editor.insert(tk.END, fact + "\n")

                self.status_var.set(f"Loaded {len(facts)} facts from CSV")

            except Exception as e:
                messagebox.showerror("Error", f"Error loading CSV: {str(e)}")

    def export_knowledge(self):
        """Export current knowledge to file"""
        file_path = filedialog.asksaveasfilename(
            title="Export Knowledge",
            defaultextension=".ace",
            filetypes=[("ACE files", "*.ace"), ("Text files", "*.txt"), ("All files", "*.*")]
        )

        if file_path:
            try:
                content = self.prog_editor.get(1.0, tk.END)
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                self.status_var.set("Knowledge exported successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Error exporting")

    def import_knowledge(self):
        """Import knowledge from file"""
        file_path = filedialog.askopenfilename(
            title="Import Knowledge",
            filetypes=[("ACE files", "*.ace"), ("Text files", "*.txt"), ("All files", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

                self.prog_editor.delete(1.0, tk.END)
                self.prog_editor.insert(tk.END, content)
                self.status_var.set("Knowledge imported successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Error importing: {str(e)}")


def show_installation_help():
    """Show installation help dialog"""
    help_text = """
ACE Logical Inference Calculator - Installation Guide

REQUIREMENTS:
1. Python 3.7 or higher
2. SWI-Prolog
3. janus_swi Python package

INSTALLATION STEPS:

1. Install SWI-Prolog:
   • Windows: Download from https://www.swi-prolog.org/download/stable
   • Ubuntu/Debian: sudo apt-get install swi-prolog
   • macOS: brew install swi-prolog
   • Fedora/CentOS: sudo yum install pl

2. Install Python dependencies:
   pip install janus_swi

3. Verify installation:
   • Open terminal/command prompt
   • Type: swipl --version
   • Should show SWI-Prolog version

4. Run the program:
   python ace_calculator_prolog.py

USAGE EXAMPLES:

Facts:
• John is a person.
• Mary likes chocolate.
• Bob has age 25.

Rules:
• X is happy if X likes chocolate.
• X is adult if X has age Y and Y > 18.

Queries:
• Is John happy?
• Who is happy?
• What does Mary like?

TROUBLESHOOTING:

• If you get "janus_swi not found":
  pip install janus_swi

• If you get "SWI-Prolog not found":
  Make sure SWI-Prolog is installed and in your PATH

• If queries don't work:
  Check that your ACE syntax is correct
    """

    help_window = tk.Toplevel()
    help_window.title("Installation & Usage Help")
    help_window.geometry("600x500")

    text_widget = scrolledtext.ScrolledText(help_window, wrap=tk.WORD)
    text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    text_widget.insert(tk.END, help_text)
    text_widget.config(state=tk.DISABLED)


def main():
    """Main application entry point"""
    root = tk.Tk()

    # Add help menu
    menubar = tk.Menu(root)
    root.config(menu=menubar)

    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=help_menu)
    help_menu.add_command(label="Installation Help", command=show_installation_help)
    help_menu.add_separator()
    help_menu.add_command(label="About", command=lambda: messagebox.showinfo(
        "About",
        "ACE Logical Inference Calculator\n"
        "Version 2.0 with Prolog Backend\n\n"
        "Uses SWI-Prolog through janus_swi for\n"
        "robust logical inference and reasoning.\n\n"
        "Supports Attempto Controlled English\n"
        "for natural language logical statements."
    ))

    app = ACECalculatorApp(root)

    # Show startup message if Prolog is not available
    if not PROLOG_AVAILABLE:
        root.after(1000, lambda: messagebox.showinfo(
            "Setup Required",
            "For full functionality, please install:\n\n"
            "1. SWI-Prolog (https://www.swi-prolog.org/)\n"
            "2. janus_swi: pip install janus_swi\n\n"
            "Click Help → Installation Help for detailed instructions."
        ))

    root.mainloop()


if __name__ == "__main__":
    main()