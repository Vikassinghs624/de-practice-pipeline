# Proposal: Add customer_id data quality validation before Snowflake load

## Summary
Add a batch-level data quality gate to the ETL load path so rows with missing customer_id values are detected before insertion into Snowflake. If the percentage of null customer_id values in a batch exceeds 5%, the load is rejected and an error is logged instead of inserting bad data.

## Why
The current pipeline only cleans obvious bad amounts. Missing customer IDs can silently propagate to Snowflake and break downstream analytics or customer joins. A threshold-based reject policy prevents bad batches from contaminating warehouse data while keeping the pipeline deterministic.

## Scope
- Add a reusable validation step in the ETL pipeline for null customer_id values.
- Enforce a 5% threshold per batch.
- Reject the load and log an error when the threshold is exceeded.
- Cover the behavior with unit tests.

## Non-goals
- Rewriting the Snowflake loader or introducing a new orchestration framework.
- Automatically repairing or imputing missing customer IDs.

## Success criteria
- A batch with 5% or fewer missing customer_id values continues to load.
- A batch with more than 5% missing customer_id values is rejected before insert.
- The failure is surfaced through logging and a clear exception.
