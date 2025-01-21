"""
# || Name   : Kartikey Baghel
# || Github : https://github.com/piyushk789/Find_by_name-extension
# || Mail   : kartikeybaghel@hotmail.com
# File Finder Pro
"""
import os
import json
import subprocess
import threading
from customtkinter import CTk, CTkButton as Button, CTkEntry as Entry, CTkLabel as Label, CTkComboBox, CTkScrollableFrame, filedialog, StringVar
from tkinter import messagebox


class BackgroundProcess:
    """Handles the file and folder search operation."""
    file_count = folder_count = total_count = 0

    def __init__(self, name, extension, loc):
        self.loc, self.name, self.extension = loc, name.lower(), extension.lower()
        self.found_files, self.found_folders, self.all_files, self.all_folders = [], [], [], []
        self.directory = None

    def find(self, current_folder):
        """Recursively searches for files and folders matching the criteria."""
        try:
            for item in os.listdir(current_folder):
                path = os.path.join(current_folder, item).lower()
                if os.path.isfile(path) and self.extension != "only_folder":
                    divide = os.path.splitext(item.lower())
                    if self.name in os.path.split(divide[0])[1] and self.extension in divide[1]:
                        self.found_files.append(os.path.abspath(path))
                    self.all_files.append(path)
                    self.file_count += 1
                elif os.path.isdir(path):  # Process directories
                    if self.name in item.lower():
                        self.found_folders.append(path)
                    self.all_folders.append(path)
                    self.folder_count += 1
                    self.find(path)  # Recursive search in subdirectories
            self.total_count += 1
        except Exception as error:
            print(f"Error during search: {error}")
        else:
            results = self.found_files if self.extension != "only_folder" else self.found_folders
            self.directory = [{os.path.split(entry)[1]: entry} for entry in results]
            return self.directory

    def start(self):
        return self.find(self.loc)


def load_json():
    """Loads file extensions from extension.json."""
    if os.path.exists('extension.json'):
        with open('extension.json', "r") as load_ext:
            data = json.load(load_ext).get('ext', [])
            if data:
                return data
    raise ValueError("Cannot load data from extension.json")


class Frontend:
    """Handles the GUI for the file finder."""

    def __init__(self, master):
        self.master = master
        self.master.geometry("435x435")
        self.master.resizable(False, False)
        self.master.title("FileFinder Pro")
        self.search_instance = None
        self.font_style, self.line_color = ("Aptos", 16), "#888"

        try:
            self.extension_options = [_.upper() for _ in load_json()]
            self.extension_options.insert(0, "ONLY_FOLDER")
            self.extension_options.insert(1, "ALL")
        except ValueError:
            self.extension_options = ["ONLY_FOLDER", "ALL", "DOC", "TXT", "PDF", "JPG", "PNG", "MP3", "MP4", "ZIP",
                                      "EXE", "HTML", "CSS", "JSON", "PY", "JS", "C", "CPP", "BAT"]
        except Exception as e:
            messagebox.showerror("Error", f"Cannot load data from extension.json\n\nError: {e}")

        # UI Components
        Label(self.master, font=(self.font_style[0], 24), text="Quick File & Folder Locator").grid(row=0, column=0, padx=10, pady=10, columnspan=3)
        Label(self.master, font=self.font_style, text="File Name").grid(row=1, column=0, padx=10, pady=10)
        self.file_var = StringVar()
        Entry(self.master, font=self.font_style, textvariable=self.file_var).grid(row=1, column=1, padx=10, pady=10)

        self.ext_var = StringVar()
        ls_data = CTkComboBox(self.master, font=self.font_style, variable=self.ext_var, values=self.extension_options)
        ls_data.set('EXE')
        ls_data.grid(row=1, column=2, padx=10, pady=10)

        Label(self.master, font=self.font_style, text="Search Folder").grid(row=2, column=0, padx=10, pady=10)
        self.loc_var = StringVar()
        Entry(self.master, font=self.font_style, width=300, textvariable=self.loc_var).grid(row=2, column=1, columnspan=2)

        # Buttons
        Button(self.master, text="Clear", command=self.show_instructions, font=self.font_style, width=100).grid(row=3, column=0)
        Button(self.master, text="Browse", command=self.select_directory, font=self.font_style).grid(row=3, column=1)
        Button(self.master, text="Find", command=self.start_search, font=self.font_style).grid(row=3, column=2)

        self.divider = Label(self.master, text="-" * 100, text_color=self.line_color)
        self.divider.grid(row=4, column=0, columnspan=3, pady=10)
        self.results_view = CTkScrollableFrame(self.master, width=400, fg_color="#333")
        self.results_view.grid(row=5, column=0, columnspan=3)

    def start_search(self):
        """Starts the file search process."""
        if not self.file_var.get().strip():
            return messagebox.showinfo("Invalid Input", "Enter at least one character to search.")
        if ' ' in self.ext_var.get():
            return messagebox.showinfo("Invalid Extension",
                                       "To search all types, select ALL or enter an extension without spaces!")
        if not os.path.isdir(self.loc_var.get()):
            return messagebox.showinfo("Invalid Directory", "Directory does not exist or is inaccessible!")
        if self.ext_var.get().lower() == "all":
            ext = ''
        else:
            ext = self.ext_var.get().lower()

        self.divider.configure(text="Searching... Please wait.")
        self.clear_results()
        self.search_instance = BackgroundProcess(self.file_var.get(), ext, self.loc_var.get())

        threading.Thread(target=self.run_search, daemon=True).start()

    def run_search(self):
        """Runs the search in a background thread."""
        self.search_instance.start()

        if self.search_instance.directory:
            for entry in self.search_instance.directory:
                for name, path in entry.items():
                    if self.search_instance.extension == "only_folder":
                        self.add_result_button(name, path, True)
                    else:
                        self.add_result_button(name, path)
            self.search_instance.directory.clear()
        else:
            messagebox.showinfo("No Results Found", "No matching files or folders found.")
        self.divider.configure(text="-" * 100)

    def add_result_button(self, name, path, is_folder=False):
        """Adds buttons for found results."""
        button = Button(self.results_view, text=name, fg_color="#444", text_color="white", font=self.font_style)
        if is_folder:
            button.configure(command=lambda: os.startfile(path))
        else:
            button.configure(command=lambda: subprocess.run(fr'explorer /select, "{path}"'))
        button.pack(fill="x", pady=2, padx=2)

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


if __name__ == "__main__":
    root = CTk()
    app = Frontend(root)
    app.show_instructions()
    root.mainloop()
