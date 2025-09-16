import sqlite3
import pandas as pd
from typing import List, Optional, Tuple
from utils import DB_FILE

class ExpenseDB:
    def __init__(self, db_path: str = DB_FILE):
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    amount REAL NOT NULL,
                    payment_method TEXT NOT NULL
                );
                """
            )
            conn.commit()

    def add_expense(self, date_str: str, category: str, description: str, amount: float, payment_method: str):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO expenses (date, category, description, amount, payment_method) VALUES (?,?,?,?,?)",
                (date_str, category, description, amount, payment_method),
            )
            conn.commit()

    def fetch_expenses(self, start_date: Optional[str] = None, end_date: Optional[str] = None,
                        category: Optional[str] = None, payment_method: Optional[str] = None) -> pd.DataFrame:
        query = "SELECT id, date, category, description, amount, payment_method FROM expenses WHERE 1=1"
        params: List = []

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        if category and category != "All":
            query += " AND category = ?"
            params.append(category)
        if payment_method and payment_method != "All":
            query += " AND payment_method = ?"
            params.append(payment_method)
        query += " ORDER BY date ASC, id ASC"

        with self._connect() as conn:
            df = pd.read_sql_query(query, conn, params=params)
        return df

    def delete_expense(self, expense_id: int):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            conn.commit()

    def upsert_many(self, rows: List[Tuple[str, str, str, float, str]]):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.executemany(
                "INSERT INTO expenses (date, category, description, amount, payment_method) VALUES (?,?,?,?,?)",
                rows,
            )
            conn.commit()
