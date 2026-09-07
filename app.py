from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import date as today_date
import database

app = Flask(__name__)
app.secret_key = "poker-tracker-secret-key-2024"

# Initialize the database on startup
database.init_db()


@app.route("/")
def index():
    """Home / landing page."""
    agg = database.get_aggregates()
    return render_template("index.html", agg=agg)


@app.route("/add", methods=["GET", "POST"])
def add_session():
    """Add a new poker session."""
    if request.method == "POST":
        date = request.form.get("date", "").strip()
        game_type = request.form.get("game_type", "live").strip()
        blinds = request.form.get("blinds", "").strip()
        buy_in_str = request.form.get("buy_in", "0").strip()
        end_amount_str = request.form.get("end_amount", "0").strip()
        notes = request.form.get("notes", "").strip()

        # Basic validation
        errors = []
        if not date:
            errors.append("Date is required.")
        if not blinds:
            errors.append("Blinds are required.")
        try:
            buy_in = float(buy_in_str)
        except ValueError:
            buy_in = 0
            errors.append("Buy-in must be a number.")
        try:
            end_amount = float(end_amount_str)
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
            )

        database.add_session(date, game_type, blinds, buy_in, end_amount, notes)
        flash("Session added successfully!", "success")
        return redirect(url_for("analytics"))

    return render_template(
        "add_session.html",
        today=today_date.today().isoformat(),
        form_data=None,
    )


@app.route("/analytics")
def analytics():
    """Analytics dashboard with session log."""
    sessions = database.get_all_sessions()
    agg = database.get_aggregates()
    chart_data = database.get_sessions_for_chart()

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
def delete_session(session_id):
    """Delete a session by ID."""
    database.delete_session(session_id)
    flash("Session deleted.", "info")
    return redirect(url_for("analytics"))


if __name__ == "__main__":
    app.run(debug=True)
