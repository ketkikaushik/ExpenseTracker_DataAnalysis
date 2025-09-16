import sys, traceback
import tkinter as tk
from tkinter import ttk, messagebox
from app import ExpenseTrackerApp

def main():
    try:
        root = tk.Tk()
        try:
            if sys.platform.startswith("win"):
                ttk.Style().theme_use('vista')
            else:
                ttk.Style().theme_use('clam')
        except Exception:
            pass
        app = ExpenseTrackerApp(root)
        root.geometry("1100x650")
        root.minsize(900, 550)
        root.mainloop()
    except Exception as e:
        traceback.print_exc()
        messagebox.showerror("Fatal Error", str(e))

if __name__ == "__main__":
    main()
