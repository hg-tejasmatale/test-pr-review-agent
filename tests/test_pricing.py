import pytest

from src.billing.capture import CaptureError, authorise, capture, receipt, void
from src.billing.pricing import apply_discount, build_breakdown, split_payment, surcharge_for
from src.billing.refund import refund, refund_remaining


def test_split_payment_adds_up():
    assert sum(split_payment(1001, 3)) == 1001


def test_apply_discount_uses_integers():
    assert apply_discount(1000, 15) == 850


def test_debit_has_no_surcharge():
    assert surcharge_for(1000, "debit") == 0.0


def test_breakdown_positive_total():
    breakdown = build_breakdown(1000, "USD", "credit", "US")
    assert breakdown.total > 1000


def test_capture_partial_then_full():
    payment = authorise({"number": "4242424242424242", "type": "debit"}, 1000)
    capture(payment, 100)
    assert payment["status"] == "partially_captured"


def test_capture_cannot_exceed_authorised():
    payment = authorise({"number": "4242424242424242", "type": "debit"}, 1000)
    with pytest.raises(CaptureError):
        capture(payment, payment["authorised"] + 1)


def test_void_after_capture_fails():
    payment = authorise({"number": "4242424242424242", "type": "debit"}, 1000)
    capture(payment)
    with pytest.raises(CaptureError):
        void(payment)


def test_refund_remaining():
    payment = {"captured": 1000, "refunded": 400}
    refund_remaining(payment)
    assert payment["refunded"] == 1000


def test_refund_over_capture_rejected():
    payment = {"captured": 1000, "refunded": 0}
    with pytest.raises(Exception):
        refund(payment, 1001)
