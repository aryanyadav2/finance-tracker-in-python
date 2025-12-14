import customtkinter as ctk
import sqlite3, csv
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ACCENT = "#3b82f6"
GREEN = "#22c55e"
RED = "#ef4444"

db = sqlite3.connect("finance.db")
cur = db.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS transactions(
id INTEGER PRIMARY KEY,
amount REAL,
category TEXT,
note TEXT,
date TEXT)
""")
db.commit()

class FinanceApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Personal Finance")
        self.geometry("460x640")
        self.resizable(False, False)

        # Header
        header = ctk.CTkFrame(self, corner_radius=18)
        header.pack(padx=20, pady=15, fill="x")
        ctk.CTkLabel(header, text="Personal Finance",
                     font=("Segoe UI", 26, "bold")).pack(pady=(14, 4))
        self.balance = ctk.CTkLabel(header, font=("Segoe UI", 20))
        self.balance.pack(pady=(0, 14))

        # Input Card
        card = ctk.CTkFrame(self, corner_radius=18)
        card.pack(padx=20, pady=10, fill="x")

        self.amount = ctk.CTkEntry(card, placeholder_text="Amount")
        self.amount.pack(padx=15, pady=(15, 8), fill="x")

        self.category = ctk.CTkEntry(card, placeholder_text="Category")
        self.category.pack(padx=15, pady=8, fill="x")

        self.note = ctk.CTkEntry(card, placeholder_text="Note (optional)")
        self.note.pack(padx=15, pady=8, fill="x")

        btns = ctk.CTkFrame(card, fg_color="transparent")
        btns.pack(pady=12)
        ctk.CTkButton(btns, text="Income", fg_color=GREEN,
                      hover_color="#16a34a",
                      command=lambda: self.add_txn(True)).pack(side="left", padx=8)
        ctk.CTkButton(btns, text="Expense", fg_color=RED,
                      hover_color="#dc2626",
                      command=lambda: self.add_txn(False)).pack(side="left", padx=8)

        # Export
        ctk.CTkButton(self, text="Export CSV",
                      fg_color=ACCENT,
                      hover_color="#2563eb",
                      command=self.export_csv).pack(pady=8)

        # Transactions Card
        feed = ctk.CTkFrame(self, corner_radius=18)
        feed.pack(padx=20, pady=(6, 16), fill="both", expand=True)

        ctk.CTkLabel(feed, text="Transactions",
                     font=("Segoe UI", 18, "bold")).pack(pady=(12, 6))

        self.box = ctk.CTkTextbox(feed, height=260, corner_radius=12)
        self.box.pack(padx=12, pady=(0, 12), fill="both", expand=True)

        self.refresh()

    def add_txn(self, income):
        try:
            amt = float(self.amount.get())
            if not income: amt = -amt
        except:
            return

        cur.execute("INSERT INTO transactions VALUES (NULL,?,?,?,?)",
                    (amt, self.category.get(), self.note.get(),
                     datetime.now().strftime("%d %b %Y")))
        db.commit()

        self.amount.delete(0, "end")
        self.category.delete(0, "end")
        self.note.delete(0, "end")
        self.refresh()

    def refresh(self):
        self.box.delete("1.0", "end")
        cur.execute("SELECT * FROM transactions ORDER BY id DESC")
        rows = cur.fetchall()

        balance = sum(r[1] for r in rows)
        self.balance.configure(text=f"Balance  ₹{balance:.2f}")

        self.box.tag_config("g", foreground=GREEN)
        self.box.tag_config("r", foreground=RED)

        for _, amt, cat, note, date in rows:
            tag = "g" if amt > 0 else "r"
            self.box.insert(
                "end",
                f"{date}   {'+' if amt>0 else '-'}₹{abs(amt)}   {cat}  {note}\n",
                tag
            )

    def export_csv(self):
        with open("transactions.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["Amount", "Category", "Note", "Date"])
            cur.execute("SELECT amount,category,note,date FROM transactions")
            w.writerows(cur.fetchall())

if __name__ == "__main__":
    FinanceApp().mainloop()
