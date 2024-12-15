import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
import json
import re
import sys
import subprocess
import threading
from typing import Dict, List
import os
from ctypes import windll, byref, sizeof, c_int
from pygments import highlight
from pygments.lexers import get_lexer_for_filename
from pygments.formatters import get_formatter_by_name
from pygments.formatters import HtmlFormatter
from html.parser import HTMLParser

WindowName = "FiveM Data Files Editor v2.8.2"


class CodeEditor:
    def __init__(self, root):
        self.root = root
        self.root.title(WindowName)
        self.current_file = None
        self.marked_lines = set()
        self.lb_path = None # stores the Liberty BASIC installation path
        root.iconbitmap(r'C:\Users\peter\Desktop\FiveM_Data_File_Editor\Example_Files\Editor\FDFE.ico')  # FiveM Data File Editor icon


        # Set dark theme colors
        self.colors = {
            'bg': '#1E1E1E',           
            'fg': '#D4D4D4',           
            'select_bg': '#264F78',    
            'line_bg': '#252526',      
            'line_fg': '#858585',      
            'menu_bg': '#333333',      
            'menu_fg': '#CCCCCC',      
            'accent': '#404040'         
        }
        
        # Initialize components
        self.setup_theme()
        self.setup_ui()
        self.setup_menus()
        self.setup_shortcuts()
        self.setup_tags()

        # Configure syntax highlighting
        self.blue_keywords = r'\b(import|for|print|as|fx_version|game|from)\b'
        self.green_keywords = r'\b(client_script|server_script|files)\b|\'.*?\'|\".*?\"|\#.*?(?:\#|$)'
        
    def setup_theme(self):
        """Configure the dark theme for all UI elements"""
        style = ttk.Style()
        style.configure('Dark.TFrame', background=self.colors['bg'])
        style.configure('Dark.TButton', background=self.colors['accent'], foreground=self.colors['fg'])
        style.configure('Dark.TLabel', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('Dark.TEntry', fieldbackground=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('Dark.TNotebook', background=self.colors['bg'])
        style = ttk.Style()
        style.configure('Dark.TRadiobutton',
        background=self.colors['bg'],
        foreground=self.colors['fg']
    )
        self.root.configure(bg=self.colors['bg'])
        try:
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            set_window_attribute = windll.dwmapi.DwmSetWindowAttribute
            get_parent = windll.user32.GetParent
            hwnd = get_parent(self.root.winfo_id())
            rendering_policy = c_int(2)
            value = c_int(1)
            set_window_attribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, byref(value), sizeof(value))
        except:
            pass  # Fallback for non-Windows systems

    def setup_tags(self):
        # Configure basic tags
        self.text_area.tag_configure("keyword", foreground="#569CD6")    # Blue
        self.text_area.tag_configure("string", foreground="#CE9178")     # Orange-red
        self.text_area.tag_configure("comment", foreground="#6A9955")    # Green
        self.text_area.tag_configure("function", foreground="#DCDCAA")   # Yellow
        self.text_area.tag_configure("function2", foreground="#FFDD0D")   # Bright Yellow
        self.text_area.tag_configure("number", foreground="#B5CEA8")     # Light green
    
        # Configure Pygments tags
        pygments_tags = {
            'token_keyword_namespace': '#569CD6',  # Blue
            'token_name_namespace': '#4EC9B0',     # Teal
            'token_string': '#CE9178',             # Orange
            'token_comment': '#6A9955',            # Green
            'token_name': '#D4D4D4'                # Light gray
        }
    
        for tag, color in pygments_tags.items():
            print(f"Configuring tag: {tag} with color: {color}")
            self.text_area.tag_configure(tag, foreground=color)


    def toggle_line_mark(self, event):
        """Toggle line marking when clicking line numbers"""
        # Get clicked line number
        index = self.line_numbers.index(f"@{event.x},{event.y}")
        line = int(float(index))
    
        # Configure marked line appearance if not already done
        self.text_area.tag_configure("marked_line", background="#2d4b6d")
    
        # Toggle the mark
        if line in self.marked_lines:
            self.marked_lines.remove(line)
            self.text_area.tag_remove("marked_line", f"{line}.0", f"{line+1}.0")
        else:
            self.marked_lines.add(line)
            self.text_area.tag_add("marked_line", f"{line}.0", f"{line+1}.0")

    # Add this method to the CodeEditor class
    def on_text_modified(self, event=None):
        """Handle text modifications"""
        if self.text_area.edit_modified():
            # Apply appropriate highlighting based on file type
            if self.current_file and self.current_file.endswith('.bas'):
                self.highlight_syntax()
            else:
                self.apply_pygments_highlighting()
        
            # Update line numbers
            self.update_line_numbers()
        
            # Reset the modified flag
            self.text_area.edit_modified(False)


    def highlight_syntax(self, event=None):
        """Apply syntax highlighting based on file type"""
        # Remove existing tags
        for tag in self.text_area.tag_names():
            if tag != "sel":
                self.text_area.tag_remove(tag, "1.0", tk.END)
    
        content = self.text_area.get("1.0", tk.END)
    
        if self.current_file and self.current_file.endswith('.bas'):
            # Liberty BASIC handling remains unchanged
            patterns = self.syntax_patterns['.bas']
            for pattern_type, pattern in patterns.items():
                tag_name = pattern_type.rstrip('s')
                for match in re.finditer(pattern, content, re.MULTILINE):
                    start = f"1.0+{match.start()}c"
                    end = f"1.0+{match.end()}c"
                    self.text_area.tag_add(tag_name, start, end)
        else:
            try:
                if self.current_file:
                    content = self.text_area.get("1.0", tk.END)
                    lexer = get_lexer_for_filename(self.current_file)
                    tokens = lexer.get_tokens(content)
                
                    pos = "1.0"
                    for ttype, value in tokens:
                        # Skip whitespace tokens
                        if str(ttype) == 'Token.Text' and value.isspace():
                            pos = self.text_area.index(f"{pos}+{len(value)}c")
                            continue
                        # Inside highlight_syntax method, before token mapping:
                        print(f"Found token: {str(ttype)} = '{value}'")  # Debug print

                        # Map token types
                        if str(ttype).startswith('Token.Keyword'):
                            tag = 'token_keyword_namespace'  # Blue
                        elif str(ttype).startswith('Token.Name.Namespace'):
                            tag = 'token_name_namespace'     # Cyan
                        elif str(ttype).startswith('Token.Name.Function'):
                            tag = 'function'                 # Yellow
                        elif str(ttype).startswith('Token.Name.Builtin'):
                            tag = 'token_keyword_namespace'  # Blue (for built-in functions)
                        elif str(ttype).startswith('Token.Literal.String'):
                            tag = 'token_string'             # Orange
                        elif str(ttype).startswith('Token.Comment'):
                            tag = 'token_comment'            # Green
                        elif str(ttype).startswith('Token.Number'):
                            tag = 'number'                   # Light green
                        elif str(ttype) == 'Token.Punctuation':
                            if value in '()':
                                tag = 'function2'             # Yellow for parentheses
                            else:
                                tag = 'token_name'           # Gray for other punctuation like colon
                        else:
                            pos = self.text_area.index(f"{pos}+{len(value)}c")
                            continue
                    
                        print(f"Token: {ttype}, Value: '{value}', Position: {pos}")  # Debug print
                        end_pos = self.text_area.index(f"{pos}+{len(value)}c")
                        self.text_area.tag_add(tag, pos, end_pos)
                        pos = end_pos
                    
            except Exception as e:
                print(f"Highlighting error: {e}")





    def apply_pygments_highlighting(self):
        print("\n--- Starting Pygments Highlighting ---")
        print(f"Current file: {self.current_file}")
    
        if not self.current_file or self.current_file.endswith('.bas'):
            print("Skipping highlighting - no file or Liberty BASIC file")
            return
        
        content = self.text_area.get("1.0", tk.END)
        print(f"Content to highlight: '{content.strip()}'")
    
        try:
            lexer = get_lexer_for_filename(self.current_file)
            tokens = list(lexer.get_tokens(content))
            print(f"Found {len(tokens)} tokens:")
        
            pos = "1.0"
            for token_type, value in tokens:
                end_pos = self.text_area.index(f"{pos}+{len(value)}c")
                tag = str(token_type).lower().replace('.', '_')
                print(f"Token: {token_type}, Value: '{value}', Position: {pos}-{end_pos}")
                self.text_area.tag_add(tag, pos, end_pos)
                pos = end_pos
            
        except Exception as e:
            print(f"Pygments error: {e}")
        print("--- End Highlighting ---\n")



        

        # Syntax Colors For Liberty BASIC
        self.text_area.tag_configure("keyword", foreground="#569CD6")    # Blue
        self.text_area.tag_configure("string", foreground="#CE9178")     # Orange-red
        self.text_area.tag_configure("comment", foreground="#6A9955")    # Green
        self.text_area.tag_configure("function", foreground="#DCDCAA")   # Yellow
        self.text_area.tag_configure("number", foreground="#B5CEA8")     # Light green
        self.text_area.tag_configure("category", foreground="#C586C0")  # Purple color
        self.text_area.tag_configure("handle", foreground="#FF8C00")    # Orange color
        self.text_area.tag_configure("variable", foreground="#00FFFF")  # Cyan color

        # Pygments Syntax Highlighting
        self.text_area.tag_configure("token_keyword_namespace", foreground="#569CD6")
        self.text_area.tag_configure("token_name_namespace", foreground="#4EC9B0")
        self.text_area.tag_configure("token_name", foreground="#D4D4D4")

        # Defines Liberty BASIC Syntax Highlighting

        self.syntax_patterns = {
                '.bas': {
                    'variables': r'[A-Za-z]+\$',                     
                    'categories': r'\[.*?\]',
                    'handles': r'#\w+', 
                    'keywords': r'\b(bmpbutton|BMPBUTTON|MENU|menu|textbox|TEXTBOX|CallDLL|loadbmp|LOADBMP|WindowWidth|WindowHeight|UpperLeftX|UpperLeftY|timer|TIMER|WAIT|wait|Wait|PRINT|print|Print|INPUT|input|Input|IF|if|If|THEN|then|Then|ELSE|else|Else|END|end|End|FOR|for|For|TO|to|To|NEXT|next|Next|GOTO|goto|Goto|GOSUB|gosub|Gosub|RETURN|return|Return|DIM|dim|Dim|LET|let|Let|REM|rem|Rem|OPEN|open|Open|CLOSE|close|Close|READ|read|Read|DATA|data|Data|RESTORE|restore|Restore|CLS|cls|Cls|LOCATE|locate|Locate|COLOR|color|Color|AS|as|As)\b',
                    'functions': r'[A-Za-z_][A-Za-z0-9_]*(?=\s*\()',
                    'strings': r'\".*?\"',
                    'comments': r'\'.*$',
                    'numbers': r'\b\d+\.?\d*\b'
                }
            }
        
        # Colors for pygments
        pygments_tags = {
            'token_keyword_namespace': '#569CD6',  # Blue
            'token_name_namespace': '#4EC9B0',     # Teal
            'token_string': '#CE9178',             # Orange
            'token_comment': '#6A9955',            # Green
            'token_name': '#D4D4D4'                # Light gray
        }
    
        for tag, color in pygments_tags.items():
            print(f"Configuring tag: {tag} with color: {color}")  # Debug print
            self.text_area.tag_configure(tag, foreground=color)

    def on_key_press(self, event=None):
        """Handle key press events"""
        self.update_line_numbers()

    def update_line_numbers(self):
        """Update the line numbers display"""
        lines = self.text_area.get("1.0", tk.END).count("\n")
        line_numbers_text = "\n".join(str(i) for i in range(1, lines + 1))
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", tk.END)
        self.line_numbers.insert("1.0", line_numbers_text)
        self.line_numbers.config(state="disabled")

    def on_click(self, event=None):
        """Handle mouse click events"""
        print(f"Click event at: {event.x}, {event.y}")  # Debug print
        self.update_line_numbers()
        self.text_area.focus_set()
        # Ensure scroll positions stay synced after click
        first = self.text_area.yview()[0]
        self.line_numbers.yview_moveto(first)
        # Get visible lines range instead of resetting
        first_visible = self.text_area.index("@0,0")
        last_visible = self.text_area.index(f"@0,{self.text_area.winfo_height()}")
    
        # Update only visible line numbers
        first_line = int(float(first_visible))
        last_line = int(float(last_visible)) + 1
    
        line_numbers = '\n'.join(str(i) for i in range(first_line, last_line))
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", tk.END)
        self.line_numbers.insert("1.0", line_numbers)
        self.line_numbers.config(state="disabled")
        self.sync_line_numbers()

    def new_file(self):
        """Create a new empty file"""
        self.current_file = None
        self.text_area.delete("1.0", tk.END)
        self.show_language_dialog()
        self.update_line_numbers()
        

    def show_language_dialog(self):
        """Show dialog for selecting file language"""
        lang_window = tk.Toplevel(self.root)
        lang_window.title("Select Language")
        lang_window.geometry("150x200")
        lang_window.configure(bg=self.colors['bg'])
        lang_window.transient(self.root)
    
        button_style = ttk.Style()
        button_style.configure('Dialog.TButton', foreground='#404040')

        # Define supported languages
        languages = [
            ("Python", ".py"),
            ("Lua", ".lua"),
            ("JSON", ".json"),
            ("XML", ".xml"),
            ("Liberty BASIC", ".bas")
        ]
    
        selected_lang = tk.StringVar()
        selected_lang.set(".py")  # Default selection
        # Create radio buttons for each language
        for lang, ext in languages:
            ttk.Radiobutton(
                lang_window,
                text=lang,
                variable=selected_lang,
                value=ext,
                style='Dark.TRadiobutton'
            ).pack(pady=5)
    
        def confirm_selection():
            self.current_file = f"untitled{selected_lang.get()}"
            self.highlight_syntax()  # Changed from apply_pygments_highlighting
            lang_window.destroy()
            TempName = "Untitled" + selected_lang.get()
            WindowName = "FiveM Data Files Editor v2.8.2 - " + TempName
            self.root.title(WindowName)
        ttk.Button(
            lang_window,
            text="Confirm",
            command=confirm_selection,
            style='Dialog.TButton'
        ).pack(pady=10)


    def open_file(self):
        """Open and load a file into the editor"""
        file_types = [
            ('All Supported Files', '*.lua;*.meta;*.xml;*.txt;*.json;*.py;*.bas'),
            ('Lua Files', '*.lua'),
            ('Meta Files', '*.meta'),
            ('XML Files', '*.xml'),
            ('Text Files', '*.txt'),
            ('JSON Files', '*.json'),
            ('Python Files', '*.py'),
            ('Liberty Basic Files', '*.bas')
        ]
        filename = filedialog.askopenfilename(filetypes=file_types)
        if filename:
            self.current_file = filename
            with open(filename, 'r') as file:
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", file.read())
            self.update_line_numbers()
            self.highlight_syntax()
            TempName = filename
            WindowName = "FiveM Deata Files Editor v2.8.2 - " + TempName
            self.root.title(WindowName)



    def save_file(self):
        """Save the current file"""
        if self.current_file:
            with open(self.current_file, 'w') as file:
                file.write(self.text_area.get("1.0", tk.END))
                filename = self.current_file
                TempName = filename
                WindowName = "FiveM Deata Files Editor v2.8.2 - " + TempName
                self.root.title(WindowName)
        else:
            self.save_as()

    def save_as(self):
        """Save the current file with a new name"""
        file_types = [
            ('All Supported Files', '*.lua;*.meta;*.xml;*.txt;*.json;*.py;*.bas'),
            ('Lua Files', '*.lua'),
            ('Meta Files', '*.meta'),
            ('XML Files', '*.xml'),
            ('Text Files', '*.txt'),
            ('JSON Files', '*.json'),
            ('Python Files', '*.py'),
            ('Liberty Basic Files', '*.bas')
        ]
        filename = filedialog.asksaveasfilename(filetypes=file_types)
        if filename:
            self.current_file = filename
            with open(filename, 'w') as file:
                file.write(self.text_area.get("1.0", tk.END))
            self.update_line_numbers()
            self.highlight_syntax()
            TempName = filename
            WindowName = "FiveM Deata Files Editor v2.8.2 - " + TempName
            self.root.title(WindowName)

    def show_find_dialog(self):
        """Create and display the find dialog"""
        self.find_window = tk.Toplevel(self.root)
        self.find_window.title("Find")
        self.find_window.transient(self.root)
        self.find_window.configure(bg=self.colors['bg'])
    

        ttk.Label(self.find_window, text="Find:", style='Dark.TLabel').grid(row=0, column=0, padx=5, pady=5)
        self.find_entry = ttk.Entry(self.find_window, style='Dark.TEntry')
        self.find_entry.grid(row=0, column=1, padx=5, pady=5)

    def find_next(self):
        """Find the next occurrence of search text"""
        search_text = self.find_entry.get()
        current_pos = self.text_area.index(tk.INSERT)
    
        pos = self.text_area.search(search_text, current_pos, tk.END)
        if not pos:
            pos = self.text_area.search(search_text, "1.0", current_pos)
    
        if pos:
            self.text_area.mark_set(tk.INSERT, pos)
            self.text_area.see(pos)
            self.text_area.tag_remove(tk.SEL, "1.0", tk.END)
            self.text_area.tag_add(tk.SEL, pos, f"{pos}+{len(search_text)}c")
            self.text_area.focus_set()

    def show_replace_dialog(self):
        """Create and display the replace dialog"""
        self.replace_window = tk.Toplevel(self.root)
        self.replace_window.title("Replace")
        self.replace_window.transient(self.root)
        self.replace_window.configure(bg=self.colors['bg'])
    
        ttk.Label(self.replace_window, text="Find:", style='Dark.TLabel').grid(row=0, column=0, padx=5, pady=5)
        self.find_entry = ttk.Entry(self.replace_window, style='Dark.TEntry')
        self.find_entry.grid(row=0, column=1, padx=5, pady=5)
    
        ttk.Label(self.replace_window, text="Replace with:", style='Dark.TLabel').grid(row=1, column=0, padx=5, pady=5)
        self.replace_entry = ttk.Entry(self.replace_window, style='Dark.TEntry')
        self.replace_entry.grid(row=1, column=1, padx=5, pady=5)
    
        ttk.Button(self.replace_window, text="Find Next",
                  command=self.find_next, style='Dark.TButton').grid(row=2, column=0, pady=5)
        ttk.Button(self.replace_window, text="Replace",
                  command=self.replace_next, style='Dark.TButton').grid(row=2, column=1, pady=5)

    def replace_next(self):
        """Replace the current selection with replacement text"""
        if tk.SEL in self.text_area.tag_names():
            self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text_area.insert(tk.INSERT, self.replace_entry.get())
        self.find_next()

    def configure_lb_path(self):
        """Configure Liberty BASIC installation path"""
        path = filedialog.askdirectory(
            title="Select Liberty BASIC Installation Directory",
            mustexist=True
        )
        if path:
            exe_path = os.path.join(path, "liberty.exe")
            if os.path.exists(exe_path):
                self.lb_path = exe_path
                messagebox.showinfo("Success", f"Liberty BASIC path set to: {exe_path}")
                return True
            else:
                messagebox.showerror("Error", f"liberty.exe not found in: {path}")
                return False


    def run_liberty_basic_file(self):
        """Open the current file in Liberty BASIC IDE"""
        if not self.current_file:
            messagebox.showwarning("Warning", "Please save the file first")
            return
        
        if not self.current_file.endswith('.bas'):
            messagebox.showwarning("Warning", "Only Liberty BASIC files can be executed")
            return
    
        try:
            subprocess.Popen([self.lb_path, self.current_file])
        except Exception as e:
            messagebox.showerror("Error", f"Error running Liberty BASIC: {str(e)}")

    def run_python_file(self):
        """Execute the current editor contents if Python"""
        if not self.current_file or not self.current_file.endswith('.py'):
            messagebox.showwarning("Warning", "Only Python files can be executed")
            return
        
        # Create output window
        output_window = tk.Toplevel(self.root)
        output_window.title("Python Output")
        output_window.geometry("600x400")
        output_window.configure(bg=self.colors['bg'])

        output_text = ScrolledText(output_window, wrap=tk.WORD,
                                 background=self.colors['bg'],
                                 foreground=self.colors['fg'])
        output_text.pack(fill=tk.BOTH, expand=True)

        def update_output(text, tag=None):
            """Thread-safe output update"""
            output_text.configure(state='normal')
            if tag:
                output_text.insert(tk.END, text, tag)
            else:
                output_text.insert(tk.END, text)
        output_text.configure(state='disabled')
        output_text.see(tk.END)

        

        def run_code():
            try:
                code = self.text_area.get("1.0", tk.END)
                process = subprocess.Popen([sys.executable, '-c', code],
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         universal_newlines=True)
        
                stdout, stderr = process.communicate()
            
                # Use after() to safely update UI from thread
                if stdout:
                    output_window.after(0, update_output, stdout)
                if stderr:
                    output_text.tag_configure("error", foreground="red")
                    output_window.after(0, update_output, f"\nErrors:\n{stderr}", "error")
            
            except Exception as e:
                output_text.tag_configure("error", foreground="red")
                output_window.after(0, update_output, f"\nError executing code: {str(e)}", "error")
        
        threading.Thread(target=run_code, daemon=True).start()



    def run_selection(self):
        """Execute the selected Python code"""
        if not tk.SEL in self.text_area.tag_names():
            messagebox.showwarning("Warning", "No code selected")
            return
        
        selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
    
        # Create temp file and run selected code
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tf:
            tf.write(selected_text)
            temp_file = tf.name
        
        self.current_file = temp_file
        self.run_python_file()

    def new_terminal(self):
        """Create a new terminal tab"""
        # Create output window for terminal
        terminal_window = tk.Toplevel(self.root)
        terminal_window.title("Terminal")
        terminal_window.geometry("600x400")
        terminal_window.configure(bg=self.colors['bg'])
    
        # Create terminal output area
        terminal_output = ScrolledText(terminal_window, wrap=tk.WORD,
                                     background=self.colors['bg'],
                                     foreground=self.colors['fg'],
                                     insertbackground=self.colors['fg'])
        terminal_output.pack(fill=tk.BOTH, expand=True)

    def show_docs(self):
        """Display the documentation window"""
        docs_window = tk.Toplevel(self.root)
        docs_window.title("Documentation")
        docs_window.geometry("800x600")
        docs_window.configure(bg=self.colors['bg'])
    
        docs_text = ScrolledText(docs_window, wrap=tk.WORD,
                               background=self.colors['bg'],
                               foreground=self.colors['fg'])
        docs_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
        docs_content = """
        FiveM Data Files Editor Documentation
    
        Keyboard Shortcuts:
        - Ctrl + N: New File
        - Ctrl + O: Open File
        - Ctrl + S: Save File
        - Ctrl + F: Find
        - Ctrl + H: Replace
    
        Features:
        - Super Lightweight
        - Syntax highlighting for multiple file types
        - Line numbering
        - Dark theme
        - Find and Replace functionality
        - Python code execution
        - Liberty BASIC code execution (WIP)
        - Terminal integration
        """
    
        docs_text.insert("1.0", docs_content)
        docs_text.config(state="disabled")

    def show_about(self):
        """Display information about the editor"""
        about_window = tk.Toplevel(self.root)
        about_window.title("About FiveM Data Files Editor")
        about_window.geometry("400x400")
        about_window.configure(bg=self.colors['bg'])
    
        content_frame = ttk.Frame(about_window, style='Dark.TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
        title_label = ttk.Label(content_frame, 
                               text="FiveM Data Files Editor",
                               style='Dark.TLabel',
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)
    
        version_label = ttk.Label(content_frame,
                                 text="Version 2.4.1",
                                 style='Dark.TLabel')
        version_label.pack()
    
        desc_text = """
        A modern code editor designed specifically
        for FiveM resource development plus.

        Bonus Language Support:
        Python
        Liberty BASIC
    
        Features dark theme, syntax highlighting,
        and integrated terminal functionality.

        NOTE: This software is in BETA - some features 
        do not work as intended yet.

        Questions?
        https://discord.gg/prau4ysZSK
        """
    
        desc_label = ttk.Label(content_frame,
                              text=desc_text,
                              style='Dark.TLabel',
                              justify=tk.CENTER)
        desc_label.pack(pady=20)

    def setup_shortcuts(self):
        """Configure keyboard shortcuts"""
        self.text_area.bind('<Control-s>', lambda e: self.save_file())
        self.text_area.bind('<Control-o>', lambda e: self.open_file())
        self.text_area.bind('<Control-n>', lambda e: self.new_file())
        self.text_area.bind('<Control-f>', lambda e: self.show_find_dialog())
        self.text_area.bind('<Control-h>', lambda e: self.show_replace_dialog())

    def sync_line_numbers(self, *args):
        """Keep line numbers synchronized with text area"""
        # Get visible range
        first = self.text_area.yview()[0]
        last = self.text_area.yview()[1]
    
        # Calculate visible lines
        total_lines = int(float(self.text_area.index("end-1c")))
        first_line = int(first * total_lines)
        last_line = min(int(last * total_lines) + 1, total_lines)
    
        # Update line numbers
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', tk.END)
        line_numbers = '\n'.join(str(i+1) for i in range(first_line, last_line))
        self.line_numbers.insert('1.0', line_numbers)
        self.line_numbers.config(state='disabled')
    
        # Sync scroll position
        self.line_numbers.yview_moveto(first)



    def on_text_change(self, event=None):
        """Handle text changes"""
        if self.current_file and self.current_file.endswith('.bas'):
            self.highlight_syntax()
        else:
            self.apply_pygments_highlighting()


    def setup_ui(self):
        # 1. Create main frame
        self.main_frame = ttk.Frame(self.root, style='Dark.TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 2. Create line numbers
        self.line_numbers = tk.Text(self.main_frame, width=6, padx=3, takefocus=0,
                                   border=0, background=self.colors['line_bg'],
                                   foreground=self.colors['line_fg'],
                                   state='disabled',
                                   font=('Monaco', 11, 'bold'))
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # 3. Create text area
        self.text_area = ScrolledText(self.main_frame, wrap=tk.NONE, undo=True,
                                    background=self.colors['bg'],
                                    foreground=self.colors['fg'],
                                    insertbackground=self.colors['fg'],
                                    selectbackground=self.colors['select_bg'],
                                    selectforeground=self.colors['fg'],
                                    font=('Monaco', 11, 'bold'))
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 4. Get the scrollbar from ScrolledText widget
        self.scrollbar = self.text_area.vbar

        # 5. Configure synchronized scrolling
        self.text_area.config(yscrollcommand=self._sync_scroll)
        self.scrollbar.config(command=self._on_scroll_all)


        # 6. Bind events
        self.text_area.bind('<KeyRelease>', self.highlight_syntax)
        self.text_area.bind('<FocusIn>', self.highlight_syntax)
        self.text_area.bind('<Key>', self.on_key_press)
        self.text_area.bind('<Button-1>', self.on_click)
        self.line_numbers.bind('<Button-1>', self.toggle_line_mark)
        self.text_area.bind('<<Modified>>', self.on_text_modified)
        self.text_area.bind('<MouseWheel>', self._on_mousewheel)
        self.line_numbers.bind('<MouseWheel>', self._on_mousewheel)

    
    def _sync_scroll(self, *args):
        """Synchronize scrolling between text area and line numbers"""
        print(f"Sync scroll called with args: {args}")  # Debug print
        self.line_numbers.yview_moveto(args[0])
        self.scrollbar.set(*args)
        return True

    
    def _on_scroll_all(self, *args):
        """Handle scrollbar movement"""
        print(f"Scroll all called with args: {args}")  # Debug print
        self.text_area.yview(*args)
        self.line_numbers.yview(*args)

    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        delta = int(-1 * (event.delta / 120))
        self.text_area.yview_scroll(delta, "units")
        self.line_numbers.yview_scroll(delta, "units")
        return "break"

    
    def handle_modified(self, event=None):
        """Handle text modifications"""
        if self.text_area.edit_modified():
            if self.current_file and self.current_file.endswith('.bas'):
                self.highlight_syntax()
            else:
                self.apply_pygments_highlighting()
            self.text_area.edit_modified(False)

    def setup_menus(self):
        """Create and configure the menu bar with all menu items"""
        menubar = tk.Menu(self.root, bg=self.colors['menu_bg'], fg=self.colors['menu_fg'])
        
        # Base menu configuration
        menu_config = {
            'bg': self.colors['menu_bg'],
            'fg': self.colors['menu_fg'],
            'activebackground': self.colors['accent'],
            'activeforeground': self.colors['fg'],
            'tearoff': 0
        }
        
        # File Menu
        file_menu = tk.Menu(menubar, **menu_config)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Edit Menu
        edit_menu = tk.Menu(menubar, **menu_config)
        edit_menu.add_command(label="Undo", command=self.text_area.edit_undo)
        edit_menu.add_command(label="Redo", command=self.text_area.edit_redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Find", command=self.show_find_dialog)
        edit_menu.add_command(label="Replace", command=self.show_replace_dialog)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        # Setup advanced menus
        self.setup_advanced_menus(menubar, menu_config)
        
        self.root.config(menu=menubar)
    def setup_advanced_menus(self, menubar, menu_config):
        """Setup VSCode-like advanced menus"""
        # Selection Menu
        selection_menu = tk.Menu(menubar, **menu_config)
        selection_menu.add_command(label="Select All", 
                                 command=lambda: self.text_area.tag_add(tk.SEL, "1.0", tk.END))
        menubar.add_cascade(label="Selection", menu=selection_menu)
        
        # View Menu
        view_menu = tk.Menu(menubar, **menu_config)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Go Menu
        go_menu = tk.Menu(menubar, **menu_config)
        menubar.add_cascade(label="Go", menu=go_menu)
        
        # Run Menu
        run_menu = tk.Menu(menubar, **menu_config)
        run_menu.add_command(label="Run Python File", command=self.run_python_file)
        run_menu.add_command(label="Run Selection (Python Only)", command=self.run_selection)
        run_menu.add_command(label="Configure Liberty BASIC path", command=self.configure_lb_path)
        run_menu.add_command(label="Run Liberty BASIC File (Not Working)", command=self.run_liberty_basic_file)
        menubar.add_cascade(label="Run", menu=run_menu)
        
        # Terminal Menu
        terminal_menu = tk.Menu(menubar, **menu_config)
        terminal_menu.add_command(label="New Terminal", command=self.new_terminal)
        menubar.add_cascade(label="Terminal", menu=terminal_menu)
        
        # Help Menu
        help_menu = tk.Menu(menubar, **menu_config)
        help_menu.add_command(label="Documentation", command=self.show_docs)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

class HTMLtoTk(HTMLParser):
    def __init__(self, text_widget):
        super().__init__()
        self.text = text_widget
        self.current_pos = "1.0"
        
    def handle_starttag(self, tag, attrs):
        if tag == "span":
            for attr, value in attrs:
                if attr == "class":
                    # Convert Pygments class to tag name
                    self.current_class = value
                    
    def handle_data(self, data):
        # Insert text and apply tag
        self.text.insert(self.current_pos, data)
        if hasattr(self, 'current_class'):
            end_pos = self.text.index(f"{self.current_pos}+{len(data)}c")
            self.text.tag_add(self.current_class, self.current_pos, end_pos)
        self.current_pos = self.text.index(f"{self.current_pos}+{len(data)}c")


# Main Entry Point
if __name__ == "__main__":
    root = tk.Tk()
    editor = CodeEditor(root)
    root.geometry("1200x800")
    root.mainloop()



