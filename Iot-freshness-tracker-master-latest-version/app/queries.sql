SELECT * from sensor_freshness order by time desc limit 10;

-- how many patches inserted at a timestamp
SELECT time, COUNT(*) AS records, COUNT(DISTINCT patch_id) AS unique_patches
FROM sensor_freshness
WHERE phase = 'farm'
GROUP BY time
ORDER BY time DESC
LIMIT 5;

-- which patch ids inserted at a timestamp
SELECT patch_id, freshness
FROM sensor_freshness
WHERE time = (
    SELECT time
    FROM sensor_freshness
    WHERE phase = 'farm'
    ORDER BY time DESC
    LIMIT 1
)
ORDER BY patch_id;

-- check if freshness index varies across patches
SELECT patch_id, freshness
FROM sensor_freshness
WHERE time = (
    SELECT time
    FROM sensor_freshness
    ORDER BY time DESC
    LIMIT 1
)
ORDER BY patch_id;


-- clear stored data
TRUNCATE TABLE sensor_freshness;
