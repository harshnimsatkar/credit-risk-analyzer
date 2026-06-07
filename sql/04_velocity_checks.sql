WITH ranked AS (
    SELECT
        cc_num, trans_date_trans_time, amt, is_fraud, unix_time,
        LAG(unix_time, 1) OVER (PARTITION BY cc_num ORDER BY unix_time) AS prev_1,
        LAG(unix_time, 2) OVER (PARTITION BY cc_num ORDER BY unix_time) AS prev_2,
        LAG(unix_time, 3) OVER (PARTITION BY cc_num ORDER BY unix_time) AS prev_3,
        LAG(unix_time, 4) OVER (PARTITION BY cc_num ORDER BY unix_time) AS prev_4
    FROM transactions
),
velocity AS (
    SELECT
        cc_num, trans_date_trans_time, amt, is_fraud, unix_time,
        CASE 
            WHEN (unix_time - prev_4) <= 3600 THEN 'HIGH VELOCITY'
            WHEN (unix_time - prev_2) <= 3600 THEN 'MEDIUM VELOCITY'
            ELSE 'NORMAL'
        END AS velocity_flag
    FROM ranked WHERE prev_4 IS NOT NULL
)
SELECT
    velocity_flag,
    COUNT(*) AS total_txns,
    SUM(is_fraud) AS fraud_txns,
    ROUND(SUM(is_fraud) * 100.0 / COUNT(*), 3) AS fraud_pct,
    ROUND(AVG(amt), 2) AS avg_amt
FROM velocity
GROUP BY velocity_flag
ORDER BY fraud_pct DESC