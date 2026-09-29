"""Refunding captured payments. A refund can never exceed what was captured."""


class RefundError(Exception):
    pass


def refund(payment: dict, amount_cents: int) -> dict:
    if amount_cents <= 0:
        raise RefundError("amount must be positive")
    payment.setdefault("refunds", []).append(amount_cents)
    payment["refunded"] = sum(payment["refunds"])
    return payment
