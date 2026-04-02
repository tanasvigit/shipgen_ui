import { io, Socket } from 'socket.io-client';
import { API_BASE } from './api';

let socket: Socket | null = null;

export function initializeSocket(): Socket {
  if (socket?.connected) {
    return socket;
  }

  const token = localStorage.getItem('accessToken');
  if (!token) {
    throw new Error('No access token found');
  }

  // Extract base URL from API_BASE (remove /api)
  const baseUrl = API_BASE.replace('/api', '');

  socket = io(baseUrl, {
    auth: { token },
    transports: ['websocket', 'polling'],
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionAttempts: 5
  });

  socket.on('connect', () => {
    if (import.meta.env.DEV) {
      // eslint-disable-next-line no-console -- dev-only diagnostics
      console.debug('[socket] connected', socket?.id);
    }
  });

  socket.on('disconnect', () => {
    if (import.meta.env.DEV) {
      // eslint-disable-next-line no-console
      console.debug('[socket] disconnected');
    }
  });

  socket.on('connect_error', (error) => {
    if (import.meta.env.DEV) {
      // eslint-disable-next-line no-console
      console.debug('[socket] connect_error', error);
    }
  });

  return socket;
}

export function disconnectSocket(): void {
  if (socket) {
    socket.disconnect();
    socket = null;
  }
}

export function getSocket(): Socket | null {
  return socket;
}

export function onVehicleLocationUpdate(callback: (data: any) => void): void {
  if (socket) {
    socket.on('vehicle_location_update', callback);
  }
}

export function offVehicleLocationUpdate(callback: (data: any) => void): void {
  if (socket) {
    socket.off('vehicle_location_update', callback);
  }
}
