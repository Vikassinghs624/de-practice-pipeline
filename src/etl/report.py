from src.etl.pipeline import load_sales, clean_rows, total_revenue


def revenue_summary(path):
    """Returns a small dict summary -- depends on pipeline.py's functions."""
    rows = clean_rows(load_sales(path))
    return {
        "row_count": len(rows),
        "total_revenue": total_revenue(rows),
        "average_order_value": total_revenue(rows) / len(rows) if rows else 0,
    }


if __name__ == "__main__":
    summary = revenue_summary("data/raw/sales.csv")
    print(summary)
