import os
import json
import time
import subprocess
import threading
from PIL import Image
from customtkinter import (CTk, CTkButton as Button, CTkEntry as Entry, CTkLabel as Label, CTkComboBox, CTkCheckBox,
                           CTkScrollableFrame, filedialog, StringVar, CTkProgressBar, CTkImage)
from tkinter import messagebox

def load_json():
    """Loads file extensions from extension.json."""
    if os.path.exists('extension.json'):
        with open('extension.json', "r") as load_ext:
            data = json.load(load_ext).get('ext', [])
            if data:
                return data
    raise ValueError("Cannot load data from extension.json")

def load_theme(moder: str = "read"):
    if os.path.exists('additional.json'):
        match moder:
            case "read":
                with open('additional.json', "r") as load_thm:
                    return True if json.load(load_thm)['theme'] == 'dark' else False
            case "write":
                with open('additional.json', "r") as read_t:
                    read_theme = json.load(read_t)
                    read_theme["theme"] = "light" if read_theme['theme'] == "dark" else "dark"
                with open('additional.json', "w+") as load_thm:
                    load_thm.write(json.dumps(read_theme, indent=4))
                return load_theme()
            case _:
                return None
    else:
        with open("additional.json", "w+") as write_thm:
            write_thm.write(json.dumps({"name": "Kartikey Baghel", "theme": "dark"}, indent=4))
            return load_theme()

class BackgroundProcess:
    """Handles the file and folder search operation."""

    def __init__(self, name, extensions, loc, case_sensitive=False):
        self.loc = loc
        self.name = name if case_sensitive else name.lower()
        self.extensions = extensions if case_sensitive else [ext.lower() for ext in extensions]
        self.case_sensitive = case_sensitive
        self.found_files, self.found_folders = [], []
        self.all_files, self.all_folders = [], []
        self.directory = None
        self.cancelled = False
        self.total_size = 0

    def find(self, current_folder):
        """Recursively searches for files and folders matching the criteria."""
        if self.cancelled:
            return

        try:
            for item in os.listdir(current_folder):
                if self.cancelled:
                    return

                path = os.path.join(current_folder, item)
                search_item = item if self.case_sensitive else item.lower()

                if os.path.isfile(path) and "only_folder" not in self.extensions:
                    divide = os.path.splitext(search_item)
                    if self.name in os.path.split(divide[0])[1]:
                        if not self.extensions or any(ext in divide[1] for ext in self.extensions):
                            self.found_files.append((path, os.path.getsize(path), time.ctime(os.path.getmtime(path))))
                            self.total_size += os.path.getsize(path)
                    self.all_files.append(path)
                elif os.path.isdir(path):
                    if self.name in search_item:
                        self.found_folders.append((path, 0, time.ctime(os.path.getmtime(path))))
                    self.all_folders.append(path)
                    self.find(path)
        except Exception as error:
            print(f"Error during search: {error}")

    def start(self):
        """Starts the search process."""
        self.find(self.loc)
        if "only_folder" in self.extensions:
            results = self.found_folders
        else:
            results = self.found_files
        self.directory = [{os.path.split(entry[0])[1]: entry} for entry in results]
        return self.directory

    def cancel(self):
        """Cancels the ongoing search."""
        self.cancelled = True


class Frontend:
    """Handles the GUI for the file finder."""

    def __init__(self, master: CTk):
        self.info_text = None
        self.search_instance = None
        self.master = master
        # self.master.geometry("600x600")
        self.master.resizable(False, False)
        self.master.title(f"File Finder Pro")
        self.font_style = ("Aptos", 16 * -1)
        self.light_color = "#ebebeb"
        self.dark_color = "#242424"

        try:
            self.extension_options = [_.upper() for _ in load_json()]
            self.extension_options.insert(0, "ONLY_FOLDER")
            self.extension_options.insert(1, "ALL")
        except ValueError:
            self.extension_options = ["ONLY_FOLDER", "ALL", "DOC", "TXT", "PDF", "JPG", "PNG", "MP3", "MP4", "ZIP",
                                      "EXE", "HTML", "CSS", "JSON", "PY", "JS", "C", "CPP", "BAT"]

        # UI Components
        self.title = Label(self.master, font=("Aptos", 24), text="File & Folder Locator")
        self.title.grid(row=0, column=0, padx=10, pady=10, columnspan=4)
        self.theme = Button(self.master, font=("Aptos", 24), text="", width=10, command=self.swapping, corner_radius=10)
        self.theme.grid(row=0, column=3, padx=10, pady=10, sticky="E")

        self.file_var = StringVar()
        self.ext_var = StringVar()
        self.loc_var = StringVar()

        self.file_label = Label(self.master, font=self.font_style, text="File Name ")
        self.file_label.grid(row=1, column=0, padx=20, pady=5, sticky="E")
        self.file_entry = Entry(self.master, font=self.font_style, textvariable=self.file_var, width=280)
        self.file_entry.grid(row=1, column=1, columnspan=2, pady=5, sticky="E")

        self.ext_combo = CTkComboBox(self.master, font=self.font_style, variable=self.ext_var,
                                     values=self.extension_options, justify="center", width=130)
        self.ext_combo.set('ALL')
        self.ext_combo.grid(row=1, column=3, padx=5, pady=5, sticky="W")

        self.search_label = Label(self.master, font=self.font_style, text="Search Folder")
        self.search_label.grid(row=2, column=0, padx=10, pady=5, sticky="W")
        self.search_entry = Entry(self.master, font=self.font_style, width=410, textvariable=self.loc_var)
        self.search_entry.grid(row=2, column=1, columnspan=3, sticky="W")

        # Additional Controls
        self.is_case = CTkCheckBox(self.master, text="Case\nSensitive", font=("Aptos", 12))
        self.is_case.grid(row=3, column=0, pady=5, sticky="E")

        # Buttons
        # Button(self.master, text="Instructions", command=self.show_instructions, font=self.font_style).grid(row=4, column=0, pady=5)
        self.browse = Button(self.master, text="Browse", command=self.select_directory, font=self.font_style, width=100)
        self.browse.grid(row=3, column=1, padx=5, pady=5, sticky="W")
        self.start_btn = Button(self.master, text="Find", command=self.start_search, font=self.font_style, width=100)
        self.start_btn.grid(row=3, column=2, padx=5, pady=5, sticky="W")
        self.saving = Button(self.master, text="Save", command=self.save_results, font=self.font_style, width=100)
        self.saving.grid(row=3, column=3, padx=10, pady=5, sticky="W")

        self.divider = Label(self.master, text="-" * 125, text_color="#888")
        self.divider.grid(row=5, column=0, columnspan=4, pady=5)

        self.results_view = CTkScrollableFrame(self.master, width=500, height=300, fg_color=self.dark_color,
                                               border_width=1)
        self.results_view.grid(row=6, column=0, columnspan=4, padx=10, pady=5)

        self.progress = CTkProgressBar(self.master, width=525, height=10, border_width=2)
        self.progress.grid(row=7, column=0, columnspan=4, pady=5)
        self.progress.set(0)
        # self.change_theme()

        self.master.bind("<Return>", self.event_handling)
        self.master.bind("<Escape>", self.event_handling)

    def event_handling(self, event):
        if event.keysym == "Return" and self.start_btn._text == "Find": self.start_search()
        if event.keysym == "Escape" and self.start_btn._text == "Cancel": self.cancel_search()


    def change_theme(self):
        mode = self.master._get_appearance_mode()
        new_mode, img_file, fg, bg, text, border = (
            ("dark", "moon.png", self.light_color, self.dark_color, self.light_color, self.dark_color)
            if mode == "light" else
            ("light", "sun.png", self.dark_color, self.light_color, self.dark_color, self.light_color))

        self.master._set_appearance_mode(new_mode)
        icon_image = CTkImage(light_image=Image.open(img_file).resize((50, 50)))
        self.theme.configure(fg_color=fg, image=icon_image, bg_color=bg, hover_color=fg)

        buttons = [self.file_entry, self.ext_combo, self.search_entry, self.browse, self.start_btn,
                   self.saving]  # , self.info_text]
        labels = [self.title, self.file_label, self.search_label, self.divider]
        extra = [self.results_view, self.progress]

        for widget in buttons:
            widget.configure(fg_color=fg, text_color=bg, bg_color=bg)
        for widget in labels:
            widget.configure(fg_color=bg, text_color=fg, bg_color=fg)
        for widget in extra:
            widget.configure(bg_color=bg, fg_color=bg, border_color=fg)
        self.is_case.configure(text_color=fg, bg_color=bg)
        try:
            self.info_text.configure(bg_color=fg, fg_color=bg, text_color=fg)
        except:
            pass

    def swapping(self):
        load_theme("write")
        self.change_theme()


    def start_search(self):
        """Starts the file search process."""
        if not self.file_var.get().strip():
            return messagebox.showinfo("Invalid Input", "Enter at least one character to search.")
        if not os.path.isdir(self.loc_var.get()):
            return messagebox.showinfo("Invalid Directory", "Directory does not exist or is inaccessible!")

        extensions = [self.ext_var.get().lower()] if self.ext_var.get().lower() != "all" else []
        self.divider.configure(text="Searching... Please wait.")
        self.clear_results()
        self.start_btn.configure(command=self.cancel_search, text="Cancel")
        self.search_instance = BackgroundProcess(self.file_var.get(), extensions, self.loc_var.get(), self.is_case.get())
        self.progress.set(0)

        threading.Thread(target=self.run_search, daemon=True).start()

    def run_search(self):
        """Runs the search in a background thread with progress."""
        self.search_instance.start()

        if self.search_instance.directory:
            total_items = len(self.search_instance.directory)
            for i, entry in enumerate(self.search_instance.directory):
                if self.search_instance.cancelled:
                    break
                for name, (path, size, timestamp) in entry.items():
                    self.add_result_button(name, path, size, "only_folder" in self.search_instance.extensions)
                self.progress.set((i + 1) / total_items)

            if not self.search_instance.cancelled:
                self.divider.configure(
                    text=f"Found {total_items} items - Total size: {self.format_size(self.search_instance.total_size)}")
            else:
                self.divider.configure(text="Search cancelled")
        else:
            messagebox.showinfo("No Results Found", "No matching files or folders found.")
            self.divider.configure(text="-" * 125)

        self.start_btn.configure(command=self.start_search, text="Find")
        self.progress.set(1)

    def add_result_button(self, name, path, size, is_folder=False):
        """Adds buttons for found results with additional info."""
        text = f"{name} - ({self.format_size(size)})"
        button = Button(self.results_view, text=text, fg_color="#444", text_color="white", font=self.font_style)
        if is_folder:
            button.configure(command=lambda: os.startfile(path))
        else:
            path = os.path.abspath(path)
            button.configure(command=lambda: subprocess.run([fr"explorer", "/select,", path]))
        button.pack(fill="x", pady=2, padx=2)

    # """Shows a simple file preview."""

    def select_directory(self):
        """Opens a dialog to select a directory."""
        self.loc_var.set(filedialog.askdirectory())

    def clear_results(self):
        """Clears previous search results."""
        for widget in self.results_view.winfo_children():
            widget.destroy()

    def show_instructions(self):
        """Displays usage instructions."""
        self.clear_results()
        self.info_text = Label(self.results_view, text="Enter a file name and select an extension or ALL\n"
            "Choose a directory and click Find\nUse Case Sensitive option for exact matches", font=self.font_style)
        self.info_text.pack()

    def cancel_search(self):
        """Cancels the current search."""
        if self.search_instance:
            self.search_instance.cancel()

    def save_results(self):
        """Saves search results to a file."""
        if not self.search_instance or not self.search_instance.directory:
            return messagebox.showinfo("No Results", "Nothing to save!")

        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                for entry in self.search_instance.directory:
                    for name, (path, size, timestamp) in entry.items():
                        f.write(f"{name} | {path} | {self.format_size(size)} | {timestamp}\n")
            messagebox.showinfo("Success", "Results saved successfully!")

    @staticmethod
    def format_size(size):
        """Formats file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024


if __name__ == "__main__":
    root = CTk()
    app = Frontend(root)
    app.show_instructions()
    is_dark = load_theme()
    app.change_theme() if is_dark else None
    app.change_theme()
    root.mainloop()

