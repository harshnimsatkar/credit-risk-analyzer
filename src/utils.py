import os
import pickle
import sqlite3
import pandas as pd
from src.logger import logger
from src.exception import CreditRiskException
import sys


def save_object(file_path: str, obj):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            pickle.dump(obj, f)
        logger.info(f"Object saved at: {file_path}")
    except Exception as e:
        raise CreditRiskException(e, sys)


def load_object(file_path: str):
    try:
        with open(file_path, "rb") as f:
            obj = pickle.load(f)
        logger.info(f"Object loaded from: {file_path}")
        return obj
    except Exception as e:
        raise CreditRiskException(e, sys)


def run_sql_query(query: str, db_path: str) -> pd.DataFrame:
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()
        logger.info(f"SQL query executed — {len(df)} rows returned")
        return df
    except Exception as e:
        raise CreditRiskException(e, sys)


def load_sql_file(sql_file: str, db_path: str) -> pd.DataFrame:
    try:
        with open(sql_file, "r") as f:
            query = f.read()
        return run_sql_query(query, db_path)
    except Exception as e:
        raise CreditRiskException(e, sys)