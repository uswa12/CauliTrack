import { useEffect, useState, useRef } from 'react';
import { io } from 'socket.io-client';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000';

export default function useSocketIO() {
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState([]);  // ✅ Store array of messages
  const socketRef = useRef(null);

  useEffect(() => {
    const socket = io(API_BASE, {
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      autoConnect: true,
      transports: ['websocket', 'polling']
    });

    socketRef.current = socket;

    socket.on('connect', () => {
      console.log('✅ Socket connected:', socket.id);
      setIsConnected(true);
      socket.emit('ping', { message: 'Hello from client' });
    });

    socket.on('disconnect', (reason) => {
      console.log('❌ Socket disconnected:', reason);
      setIsConnected(false);
    });

    socket.on('connect_error', (error) => {
      console.error('Socket connection error:', error.message);
      if (error.message.includes('CORS')) {
        console.log('Trying different transport...');
        socket.io.opts.transports = ['polling', 'websocket'];
      }
    });

    socket.on('welcome', (data) => {
      console.log('Received welcome:', data);
    });

    socket.on('pong', (data) => {
      console.log('Received pong:', data);
    });

    // ✅ Append each update to message list
    socket.on('sensor_update', (data) => {
      console.log('Received sensor update:', data);
      setMessages(prev => [...prev, data]);
    });

    return () => {
      console.log('Cleaning up socket connection');
      socket.disconnect();
    };
  }, []);

  return {
    socket: socketRef.current,
    isConnected,
    messages  // ✅ Return the full array for the chart
  };
}
