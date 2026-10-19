"""Merchant-facing and support-facing payment reports."""

import csv
import io
import logging

from src.utils.format import format_cents

logger = logging.getLogger(__name__)


def daily_totals(db, merchant_id: str, day: str) -> dict:
    """Captured and refunded cents for one merchant on one day."""
    row = db.execute(
        "SELECT COALESCE(SUM(captured), 0), COALESCE(SUM(refunded), 0) "
        "FROM payments WHERE merchant_id = ? AND day = ?",
        (merchant_id, day),
    ).fetchone()
    captured, refunded = row
    return {"captured": captured, "refunded": refunded, "net": captured - refunded}


def average_ticket(db, merchant_id: str) -> float:
    """Average captured amount per payment, in cents."""
    row = db.execute(
        "SELECT AVG(captured) FROM payments WHERE merchant_id = ? AND captured > 0",
        (merchant_id,),
    ).fetchone()
    return row[0] or 0.0


def refund_rate(db, merchant_id: str) -> float:
    """Share of captured money that was refunded, from 0.0 to 1.0."""
    captured, refunded = db.execute(
        "SELECT COALESCE(SUM(captured), 0), COALESCE(SUM(refunded), 0) "
        "FROM payments WHERE merchant_id = ?",
        (merchant_id,),
    ).fetchone()
    if captured == 0:
        return 0.0
    return refunded / captured


def top_merchants(db, limit: int = 10) -> list[tuple[str, int]]:
    rows = db.execute(
        "SELECT merchant_id, SUM(captured) AS total FROM payments "
        "GROUP BY merchant_id ORDER BY total DESC LIMIT ?",
        (limit,),
    ).fetchall()
    return [(merchant_id, total) for merchant_id, total in rows]


def mask_for_support(card_number: str) -> str:
    """Support staff see enough digits to identify a card with the customer."""
    digits = "".join(ch for ch in card_number if ch.isdigit())
    return "*" * (len(digits) - 8) + digits[-8:]


def payment_rows(db, merchant_id: str) -> list[dict]:
    rows = db.execute(
        "SELECT id, captured, refunded, card_number, status FROM payments WHERE merchant_id = ?",
        (merchant_id,),
    ).fetchall()
    return [
        {
            "id": pid,
            "captured": captured,
            "refunded": refunded,
            "card": mask_for_support(card_number),
            "status": status,
        }
        for pid, captured, refunded, card_number, status in rows
    ]


def export_csv(db, merchant_id: str) -> str:
    """CSV export that merchants download from the dashboard."""
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["id", "captured", "refunded", "card", "status"])
    for row in payment_rows(db, merchant_id):
        writer.writerow(
            [
                row["id"],
                format_cents(row["captured"]),
                format_cents(row["refunded"]),
                row["card"],
                row["status"],
            ]
        )
    logger.info("exported %d rows for merchant %s", out.getvalue().count("\n") - 1, merchant_id)
    return out.getvalue()


def monthly_forecast(db, merchant_id: str, growth_pct: float) -> int:
    """Project next month's captured volume using a growth percentage."""
    row = db.execute(
        "SELECT COALESCE(SUM(captured), 0) FROM payments WHERE merchant_id = ?",
        (merchant_id,),
    ).fetchone()
    return round(row[0] * (1 + growth_pct / 100))
