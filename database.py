"""Database helpers for Smart Expense Tracker.

Local development uses SQLite. For a deployed multi-user app, configure
DATABASE_URL to a PostgreSQL connection string (for example Supabase).
"""
import os
import sqlite3
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path(__file__).resolve().parent / "data" / "expenses.db"
def _database_url():
    value = os.getenv("DATABASE_URL", "").strip()
    if value:
        return value
    try:
        import streamlit as st
        return str(st.secrets.get("DATABASE_URL", "")).strip()
    except Exception:
        return ""


@contextmanager
def get_connection():
    database_url = _database_url()
    if database_url:
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError as exc:
            raise RuntimeError("Install psycopg[binary] to use PostgreSQL.") from exc
        conn = psycopg.connect(database_url, row_factory=dict_row)
        try:
            yield conn, True
        finally:
            conn.close()
    else:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        try:
            yield conn, False
        finally:
            conn.close()

def _sql(sql, postgres):
    return sql.replace("?", "%s") if postgres else sql

def initialize_database():
    with get_connection() as (conn, postgres):
        if postgres:
            conn.execute("""CREATE TABLE IF NOT EXISTS expenses (
                id BIGSERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                amount DOUBLE PRECISION NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                expense_date TEXT NOT NULL
            )""")
            conn.execute("CREATE INDEX IF NOT EXISTS expenses_user_id_idx ON expenses(user_id)")
        else:
            conn.execute("""CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL DEFAULT 'local-user',
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                expense_date TEXT NOT NULL
            )""")
            # Upgrade a database created by the original single-user version.
            cols = [r["name"] for r in conn.execute("PRAGMA table_info(expenses)").fetchall()]
            if "user_id" not in cols:
                conn.execute("ALTER TABLE expenses ADD COLUMN user_id TEXT NOT NULL DEFAULT 'local-user'")
        conn.commit()

def add_expense(user_id, amount, category, description, expense_date):
    with get_connection() as (conn, pg):
        conn.execute(_sql("INSERT INTO expenses (user_id, amount, category, description, expense_date) VALUES (?, ?, ?, ?, ?)", pg), (user_id, amount, category, description, expense_date))
        conn.commit()

def get_expenses(user_id):
    with get_connection() as (conn, pg):
        rows = conn.execute(_sql("SELECT id, amount, category, description, expense_date FROM expenses WHERE user_id = ? ORDER BY expense_date DESC, id DESC", pg), (user_id,)).fetchall()
        if pg:
            return [(r["id"], r["amount"], r["category"], r["description"], r["expense_date"]) for r in rows]
        return [tuple(r) for r in rows]

def update_expense(user_id, expense_id, amount, category, description, expense_date):
    with get_connection() as (conn, pg):
        conn.execute(_sql("UPDATE expenses SET amount = ?, category = ?, description = ?, expense_date = ? WHERE id = ? AND user_id = ?", pg), (amount, category, description, expense_date, expense_id, user_id))
        conn.commit()

def delete_expense(user_id, expense_id):
    with get_connection() as (conn, pg):
        conn.execute(_sql("DELETE FROM expenses WHERE id = ? AND user_id = ?", pg), (expense_id, user_id))
        conn.commit()

def delete_expenses(user_id, expense_ids):
    if not expense_ids:
        return
    with get_connection() as (conn, pg):
        placeholders = ",".join(["%s" if pg else "?"] * len(expense_ids))
        sql = f"DELETE FROM expenses WHERE user_id = ? AND id IN ({placeholders})"
        params = [user_id, *[int(i) for i in expense_ids]]
        conn.execute(_sql(sql, pg), params)
        conn.commit()

def clear_expenses(user_id):
    with get_connection() as (conn, pg):
        conn.execute(_sql("DELETE FROM expenses WHERE user_id = ?", pg), (user_id,))
        conn.commit()
