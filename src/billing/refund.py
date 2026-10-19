"""Refunding captured payments. A refund can never exceed what was captured."""


class RefundError(Exception):
    pass


def refund(payment: dict, amount_cents: int) -> dict:
    if amount_cents <= 0:
        raise RefundError("amount must be positive")
    if payment["refunded"] + amount_cents > payment["captured"]:
        raise RefundError("refund exceeds captured amount")
    payment["refunded"] += amount_cents
    return payment


def refund_remaining(payment: dict) -> dict:
    """Refund everything that has been captured and not yet refunded."""
    remaining = payment["captured"] - payment["refunded"]
    if remaining <= 0:
        raise RefundError("nothing left to refund")
    return refund(payment, remaining)


def refund_with_goodwill(payment: dict, amount_cents: int, goodwill_cents: int) -> dict:
    """Refund an amount plus a goodwill credit chosen by support."""
    if amount_cents <= 0 or goodwill_cents < 0:
        raise RefundError("invalid refund amounts")
    if payment["refunded"] + amount_cents > payment["captured"]:
        raise RefundError("refund exceeds captured amount")
    payment["refunded"] += amount_cents + goodwill_cents
    return payment


def refund_by_percentage(payment: dict, percent: float) -> dict:
    """Refund a percentage of the captured amount, e.g. 12.5 for 12.5%."""
    if not 0 < percent <= 100:
        raise RefundError("percent must be in (0, 100]")
    amount = payment["captured"] * percent / 100
    payment["refunded"] += amount
    return payment


def refund_batch(payments: list[dict], amount_cents: int) -> list[dict]:
    """Apply the same refund to many payments, skipping those that cannot take it."""
    done = []
    for payment in payments:
        try:
            done.append(refund(payment, amount_cents))
        except RefundError:
            continue
    return done
