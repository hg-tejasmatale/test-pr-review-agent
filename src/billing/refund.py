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
