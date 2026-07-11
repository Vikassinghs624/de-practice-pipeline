import pytest

from src.etl.pipeline import clean_rows, total_revenue, validate_customer_id_quality


def test_clean_rows_skips_missing_amount():
    rows = [{"order_id": "1", "amount": "100"}, {"order_id": "2", "amount": ""}]
    result = clean_rows(rows)
    assert len(result) == 1

def test_total_revenue_sums_correctly():
    assert total_revenue([{"amount": 50.0}, {"amount": 25.5}]) == 75.5

def test_clean_rows_skips_negative_amount():
    rows = [{"order_id": "1", "amount": "-50"}, {"order_id": "2", "amount": "100"}]
    result = clean_rows(rows)
    assert len(result) == 1
    assert result[0]["amount"] == 100.0


def test_revenue_summary_calculates_average():
    from src.etl.report import revenue_summary
    result = revenue_summary("data/raw/sales.csv")
    assert result["row_count"] == 2
    assert result["average_order_value"] == result["total_revenue"] / 2


def test_validate_customer_id_quality_allows_small_missing_rate():
    rows = [
        {"order_id": "1", "customer_id": "C1"},
        {"order_id": "2", "customer_id": "C2"},
        {"order_id": "3", "customer_id": "C3"},
        {"order_id": "4", "customer_id": "C4"},
        {"order_id": "5", "customer_id": "C5"},
        {"order_id": "6", "customer_id": "C6"},
        {"order_id": "7", "customer_id": "C7"},
        {"order_id": "8", "customer_id": "C8"},
        {"order_id": "9", "customer_id": "C9"},
        {"order_id": "10", "customer_id": "C10"},
        {"order_id": "11", "customer_id": "C11"},
        {"order_id": "12", "customer_id": "C12"},
        {"order_id": "13", "customer_id": "C13"},
        {"order_id": "14", "customer_id": "C14"},
        {"order_id": "15", "customer_id": "C15"},
        {"order_id": "16", "customer_id": "C16"},
        {"order_id": "17", "customer_id": "C17"},
        {"order_id": "18", "customer_id": "C18"},
        {"order_id": "19", "customer_id": "C19"},
        {"order_id": "20", "customer_id": ""},
    ]

    validate_customer_id_quality(rows)


def test_validate_customer_id_quality_rejects_threshold_exceeded():
    rows = [
        {"order_id": "1", "customer_id": ""},
        {"order_id": "2", "customer_id": ""},
        {"order_id": "3", "customer_id": "C3"},
        {"order_id": "4", "customer_id": "C4"},
        {"order_id": "5", "customer_id": "C5"},
        {"order_id": "6", "customer_id": "C6"},
        {"order_id": "7", "customer_id": "C7"},
        {"order_id": "8", "customer_id": "C8"},
        {"order_id": "9", "customer_id": "C9"},
        {"order_id": "10", "customer_id": "C10"},
    ]

    with pytest.raises(ValueError, match="customer_id"):
        validate_customer_id_quality(rows)