import tkinter as tk
from tkinter import messagebox, simpledialog
import pyotp
import json
import os
import pyperclip

DATA_FILE = "otp_secrets.json"

class AuthenticatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Desktop OTP Manager")
        self.root.geometry("400x550")
        
        self.accounts = self.load_data()
        
        # UI Setup
        self.header = tk.Label(root, text="My Auth Codes", font=("Arial", 16, "bold"), pady=10)
        self.header.pack()

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
        
        tk.Button(self.btn_frame, text="+ Add New Code", command=self.add_account, bg="#4CAF50", fg="white").pack(side="left", padx=20)
        
        self.update_codes()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        return []

    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.accounts, f, indent=4)

    def add_account(self):
        name = simpledialog.askstring("Account Name", "Enter a name (e.g., GitHub):")
        if not name: return
        secret = simpledialog.askstring("Secret Key", "Enter the Base32 Secret Key:").replace(" ", "").upper()
        if not secret: return

        try:
            pyotp.TOTP(secret).now() # Validate secret
            self.accounts.append({"name": name, "secret": secret, "pinned": False})
            self.save_data()
            self.refresh_ui()
        except Exception:
            messagebox.showerror("Error", "Invalid Secret Key format.")

    def delete_account(self, index):
        if messagebox.askyesno("Delete", f"Remove {self.accounts[index]['name']}?"):
            del self.accounts[index]
            self.save_data()
            self.refresh_ui()

    def toggle_pin(self, index):
        self.accounts[index]['pinned'] = not self.accounts[index]['pinned']
        # Sort so pinned are at the top
        self.accounts.sort(key=lambda x: x.get('pinned', False), reverse=True)
        self.save_data()
        self.refresh_ui()

    def copy_code(self, code):
        pyperclip.copy(code)
        # Temporary visual feedback could be added here

    def refresh_ui(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        for i, acc in enumerate(self.accounts):
            frame = tk.Frame(self.list_frame, bd=1, relief="groove", pady=5, padx=5)
            frame.pack(fill="x", pady=2, padx=5)

            # Pin icon/button
            pin_text = "★" if acc.get('pinned') else "☆"
            tk.Button(frame, text=pin_text, command=lambda i=i: self.toggle_pin(i), borderwidth=0).pack(side="left")

            lbl_name = tk.Label(frame, text=acc['name'], font=("Arial", 10, "bold"), width=12, anchor="w")
            lbl_name.pack(side="left", padx=5)

            code = pyotp.TOTP(acc['secret']).now()
            btn_code = tk.Button(frame, text=code, font=("Courier", 12, "bold"), fg="blue", 
                                 command=lambda c=code: self.copy_code(c), width=8)
            btn_code.pack(side="left", padx=10)

            tk.Button(frame, text="🗑", fg="red", command=lambda i=i: self.delete_account(i), borderwidth=0).pack(side="right")

    def update_codes(self):
        # Refresh the codes every 1 second to keep them current
        self.refresh_ui()
        self.root.after(10000, self.update_codes) # Updates every 10 seconds

if __name__ == "__main__":
    root = tk.Tk()
    app = AuthenticatorApp(root)
    root.mainloop()