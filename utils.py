from datetime import datetime, date
from typing import Optional

CATEGORIES = [
    "Food", "Travel", "Groceries", "Utilities", "Rent", "Healthcare",
    "Education", "Entertainment", "Shopping", "Savings", "Other"
]
PAYMENT_METHODS = ["UPI", "Cash", "Card", "NetBanking", "Other"]
DB_FILE = "expenses.db"

def parse_date(s: str) -> Optional[date]:
    try:
        return datetime.strptime(s.strip(), "%Y-%m-%d").date()
    except Exception:
        return None

def today_str() -> str:
    return date.today().strftime("%Y-%m-%d")
