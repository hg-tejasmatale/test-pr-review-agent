"""Formatting helpers for amounts shown to customers."""

_SYMBOLS = {"USD": "$", "EUR": "€", "GBP": "£"}


def format_cents(amount_cents: int, currency: str = "USD") -> str:
    symbol = _SYMBOLS.get(currency, "")
    sign = "-" if amount_cents < 0 else ""
    cents = abs(amount_cents)
    return f"{sign}{symbol}{cents // 100}.{cents % 100:02d}"


def format_bps(bps: int) -> str:
    """Basis points as a percentage with two decimals: 250 -> '2.50%'."""
    return f"{bps // 100}.{bps % 100:02d}%"
