# backend/app/routes.py

import os
from flask import request, jsonify, send_from_directory
from app import app, socketio, db_pool

@app.route('/')
def index():
    # This will now serve the React index.html if it exists
    return send_from_directory(app.static_folder, 'index.html')

# Existing simulation control endpoints
@app.route('/start/<phase>', methods=['POST'])
def start_phase(phase):
    from app.simulation import sim_manager
    sim_manager.start_phase(phase)
    return jsonify({'status': 'started', 'phase': phase}), 200

@app.route('/stop/<phase>', methods=['POST'])
def stop_phase(phase):
    from app.simulation import sim_manager
    sim_manager.stop_phase(phase)
    return jsonify({'status': 'stopped', 'phase': phase}), 200

# NEW: Historical data endpoint
@app.route('/api/history')
def get_history():
    """
    Query TimescaleDB for all (time, freshness) rows
    for the given patch_id and phase, ordered by time.
    """
    # 1) Extract query params
    patch_id = request.args.get('patch_id', type=int)
    phase    = request.args.get('phase', type=str)

    if not patch_id or not phase:
        return jsonify({'error': 'patch_id and phase are required'}), 400

    # 2) Pull a connection from the pool
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                  EXTRACT(EPOCH FROM time) * 1000 AS timestamp,
                  freshness
                FROM sensor_freshness
                WHERE patch_id = %s AND phase = %s
                ORDER BY time;
            """, (patch_id, phase))
            rows = cur.fetchall()
    finally:
        db_pool.putconn(conn)

    # 3) Format and return JSON
    result = [
        {'timestamp': int(r[0]), 'freshness': r[1]}
        for r in rows
    ]
    return jsonify(result), 200

# NEW: Serve all other frontend routes (so React Router works)
@app.route('/<path:path>')
def serve_frontend(path):
    """
    If the requested file exists in frontend/dist, serve it;
    otherwise fall back to index.html so client‑side routing works.
    """
    full_path = os.path.join(app.static_folder, path)
    if os.path.exists(full_path):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')
