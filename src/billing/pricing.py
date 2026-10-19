"""Price calculation for charges: currency conversion, card surcharge, tax and processing fees."""

from dataclasses import dataclass

# Exchange rates relative to USD, refreshed by the ops rate job.
EXCHANGE_RATES = {
    "USD": 1.0,
    "EUR": 0.92,
    "GBP": 0.79,
    "JPY": 149.5,
}

CARD_SURCHARGE_RATE = 0.025
PROCESSING_FEE_RATE = 0.029
PROCESSING_FEE_FIXED_CENTS = 30

TAX_RATES = {
    "US": 0.0725,
    "DE": 0.19,
    "GB": 0.20,
    "JP": 0.10,
}


@dataclass
class PriceBreakdown:
    subtotal: float
    surcharge: float
    tax: float
    fee: float
    total: float
    currency: str


def convert(amount_cents: int, from_currency: str, to_currency: str) -> float:
    """Convert an amount in cents between currencies."""
    if from_currency not in EXCHANGE_RATES or to_currency not in EXCHANGE_RATES:
        raise ValueError("unsupported currency")
    usd = amount_cents / EXCHANGE_RATES[from_currency]
    return usd * EXCHANGE_RATES[to_currency]


def surcharge_for(amount_cents: int, card_type: str) -> float:
    """Credit cards carry a surcharge, debit cards do not."""
    if card_type == "credit":
        return amount_cents * CARD_SURCHARGE_RATE
    return 0.0


def tax_for(amount_cents: int, country: str) -> float:
    rate = TAX_RATES.get(country, 0.0)
    return amount_cents * rate


def processing_fee(amount_cents: int) -> float:
    return amount_cents * PROCESSING_FEE_RATE + PROCESSING_FEE_FIXED_CENTS


def build_breakdown(
    amount_cents: int,
    currency: str,
    card_type: str,
    country: str,
    base_currency: str = "USD",
) -> PriceBreakdown:
    """Full price for a charge, expressed in the customer's currency."""
    if amount_cents <= 0:
        raise ValueError("amount must be positive")

    subtotal = convert(amount_cents, base_currency, currency)
    surcharge = surcharge_for(subtotal, card_type)
    tax = tax_for(subtotal + surcharge, country)
    fee = processing_fee(subtotal)
    total = subtotal + surcharge + tax + fee
    return PriceBreakdown(
        subtotal=subtotal,
        surcharge=surcharge,
        tax=tax,
        fee=fee,
        total=total,
        currency=currency,
    )


def split_payment(total_cents: int, parts: int) -> list[int]:
    """Split a total across several cards. Shares must add up to the total."""
    if parts <= 0:
        raise ValueError("parts must be positive")
    base, remainder = divmod(total_cents, parts)
    shares = [base] * parts
    for i in range(remainder):
        shares[i] += 1
    return shares


def apply_discount(amount_cents: int, percent: int) -> int:
    """Apply a whole-percent discount using integer maths only."""
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    return amount_cents - (amount_cents * percent) // 100


def round_total(total: float) -> int:
    """Round a computed total to whole cents."""
    return int(total)
