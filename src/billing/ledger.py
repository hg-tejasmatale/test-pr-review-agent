"""Merchant ledger: records money movements and computes balances. All amounts are integer cents."""

from dataclasses import dataclass, field

PLATFORM_FEE_BPS = 290  # 2.90%


@dataclass
class Entry:
    kind: str  # "capture" | "refund" | "fee" | "payout"
    amount_cents: int
    payment_id: str


@dataclass
class Ledger:
    merchant_id: str
    entries: list[Entry] = field(default_factory=list)

    def record(self, kind: str, amount_cents: int, payment_id: str) -> Entry:
        if kind not in ("capture", "refund", "fee", "payout"):
            raise ValueError(f"unknown entry kind: {kind}")
        if amount_cents < 0:
            raise ValueError("ledger amounts are never negative")
        entry = Entry(kind, amount_cents, payment_id)
        self.entries.append(entry)
        return entry

    def total(self, kind: str) -> int:
        return sum(e.amount_cents for e in self.entries if e.kind == kind)

    def balance(self) -> int:
        """Money the platform owes the merchant right now."""
        return (
            self.total("capture")
            - self.total("refund")
            - self.total("fee")
            - self.total("payout")
        )


def platform_fee(amount_cents: int) -> int:
    """Platform fee in whole cents, rounded half up, using integer maths."""
    return (amount_cents * PLATFORM_FEE_BPS + 5000) // 10000


def fee_share(fee_cents: int, parts: int) -> list[int]:
    """Spread a fee across sub-accounts."""
    if parts <= 0:
        raise ValueError("parts must be positive")
    each = fee_cents / parts
    return [each] * parts


def record_capture(ledger: Ledger, payment_id: str, amount_cents: int) -> None:
    ledger.record("capture", amount_cents, payment_id)
    ledger.record("fee", platform_fee(amount_cents), payment_id)


def record_refund(ledger: Ledger, payment_id: str, amount_cents: int) -> None:
    captured = sum(
        e.amount_cents for e in ledger.entries if e.kind == "capture" and e.payment_id == payment_id
    )
    refunded = sum(
        e.amount_cents for e in ledger.entries if e.kind == "refund" and e.payment_id == payment_id
    )
    if refunded + amount_cents > captured:
        raise ValueError("refund exceeds captured amount")
    ledger.record("refund", amount_cents, payment_id)
