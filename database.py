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

    # Create table with user_id column
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     TEXT,
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

    # Migration: add user_id column to existing databases that predate auth
    existing_cols = [
        row[1]
        for row in cursor.execute("PRAGMA table_info(sessions)").fetchall()
    ]
    if "user_id" not in existing_cols:
        cursor.execute("ALTER TABLE sessions ADD COLUMN user_id TEXT")

    conn.commit()
    conn.close()


def add_session(user_id, date, game_type, blinds, buy_in, end_amount, notes):
    """Insert a new session record scoped to the given user."""
    net = end_amount - buy_in
    conn = get_db()
    conn.execute(
        """
        INSERT INTO sessions (user_id, date, game_type, blinds, buy_in, end_amount, net, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, date, game_type, blinds, buy_in, end_amount, net, notes),
    )
    conn.commit()
    conn.close()


def get_all_sessions(user_id):
    """Return all sessions for the given user, ordered by date descending."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM sessions WHERE user_id = ? ORDER BY date DESC, id DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    return rows


def delete_session(session_id, user_id):
    """Delete a session by ID, scoped to the user to prevent cross-user deletion."""
    conn = get_db()
    conn.execute(
        "DELETE FROM sessions WHERE id = ? AND user_id = ?",
        (session_id, user_id),
    )
    conn.commit()
    conn.close()


def get_aggregates(user_id):
    """Return aggregate stats for the given user."""
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
        WHERE user_id = ?
        """,
        (user_id,),
    ).fetchone()
    conn.close()
    return row


def get_sessions_for_chart(user_id):
    """Return sessions ordered chronologically for the profit chart."""
    conn = get_db()
    rows = conn.execute(
        "SELECT date, net FROM sessions WHERE user_id = ? ORDER BY date ASC, id ASC",
        (user_id,),
    ).fetchall()
    conn.close()
    return rows


def get_previous_blinds(user_id):
    """Return unique blinds from the user's past sessions, most recently used first."""
    conn = get_db()
    rows = conn.execute(
        """
        SELECT blinds
        FROM sessions
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,),
    ).fetchall()
    conn.close()
    seen = set()
    unique = []
    for row in rows:
        if row["blinds"] not in seen:
            seen.add(row["blinds"])
            unique.append(row["blinds"])
    return unique
