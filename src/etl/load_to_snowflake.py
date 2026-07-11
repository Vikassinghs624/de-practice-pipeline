import os
import snowflake.connector
from dotenv import load_dotenv
from src.etl.pipeline import load_sales, clean_rows, validate_customer_id_quality  # ← add this import

load_dotenv()

conn = snowflake.connector.connect(
    account=os.environ["SNOWFLAKE_ACCOUNT"],
    user=os.environ["SNOWFLAKE_USER"],
    password=os.environ["SNOWFLAKE_PASSWORD"],
    warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
    database=os.environ["SNOWFLAKE_DATABASE"],
    schema=os.environ["SNOWFLAKE_SCHEMA"],
)

rows = clean_rows(load_sales("data/raw/sales.csv"))
validate_customer_id_quality(rows)   # ← add this, BEFORE truncate/insert — will raise and stop the script if >5% missing

cur = conn.cursor()
cur.execute("TRUNCATE TABLE SALES")
for row in rows:
    cur.execute(
        "INSERT INTO SALES (order_id, customer_id, amount) VALUES (%s, %s, %s)",
        (row["order_id"], row["customer_id"], row["amount"]),
    )
conn.commit()
print(f"Loaded {len(rows)} rows into Snowflake.")
cur.close()
conn.close()