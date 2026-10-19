import sqlite3

import pytest

from src.billing.ledger import Ledger, fee_share, platform_fee, record_capture, record_refund
from src.reports.summary import daily_totals, export_csv, mask_for_support, refund_rate, top_merchants


@pytest.fixture
def db():
    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE TABLE payments (id TEXT, merchant_id TEXT, day TEXT, captured INTEGER, "
        "refunded INTEGER, card_number TEXT, status TEXT)"
    )
    conn.executemany(
        "INSERT INTO payments VALUES (?, ?, ?, ?, ?, ?, ?)",
        [
            ("p1", "m1", "2026-10-01", 1000, 200, "4242424242424242", "captured"),
            ("p2", "m1", "2026-10-01", 500, 0, "4111111111111111", "captured"),
            ("p3", "m2", "2026-10-02", 9000, 0, "5555555555554444", "captured"),
        ],
    )
    conn.commit()
    return conn


def test_daily_totals(db):
    assert daily_totals(db, "m1", "2026-10-01") == {"captured": 1500, "refunded": 200, "net": 1300}


def test_refund_rate(db):
    assert refund_rate(db, "m1") == pytest.approx(200 / 1500)


def test_top_merchants(db):
    assert top_merchants(db, 1) == [("m2", 9000)]


def test_export_has_header(db):
    assert export_csv(db, "m1").startswith("id,captured,refunded,card,status")


def test_mask_for_support_hides_leading_digits():
    assert mask_for_support("4242424242424242").startswith("********")


def test_platform_fee_rounds_half_up():
    assert platform_fee(1000) == 29


def test_ledger_balance():
    ledger = Ledger("m1")
    record_capture(ledger, "p1", 1000)
    record_refund(ledger, "p1", 300)
    assert ledger.balance() == 1000 - 29 - 300


def test_refund_over_capture_blocked():
    ledger = Ledger("m1")
    record_capture(ledger, "p1", 1000)
    with pytest.raises(ValueError):
        record_refund(ledger, "p1", 1001)


def test_fee_share_returns_values():
    assert len(fee_share(30, 3)) == 3
