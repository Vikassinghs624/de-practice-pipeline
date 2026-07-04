from src.etl.pipeline import clean_rows, total_revenue

def test_clean_rows_skips_missing_amount():
    rows = [{"order_id": "1", "amount": "100"}, {"order_id": "2", "amount": ""}]
    result = clean_rows(rows)
    assert len(result) == 1

def test_total_revenue_sums_correctly():
    assert total_revenue([{"amount": 50.0}, {"amount": 25.5}]) == 75.5