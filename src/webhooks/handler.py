"""Payment-provider webhooks. The provider retries deliveries, so handlers must be idempotent."""


def handle_event(db, event: dict) -> str:
    seen = db.execute("SELECT 1 FROM processed_events WHERE id = ?", (event["id"],)).fetchone()
    if seen:
        return "duplicate"
    db.execute(
        "INSERT INTO processed_events (id, type) VALUES (?, ?)", (event["id"], event["type"])
    )
    db.commit()
    return "processed"
