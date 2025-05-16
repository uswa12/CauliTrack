import os
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from app.db import init_db



# Path to frontend build folder (adjust if different)
FRONTEND_DIST = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../frontend/dist')
)

# Initialize Flask app with static file config
app = Flask(
    __name__,
    static_folder=FRONTEND_DIST,
    static_url_path=''  # Serve at root URL
)

# List of allowed frontend origins
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",        # ✅ Vite default
    "http://127.0.0.1:5173",        # ✅ Optional (if accessed via 127.0.0.1)
    "*"                             # ✅ Fallback for dev (optional, use with caution)
]

# Enable CORS for frontend and WebSocket clients
CORS(app, origins="*")

# Flask app config
app.config['SECRET_KEY'] = 'flask123'
app.config['DATABASE_URI'] = 'postgresql://postgres:uswa123khan@localhost/mydb'

# Initialize Socket.IO with correct CORS settings
socketio = SocketIO(
    app,
    cors_allowed_origins="*"
)

# Initialize DB connection pool
db_pool = init_db(app)

# Import REST routes
from app import routes

# Register WebSocket event handlers if available
try:
    from app import socketio_handlers
except ImportError:
    print("⚠ No socketio_handlers.py found, skipping Socket.IO handlers.")


from app import summary
