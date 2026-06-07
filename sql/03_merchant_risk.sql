SELECT
    category,
    COUNT(*)AS total_txns,
    SUM(is_fraud) AS fraud_txns,
    ROUND(SUM(is_fraud) * 100.0 / COUNT(*), 3) AS fraud_pct,
    ROUND(AVG(amt), 2) AS avg_amt,
    ROUND(SUM(CASE WHEN is_fraud=1 THEN amt ELSE 0 END), 2) AS total_fraud_amt
FROM transactions
GROUP BY category
ORDER BY fraud_pct DESC