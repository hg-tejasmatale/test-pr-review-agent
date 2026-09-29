"""Formatting helpers for amounts shown to customers."""

_SYMBOLS = {"USD": "$", "EUR": "€", "GBP": "£"}
_RECEIPT_WIDTH = 40


def format_cents(amount_cents: int, currency: str = "USD") -> str:
    symbol = _SYMBOLS.get(currency, "")
    sign = "-" if amount_cents < 0 else ""
    cents = abs(amount_cents)
    return f"{sign}{symbol}{cents // 100}.{cents % 100:02d}"


def receipt_line(description: str, amount_cents: int, currency: str = "USD") -> str:
    """One receipt row: description on the left, amount right-aligned, dots in between."""
    amount = format_cents(amount_cents, currency)
    label = description[: _RECEIPT_WIDTH - len(amount) - 2]
    dots = "." * (_RECEIPT_WIDTH - len(label) - len(amount) - 2)
    return f"{label} {dots} {amount}"
