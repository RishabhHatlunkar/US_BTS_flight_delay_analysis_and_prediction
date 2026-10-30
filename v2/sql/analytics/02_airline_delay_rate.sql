-- 02. Arrival Delay Rate by Airline
SELECT 
    a.reporting_airline,
    COUNT(*) AS total_flights,
    SUM(CASE WHEN f.cancelled = 1 THEN 1 ELSE 0 END) AS cancelled_flights,
    SUM(CASE WHEN f.diverted = 1 THEN 1 ELSE 0 END) AS diverted_flights,
    SUM(CASE WHEN f.arrival_delay_flag = 1 THEN 1 ELSE 0 END) AS delayed_flights,
    SUM(CASE WHEN f.arrival_delay_flag = 0 THEN 1 ELSE 0 END) AS ontime_flights,
    ROUND(100.0 * SUM(CASE WHEN f.arrival_delay_flag = 1 THEN 1 ELSE 0 END) /
          NULLIF(SUM(CASE WHEN f.arrival_delay_flag IS NOT NULL THEN 1 ELSE 0 END), 0), 2) AS delay_rate_pct,
    ROUND(AVG(CASE WHEN f.cancelled = 0 AND f.diverted = 0 THEN f.arrival_delay_minutes END), 2) AS avg_arrival_delay_minutes
FROM gold_fact_flight f
JOIN gold_dim_airline a ON f.airline_key = a.airline_key
GROUP BY a.reporting_airline
ORDER BY delay_rate_pct DESC;
