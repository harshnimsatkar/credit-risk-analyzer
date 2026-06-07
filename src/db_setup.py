import sqlite3
import pandas as pd

conn = sqlite3.connect("data/credit_risk.db")

#load fraudtrain and fraud test and combine
train = pd.read_csv("data/fraudTrain.csv")
test = pd.read_csv("data/fraudTest.csv")
transactions = pd.concat([train, test], ignore_index=True)

#Drop unnamed index column
transactions.drop(columns=["Unnamed: 0"], inplace=True)

#load creditcard.csv
cc = pd.read_csv("data/creditcard.csv")

#push to SQLite tables
transactions.to_sql("transactions", conn, if_exists="replace", index=False)
cc.to_sql("creditcard", conn, if_exists="replace", index=False)

print("Tables created:")
for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
    count = conn.execute(f"SELECT COUNT(*) FROM {row[0]}").fetchone()[0]
    print(row[0])

conn.close()