-- 06. Delay Cause Breakdown by Airline
SELECT 
    a.reporting_airline,
    SUM(CASE WHEN f.arrival_delay_flag = 1 THEN 1 ELSE 0 END) AS total_delayed_flights,
    ROUND(SUM(COALESCE(f.carrier_delay_minutes, 0)), 1) AS total_carrier_delay_mins,
    ROUND(SUM(COALESCE(f.weather_delay_minutes, 0)), 1) AS total_weather_delay_mins,
    ROUND(SUM(COALESCE(f.nas_delay_minutes, 0)), 1) AS total_nas_delay_mins,
    ROUND(SUM(COALESCE(f.security_delay_minutes, 0)), 1) AS total_security_delay_mins,
    ROUND(SUM(COALESCE(f.late_aircraft_delay_minutes, 0)), 1) AS total_late_aircraft_delay_mins,
    ROUND(100.0 * SUM(COALESCE(f.carrier_delay_minutes, 0)) / 
          NULLIF(SUM(COALESCE(f.carrier_delay_minutes,0) + COALESCE(f.weather_delay_minutes,0) + 
                     COALESCE(f.nas_delay_minutes,0) + COALESCE(f.security_delay_minutes,0) + 
                     COALESCE(f.late_aircraft_delay_minutes,0)), 0), 2) AS carrier_delay_share_pct
FROM gold_fact_flight f
JOIN gold_dim_airline a ON f.airline_key = a.airline_key
WHERE f.arrival_delay_flag = 1
GROUP BY a.reporting_airline
ORDER BY total_delayed_flights DESC;
