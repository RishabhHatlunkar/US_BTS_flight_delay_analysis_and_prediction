-- 08. OLAP Roll-up & Drill-down: Year -> Quarter -> Month -> Airline
SELECT 
    d.year,
    d.quarter,
    d.month,
    a.reporting_airline,
    COUNT(*) AS total_flights,
    ROUND(AVG(CASE WHEN f.cancelled = 0 AND f.diverted = 0 THEN f.arrival_delay_minutes END), 2) AS avg_arr_delay,
    ROUND(100.0 * SUM(CASE WHEN f.arrival_delay_flag = 1 THEN 1 ELSE 0 END) / 
          NULLIF(SUM(CASE WHEN f.arrival_delay_flag IS NOT NULL THEN 1 ELSE 0 END), 0), 2) AS delay_rate_pct
FROM gold_fact_flight f
JOIN gold_dim_date d ON f.date_key = d.date_key
JOIN gold_dim_airline a ON f.airline_key = a.airline_key
GROUP BY d.year, d.quarter, d.month, a.reporting_airline
ORDER BY d.year, d.quarter, d.month, total_flights DESC;
