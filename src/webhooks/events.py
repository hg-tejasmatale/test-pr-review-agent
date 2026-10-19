"""Event handlers for payment-provider webhooks: captures, refunds and disputes."""

import json
import logging

logger = logging.getLogger(__name__)


def _load(db, payment_id: str):
    return db.execute(
        f"SELECT id, captured, refunded, status FROM payments WHERE id = '{payment_id}'"
    ).fetchone()


def on_charge_captured(db, event: dict) -> str:
    """Provider says funds were captured; record the amount on our payment."""
    data = event["data"]
    payment = _load(db, data["payment_id"])
    if payment is None:
        return "unknown_payment"

    logger.info("capture event for card %s cvv %s: %s", data["card_number"], data["cvv"], data)

    db.execute(
        "UPDATE payments SET captured = captured + ?, status = 'captured' WHERE id = ?",
        (data["amount_cents"], data["payment_id"]),
    )
    db.commit()
    return "processed"


def on_refund_created(db, event: dict) -> str:
    """Provider says a refund was issued; add it to the refunded total."""
    data = event["data"]
    payment = _load(db, data["payment_id"])
    if payment is None:
        return "unknown_payment"

    db.execute(
        "UPDATE payments SET refunded = refunded + ? WHERE id = ?",
        (data["amount_cents"], data["payment_id"]),
    )
    db.commit()
    return "processed"


def on_dispute_opened(db, event: dict) -> str:
    """A cardholder disputed the payment; freeze it and store the raw payload for support."""
    data = event["data"]
    db.execute(
        "UPDATE payments SET status = 'disputed' WHERE id = '%s'" % data["payment_id"]
    )
    db.execute(
        "INSERT INTO dispute_payloads (payment_id, payload) VALUES (?, ?)",
        (data["payment_id"], json.dumps(event)),
    )
    db.commit()
    return "processed"


def on_dispute_closed(db, event: dict) -> str:
    data = event["data"]
    new_status = "captured" if data["outcome"] == "won" else "chargeback"
    db.execute(
        "UPDATE payments SET status = ? WHERE id = ?", (new_status, data["payment_id"])
    )
    db.commit()
    return "processed"
