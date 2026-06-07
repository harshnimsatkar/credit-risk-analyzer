import pandas as pd
import sqlite3

def load_transactions(db_path="../data/credit_risk.db"):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()
    return df

def load_creditcard(db_path="../data/credit_risk.db"):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM creditcard", conn)
    conn.close()
    return df