"""
IntelliAttend Real-Time Presence WebSocket Server
This module adds real-time online/offline tracking for students using WebSocket and Redis.
It is fully isolated from existing system functionality.
"""
import asyncio
import websockets
import json
import redis.asyncio as redis
import logging
from datetime import datetime
from typing import Dict, Optional

# Configuration
REDIS_URL = "redis://localhost:6379/0"
PRESENCE_KEY = "student_presence"
HEARTBEAT_TIMEOUT = 60  # seconds
HEARTBEAT_CHECK_INTERVAL = 10  # seconds

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def update_presence(redis_client, student_id: str, status: str) -> None:
    """Update student presence status in Redis"""
    try:
        now = datetime.utcnow().isoformat()
        presence_data = {
            "status": status,
            "last_seen": now
        }
        await redis_client.hset(PRESENCE_KEY, student_id, json.dumps(presence_data))
        logger.info(f"Updated presence for student {student_id}: {status}")
    except Exception as e:
        logger.error(f"Failed to update presence for student {student_id}: {e}")
        raise

async def get_presence(redis_client, student_id: str) -> Dict:
    """Get presence status for a specific student"""
    try:
        data = await redis_client.hget(PRESENCE_KEY, student_id)
        if data:
            return json.loads(data)
        return {"status": "offline", "last_seen": None}
    except Exception as e:
        logger.error(f"Failed to get presence for student {student_id}: {e}")
        return {"status": "offline", "last_seen": None}

async def get_all_presence(redis_client) -> Dict:
    """Get presence status for all students"""
    try:
        all_data = await redis_client.hgetall(PRESENCE_KEY)
        return {k.decode(): json.loads(v) for k, v in all_data.items()}
    except Exception as e:
        logger.error(f"Failed to get all presence data: {e}")
        return {}

# Global state - in production, consider using a proper state management solution
connected_students: Dict[str, websockets.WebSocketServerProtocol] = {}

async def handler(websocket: websockets.WebSocketServerProtocol) -> None:
    """Handle WebSocket connections for student presence tracking"""
    redis_client = None
    student_id: Optional[str] = None
    
    try:
        # Initialize Redis connection
        redis_client = redis.Redis.from_url(REDIS_URL)
        
        async for message in websocket:
            try:
                data = json.loads(message)
                event = data.get("event")
                
                if event == "connect":
                    student_id = data["student_id"]
                    connected_students[student_id] = websocket
                    await update_presence(redis_client, student_id, "online")
                    await websocket.send(json.dumps({"event": "connected", "student_id": student_id}))
                    logger.info(f"Student {student_id} connected")
                    
                elif event == "ping":
                    student_id = data["student_id"]
                    await update_presence(redis_client, student_id, "online")
                    await websocket.send(json.dumps({"event": "pong", "student_id": student_id}))
                    
                else:
                    logger.warning(f"Unknown event received: {event}")
                    
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON message received: {e}")
                await websocket.send(json.dumps({"error": "Invalid message format"}))
                
    except websockets.ConnectionClosed:
        logger.info(f"WebSocket connection closed for student {student_id}")
        if student_id:
            await update_presence(redis_client, student_id, "offline")
        if student_id in connected_students:
            del connected_students[student_id]
            
    except Exception as e:
        logger.error(f"Handler error for student {student_id}: {e}")
        if student_id:
            await update_presence(redis_client, student_id, "offline")
        if student_id in connected_students:
            del connected_students[student_id]
            
    finally:
        # Cleanup connection
        if student_id and student_id in connected_students:
            del connected_students[student_id]
        logger.info(f"Cleaned up connection for student {student_id}")

async def heartbeat_monitor() -> None:
    """Monitor student connections and mark as offline if no heartbeat received"""
    redis_client = redis.Redis.from_url(REDIS_URL)
    
    while True:
        try:
            all_presence = await get_all_presence(redis_client)
            now = datetime.utcnow()
            
            for student_id, info in all_presence.items():
                last_seen = info.get("last_seen")
                if last_seen:
                    try:
                        last_dt = datetime.fromisoformat(last_seen)
                        if (now - last_dt).total_seconds() > HEARTBEAT_TIMEOUT:
                            await update_presence(redis_client, student_id, "offline")
                            logger.info(f"Marked student {student_id} as offline due to timeout")
                    except ValueError as e:
                        logger.error(f"Invalid datetime format for student {student_id}: {e}")
                        
            await asyncio.sleep(HEARTBEAT_CHECK_INTERVAL)
            
        except Exception as e:
            logger.error(f"Error in heartbeat monitor: {e}")
            await asyncio.sleep(HEARTBEAT_CHECK_INTERVAL)

async def main() -> None:
    """Main entry point for the WebSocket server"""
    try:
        logger.info("Starting IntelliAttend Real-Time Presence WebSocket Server on port 8765")
        server = await websockets.serve(handler, "0.0.0.0", 8765)
        logger.info("WebSocket server started successfully")
        
        # Start heartbeat monitor
        asyncio.create_task(heartbeat_monitor())
        logger.info("Heartbeat monitor started")
        
        # Keep server running
        await server.wait_closed()
        logger.info("WebSocket server stopped")
        
    except Exception as e:
        logger.error(f"Failed to start WebSocket server: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
