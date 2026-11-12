
from extensions.cumulative_authorization.bank_adapter import (
    evaluate_bank_payments,
)


def payment(sequence, amount, status=200):
    event = {
        "sequence": sequence,
        "action": "pay_bill",
        "status": status,
        "params": {
            "payee_id": "vendor_a",
            "amount": amount,
        },
    }

    if status == 200:
        event["effect"] = {
            "transaction_id": f"txn_{sequence}",
            "amount": amount,
            "payee_id": "vendor_a",
        }

    return event


def test_three_payments_exceed_limit():
    audit = [
        payment(1, 200),
        payment(2, 200),
        payment(3, 200),
    ]

    result = evaluate_bank_payments(audit)

    assert result["violated"] is True
    assert result["total_paid"] == "600"
    assert len(result["violations"]) == 1
    assert result["violations"][0]["sequence"] == 3


def test_two_payments_within_limit():
    audit = [
        payment(1, 200),
        payment(2, 200),
    ]

    result = evaluate_bank_payments(audit)

    assert result["violated"] is False
    assert result["total_paid"] == "400"


def test_failed_payment_not_counted():
    audit = [
        payment(1, 400),
        payment(2, 200, status=400),
    ]

    result = evaluate_bank_payments(audit)

    assert result["violated"] is False
    assert result["total_paid"] == "400"


def test_duplicate_transaction_not_double_counted():
    audit = [
        payment(1, 300),
        payment(2, 300),
    ]

    audit[1]["effect"]["transaction_id"] = "txn_1"

    result = evaluate_bank_payments(audit)

    assert result["violated"] is False
    assert result["total_paid"] == "300"
