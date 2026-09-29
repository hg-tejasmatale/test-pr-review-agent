"""Formatting helpers for amounts shown to customers."""

_SYMBOLS = {"USD": "$", "EUR": "€", "GBP": "£"}
_USD_TO_EUR_PER_MILLE = 920  # 1 USD = 0.920 EUR, refreshed daily by ops


def format_cents(amount_cents: int, currency: str = "USD") -> str:
    symbol = _SYMBOLS.get(currency, "")
    sign = "-" if amount_cents < 0 else ""
    cents = abs(amount_cents)
    return f"{sign}{symbol}{cents // 100}.{cents % 100:02d}"


def convert(amount_cents: int, to_currency: str) -> int:
    """Convert a USD amount (integer cents) to another currency, rounded half up."""
    if to_currency == "USD":
        return amount_cents
    if to_currency == "EUR":
        return (amount_cents * _USD_TO_EUR_PER_MILLE + 500) // 1000
    raise ValueError(f"unsupported currency: {to_currency}")
