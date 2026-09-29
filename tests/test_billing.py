import sqlite3

import pytest

from src.billing.charge import charge, mask
from src.billing.refund import RefundError, refund
from src.utils.format import format_cents
from src.webhooks.handler import handle_event


def test_charge_captures_integer_cents():
    payment = charge({"number": "4242424242424242"}, 1999)
    assert payment == {"status": "captured", "captured": 1999, "refunded": 0}


def test_mask_keeps_only_last_four_digits():
    assert mask("4242424242424242") == "**** 4242"


def test_refund_never_exceeds_captured():
    payment = {"captured": 1000, "refunded": 0}
    refund(payment, 600)
    with pytest.raises(RefundError):
        refund(payment, 500)


def test_format_cents():
    assert format_cents(1999) == "$19.99"
    assert format_cents(-5, "EUR") == "-€0.05"


def test_webhook_is_idempotent():
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE processed_events (id TEXT PRIMARY KEY, type TEXT)")
    event = {"id": "evt_1", "type": "charge.captured"}
    assert handle_event(db, event) == "processed"
    assert handle_event(db, event) == "duplicate"
