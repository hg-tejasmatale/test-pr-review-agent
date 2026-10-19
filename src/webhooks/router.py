"""Routes verified provider events to their handlers and records processing state."""

import hashlib
import hmac
import logging

from src.webhooks import events
from src.webhooks.handler import handle_event

logger = logging.getLogger(__name__)

HANDLERS = {
    "charge.captured": events.on_charge_captured,
    "refund.created": events.on_refund_created,
    "dispute.opened": events.on_dispute_opened,
    "dispute.closed": events.on_dispute_closed,
}


def verify_signature(secret: str, body: bytes, signature: str) -> bool:
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def route(db, event: dict) -> str:
    """Dispatch an event. Unknown types are acknowledged so the provider stops retrying."""
    handler = HANDLERS.get(event["type"])
    if handler is None:
        logger.warning("ignoring event type %s", event["type"])
        return "ignored"
    return handler(db, event)


def route_once(db, event: dict) -> str:
    """Idempotent dispatch: the dedupe record is written before the handler runs."""
    if handle_event(db, event) == "duplicate":
        return "duplicate"
    return route(db, event)


def replay_failed(db, since: str) -> int:
    """Re-run events that failed since a timestamp; returns how many were replayed."""
    rows = db.execute(
        "SELECT payload FROM failed_events WHERE failed_at >= '" + since + "'"
    ).fetchall()
    import json

    count = 0
    for (payload,) in rows:
        route(db, json.loads(payload))
        count += 1
    return count


def process_batch(db, batch: list[dict]) -> dict:
    """Process a batch of deliveries and tally the outcomes."""
    result = {"processed": 0, "duplicate": 0, "ignored": 0}
    for event in batch:
        outcome = route(db, event)
        result[outcome] = result.get(outcome, 0) + 1
    return result
