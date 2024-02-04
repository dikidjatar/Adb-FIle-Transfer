import os
import subprocess
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

class ADBFileTransferApp:
    def __init__(self, master):
        self.master = master
        master.title("ADB File Transfer")

        self.home_frame = tk.Frame(master)
        self.home_frame.pack()

        self.is_connected = False;

        self.check_connection()

        self.push_button = tk.Button(self.home_frame, text="Push file to device", command=self.push_file_window)
        self.push_button.pack(pady=10)

        self.pull_button = tk.Button(self.home_frame, text="Pull file from device", command=self.pull_file_window)
        self.pull_button.pack(pady=10)


    def check_connection(self):
        try:
            output = subprocess.check_output(["adb", "devices"]).decode("utf-8")
            if "device" in output:
                parts = output.split()
                devices = sum(1 for part in parts if 'device' in part)
                # exit()
                if devices > 1:
                    self.is_connected = True
                    device_info = output.split('\n')[1].split('\t')
                    device_model = device_info[0]
                    self.connection_label = tk.Label(self.master, text=f"Connected to device ({device_model})", fg="green")
                    self.connection_label.pack()
                else:
                    self.is_connected = False
                    self.connection_label = tk.Label(self.master, text="No device connected", fg="red")
                    self.connection_label.pack()

            else:
                self.is_connected = False
                messagebox.showerror('Error', 'adb not installed!')
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "ADB command not found. Make sure ADB is installed and added to the system PATH.")

    def push_file_window(self):
        if not self.is_connected:
            messagebox.showerror('Error', 'No device connected!')
            return;

        self.push_window = tk.Toplevel(self.master)
        self.push_window.title("Push File to Device")
        self.push_window.geometry('300x200')

        self.select_button = tk.Button(self.push_window, text="Pilih File", command=self.select_file)
        self.select_button.pack(pady=10)

        self.file_label = tk.Label(self.push_window, text="")
        self.file_label.pack()

        self.send_button = tk.Button(self.push_window, text="Send to Device", command=self.send_to_device)
        self.send_button.pack(pady=10)

    def pull_file_window(self):
        if not self.is_connected:
            messagebox.showerror('Error', 'No device connected!')
            return;

        self.pull_window = tk.Toplevel(self.master)
        self.pull_window.title("Pull File from Device")
        self.pull_window.geometry('500x400')

        self.refresh_button = tk.Button(self.pull_window, text="Refresh", command=self.refresh_list)
        self.refresh_button.pack(pady=10)

        self.file_listbox = tk.Listbox(self.pull_window, selectmode=tk.SINGLE, width=80)
        self.file_listbox.pack()

        self.file_listbox.bind("<Double-1>", self.on_double_click)

        self.select_button = tk.Button(self.pull_window, text="Pilih File", command=self.select_file_to_pull)
        self.select_button.pack(pady=10)

        self.selected_file_label = tk.Label(self.pull_window, text="")
        self.selected_file_label.pack()

        self.pull_button = tk.Button(self.pull_window, text="Pull File", command=self.pull_file)
        self.pull_button.pack(pady=10)

        self.refresh_list()

    def refresh_list(self):
        self.file_listbox.delete(0, tk.END)
        adb_output = subprocess.run(["adb", "shell", "ls", "/sdcard"], capture_output=True, text=True).stdout.splitlines()
        for item in adb_output:
            self.file_listbox.insert(tk.END, item)

    def on_double_click(self, event):
        selection = self.file_listbox.curselection()
        if selection:
            index = selection[0]
            filename = self.file_listbox.get(index)
            if not filename.startswith("."):
                # It's a directory, show its content
                directory_content = subprocess.run(["adb", "shell", "ls", "/sdcard/" + filename], capture_output=True, text=True).stdout.splitlines()
                self.file_listbox.delete(0, tk.END)
                for item in directory_content:
                    self.file_listbox.insert(tk.END, item)

    def select_file_to_pull(self):
        selection = self.file_listbox.curselection()
        if selection:
            index = selection[0]
            self.selected_file = self.file_listbox.get(index)
            self.selected_file_label.config(text=self.selected_file)

    def pull_file(self):
        if hasattr(self, "selected_file"):
            save_path = filedialog.askdirectory()
            if save_path:
                subprocess.run(["adb", "pull", "/sdcard/" + self.selected_file, save_path])
                messagebox.showinfo("Berhasil", "File berhasil diterima dari device")
        else:
            messagebox.showerror("Gagal", "Tidak ada file yang dipilih!")

    def select_file(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            self.file_label.config(text=os.path.basename(self.file_path))

    def send_to_device(self):
        if self.file_path:
            destination = "/sdcard/Download/" + os.path.basename(self.file_path)
            subprocess.run(["adb", "push", self.file_path, destination])
            messagebox.showinfo("Berhasil", "File berhasil terkirim ke device")
        else:
            messagebox.showerror("Gagal", "Tidak ada file yang dipilih!")

root = tk.Tk()
root.geometry('400x300')
app = ADBFileTransferApp(root)
root.mainloop()
