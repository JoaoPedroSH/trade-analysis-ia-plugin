import tkinter as tk
from tkinter import messagebox
import json
from cryptography.fernet import Fernet
from pathlib import Path

CONFIG_DIR = Path(".") / "config"
CONFIG_DIR.mkdir(exist_ok=True)
CONFIG_FILE = CONFIG_DIR / "config.enc"
KEY_FILE = CONFIG_DIR / "key.key"

class SetupApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Configuração Inicial")
        self.setup_widgets()

    def setup_widgets(self):
        tk.Label(self.root, text="User ID:").pack(pady=5)
        self.user_id_entry = tk.Entry(self.root)
        self.user_id_entry.pack(pady=5)

        tk.Label(self.root, text="Token JWT:").pack(pady=5)
        self.token_entry = tk.Entry(self.root)
        self.token_entry.pack(pady=5)

        tk.Button(self.root, text="Salvar", command=self.save_config).pack(pady=10)

    def save_config(self):
        user_id = self.user_id_entry.get()
        token = self.token_entry.get()

        key = Fernet.generate_key()
        cipher = Fernet(key)
        encrypted_data = cipher.encrypt(json.dumps({
            "user_id": user_id,
            "token": token
        }).encode())

        with open(KEY_FILE, "wb") as f:
            f.write(key)
        with open(CONFIG_FILE, "wb") as f:
            f.write(encrypted_data)

        messagebox.showinfo("Sucesso", "Configuração salva!")
        self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SetupApp()
    app.run()
