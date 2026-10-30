-- 03. Airport Departure and Arrival Delay Performance
WITH dep_stats AS (
    SELECT 
        orig.airport_code,
        orig.city_name,
        orig.state_code,
        COUNT(*) AS total_departures,
        ROUND(AVG(f.departure_delay_minutes), 2) AS avg_departure_delay,
        ROUND(100.0 * SUM(CASE WHEN f.departure_delay_minutes >= 15 THEN 1 ELSE 0 END) / COUNT(*), 2) AS dep_delay_rate_pct
    FROM gold_fact_flight f
    JOIN gold_dim_airport orig ON f.origin_airport_key = orig.airport_key
    WHERE f.cancelled = 0
    GROUP BY orig.airport_code, orig.city_name, orig.state_code
),
arr_stats AS (
    SELECT 
        dest.airport_code,
        COUNT(*) AS total_arrivals,
        ROUND(AVG(f.arrival_delay_minutes), 2) AS avg_arrival_delay,
        ROUND(100.0 * SUM(CASE WHEN f.arrival_delay_flag = 1 THEN 1 ELSE 0 END) / 
              NULLIF(SUM(CASE WHEN f.arrival_delay_flag IS NOT NULL THEN 1 ELSE 0 END), 0), 2) AS arr_delay_rate_pct
    FROM gold_fact_flight f
    JOIN gold_dim_airport dest ON f.destination_airport_key = dest.airport_key
    WHERE f.cancelled = 0 AND f.diverted = 0
    GROUP BY dest.airport_code
)
SELECT 
    d.airport_code,
    d.city_name,
    d.state_code,
    d.total_departures,
    d.avg_departure_delay,
    d.dep_delay_rate_pct,
    a.total_arrivals,
    a.avg_arrival_delay,
    a.arr_delay_rate_pct
FROM dep_stats d
LEFT JOIN arr_stats a ON d.airport_code = a.airport_code
ORDER BY d.total_departures DESC;
