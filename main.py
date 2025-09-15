#!/usr/bin/env python3
"""
ACE Logical Inference Calculator - Enhanced with IDE Mode and AI Assist
A redesigned desktop application with calculator-like interface for logical reasoning
Combines free-form text input with tagged template insertion
Now includes IDE-like programming mode with file browser and enhanced code editing
Added AI assistance for natural language to ACE translation via Ollama
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog, simpledialog
import csv
import re
import os
import requests
import threading
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

from src.QueryType import QueryType
from src.ace_prolog_parser import ACEToPrologParser

try:
    import janus_swi as janus

    PROLOG_AVAILABLE = True
except ImportError:
    PROLOG_AVAILABLE = False


@dataclass
class ProjectFile:
    """Represents a project file"""
    name: str
    path: str
    content: str = ""
    is_modified: bool = False


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

Convert to ACE format (cut out everything else):"""

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
        # Take first line that looks like ACE
        for line in result.split('\n'):
            line = line.strip().strip('"\'')
            if line and (line.endswith('.') or line.endswith('?')):
                return self._capitalize_names(line)

        # Fallback to first non-empty line
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

        # Basic patterns
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

        prolog_query = self.parser.ace_to_prolog_query(ace_query)
        ace_query = ace_query.strip().rstrip('?')
        query_type = self.parser.parse_query_type(ace_query)

        try:
            # Is X Y? queries
            if query_type is QueryType.IS_X_Y:
                query_content = ace_query[3:].strip()

                # Pattern: is X happy
                if re.match(r'^([a-zA-Z][a-zA-Z0-9_]*) ([a-zA-Z][a-zA-Z0-9_]*)', query_content):
                    results = list(janus.query(prolog_query))
                    return "Yes" if results else "No"

            # Who is X? queries
            elif query_type is QueryType.WHO_IS_X:
                try:
                    results = list(janus.query(prolog_query))
                    if results:
                        entities = [result['X'].title() for result in results]
                        return ', '.join(entities)
                    else:
                        return "No one"
                except Exception:
                    return "Cannot answer this query"

            # What does X like? queries
            elif query_type is QueryType.WHAT_DOES_X_LIKE:
                try:
                    results = list(prolog_query)
                    if results:
                        objects = [result['X'].title() for result in results]
                        return ', '.join(objects)
                    else:
                        return "Nothing found"
                except Exception:
                    return "Cannot answer this query"
            return "Syntax error: query type not recognized"

        except Exception as e:
            print(f"Query error: {e}")
            return f"Error in query: {str(e)}"

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

        self.line_numbers = tk.Text(
            numbers_frame,
            width=4,
            padx=3,
            takefocus=0,
            border=0,
            state='disabled',
            bg='#f0f0f0',
            font=('Consolas', 10)
        )
        self.line_numbers.pack(fill='y', expand=True)

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
        text_widget.bind('<KeyRelease>', lambda e: self.update_line_numbers(text_widget))
        text_widget.bind('<Button-1>', lambda e: self.update_line_numbers(text_widget))
        text_widget.bind('<MouseWheel>', lambda e: self.sync_scroll(text_widget, e))

        # Store references
        tab_frame.text_widget = text_widget
        tab_frame.file_obj = file_obj
        tab_frame.line_numbers = self.line_numbers

        # Add tab to notebook
        tab_name = file_obj.name + ("*" if file_obj.is_modified else "")
        self.notebook.add(tab_frame, text=tab_name)
        self.open_tabs[file_obj.path] = tab_frame

        # Select the new tab
        self.notebook.select(tab_frame)
        self.current_file = file_obj

        # Update line numbers
        self.update_line_numbers(text_widget)

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
            keywords = ['is', 'are', 'if', 'then', 'who', 'what', 'does', 'like', 'has', 'have']
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

    def update_line_numbers(self, text_widget):
        """Update line numbers"""
        if not hasattr(self, 'line_numbers'):
            return

        line_count = int(text_widget.index('end').split('.')[0])

        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', 'end')

        for i in range(1, line_count):
            self.line_numbers.insert('end', f"{i:>3}\n")

        self.line_numbers.config(state='disabled')

    def sync_scroll(self, text_widget, event):
        """Sync scrolling between text and line numbers"""
        if hasattr(self, 'line_numbers'):
            self.line_numbers.yview_scroll(int(-1 * (event.delta / 120)), "units")

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
    """Enhanced ACE Calculator with IDE mode and AI Assist"""

    def __init__(self, root):
        self.root = root
        self.root.title("ACE Logic Calculator")
        self.root.geometry("1200x900")
        self.root.configure(bg='#2c3e50')

        # Mode state
        self.is_ide_mode = False

        # Style configuration
        self.setup_styles()

        # Core components
        self.parser = ACEToPrologParser()
        self.inference_engine = SimplePrologEngine()

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

    def show_ai_assist(self):
        """Show AI assist dialog"""
        user_input = simpledialog.askstring(
            "AI Assistant",
            "Enter natural language statement:\n\n"
            "Examples:\n"
            "• 'John is happy'\n"
            "• 'If someone likes chocolate then they are happy'\n"
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

        # Title
        title_label = ttk.Label(mode_frame, text="ACE Logic Calculator", style='Title.TLabel')
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
        title_label = ttk.Label(mode_frame, text="Programming Mode", style='Title.TLabel')
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

        results_label = ttk.Label(results_frame, text="Results & Output", style='Subtitle.TLabel')
        results_label.pack(pady=(10, 5))

        # Control buttons
        control_frame = tk.Frame(results_frame, bg=self.colors['card'])
        control_frame.pack(fill='x', padx=10, pady=5)

        tk.Button(control_frame, text="▶️ Execute", command=self.execute_ide_code,
                  bg=self.colors['success'], fg='white', font=('Arial', 9, 'bold'),
                  padx=15, pady=5).pack(side='left', padx=5)

        tk.Button(control_frame, text="💾 Save", command=self.save_current_file,
                  bg=self.colors['accent'], fg='white', font=('Arial', 9, 'bold'),
                  padx=15, pady=5).pack(side='left', padx=5)

        tk.Button(control_frame, text="🗑️ Clear Results", command=self.clear_ide_results,
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
            self.root.title("ACE Logic Calculator - Programming Mode")
        else:
            self.setup_calculator_mode()
            self.root.title("ACE Logic Calculator")

    def execute_ide_code(self):
        """Execute code from IDE editor"""
        content = self.code_editor.get_current_content()
        if not content.strip():
            messagebox.showwarning("Warning", "No code to execute")
            return

        try:
            statements = self.parser.parse_text(content)

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
            results.append(f"=== Execution Results ===")
            results.append(f"Processed {facts_count} facts and {rules_count} rules")
            results.append("")

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
            self.ide_results_display.config(state=tk.NORMAL)
            self.ide_results_display.delete(1.0, tk.END)
            self.ide_results_display.insert(tk.END, "\n".join(results))
            self.ide_results_display.config(state=tk.DISABLED)

            # Update status
            if hasattr(self, 'ide_status_var'):
                self.ide_status_var.set(f"Executed {len(statements)} statements successfully")

        except Exception as e:
            messagebox.showerror("Error", f"Error executing code: {str(e)}")
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
        status_text = "Programming Mode Ready - Prolog Available" if PROLOG_AVAILABLE else "IDE Ready - Prolog NOT Available"
        self.ide_status_var.set(status_text)

        status_label = tk.Label(status_frame, textvariable=self.ide_status_var,
                                bg=self.colors['card'], fg=self.colors['text'],
                                font=('Arial', 9), anchor='w')
        status_label.pack(fill=tk.X, padx=10, pady=5)

    # Original calculator mode methods
    def setup_calc_input_section(self, parent):
        """Setup main text input area for calculator mode"""
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

    def setup_calc_button_section(self, parent):
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
        self.create_calc_button(grid_container, "ASSIST", lambda: self.show_ai_assist(), '#e74c3c', 1, 3, width=15)

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

    def setup_calc_status_bar(self, parent):
        """Setup status bar for calculator mode"""
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
        """Execute all statements in the text box (calculator mode)"""
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
        """Clear everything (calculator mode)"""
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

    app = EnhancedACECalculator(root)

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