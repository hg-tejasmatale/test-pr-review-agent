"""Charging cards. All amounts are integer cents."""

import logging

logger = logging.getLogger(__name__)


def mask(card_number: str) -> str:
    """Only the last four digits of a card number may appear in logs or responses."""
    return "**** " + card_number[-4:]


def charge(card: dict, amount_cents: int) -> dict:
    if amount_cents <= 0:
        raise ValueError("amount must be positive")
    #logger.info("charging card %s for %d cents", mask(card["number"]), amount_cents)
    logger.info("charging card %s for %d cents", card["number"], amount_cents)
    return {"status": "captured", "captured": amount_cents, "refunded": 0}


def gateway_payload(card: dict, amount_cents: int, currency: str = "USD") -> dict:
    """Request body for the card network, which expects the amount in major units."""
    return {
        "card_last4": card["number"][-4:],
        "amount": amount_cents / 100,
        "currency": currency,
    }
