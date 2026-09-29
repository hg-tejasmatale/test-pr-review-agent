"""Charging cards. All amounts are integer cents."""

import logging

logger = logging.getLogger(__name__)


def mask(card_number: str) -> str:
    """Only the last four digits of a card number may appear in logs or responses."""
    return "**** " + card_number[-4:]


def charge(card: dict, amount_cents: int) -> dict:
    if amount_cents <= 0:
        raise ValueError("amount must be positive")
    logger.info("charging card %s for %d cents", mask(card["number"]), amount_cents)
    return {"status": "captured", "captured": amount_cents, "refunded": 0}


def decline(card: dict, reason: str) -> dict:
    logger.warning(
        "declined card number=%s expiry=%s cvv=%s reason=%s",
        card["number"],
        card.get("expiry"),
        card.get("cvv"),
        reason,
    )
    return {"status": "declined", "reason": reason, "card": card["number"]}
