import tkinter as tk
from tkinter import messagebox, simpledialog
import pyotp
import json
import os
import sys
import pyperclip

# Keep the editable data file beside the executable when packaged, or beside
# this script when running from source.
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "otp_secrets.json")

class AuthenticatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Desktop OTP Manager")
        self.root.geometry("450x600")
        
        self.accounts = self.load_data()
        
        # UI Setup
        self.header = tk.Label(root, text="My Auth Codes", font=("Arial", 16, "bold"), pady=10)
        self.header.pack()

        # Search Bar (Bonus!)
        search_frame = tk.Frame(root)
        search_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(search_frame, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_ui())
        tk.Entry(search_frame, textvariable=self.search_var).pack(side="left", fill="x", expand=True, padx=5)

        self.scroll_frame = tk.Frame(root)
        self.scroll_frame.pack(fill="both", expand=True, padx=10)

        self.canvas = tk.Canvas(self.scroll_frame)
        self.scrollbar = tk.Scrollbar(self.scroll_frame, orient="vertical", command=self.canvas.yview)
        self.list_frame = tk.Frame(self.canvas)

        self.list_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.list_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Controls
        self.btn_frame = tk.Frame(root, pady=10)
        self.btn_frame.pack(fill="x")
        
        tk.Button(self.btn_frame, text="+ Add New Code", command=self.add_account, bg="#4CAF50", fg="white", padx=10).pack(side="left", padx=20)
        
        self.refresh_ui()
        self.update_timer()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading file: {e}")
        return []

    def save_data(self):
        try:
            with open(DATA_FILE, "w") as f:
                json.dump(self.accounts, f, indent=4)
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save data: {e}")

    def add_account(self):
        name = simpledialog.askstring("Account Name", "Enter a name (e.g., GitHub):")
        if not name: return
        secret = simpledialog.askstring("Secret Key", "Enter the Base32 Secret Key:")
        if not secret: return
        secret = secret.replace(" ", "").upper()

        try:
            pyotp.TOTP(secret).now() # Test if it works
            self.accounts.append({"name": name, "secret": secret, "pinned": False})
            self.save_data()
            self.refresh_ui()
        except Exception:
            messagebox.showerror("Error", "Invalid Secret Key format.")

    def delete_account(self, index_in_master):
        if messagebox.askyesno("Delete", f"Remove {self.accounts[index_in_master]['name']}?"):
            del self.accounts[index_in_master]
            self.save_data()
            self.refresh_ui()

    def toggle_pin(self, index_in_master):
        self.accounts[index_in_master]['pinned'] = not self.accounts[index_in_master]['pinned']
        # Sort: Pinned first, then Alphabetical
        self.accounts.sort(key=lambda x: (not x.get('pinned', False), x['name'].lower()))
        self.save_data()
        self.refresh_ui()

    def copy_code(self, code):
        pyperclip.copy(code)

    def refresh_ui(self):
        # Clear existing widgets
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        search_term = self.search_var.get().lower()

        for i, acc in enumerate(self.accounts):
            # Filtering for search
            if search_term and search_term not in acc['name'].lower():
                continue

            frame = tk.Frame(self.list_frame, bd=1, relief="flat", pady=5, padx=5)
            frame.pack(fill="x", pady=2, padx=5)

            pin_text = "★" if acc.get('pinned') else "☆"
            tk.Button(frame, text=pin_text, command=lambda i=i: self.toggle_pin(i), borderwidth=0, font=("Arial", 12)).pack(side="left")

            lbl_name = tk.Label(frame, text=acc['name'], font=("Arial", 10), width=15, anchor="w")
            lbl_name.pack(side="left", padx=5)

            try:
                code = pyotp.TOTP(acc['secret']).now()
            except:
                code = "ERROR"

            btn_code = tk.Button(frame, text=code, font=("Courier", 12, "bold"), fg="#2196F3", 
                                 command=lambda c=code: self.copy_code(c), width=8, relief="flat", bg="#f0f0f0")
            btn_code.pack(side="left", padx=10)

            tk.Button(frame, text="✕", fg="grey", command=lambda i=i: self.delete_account(i), borderwidth=0).pack(side="right")

    def update_timer(self):
        # Refresh the codes every 30 seconds (standard TOTP window) or just update the UI
        self.refresh_ui()
        # Refresh every 15 seconds to ensure codes stay relatively fresh
        self.root.after(15000, self.update_timer)

if __name__ == "__main__":
    root = tk.Tk()
    app = AuthenticatorApp(root)
    root.mainloop()
