SELECT
    CAST(strftime('%H', trans_date_trans_time) AS INTEGER) AS hour_of_day,
    COUNT(*) AS total_txns,
    SUM(is_fraud) AS fraud_txns,
    ROUND(SUM(is_fraud) * 100.0 / COUNT(*), 3) AS fraud_pct
FROM transactions
GROUP BY hour_of_day
ORDER BY hour_of_day