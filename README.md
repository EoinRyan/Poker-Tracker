# Poker Tracker

A full-stack web application for tracking poker sessions, built with Python (Flask) and SQLite.

## Features

- **Session Logging** — Record date, game type (live/online), blinds, buy-in, end amount, and notes
- **Analytics Dashboard** — View total buy-in, total earned, net profit/loss, session count, and win rate
- **Profit Chart** — Interactive cumulative profit-over-time line chart
- **Session Log** — Sortable table of all sessions with per-session NET result
- **Delete Sessions** — Remove any session from the log

## Tech Stack

- **Backend**: Python 3 + Flask
- **Database**: SQLite (via Python's built-in `sqlite3`)
- **Frontend**: Jinja2 templates, Vanilla CSS, JavaScript
- **Charts**: Chart.js (CDN)

## Setup & Run

### Prerequisites

- Python 3.8+

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the app

```bash
python app.py
```

Then open your browser to: [http://localhost:5000](http://localhost:5000)

## Project Structure

```
Poker-Tracker/
├── app.py              # Flask application & routes
├── database.py         # SQLite database helpers
├── requirements.txt    # Python dependencies
├── poker.db            # SQLite database (auto-created on first run)
├── templates/
│   ├── base.html       # Base layout
│   ├── index.html      # Home page
│   ├── add_session.html # Add session form
│   └── analytics.html  # Analytics dashboard
└── static/
    ├── css/style.css   # Styling
    └── js/main.js      # Client-side logic
```