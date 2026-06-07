import sqlite3
import pandas as pd

def run_sql_file(sql_file, db_path="../data/credit_risk.db"):
    conn = sqlite3.connect(db_path)
    with open(sql_file, "r") as f:
        query = f.read()
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

if __name__ == "__main__":
    for sql in ["../sql/02_fraud_rate_by_hour.sql",
                "../sql/03_merchant_risk.sql",
                "../sql/04_velocity_checks.sql",
                "../sql/05_high_risk_profiles.sql"]:
        print(f"\n=== {sql} ===")
        print(run_sql_file(sql).to_string(index=False))