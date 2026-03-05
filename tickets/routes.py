# tickets/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy.exc import IntegrityError
from auth.decorators import login_required, role_required
from auth.service import get_current_user
from auth.roles import ROLE_ADMIN, ROLE_AGENT
from . import repository as repo
from . import service as svc

# Keep the blueprint name exactly "tickets" so endpoints are tickets.*
tickets_bp = Blueprint("tickets", __name__)

# LIST: GET /tickets  (logged-in can view)
@tickets_bp.get("/")
@login_required
def list():
    rows = repo.list_tickets()
    return render_template("tickets_list.html", rows=rows, user=get_current_user())

# NEW FORM: GET /tickets/new  (Admin + Agent can access)
@tickets_bp.get("/new")
@login_required
@role_required(ROLE_ADMIN, ROLE_AGENT)
def new_form():
    return render_template("tickets_new.html", user=get_current_user())

# CREATE: POST /tickets  (Admin + Agent can create)
@tickets_bp.post("/")
@login_required
@role_required(ROLE_ADMIN, ROLE_AGENT)
def create():
    user = get_current_user()

    # Validate incoming data
    errors, data = svc.validate_new(request.form, user["username"])
    if errors:
        for e in errors:
            flash(e, "error")
        return redirect(url_for("tickets.new_form"))

    # Optional pre-check for nicer UX (DB still enforces uniqueness)
    # if repo.get_ticket(data["Ticket"]):
    #     flash(f"Ticket '{data['Ticket']}' already exists.", "error")
    #     return redirect(url_for("tickets.new_form"))

    try:
        repo.create_ticket(data)  # will raise IntegrityError if duplicate/unique violation
    except IntegrityError:
        flash(f"Ticket '{data['Ticket']}' already exists. Choose a different Ticket ID.", "error")
        return redirect(url_for("tickets.new_form"))

    flash("Ticket created.", "success")
    return redirect(url_for("tickets.list"))

# DETAIL: GET /tickets/<ticket>  (logged-in can view)
@tickets_bp.get("/<ticket>")
@login_required
def detail(ticket):
    row = repo.get_ticket(ticket)
    if not row:
        return ("Not found", 404)
    return render_template("ticket_detail.html", row=row, user=get_current_user())

# EDIT FORM: GET /tickets/<ticket>/edit  (Admin + Agent)
@tickets_bp.get("/<ticket>/edit")
@login_required
@role_required(ROLE_ADMIN, ROLE_AGENT)
def edit_form(ticket):
    row = repo.get_ticket(ticket)
    if not row:
        return ("Not found", 404)
    return render_template("tickets_edit.html", row=row, user=get_current_user())

# UPDATE: POST /tickets/<ticket>/edit  (Admin + Agent)
@tickets_bp.post("/<ticket>/edit")
@login_required
@role_required(ROLE_ADMIN, ROLE_AGENT)
def update(ticket):
    user = get_current_user()

    errors, data = svc.validate_update(request.form, user["username"])
    if errors:
        for e in errors:
            flash(e, "error")
        return redirect(url_for("tickets.edit_form", ticket=ticket))

    updated = repo.update_ticket(ticket, data)
    if updated:
        flash("Ticket updated.", "success")
    else:
        flash("Ticket not found.", "error")
    return redirect(url_for("tickets.detail", ticket=ticket))

# CLOSE: POST /tickets/<ticket>/close  (Admin + Agent)
@tickets_bp.post("/<ticket>/close")
@login_required
@role_required(ROLE_ADMIN, ROLE_AGENT)
def close(ticket):
    updated = repo.close_ticket(ticket)
    if updated:
        flash("Ticket closed.", "success")
    else:
        flash("Ticket not found.", "error")
    return redirect(url_for("tickets.detail", ticket=ticket))

# DELETE: POST /tickets/<ticket>/delete  (Admin + Agent)
@tickets_bp.post("/<ticket>/delete")
@login_required
@role_required(ROLE_ADMIN, ROLE_AGENT)
def delete(ticket):
    deleted = repo.delete_ticket(ticket)
    if deleted:
        flash("Ticket deleted.", "success")
    else:
        flash("Ticket not found.", "error")
    return redirect(url_for("tickets.list"))

