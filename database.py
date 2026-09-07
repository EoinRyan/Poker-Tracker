import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "poker.db")


def get_db():
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database and create tables if they don't exist."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date        TEXT    NOT NULL,
            game_type   TEXT    NOT NULL,
            blinds      TEXT    NOT NULL,
            buy_in      REAL    NOT NULL,
            end_amount  REAL    NOT NULL,
            net         REAL    NOT NULL,
            notes       TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def add_session(date, game_type, blinds, buy_in, end_amount, notes):
    """Insert a new session record."""
    net = end_amount - buy_in
    conn = get_db()
    conn.execute(
        """
        INSERT INTO sessions (date, game_type, blinds, buy_in, end_amount, net, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (date, game_type, blinds, buy_in, end_amount, net, notes),
    )
    conn.commit()
    conn.close()


def get_all_sessions():
    """Return all sessions ordered by date descending."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM sessions ORDER BY date DESC, id DESC"
    ).fetchall()
    conn.close()
    return rows


def delete_session(session_id):
    """Delete a session by ID."""
    conn = get_db()
    conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()


def get_aggregates():
    """Return aggregate stats across all sessions."""
    conn = get_db()
    row = conn.execute(
        """
        SELECT
            COUNT(*)        AS total_sessions,
            COALESCE(SUM(buy_in), 0)      AS total_buy_in,
            COALESCE(SUM(end_amount), 0)  AS total_earned,
            COALESCE(SUM(net), 0)         AS total_net,
            COALESCE(SUM(CASE WHEN net > 0 THEN 1 ELSE 0 END), 0) AS wins
        FROM sessions
        """
    ).fetchone()
    conn.close()
    return row


def get_sessions_for_chart():
    """Return sessions ordered chronologically for the profit chart."""
    conn = get_db()
    rows = conn.execute(
        "SELECT date, net FROM sessions ORDER BY date ASC, id ASC"
    ).fetchall()
    conn.close()
    return rows
