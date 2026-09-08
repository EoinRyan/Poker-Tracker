import os
from functools import wraps
from datetime import timedelta

from dotenv import load_dotenv
load_dotenv()  # Load .env before anything else

from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import date as today_date
import database
from auth import auth_bp

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-fallback-secret-change-me")
app.permanent_session_lifetime = timedelta(days=30)

# Register auth blueprint
app.register_blueprint(auth_bp)



# ── Login Required Decorator ──────────────────────────────────
def login_required(f):
    """Redirect to login page if the user is not authenticated."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("auth.login_page"))
        return f(*args, **kwargs)
    return decorated_function


def get_user_id():
    """Helper to retrieve the current user's ID from the session."""
    return session.get("user_id")


# ── Routes ────────────────────────────────────────────────────

@app.route("/")
@login_required
def index():
    """Home / landing page."""
    user_id = get_user_id()
    agg = database.get_aggregates(user_id)
    return render_template("index.html", agg=agg)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add_session():
    """Add a new poker session."""
    user_id = get_user_id()
    previous_blinds = database.get_previous_blinds(user_id)

    if request.method == "POST":
        date = request.form.get("date", "").strip()
        game_type = request.form.get("game_type", "live").strip()
        small_blind_str = request.form.get("small_blind", "").strip()
        big_blind_str   = request.form.get("big_blind",   "").strip()
        buy_in_str      = request.form.get("buy_in",      "0").strip()
        end_amount_str  = request.form.get("end_amount",  "0").strip()
        notes = request.form.get("notes", "").strip()

        errors = []

        if not date:
            errors.append("Date is required.")

        # Validate small blind
        try:
            small_blind = float(small_blind_str)
            if small_blind < 0:
                errors.append("Small blind cannot be negative.")
        except ValueError:
            small_blind = None
            errors.append("Small blind must be a number.")

        # Validate big blind
        try:
            big_blind = float(big_blind_str)
            if big_blind < 0:
                errors.append("Big blind cannot be negative.")
        except ValueError:
            big_blind = None
            errors.append("Big blind must be a number.")

        # Ensure big blind >= small blind
        if small_blind is not None and big_blind is not None:
            if big_blind < small_blind:
                errors.append("Big blind must be greater than or equal to the small blind.")

        # Validate buy-in
        try:
            buy_in = float(buy_in_str)
            if buy_in < 0:
                errors.append("Buy-in cannot be negative.")
        except ValueError:
            buy_in = 0
            errors.append("Buy-in must be a number.")

        # Validate end amount
        try:
            end_amount = float(end_amount_str)
            if end_amount < 0:
                errors.append("End amount cannot be negative.")
        except ValueError:
            end_amount = 0
            errors.append("End amount must be a number.")

        if errors:
            for err in errors:
                flash(err, "error")
            return render_template(
                "add_session.html",
                today=today_date.today().isoformat(),
                form_data=request.form,
                previous_blinds=previous_blinds,
            )

        blinds = f"{small_blind:g}/{big_blind:g}"
        database.add_session(user_id, date, game_type, blinds, buy_in, end_amount, notes)
        flash("Session added successfully!", "success")
        return redirect(url_for("analytics"))

    return render_template(
        "add_session.html",
        today=today_date.today().isoformat(),
        form_data=None,
        previous_blinds=previous_blinds,
    )


@app.route("/analytics")
@login_required
def analytics():
    """Analytics dashboard with session log."""
    user_id = get_user_id()
    sessions = database.get_all_sessions(user_id)
    agg = database.get_aggregates(user_id)
    chart_data = database.get_sessions_for_chart(user_id)

    # Build cumulative profit series for the chart
    cumulative = 0
    chart_labels = []
    chart_values = []
    for row in chart_data:
        cumulative += row["net"]
        chart_labels.append(row["date"])
        chart_values.append(round(cumulative, 2))

    win_rate = 0
    if agg["total_sessions"] > 0:
        win_rate = round((agg["wins"] / agg["total_sessions"]) * 100, 1)

    return render_template(
        "analytics.html",
        sessions=sessions,
        agg=agg,
        win_rate=win_rate,
        chart_labels=chart_labels,
        chart_values=chart_values,
    )


@app.route("/delete/<int:session_id>", methods=["POST"])
@login_required
def delete_session(session_id):
    """Delete a session by ID (scoped to the current user)."""
    user_id = get_user_id()
    database.delete_session(session_id, user_id)
    flash("Session deleted.", "info")
    return redirect(url_for("analytics"))


if __name__ == "__main__":
    app.run(debug=True)
