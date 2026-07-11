# Design: customer_id quality gate for ETL loads

## Overview
Introduce a validation function in the ETL pipeline that evaluates a batch of rows before they are written to Snowflake. The validation runs after basic cleaning and before any SQL inserts.

## Proposed flow
1. `load_sales` reads rows from disk.
2. `clean_rows` continues to normalize amounts and remove rows that fail obvious data-quality checks.
3. A new function, `validate_customer_id_quality(rows, threshold=0.05)`, computes the ratio of rows with missing or empty customer_id values.
4. If the ratio exceeds the threshold, the loader logs an error and raises an exception before any inserts occur.
5. If the ratio is within the threshold, the existing Snowflake insert loop proceeds unchanged.

## Function contract
- Input: a list of row dictionaries.
- Output: `None` on success; raise `ValueError` on threshold breach.
- Behavior:
  - Treat `None`, empty string, and whitespace-only values as missing.
  - Use `len(rows)` as the batch denominator.
  - Compare `missing_count / total_count` against `0.05`.

## Logging and failure handling
- Use the existing module logger to emit an error message including batch size and missing count.
- In the Snowflake loader, catch the validation exception and log a clear failure message without attempting inserts.

## Testing approach
- Unit tests cover the pass path and the threshold-breach path.
- Loader-level tests confirm the insert loop is skipped when validation fails.
