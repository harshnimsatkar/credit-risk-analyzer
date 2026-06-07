-- total row counts
SELECT 'transactions' as table_name, COUNT(*) as total_rows FROM transactions
UNION ALL
SELECT 'creditcard', COUNT(*) FROM creditcard;

-- fraud vs legit split - transactions table
SELECT CASE is_fraud WHEN 1 THEN 'Fraud' ELSE 'Legit' END AS label,
COUNT(*) AS total,
ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM transactions), 3) AS pct
FROM transactions
GROUP BY is_fraud;

-- fraud vs legit split - creditcard table
SELECT CASE Class WHEN 1 THEN 'Fraud' ELSE 'Legit' END AS label,
COUNT (*) AS total,
ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM creditcard),3) AS pct
FROM creditcard
GROUP BY Class;

-- unique merchant categories
SELECT DISTINCT category FROM transactions ORDER BY category;

-- Transaction amount stats by fraud label
SELECT
CASE is_fraud WHEN 1 THEN 'Fraud' ELSE 'Legit' END AS label,
ROUND(MIN(amt), 2) AS min_amt,
ROUND(MAX(amt), 2) AS max_amt,
ROUND(AVG(amt), 2) AS avg_amt
FROM transactions
GROUP BY is_fraud;