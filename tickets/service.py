# tickets/service.py
from datetime import datetime

# Keep these in sync with your form options
ALLOWED_STATUSES = {"Open", "In Prog", "Closed"}

def _clean_str(v):
    return v.strip() if isinstance(v, str) else v

def _coerce_int(v):
    if v is None:
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None

def validate_new(form, created_by: str):
    """
    Validate incoming form for creating a ticket.
    Returns: (errors, data)
    -> data keys are TitleCase to match repository/DB usage.
    """
    errors = []

    # Required
    ticket = _clean_str(form.get("Ticket") or form.get("ticket") or "")
    status = _clean_str(form.get("Status") or form.get("status") or "Open")
    # DB: StatusID is VARCHAR -> accept any non-empty string
    status_id = _clean_str(form.get("StatusID") or form.get("status_id") or "")
    # DB: PriorityID is INTEGER -> must be positive int
    priority_id = _coerce_int(form.get("PriorityID") or form.get("priority_id"))

    # Optional
    description = _clean_str(form.get("Description") or form.get("description") or "")

    # --- Validation rules aligned to your schema ---
    if not ticket:
        errors.append("Ticket ID is required.")

    if not status:
        errors.append("Status is required.")
    elif status not in ALLOWED_STATUSES:
        errors.append(f"Status must be one of: {', '.join(sorted(ALLOWED_STATUSES))}.")

    if not status_id:
        errors.append("StatusID is required.")  # string allowed

    if priority_id is None or priority_id < 1:
        errors.append("PriorityID must be a positive integer.")

    # Build payload for repository.create_ticket()
    data = {
        "Ticket": ticket,
        "Status": status,
        "StatusID": status_id,
        "PriorityID": priority_id,
        "Description": description or "",
        "CreatedBy": created_by,
        # Audit fields if you want them later; repo ignores them today
        "CreatedAt": datetime.utcnow().isoformat(timespec="seconds"),
    }
    return errors, data


def validate_update(form, username: str):
    """
    Validate update form fields. Returns only fields that are provided and valid.
    -> Allowed fields for your repo.update_ticket: Status, PriorityID, StatusID, Description
    """
    errors = []
    data = {}

    raw_description = form.get("Description", form.get("description"))
    raw_status      = form.get("Status",      form.get("status"))
    raw_status_id   = form.get("StatusID",    form.get("status_id"))
    raw_priority_id = form.get("PriorityID",  form.get("priority_id"))

    # Optional fields; only include if provided
    if raw_description is not None:
        data["Description"] = _clean_str(raw_description) or ""

    if raw_status is not None:
        status = _clean_str(raw_status) or ""
        if not status:
            errors.append("Status is required when provided.")
        elif status not in ALLOWED_STATUSES:
            errors.append(f"Status must be one of: {', '.join(sorted(ALLOWED_STATUSES))}.")
        else:
            data["Status"] = status

    # StatusID is VARCHAR -> accept any non-empty string
    if raw_status_id is not None:
        sid = _clean_str(raw_status_id) or ""
        if not sid:
            errors.append("StatusID cannot be empty when provided.")
        else:
            data["StatusID"] = sid

    # PriorityID is INTEGER
    if raw_priority_id is not None:
        pid = _coerce_int(raw_priority_id)
        if pid is None or pid < 1:
            errors.append("PriorityID must be a positive integer.")
        else:
            data["PriorityID"] = pid

    # Set audit (repo ignores today; kept for future)
    data["UpdatedBy"] = username
    data["UpdatedAt"] = datetime.utcnow().isoformat(timespec="seconds")

    # Ensure at least one updatable non-audit field is present
    non_audit = {k: v for k, v in data.items() if k not in {"UpdatedBy", "UpdatedAt"}}
    if not non_audit:
        errors.append("No fields provided to update.")

    return errors, data
