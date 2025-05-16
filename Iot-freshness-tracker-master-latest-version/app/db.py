# backend/app/db.py

import psycopg2
import psycopg2.extras
from psycopg2.pool import ThreadedConnectionPool
from flask import current_app

# db connection pool
_db_pool = None

def init_db(app):
    """
    Initialize a global ThreadedConnectionPool using app.config['DATABASE_URI'].
    Returns the pool for use in other modules.
    """
    global _db_pool
    _db_pool = ThreadedConnectionPool(
        minconn=1,
        maxconn=20,
        dsn=app.config['DATABASE_URI']
    )
    return _db_pool

def insert_sensor_data(rows):
    """
    Batch-insert many sensor_freshness rows.
    `rows` is a list of tuples in the order:
      (time, patch_id, phase, temperature, humidity,
       sunlight, soil_moisture, airflow, vibration, freshness)
    """
    sql = """
    INSERT INTO sensor_freshness
      (time, patch_id, phase, temperature, humidity,
       sunlight, soil_moisture, airflow, vibration, freshness)
    VALUES %s
    """
    conn = _db_pool.getconn()
    try:
        with conn.cursor() as cur:
            # execute_values packs the rows into one INSERT for speed
            psycopg2.extras.execute_values(cur, sql, rows, page_size=100)
        conn.commit()
    except Exception as e:
        print("❌ DB INSERT FAILED:", e)
        print("❌ First few rows:", rows[:3])
    finally:
        _db_pool.putconn(conn)
