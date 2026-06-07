WITH velocity_flags AS (
    SELECT
        cc_num, trans_date_trans_time, amt, is_fraud, category, unix_time,
        CAST(strftime('%H', trans_date_trans_time) AS INTEGER) AS hour_of_day,
        LAG(unix_time, 4) OVER (PARTITION BY cc_num ORDER BY unix_time) AS prev_4
    FROM transactions
),
scored AS (
    SELECT *, 
        CASE WHEN hour_of_day BETWEEN 0 AND 3 
             OR hour_of_day IN (22,23) THEN 1 ELSE 0 END AS night_flag,
        CASE WHEN category IN ('shopping_net','misc_net','grocery_pos') 
             THEN 1 ELSE 0 END AS merchant_flag,
        CASE WHEN prev_4 IS NOT NULL 
             AND (unix_time - prev_4) <= 3600 THEN 1 ELSE 0 END AS velocity_flag,
        CASE WHEN amt > 500 THEN 1 ELSE 0 END AS amount_flag
    FROM velocity_flags
),
risk_tiered AS (
    SELECT *,
        (night_flag + merchant_flag + velocity_flag + amount_flag) AS risk_score,
        CASE
            WHEN (night_flag + merchant_flag + velocity_flag + amount_flag) >= 3 THEN 'CRITICAL'
            WHEN (night_flag + merchant_flag + velocity_flag + amount_flag) = 2  THEN 'HIGH'
            WHEN (night_flag + merchant_flag + velocity_flag + amount_flag) = 1  THEN 'MEDIUM'
            ELSE 'LOW'
        END AS risk_tier
    FROM scored
)
SELECT
    risk_tier,
    COUNT(*) AS total_txns,
    SUM(is_fraud) AS fraud_txns,
    ROUND(SUM(is_fraud) * 100.0 / COUNT(*), 3) AS fraud_pct,
    ROUND(AVG(amt), 2) AS avg_amt
FROM risk_tiered
GROUP BY risk_tier
ORDER BY CASE risk_tier 
    WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2 
    WHEN 'MEDIUM' THEN 3 ELSE 4 END