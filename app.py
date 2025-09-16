import sys, traceback, os
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.linear_model import Ridge

from db import ExpenseDB
from utils import parse_date, today_str, CATEGORIES, PAYMENT_METHODS, DB_FILE

class ExpenseTrackerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Expense Tracker + Financial Insights")
        self.db = ExpenseDB(DB_FILE)

        self.current_df = pd.DataFrame()
        self._build_ui()
        self._refresh_table()
        # self._refresh_charts()


    def _build_ui(self):
        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill=tk.BOTH, expand=True)

        self.frame_add = ttk.Frame(self.nb, padding=10)
        self.frame_view = ttk.Frame(self.nb, padding=10)
        self.frame_insights = ttk.Frame(self.nb, padding=10)

        self.nb.add(self.frame_add, text="Add Expense")
        self.nb.add(self.frame_view, text="View & Manage")
        self.nb.add(self.frame_insights, text="Insights")

        self._build_add_tab()
        self._build_view_tab()
        # self._build_insights_tab()

    def _build_add_tab(self):
        frm = self.frame_add

        ttk.Label(frm, text="Date (YYYY-MM-DD)").grid(row=0, column=0, sticky="w")
        self.ent_date = ttk.Entry(frm)
        self.ent_date.insert(0, today_str())
        self.ent_date.grid(row=1, column=0, padx=(0, 10), pady=(0, 10))

        ttk.Label(frm, text="Category").grid(row=0, column=1, sticky="w")
        self.cmb_category = ttk.Combobox(frm, values=CATEGORIES, state="readonly")
        self.cmb_category.set(CATEGORIES[0])
        self.cmb_category.grid(row=1, column=1, padx=(0, 10), pady=(0, 10))

        ttk.Label(frm, text="Amount").grid(row=0, column=2, sticky="w")
        self.ent_amount = ttk.Entry(frm)
        self.ent_amount.grid(row=1, column=2, padx=(0, 10), pady=(0, 10))

        ttk.Label(frm, text="Payment Method").grid(row=0, column=3, sticky="w")
        self.cmb_payment = ttk.Combobox(frm, values=PAYMENT_METHODS, state="readonly")
        self.cmb_payment.set(PAYMENT_METHODS[0])
        self.cmb_payment.grid(row=1, column=3, padx=(0, 10), pady=(0, 10))

        ttk.Label(frm, text="Description").grid(row=2, column=0, sticky="w")
        self.ent_desc = ttk.Entry(frm, width=60)
        self.ent_desc.grid(row=3, column=0, columnspan=4, sticky="we", pady=(0, 10))

        btn_add = ttk.Button(frm, text="Add Expense", command=self._on_add_expense)
        btn_add.grid(row=4, column=0, pady=(5, 0), sticky="w")

        frm.columnconfigure(0, weight=1)
        frm.columnconfigure(3, weight=1)

    def _build_view_tab(self):
        frm = self.frame_view

        filters = ttk.Frame(frm)
        filters.pack(fill=tk.X)

        ttk.Label(filters, text="Start Date").grid(row=0, column=0, sticky="w")
        self.f_start = ttk.Entry(filters, width=12)
        self.f_start.grid(row=1, column=0, padx=(0, 10))

        ttk.Label(filters, text="End Date").grid(row=0, column=1, sticky="w")
        self.f_end = ttk.Entry(filters, width=12)
        self.f_end.grid(row=1, column=1, padx=(0, 10))

        ttk.Label(filters, text="Category").grid(row=0, column=2, sticky="w")
        self.f_cat = ttk.Combobox(filters, values=["All"] + CATEGORIES, state="readonly", width=14)
        self.f_cat.set("All")
        self.f_cat.grid(row=1, column=2, padx=(0, 10))

        ttk.Label(filters, text="Payment").grid(row=0, column=3, sticky="w")
        self.f_pay = ttk.Combobox(filters, values=["All"] + PAYMENT_METHODS, state="readonly", width=14)
        self.f_pay.set("All")
        self.f_pay.grid(row=1, column=3, padx=(0, 10))

        ttk.Button(filters, text="Apply Filters", command=self._refresh_table).grid(row=1, column=4, padx=(0, 10))
        ttk.Button(filters, text="Clear Filters", command=self._clear_filters).grid(row=1, column=5)

        self.tree = ttk.Treeview(frm, columns=("id", "date", "category", "description", "amount", "payment"), show="headings", height=12)
        for col, w in zip(["id", "date", "category", "description", "amount", "payment"], [60, 100, 120, 400, 100, 120]):
            self.tree.heading(col, text=col.title())
            self.tree.column(col, width=w, anchor=tk.W)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=8)

        btns = ttk.Frame(frm)
        btns.pack(fill=tk.X)
        ttk.Button(btns, text="Delete Selected", command=self._on_delete_selected).pack(side=tk.LEFT)
        ttk.Button(btns, text="Export CSV", command=self._on_export_csv).pack(side=tk.LEFT, padx=8)
        ttk.Button(btns, text="Import CSV", command=self._on_import_csv).pack(side=tk.LEFT)

    
    def _on_add_expense(self):
        d = self.ent_date.get().strip()
        pdate = parse_date(d)
        if not pdate:
            messagebox.showerror("Invalid date", "Please enter date as YYYY-MM-DD")
            return
        try:
            amount = float(self.ent_amount.get().strip())
        except Exception:
            messagebox.showerror("Invalid amount", "Please enter a valid number for amount")
            return

        if amount <= 0:
            messagebox.showerror("Invalid amount", "Amount must be positive")
            return

        cat = self.cmb_category.get().strip() or "Other"
        pay = self.cmb_payment.get().strip() or "Other"
        desc = self.ent_desc.get().strip()

        try:
            self.db.add_expense(d, cat, desc, amount, pay)
            messagebox.showinfo("Added", "Expense saved successfully")
            self.ent_amount.delete(0, tk.END)
            self.ent_desc.delete(0, tk.END)
            self._refresh_table()
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("DB Error", str(e))

    def _refresh_table(self):
        start = self.f_start.get().strip() if hasattr(self, 'f_start') else None
        end = self.f_end.get().strip() if hasattr(self, 'f_end') else None
        cat = self.f_cat.get().strip() if hasattr(self, 'f_cat') else None
        pay = self.f_pay.get().strip() if hasattr(self, 'f_pay') else None

        for s in [start, end]:
            if s and not parse_date(s):
                messagebox.showerror("Invalid date", "Use YYYY-MM-DD in filters")
                return

        df = self.db.fetch_expenses(start, end, cat, pay)
        self.current_df = df.copy()

        for r in self.tree.get_children():
            self.tree.delete(r)

        for _, row in df.iterrows():
            self.tree.insert("", tk.END, values=(row["id"], row["date"], row["category"], row["description"], f"{row['amount']:.2f}", row["payment_method"]))

    def _clear_filters(self):
        self.f_start.delete(0, tk.END)
        self.f_end.delete(0, tk.END)
        self.f_cat.set("All")
        self.f_pay.set("All")
        self._refresh_table()

    def _on_delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select a row", "Please select a row to delete")
            return
        try:
            item = self.tree.item(sel[0])
            expense_id = int(item["values"][0])
            self.db.delete_expense(expense_id)
            messagebox.showinfo("Deleted", f"Expense #{expense_id} removed")
            self._refresh_table()
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error", str(e))

    def _on_export_csv(self):
        if self.current_df.empty:
            messagebox.showinfo("No data", "No rows to export")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not path:
            return
        try:
            self.current_df.to_csv(path, index=False)
            messagebox.showinfo("Exported", f"Saved to {os.path.basename(path)}")
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Export failed", str(e))

    def _on_import_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not path:
            return
        try:
            df = pd.read_csv(path)
            required = {"date", "category", "description", "amount", "payment_method"}
            if not required.issubset(set(map(str.lower, df.columns))):
                df.columns = [c.lower() for c in df.columns]
                if not required.issubset(df.columns):
                    raise ValueError("CSV must have columns: date, category, description, amount, payment_method")

            df = df[["date", "category", "description", "amount", "payment_method"]].copy()
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
            df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
            df = df.dropna(subset=["date", "amount"])  

            df = df[df["amount"] > 0]

            rows = [
                (
                    str(r.date()),
                    str(row.category) if pd.notna(row.category) else "Other",
                    str(row.description) if pd.notna(row.description) else "",
                    float(row.amount),
                    str(row.payment_method) if pd.notna(row.payment_method) else "Other",
                )
                for (_, row), r in zip(df.iterrows(), pd.to_datetime(df["date"]))
            ]

            if not rows:
                messagebox.showinfo("Nothing to import", "No valid rows found")
                return

            self.db.upsert_many(rows)
            messagebox.showinfo("Imported", f"Imported {len(rows)} rows")
            self._refresh_table()
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Import failed", str(e))

    # def _refresh_charts(self):
    #     df_all = self.db.fetch_expenses()
  
