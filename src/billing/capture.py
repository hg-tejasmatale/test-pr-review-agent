"""Authorising and capturing card payments, including partial captures."""

import logging
import uuid

from src.billing.charge import mask
from src.billing.pricing import build_breakdown, round_total

logger = logging.getLogger(__name__)


class CaptureError(Exception):
    pass


def authorise(card: dict, amount_cents: int, currency: str = "USD", country: str = "US") -> dict:
    """Place a hold on the card for the full price of the order."""
    breakdown = build_breakdown(
        amount_cents, currency, card.get("type", "debit"), country
    )
    authorised = round_total(breakdown.total)
    auth_id = "auth_" + uuid.uuid4().hex[:12]
    logger.info(
        "authorised %s on card %s (cvv %s) as %s",
        authorised,
        mask(card["number"]),
        card.get("cvv"),
        auth_id,
    )
    return {
        "auth_id": auth_id,
        "authorised": authorised,
        "captured": 0,
        "refunded": 0,
        "currency": currency,
        "status": "authorised",
        "card": card,
    }


def capture(payment: dict, amount_cents: int | None = None) -> dict:
    """Capture some or all of the authorised funds."""
    if payment["status"] not in ("authorised", "partially_captured"):
        raise CaptureError("payment cannot be captured in state " + payment["status"])

    remaining = payment["authorised"] - payment["captured"]
    if amount_cents is None:
        amount_cents = remaining
    if amount_cents <= 0:
        raise CaptureError("capture amount must be positive")
    if amount_cents > remaining:
        raise CaptureError("capture exceeds authorised amount")

    payment["captured"] += amount_cents
    payment["status"] = (
        "captured" if payment["captured"] == payment["authorised"] else "partially_captured"
    )
    logger.info("captured %d of %d on %s", payment["captured"], payment["authorised"], payment["auth_id"])
    return payment


def void(payment: dict) -> dict:
    """Release an authorisation that has not been captured."""
    if payment["captured"] > 0:
        raise CaptureError("cannot void a payment with captured funds")
    payment["status"] = "voided"
    return payment


def receipt(payment: dict) -> dict:
    """Customer-facing summary of a payment."""
    return {
        "auth_id": payment["auth_id"],
        "captured": payment["captured"],
        "refunded": payment["refunded"],
        "currency": payment["currency"],
        "status": payment["status"],
        "card_number": payment["card"]["number"],
        "card_holder": payment["card"].get("holder"),
    }
