-- 05. Cancellation and Diversion Rates by Airline
SELECT 
    a.reporting_airline,
    COUNT(*) AS total_scheduled_flights,
    SUM(f.cancelled) AS total_cancelled,
    ROUND(100.0 * SUM(f.cancelled) / COUNT(*), 2) AS cancellation_rate_pct,
    SUM(f.diverted) AS total_diverted,
    ROUND(100.0 * SUM(f.diverted) / COUNT(*), 2) AS diversion_rate_pct,
    SUM(CASE WHEN f.cancellation_code = 'A' THEN 1 ELSE 0 END) AS cancel_carrier_carrier_code_a,
    SUM(CASE WHEN f.cancellation_code = 'B' THEN 1 ELSE 0 END) AS cancel_weather_code_b,
    SUM(CASE WHEN f.cancellation_code = 'C' THEN 1 ELSE 0 END) AS cancel_nas_code_c,
    SUM(CASE WHEN f.cancellation_code = 'D' THEN 1 ELSE 0 END) AS cancel_security_code_d
FROM gold_fact_flight f
JOIN gold_dim_airline a ON f.airline_key = a.airline_key
GROUP BY a.reporting_airline
ORDER BY cancellation_rate_pct DESC;
