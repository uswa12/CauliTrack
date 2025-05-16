# run.py

# Must be first: Patch standard library for eventlet support
import eventlet
eventlet.monkey_patch()

# Now safe to import other modules
import os
import logging

# Import your Flask app and SocketIO instance
from app import app, socketio

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Static Folder Debug Info
logger.info(f"♦ static_folder: {app.static_folder}")
logger.info(f"♦ Exists on disk?: {os.path.exists(app.static_folder)}")

# Run the SocketIO server
if __name__ == '__main__':
    logger.info("🚀 Starting Flask-SocketIO server with eventlet...")
    socketio.run(
        app,
        host='0.0.0.0',     # Accessible from any IP in the local network
        port=5000,
        debug=True,
        use_reloader=True,  # Auto-reload on code changes
        log_output=True
    )
