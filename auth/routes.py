from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .service import register_user, authenticate
from .roles import ROLE_USER  # default new registrations

auth_bp = Blueprint("auth", __name__)

@auth_bp.get("/register")
def register_form():
    return render_template("register.html")

@auth_bp.post("/register")
def register_submit():
    username = (request.form.get("username") or "").strip()
    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""
    confirm = request.form.get("confirm") or ""

    if not username or not password or not confirm:
        flash("Username and password are required.", "error")
        return redirect(url_for("auth.register_form"))

    if password != confirm:
        flash("Passwords do not match.", "error")
        return redirect(url_for("auth.register_form"))

    try:
        #  Default new users to 'User' (role_id = 3)
        register_user(username, email, password, role_id=ROLE_USER)
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth.login_form"))
    except Exception:
        # e.g. UNIQUE constraint failed on username/email
        flash("Registration error. Try a different username/email.", "error")
        return redirect(url_for("auth.register_form"))

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

    # Set session
    session.clear()
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["role_id"] = user["role_id"]

    # Optional: store role_name if your authenticate() LEFT JOINs roles and returns it
    if "role_name" in user and user["role_name"]:
        session["role_name"] = user["role_name"]

    flash(f"Welcome, {user['username']}!", "success")

    # Redirect to tickets list (ensure tickets blueprint is registered with url_prefix="/tickets")
    # If you prefer, change to: return redirect(url_for("home"))
    return redirect(url_for("tickets.list"))

@auth_bp.post("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login_form"))
