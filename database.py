"""
Database layer – uses Supabase (PostgreSQL) instead of SQLite.
All functions are scoped to a user_id for multi-tenant safety.
"""

from supabase_client import supabase


# ── Write Operations ──────────────────────────────────────────

def add_session(user_id, date, game_type, blinds, buy_in, end_amount, notes):
    """Insert a new session record scoped to the given user."""
    net = end_amount - buy_in
    supabase.table("sessions").insert({
        "user_id": user_id,
        "date": date,
        "game_type": game_type,
        "blinds": blinds,
        "buy_in": buy_in,
        "end_amount": end_amount,
        "net": net,
        "notes": notes,
    }).execute()


def delete_session(session_id, user_id):
    """Delete a session by ID, scoped to the user to prevent cross-user deletion."""
    supabase.table("sessions") \
        .delete() \
        .eq("id", session_id) \
        .eq("user_id", user_id) \
        .execute()


# ── Read Operations ───────────────────────────────────────────

def get_all_sessions(user_id):
    """Return all sessions for the given user, ordered by date descending."""
    result = supabase.table("sessions") \
        .select("*") \
        .eq("user_id", user_id) \
        .order("date", desc=True) \
        .order("id", desc=True) \
        .execute()
    return result.data


def get_aggregates(user_id):
    """Return aggregate stats for the given user.

    Supabase REST API doesn't support SQL aggregates directly,
    so we fetch all rows and compute in Python.
    """
    result = supabase.table("sessions") \
        .select("buy_in, end_amount, net") \
        .eq("user_id", user_id) \
        .execute()
    rows = result.data

    total_sessions = len(rows)
    total_buy_in = sum(r["buy_in"] for r in rows)
    total_earned = sum(r["end_amount"] for r in rows)
    total_net = sum(r["net"] for r in rows)
    wins = sum(1 for r in rows if r["net"] > 0)

    return {
        "total_sessions": total_sessions,
        "total_buy_in": round(total_buy_in, 2),
        "total_earned": round(total_earned, 2),
        "total_net": round(total_net, 2),
        "wins": wins,
    }


def get_sessions_for_chart(user_id):
    """Return sessions ordered chronologically for the profit chart."""
    result = supabase.table("sessions") \
        .select("date, net") \
        .eq("user_id", user_id) \
        .order("date", desc=False) \
        .order("id", desc=False) \
        .execute()
    return result.data


def get_previous_blinds(user_id):
    """Return unique blinds from the user's past sessions, most recently used first."""
    result = supabase.table("sessions") \
        .select("blinds") \
        .eq("user_id", user_id) \
        .order("id", desc=True) \
        .execute()

    seen = set()
    unique = []
    for row in result.data:
        if row["blinds"] not in seen:
            seen.add(row["blinds"])
            unique.append(row["blinds"])
    return unique
