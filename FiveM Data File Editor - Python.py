import tkinter as tk
from tkinter import filedialog, scrolledtext, Menu

def new_file():
    text_area.delete('1.0', tk.END)

def open_file():
    file_path = filedialog.askopenfilename(filetypes=[
        ("Lua Files", "*.lua"),
        ("JSON Files", "*.json"),
        ("Text Files", "*.txt"),
        ("Meta Files", "*.meta"),
        ("XML Files", "*.xml"),
        ("Python Files", "*.py")
    ])
    if file_path:
        with open(file_path, 'r') as f:
            text_area.delete('1.0', tk.END)
            text_area.insert('1.0', f.read())

def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[
        ("Lua Files", "*.lua"),
        ("JSON Files", "*.json"),
        ("Text Files", "*.txt"),
        ("Meta Files", "*.meta"),
        ("XML Files", "*.xml"),
        ("Python Files", "*.py")
    ])
    if file_path:
        with open(file_path, 'w') as f:
            f.write(text_area.get('1.0', tk.END))

def cut_text():
    text_area.event_generate("<<Cut>>")

def copy_text():
    text_area.event_generate("<<Copy>>")

def paste_text():
    text_area.event_generate("<<Paste>>")

def undo_text():
    text_area.edit_undo()

def redo_text():
    text_area.edit_redo()

def find_text():
    find_dialog = tk.Toplevel()
    find_dialog.title("Find")

    find_label = tk.Label(find_dialog, text="Find:")
    find_label.pack(pady=5)

    find_entry = tk.Entry(find_dialog)
    find_entry.pack(pady=5)

    def find():
        text_area.tag_remove("match", "1.0", tk.END)
        start_pos = "1.0"
        while True:
            start_pos = text_area.search(find_entry.get(), start_pos, tk.END)
            if not start_pos:
                break
            end_pos = f"{start_pos}+{len(find_entry.get())}c"
            text_area.tag_add("match", start_pos, end_pos)
            start_pos = end_pos

    find_button = tk.Button(find_dialog, text="Find Next", command=find)
    find_button.pack(pady=5)

    find_dialog.mainloop()

def replace_text():
    replace_dialog = tk.Toplevel()
    replace_dialog.title("Replace")

    find_label = tk.Label(replace_dialog, text="Find:")
    find_label.pack(pady=5)

    find_entry = tk.Entry(replace_dialog)
    find_entry.pack(pady=5)

    replace_label = tk.Label(replace_dialog, text="Replace with:")
    replace_label.pack(pady=5)

    replace_entry = tk.Entry(replace_dialog)
    replace_entry.pack(pady=5)

    def replace_all():
        text_area.tag_remove("match", "1.0", tk.END)
        start_pos = "1.0"
        while True:
            start_pos = text_area.search(find_entry.get(), start_pos, tk.END)
            if not start_pos:
                break
            end_pos = f"{start_pos}+{len(find_entry.get())}c"
            text_area.tag_add("match", start_pos, end_pos)
            text_area.tag_config("match", background="yellow")
            text_area.replace(start_pos, end_pos, replace_entry.get())
            start_pos = end_pos

    def replace_next():
        text_area.tag_remove("match", "1.0", tk.END)
        start_pos = "1.0"
        start_pos = text_area.search(find_entry.get(), start_pos, tk.END)
        if start_pos:
            end_pos = f"{start_pos}+{len(find_entry.get())}c"
            text_area.tag_add("match", start_pos, end_pos)
            text_area.tag_config("match", background="yellow")
            text_area.replace(start_pos, end_pos, replace_entry.get())
            start_pos = end_pos

    replace_all_button = tk.Button(replace_dialog, text="Replace All", command=replace_all)
    replace_all_button.pack(pady=5)
    replace_next_button = tk.Button(replace_dialog, text="Replace Next", command=replace_next)
    replace_next_button.pack(pady=5)

    replace_dialog.mainloop()

def update_line_numbers():
    line_numbers.delete('1.0', tk.END)
    lines = text_area.get('1.0', tk.END).splitlines()
    for i, line in enumerate(lines):
        line_numbers.insert(tk.END, f"{i+1}\n")

def highlight_keywords():
    keywords = ["import", "as", "from", "def", "with", "root", "fx_version", "game", "data_file", "files"]
    tk_keywords = ["tkinter", "tk", "Tk", "()"]

    text_area.tag_remove("keyword1", "1.0", tk.END)
    text_area.tag_remove("keyword2", "1.0", tk.END)

    text = text_area.get("1.0", tk.END)

    for word in keywords:
        start_pos = text.find(word)
        while start_pos != -1:
            end_pos = start_pos + len(word)
            text_area.tag_add("keyword1", f"1.0+{start_pos}c", f"1.0+{end_pos}c")
            start_pos = text.find(word, end_pos)

    for word in tk_keywords:
        start_pos = text.find(word)
        while start_pos != -1:
            end_pos = start_pos + len(word)
            text_area.tag_add("keyword2", f"1.0+{start_pos}c", f"1.0+{end_pos}c")
            start_pos = text.find(word, end_pos)

    text_area.tag_config("keyword1", foreground="blue")
    text_area.tag_config("keyword2", foreground="light green")

def update_line_numbers_on_scroll(event):
    line_numbers.delete('1.0', tk.END)
    lines = text_area.get('1.0', tk.END).splitlines()
    first_line, last_line = map(int, text_area.yview()[0].split('.'))
    for i in range(first_line, last_line + 1):
        line_numbers.insert(tk.END, f"{i+1}\n")

# Create the main window
root = tk.Tk()
root.title("5M Data File Editor - Python Edition")

# Create the text area
text_area = scrolledtext.ScrolledText(root, width=80, height=10, wrap=tk.WORD)
text_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
text_area.config(background="light gray", foreground="dark green")

# Create a frame for the line numbers
line_number_frame = tk.Frame(root, width=5, bd=1, relief=tk.SUNKEN)
line_number_frame.pack(side=tk.LEFT, fill=tk.Y)

line_numbers = tk.Text(line_number_frame, width=5, height=10, wrap=tk.NONE, padx=7, yscrollcommand=text_area.yview)
line_numbers.pack(side=tk.LEFT, fill=tk.Y)
line_numbers.config(state=tk.DISABLED, background="dark gray", foreground="white")

# Link the scrollbars of the text area and line numbers
text_area.yview_moveto(0)
text_area['yscrollcommand'] = line_numbers.yview
line_numbers['yscrollcommand'] = text_area.yview

# Update line numbers when text area changes
text_area.bind('<KeyRelease>', update_line_numbers)
text_area['yscrollcommand'] = update_line_numbers_on_scroll

# Highlight keywords on initial load
text_area.bind('<KeyRelease>')
highlight_keywords()

# Create the menu bar
menu_bar = tk.Menu(root)

# File menu
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="New", command=new_file)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="Save", command=save_file)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menu_bar.add_cascade(label="File", menu=file_menu)

# Edit menu
edit_menu = tk.Menu(menu_bar, tearoff=0)
edit_menu.add_command(label="Cut", command=cut_text)  

edit_menu.add_command(label="Copy", command=copy_text)
edit_menu.add_command(label="Paste", command=paste_text)  

edit_menu.add_separator()
edit_menu.add_command(label="Undo", command=undo_text)
edit_menu.add_command(label="Redo", command=redo_text)  

edit_menu.add_separator()
edit_menu.add_command(label="Find", command=find_text)
edit_menu.add_command(label="Replace", command=replace_text)
menu_bar.add_cascade(label="Edit", menu=edit_menu)

root.config(menu=menu_bar)

root.mainloop()