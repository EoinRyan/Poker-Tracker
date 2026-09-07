import os
from flask import Blueprint, redirect, url_for, session, request, render_template
from supabase_client import supabase, SUPABASE_URL

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login")
def login_page():
    """Render the login page."""
    # Already logged in → go home
    if session.get("user_id"):
        return redirect(url_for("index"))
    return render_template("login.html")


@auth_bp.route("/auth/login")
def auth_login():
    """Redirect the user to Supabase Google OAuth."""
    # Build the callback URL (absolute, so it works locally and on Vercel)
    callback_url = url_for("auth.auth_callback", _external=True)

    response = supabase.auth.sign_in_with_oauth(
        {
            "provider": "google",
            "options": {
                "redirect_to": callback_url,
            },
        }
    )
    return redirect(response.url)


@auth_bp.route("/auth/callback")
def auth_callback():
    """
    Handle the OAuth callback from Supabase.
    Supabase redirects here with a `code` query parameter.
    We exchange it for a session and store the user info in the Flask session.
    """
    code = request.args.get("code")
    if not code:
        # No code — something went wrong, send back to login
        return redirect(url_for("auth.login_page"))

    try:
        result = supabase.auth.exchange_code_for_session({"auth_code": code})
        user = result.user
        session["user_id"] = user.id
        session["user_email"] = user.email
        # Keep login persistent across browser restarts
        session.permanent = True
    except Exception:
        return redirect(url_for("auth.login_page"))

    return redirect(url_for("index"))


@auth_bp.route("/auth/logout")
def auth_logout():
    """Sign out the current user and clear the Flask session."""
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    session.clear()
    return redirect(url_for("auth.login_page"))
