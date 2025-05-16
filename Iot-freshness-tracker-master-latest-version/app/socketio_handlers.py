# backend/app/socketio_handlers.py
from app import socketio
from flask import request
from flask_socketio import emit, join_room, leave_room
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@socketio.on('connect')
def handle_connect():
    """Handle client connection to Socket.IO server"""
    logger.info(f"Client connected: {request.sid}")
    emit('welcome', {'message': 'Connected to IoT Sensor Simulator'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnect from Socket.IO server"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('join')
def handle_join(data):
    """Handle client joining a specific room (e.g., for a specific patch or phase)"""
    room = data.get('room')
    if room:
        join_room(room)
        logger.info(f"Client {request.sid} joined room: {room}")
        emit('room_joined', {'room': room}, room=room)

@socketio.on('leave')
def handle_leave(data):
    """Handle client leaving a specific room"""
    room = data.get('room')
    if room:
        leave_room(room)
        logger.info(f"Client {request.sid} left room: {room}")

# Test event - can be removed in production
@socketio.on('ping')
def handle_ping(data):
    """Respond to ping event from client"""
    logger.info(f"Received ping from client: {data}")
    emit('pong', {'server_time': datetime.now().isoformat()})

# Add a test event that returns current sensor readings
@socketio.on('get_current_readings')
def handle_get_readings(data):
    """Provide current sensor readings for testing"""
    logger.info(f"Client requested current readings")
    
    # Import here to avoid circular imports
    from app.simulation import sim_manager
    
    # Generate sample readings
    phase = data.get('phase', 'farm')
    timestamp = datetime.now()
    readings = sim_manager._simulate_phase(phase, timestamp)
    
    # Send back to the client
    emit('current_readings', {
        'time': timestamp.isoformat(),
        'phase': phase,
        'patch_id': data.get('patch_id', 1),
        **readings
    })