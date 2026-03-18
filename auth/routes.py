# auth/routes.py
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, session
)
from .service import register_user, authenticate
from .roles import ROLE_USER  # default role for new users


auth_bp = Blueprint(
    "auth",
    __name__,
    template_folder="../templates"
)


# ------------------------
#  REGISTER (GET + POST)
# ------------------------

@auth_bp.get("/register")
def register_form():
    return render_template("register.html")


@auth_bp.post("/register")
def register_submit():
    username = (request.form.get("username") or "").strip()
    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""
    confirm = request.form.get("confirm") or ""

    # Basic validations
    if not username or not password or not confirm:
        flash("Username and password are required.", "error")
        return redirect(url_for("auth.register_form"))

    if password != confirm:
        flash("Passwords do not match.", "error")
        return redirect(url_for("auth.register_form"))

    # Attempt registration
    try:
        register_user(username, email, password, role_id=ROLE_USER)
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth.login_form"))

    except Exception:
        # e.g. duplicate username or email
        flash("Registration error. Try a different username/email.", "error")
        return redirect(url_for("auth.register_form"))


# ------------------------
#  LOGIN (GET + POST)
# ------------------------

@auth_bp.get("/login")
def login_form():
    return render_template("login.html")


@auth_bp.post("/login")
def login_submit():
    username_or_email = (request.form.get("username_or_email") or "").strip()
    password = request.form.get("password") or ""

    if not username_or_email or not password:
        flash("Please enter your login details.", "error")
        return redirect(url_for("auth.login_form"))

    user = authenticate(username_or_email, password)

    if not user:
        flash("Invalid username/email or password.", "error")
        return redirect(url_for("auth.login_form"))

    # Store session info
    session.clear()
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["role_id"] = user["role_id"]

    if "role_name" in user and user["role_name"]:
        session["role_name"] = user["role_name"]

    flash(f"Welcome, {user['username']}!", "success")

    # Redirect to ticket list.
    # In tickets/routes.py you MUST set endpoint="list"
    # or change this to url_for("tickets.list_tickets")
    return redirect(url_for("tickets.list"))


# ------------------------
#  LOGOUT
# ------------------------

@auth_bp.post("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login_form"))