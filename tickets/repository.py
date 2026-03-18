from __future__ import annotations

from typing import Any, Dict, List, Optional
from sqlalchemy import text
from db import connect, transaction


def list_tickets() -> List[Dict[str, Any]]:
    sql = text("""
        SELECT
            Ticket,
            Status,
            CreatedBy,
            PriorityID,
            StatusID,
            Description
        FROM Tickets
        ORDER BY Ticket ASC
    """)
    with connect() as conn:
        return [dict(r) for r in conn.execute(sql).mappings().all()]


def get_ticket(ticket_id: str) -> Optional[Dict[str, Any]]:
    sql = text("""
        SELECT
            Ticket,
            Status,
            CreatedBy,
            PriorityID,
            StatusID,
            Description
        FROM Tickets
        WHERE Ticket = :t
    """)
    with connect() as conn:
        row = conn.execute(sql, {"t": ticket_id}).mappings().first()
        return dict(row) if row else None


def exists_ticket(ticket_id: str) -> bool:
    sql = text("SELECT 1 FROM Tickets WHERE Ticket = :t LIMIT 1")
    with connect() as conn:
        return conn.execute(sql, {"t": ticket_id}).first() is not None


def create_ticket(data: Dict[str, Any]) -> None:
    """
    Expects: Ticket, Status, CreatedBy, PriorityID, StatusID
    Optional: Description
    """
    sql = text("""
        INSERT INTO Tickets (Ticket, Status, CreatedBy, PriorityID, StatusID, Description)
        VALUES (:Ticket, :Status, :CreatedBy, :PriorityID, :StatusID, :Description)
    """)
    params = {
        "Ticket":      data["Ticket"],
        "Status":      data["Status"],
        "CreatedBy":   data["CreatedBy"],
        "PriorityID":  data["PriorityID"],
        "StatusID":    data["StatusID"],
        "Description": data.get("Description"),  # None if not provided
    }
    with transaction() as conn:
        conn.execute(sql, params)


def update_ticket(ticket_id: str, data: Dict[str, Any]) -> bool:
    """
    Partial update.
    Allowed: Status, PriorityID, StatusID, Description
    """
    allowed = {"Status", "PriorityID", "StatusID", "Description"}
    sets: List[str] = []
    params: Dict[str, Any] = {"t": ticket_id}

    for k in allowed:
        if k in data:
            sets.append(f"{k} = :{k}")
            params[k] = data[k]

    if not sets:
        return False

    sql = text(f"UPDATE Tickets SET {', '.join(sets)} WHERE Ticket = :t")
    with transaction() as conn:
        res = conn.execute(sql, params)
        return res.rowcount > 0


def close_ticket(ticket_id: str) -> bool:
    sql = text("UPDATE Tickets SET Status = 'Closed' WHERE Ticket = :t")
    with transaction() as conn:
        res = conn.execute(sql, {"t": ticket_id})
        return res.rowcount > 0


def delete_ticket(ticket_id: str) -> bool:
    sql = text("DELETE FROM Tickets WHERE Ticket = :t")
    with transaction() as conn:
        res = conn.execute(sql, {"t": ticket_id})
        return res.rowcount > 0


