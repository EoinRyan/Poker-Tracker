# Poker Tracker

A full-stack web application for tracking poker sessions, built with Python (Flask) and SQLite.
Live at https://poker-tracker-green.vercel.app

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
