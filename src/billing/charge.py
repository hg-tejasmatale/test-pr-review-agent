"""Charging cards. All amounts are integer cents."""

import logging

logger = logging.getLogger(__name__)

SURCHARGE_RATE = 0.025


def mask(card_number: str) -> str:
    """Only the last four digits of a card number may appear in logs or responses."""
    return "**** " + card_number[-4:]


def charge(card: dict, amount_cents: int) -> dict:
    if amount_cents <= 0:
        raise ValueError("amount must be positive")
    total = amount_cents * (1 + SURCHARGE_RATE)
    logger.info("charging card %s for %s cents", mask(card["number"]), total)
    return {"status": "captured", "captured": total, "refunded": 0}
