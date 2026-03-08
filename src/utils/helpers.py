from tkinter import filedialog, messagebox

def save_to_file(content: str, default_filename: str):
    """Opens a file dialog to save content to a file."""
    if not content.strip():
        messagebox.showwarning("Warning", "Nothing to save!")
        return None

    filepath = filedialog.asksaveasfilename(
        defaultextension=".pem",
        initialfile=default_filename,
        filetypes=[("PEM Files", "*.pem"), ("All Files", "*.*")]
    )
    if filepath:
        with open(filepath, "w") as f:
            f.write(content)
        return filepath
    return None

def load_from_file():
    """Opens a file dialog to load content from a file."""
    filepath = filedialog.askopenfilename(
        filetypes=[("PEM Files", "*.pem"), ("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if filepath:
        with open(filepath, "rb") as f:
            return f.read(), filepath
    return None, None
