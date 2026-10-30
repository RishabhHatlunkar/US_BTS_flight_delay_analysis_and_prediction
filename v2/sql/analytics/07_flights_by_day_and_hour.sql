-- 07. Flight Counts and Delays by Day of Week and Scheduled Departure Hour
SELECT 
    d.day_name,
    d.day_of_week,
    SUBSTR(f.scheduled_departure_time, 1, 2) AS dep_hour,
    COUNT(*) AS flight_count,
    ROUND(AVG(CASE WHEN f.cancelled = 0 AND f.diverted = 0 THEN f.departure_delay_minutes END), 2) AS avg_dep_delay,
    ROUND(100.0 * SUM(CASE WHEN f.arrival_delay_flag = 1 THEN 1 ELSE 0 END) / 
          NULLIF(SUM(CASE WHEN f.arrival_delay_flag IS NOT NULL THEN 1 ELSE 0 END), 0), 2) AS delay_rate_pct
FROM gold_fact_flight f
JOIN gold_dim_date d ON f.date_key = d.date_key
WHERE f.scheduled_departure_time IS NOT NULL
GROUP BY d.day_name, d.day_of_week, dep_hour
ORDER BY d.day_of_week, dep_hour;
