import logging
from src.billing.charge import charge

def test_charge_does_not_log_full_card_number(caplog):
    card = {"number": "4111111111111111"}
    with caplog.at_level(logging.INFO):
        charge(card, 500)
    assert "charging card 4111111111111111 for 500 cents" not in caplog.text
    assert "charging card **** 1111 for 500 cents" in caplog.text

    card = {"number": "4111111111111111"}
    with caplog.at_level(logging.INFO):
        result = charge(card, 500)
    assert result["status"] == "captured"
    assert "4111111111111111" not in caplog.text
    assert "1111" in caplog.text
