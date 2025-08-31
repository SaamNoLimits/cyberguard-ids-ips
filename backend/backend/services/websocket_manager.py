"""
WebSocket Manager for real-time communication
"""

import json
import logging
from typing import List, Dict, Any
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_info: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_info[websocket] = {
            "connected_at": "now",
            "user_id": None,
            "subscriptions": []
        }
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            self.connection_info.pop(websocket, None)
            logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific WebSocket"""
        if websocket not in self.active_connections:
            return
        
        try:
            # Check if websocket is still open
            if websocket.client_state.name == 'CONNECTED':
                await websocket.send_text(message)
            else:
                self.disconnect(websocket)
        except Exception as e:
            # Only log actual errors, not normal disconnections
            if "1001" not in str(e) and "1005" not in str(e):
                logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        """Broadcast message to all connected WebSockets"""
        disconnected = []
        for connection in self.active_connections.copy():  # Use copy to avoid modification during iteration
            try:
                # Check if websocket is still open
                if connection.client_state.name == 'CONNECTED':
                    await connection.send_text(message)
                else:
                    disconnected.append(connection)
            except Exception as e:
                # Only log actual errors, not normal disconnections
                if "1001" not in str(e) and "1005" not in str(e):
                    logger.error(f"Error broadcasting message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_json(self, data: Dict[str, Any]):
        """Broadcast JSON data to all connections"""
        message = json.dumps(data)
        await self.broadcast(message)
    
    async def send_to_user(self, user_id: str, message: str):
        """Send message to specific user"""
        for websocket, info in self.connection_info.items():
            if info.get("user_id") == user_id:
                await self.send_personal_message(message, websocket)
    
    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)
    
    async def set_user_id(self, websocket: WebSocket, user_id: str):
        """Associate user ID with WebSocket connection"""
        if websocket in self.connection_info:
            self.connection_info[websocket]["user_id"] = user_id
    
    async def subscribe_to_topic(self, websocket: WebSocket, topic: str):
        """Subscribe WebSocket to specific topic"""
        if websocket in self.connection_info:
            subscriptions = self.connection_info[websocket]["subscriptions"]
            if topic not in subscriptions:
                subscriptions.append(topic)
    
    async def unsubscribe_from_topic(self, websocket: WebSocket, topic: str):
        """Unsubscribe WebSocket from topic"""
        if websocket in self.connection_info:
            subscriptions = self.connection_info[websocket]["subscriptions"]
            if topic in subscriptions:
                subscriptions.remove(topic)
    
    async def broadcast_to_topic(self, topic: str, message: str):
        """Broadcast message to subscribers of specific topic"""
        for websocket, info in self.connection_info.items():
            if topic in info.get("subscriptions", []):
                await self.send_personal_message(message, websocket)
