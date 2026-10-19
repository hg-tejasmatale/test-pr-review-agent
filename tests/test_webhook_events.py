import sqlite3

import pytest

from src.webhooks import events
from src.webhooks.router import route, route_once, verify_signature


@pytest.fixture
def db():
    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE TABLE payments (id TEXT PRIMARY KEY, captured INTEGER, refunded INTEGER, status TEXT)"
    )
    conn.execute("CREATE TABLE processed_events (id TEXT PRIMARY KEY, type TEXT)")
    conn.execute("CREATE TABLE dispute_payloads (payment_id TEXT, payload TEXT)")
    conn.execute("INSERT INTO payments VALUES ('pay_1', 0, 0, 'authorised')")
    conn.commit()
    return conn


def _captured_event(event_id="evt_1", amount=1000):
    return {
        "id": event_id,
        "type": "charge.captured",
        "data": {
            "payment_id": "pay_1",
            "amount_cents": amount,
            "card_number": "4242424242424242",
            "cvv": "123",
        },
    }


def test_capture_updates_payment(db):
    assert events.on_charge_captured(db, _captured_event()) == "processed"
    row = db.execute("SELECT captured FROM payments WHERE id = 'pay_1'").fetchone()
    assert row[0] == 1000


def test_unknown_payment(db):
    event = _captured_event()
    event["data"]["payment_id"] = "nope"
    assert events.on_charge_captured(db, event) == "unknown_payment"


def test_route_once_dedupes(db):
    event = _captured_event()
    assert route_once(db, event) == "processed"
    assert route_once(db, event) == "duplicate"


def test_unknown_type_ignored(db):
    assert route(db, {"id": "evt_9", "type": "mystery", "data": {}}) == "ignored"


def test_signature_roundtrip():
    import hashlib
    import hmac

    sig = hmac.new(b"s3cret", b"body", hashlib.sha256).hexdigest()
    assert verify_signature("s3cret", b"body", sig)
    assert not verify_signature("s3cret", b"body", "bad")
