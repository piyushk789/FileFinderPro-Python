# || Name   : Kartikey Baghel
# || Github : https://github.com/piyushk789/Find_by_name-extension
# || Mail   : kartikeybaghel@hotmail.com

# Find by file name-extension.

from tkinter import Tk, ttk, messagebox, filedialog, StringVar
from tkinter import Button, Entry, Label
import json
import os


class BackgroundProcess:

    file_count, folder_count, total_count = 0, 0, 0

    def __init__(self, name, extension, loc):
        self.result = []
        self.H_file = []
        self.H_dir = []
        self.loc = loc
        self.name = name.lower()
        self.extension = extension.lower()

    def find(self, get_folder: str):
        try:
            for word in os.listdir(get_folder):
                locate = f"{get_folder}/{word}".lower()
                if os.path.isfile(locate):
                    loc = locate.split("/")[-1].split(".")[0]
                    if self.name in loc and locate.endswith(self.extension):
                        self.result.append(locate)
                    self.H_file.append(locate)
                    self.file_count += 1
                elif os.path.isdir(locate):
                    self.H_dir.append(locate)
                    self.folder_count += 1
                    self.find(locate)
            else:
                self.total_count += 1
        except Exception as scanErr:
            return print(f"\n\nFind Err\n{scanErr}\n\n")
        else:
            return self.directory

    def directory(self):
        return [f"{data.split('/')[-1]} -> {data}" for data in self.result]

    def start(self):
        return self.find(self.loc)


class DataFetch:
    def __init__(self, master, ext_list):
        self.master = master
        self.fDesign = "times 16"
        self.extension_list = ext_list
        self.loc_entry = Entry()

    def process(self, name, ext, location):
        cls = BackgroundProcess(name, ext, location)
        cls.start()
        value: list = cls.directory()
        if len(value) != 0:
            return intoNotepad(value)
        else:
            return messagebox.showerror("No File Found", "Can't find data with the input")

    def select_file_location(self):
        file_location = filedialog.askdirectory()
        if file_location:
            self.file_loc_btn['bg'] = "#00f000"
            self.loc_var.set(file_location)
        else:
            self.file_loc_btn['bg'] = "SystemButtonFace"
            self.loc_var.set("")

    def screen(self):
        self.master.title("Find File & Folder")
        self.master.geometry("500x300")
        self.master.resizable(False, False)

        self.title_label = Label(
            self.master, font="sans 20", text="Find file by Name and Extension")
        self.title_label.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        self.file_label = Label(
            self.master, font=self.fDesign, text="Finding Name:")
        self.file_label.grid(row=1, column=0, padx=10, pady=10)

        self.file_var = StringVar()
        self.file_entry = Entry(
            self.master, font=self.fDesign, width=22, textvariable=self.file_var)
        self.file_entry.grid(row=1, column=1, padx=10, pady=10)

        self.loc_label = Label(
            self.master, font=self.fDesign, text="Search Folder:")
        self.loc_label.grid(row=2, column=0, padx=10, pady=10)

        self.loc_var = StringVar()
        self.loc_entry = Entry(
            self.master, font=self.fDesign, width=22, textvariable=self.loc_var)
        self.loc_entry.grid(row=2, column=1)

        self.file_loc_btn = Button(
            self.master, text="Browse", command=self.select_file_location)
        self.file_loc_btn.grid(row=2, column=2)

        self.opt_label = Label(
            self.master, font=self.fDesign, text="Extension:")
        self.opt_label.grid(row=3, column=0, padx=10, pady=10)

        self.opt_var = StringVar()
        self.option_box = ttk.Combobox(
            self.master, font=self.fDesign, textvariable=self.opt_var, values=self.extension_list)
        self.option_box.grid(row=3, column=1, padx=10, pady=10)

        self.action_btn = Button(self.master, text="Find", command=lambda: self.process(
            self.file_var.get(), self.opt_var.get(), self.loc_var.get()), font="sans 14")
        self.action_btn.grid(row=4, column=1, padx=10, pady=10, rowspan=2)

        self.master.mainloop()


def intoNotepad(data):
    with open(f"{os.environ['userprofile']}\\Downloads\\contain.txt", "wt") as f:
        for name in data:
            f.write(name+"\n")
    os.startfile(f"{os.environ['userprofile']}\\Downloads\\contain.txt")


def getJSON():
    loc = "Extension-data.json"
    if os.path.exists(loc):
        loads = open(loc)
        data = json.load(loads)
        return [data[i] for i in data][0]
    else:
        return [".doc", ".docx", ".txt", ".pdf", ".xls", ".xlsm", ".xlsx", ".ppt", ".pptx", ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".mp3", ".mp4", ".wav", ".avi", ".mkv", ".zip", ".rar", ".tar", ".7z", ".exe", ".app", ".iso", ".apk", ".htm", ".html", ".css", ".json"]


if __name__ == "__main__":
    ext = getJSON()
    root = Tk()
    app = DataFetch(root, ext)
    app.screen()
