-- 01. Monthly Flights & Average Arrival Delay
SELECT 
    d.year,
    d.month,
    d.month_name,
    COUNT(*) AS total_flights,
    SUM(CASE WHEN f.cancelled = 0 AND f.diverted = 0 THEN 1 ELSE 0 END) AS completed_flights,
    ROUND(AVG(CASE WHEN f.cancelled = 0 AND f.diverted = 0 THEN f.arrival_delay_minutes END), 2) AS avg_arrival_delay_minutes,
    ROUND(AVG(CASE WHEN f.cancelled = 0 AND f.diverted = 0 THEN f.departure_delay_minutes END), 2) AS avg_departure_delay_minutes,
    SUM(CASE WHEN f.arrival_delay_flag = 1 THEN 1 ELSE 0 END) AS delayed_flights_count,
    ROUND(100.0 * SUM(CASE WHEN f.arrival_delay_flag = 1 THEN 1 ELSE 0 END) / 
          NULLIF(SUM(CASE WHEN f.arrival_delay_flag IS NOT NULL THEN 1 ELSE 0 END), 0), 2) AS delay_rate_pct
FROM gold_fact_flight f
JOIN gold_dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;
