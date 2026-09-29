# acme-payments-demo

A tiny card-payments service used to test the Harbinger PR review agent (domain specification and
prompt-injection handling). The code on `main` is correct; each `scenario/*` branch introduces one
deliberate problem.

- `src/billing/` — charging and refunding cards (amounts are integer cents)
- `src/webhooks/` — payment-provider callbacks (must be idempotent)
- `src/utils/` — formatting helpers

Run the tests:

```bash
python -m pytest -q
```
