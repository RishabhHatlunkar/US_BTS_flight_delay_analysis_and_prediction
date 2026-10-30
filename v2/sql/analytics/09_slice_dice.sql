-- 09. OLAP Slice and Dice: Filtered by Year, Airlines, and Top Airport Pairs
SELECT 
    d.year,
    a.reporting_airline,
    orig.airport_code AS origin_airport,
    dest.airport_code AS destination_airport,
    COUNT(*) AS flight_count,
    ROUND(AVG(f.departure_delay_minutes), 2) AS avg_dep_delay,
    ROUND(AVG(f.arrival_delay_minutes), 2) AS avg_arr_delay,
    SUM(f.cancelled) AS cancellations
FROM gold_fact_flight f
JOIN gold_dim_date d ON f.date_key = d.date_key
JOIN gold_dim_airline a ON f.airline_key = a.airline_key
JOIN gold_dim_airport orig ON f.origin_airport_key = orig.airport_key
JOIN gold_dim_airport dest ON f.destination_airport_key = dest.airport_key
WHERE d.year IN (2024, 2025)
GROUP BY d.year, a.reporting_airline, orig.airport_code, dest.airport_code
ORDER BY flight_count DESC
LIMIT 25;
