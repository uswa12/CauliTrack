from flask import request, jsonify
from app import app, db_pool

# 📊 Aggregate summary per phase (latest timestamp only)
@app.route('/api/summary', methods=['GET'])
def get_phase_summary():
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    phase,
                    ROUND(AVG(freshness)::numeric, 2) AS avg_freshness,
                    MIN(freshness),
                    MAX(freshness),
                    ROUND(STDDEV(freshness)::numeric, 2) AS freshness_std,
                    ROUND(AVG(temperature)::numeric, 2),
                    ROUND(AVG(humidity)::numeric, 2),
                    ROUND(AVG(airflow)::numeric, 2),
                    COUNT(*) FILTER (WHERE freshness < 70) AS warning_patches
                FROM sensor_freshness
                WHERE time = (SELECT MAX(time) FROM sensor_freshness)
                GROUP BY phase
                ORDER BY phase;
            """)
            rows = cur.fetchall()
    finally:
        db_pool.putconn(conn)

    return jsonify([
        {
            "phase": r[0],
            "avg_freshness": float(r[1]),
            "min_freshness": float(r[2]),
            "max_freshness": float(r[3]),
            "freshness_std": float(r[4]),
            "avg_temp": float(r[5]),
            "avg_humidity": float(r[6]),
            "avg_airflow": float(r[7]),
            "warning_patches": r[8]
        }
        for r in rows
    ])


# 📈 Patch-level average freshness over the last 24 hours
@app.route('/api/summary/patches', methods=['GET'])
def get_patch_averages():
    phase = request.args.get('phase')  # Optional query param
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    patch_id,
                    phase,
                    ROUND(AVG(freshness)::numeric, 2) AS avg_freshness_24h
                FROM sensor_freshness
                WHERE time >= NOW() - INTERVAL '1 day'
                AND (%s IS NULL OR phase = %s)
                GROUP BY patch_id, phase
                ORDER BY patch_id;
            """, (phase, phase))
            rows = cur.fetchall()
    finally:
        db_pool.putconn(conn)

    return jsonify([
        {
            'patch_id': r[0],
            'phase': r[1],
            'avg_freshness': float(r[2])
        }
        for r in rows
    ])
