-- 04. Top Routes by Average Arrival Delay (with volume safeguard)
SELECT 
    r.route_code,
    orig.airport_code AS origin_code,
    dest.airport_code AS dest_code,
    COUNT(*) AS total_flights,
    ROUND(AVG(CASE WHEN f.cancelled = 0 AND f.diverted = 0 THEN f.arrival_delay_minutes END), 2) AS avg_arrival_delay_minutes,
    ROUND(100.0 * SUM(CASE WHEN f.arrival_delay_flag = 1 THEN 1 ELSE 0 END) / 
          NULLIF(SUM(CASE WHEN f.arrival_delay_flag IS NOT NULL THEN 1 ELSE 0 END), 0), 2) AS delay_rate_pct
FROM gold_fact_flight f
JOIN gold_dim_route r ON f.route_key = r.route_key
JOIN gold_dim_airport orig ON f.origin_airport_key = orig.airport_key
JOIN gold_dim_airport dest ON f.destination_airport_key = dest.airport_key
GROUP BY r.route_code, orig.airport_code, dest.airport_code
HAVING COUNT(*) >= 10
ORDER BY avg_arrival_delay_minutes DESC
LIMIT 20;
