# Tasks

1. [x] Add unit tests for customer_id validation behavior in [tests/test_pipeline.py](tests/test_pipeline.py) and a failing case for threshold breach.
2. [x] Implement `validate_customer_id_quality` in [src/etl/pipeline.py](src/etl/pipeline.py) with threshold handling and logging.
3. [x] Update [src/etl/load_to_snowflake.py](src/etl/load_to_snowflake.py) to invoke the validation step before any `INSERT` statements.
4. [x] Ensure failures stop the load and produce an error-level log entry instead of inserting bad data.
5. [x] Run the test suite and adjust the implementation until the new checks pass.
