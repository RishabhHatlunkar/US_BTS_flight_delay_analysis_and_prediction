-- 10. Semantic NULL and Delay Outcome Integrity Check
SELECT 
    'Cancelled Flights' AS flight_category,
    COUNT(*) AS total_records,
    SUM(CASE WHEN arrival_delay_flag = 0 THEN 1 ELSE 0 END) AS incorrectly_marked_ontime,
    SUM(CASE WHEN arrival_delay_flag IS NULL THEN 1 ELSE 0 END) AS correctly_marked_null
FROM gold_fact_flight
WHERE cancelled = 1

UNION ALL

SELECT 
    'Diverted Flights (No Arrival Delay Recorded)' AS flight_category,
    COUNT(*) AS total_records,
    SUM(CASE WHEN arrival_delay_flag = 0 THEN 1 ELSE 0 END) AS incorrectly_marked_ontime,
    SUM(CASE WHEN arrival_delay_flag IS NULL THEN 1 ELSE 0 END) AS correctly_marked_null
FROM gold_fact_flight
WHERE diverted = 1 AND arrival_delay_minutes IS NULL

UNION ALL

SELECT 
    'Completed On-Time Flights (< 15 mins)' AS flight_category,
    COUNT(*) AS total_records,
    SUM(CASE WHEN arrival_delay_flag = 0 THEN 1 ELSE 0 END) AS correctly_marked_ontime,
    SUM(CASE WHEN arrival_delay_flag IS NULL THEN 1 ELSE 0 END) AS null_flag_count
FROM gold_fact_flight
WHERE cancelled = 0 AND diverted = 0 AND arrival_delay_minutes < 15.0;
