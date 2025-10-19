"""
REST API for querying student presence (isolated from main system)
"""
import logging
from flask import Flask, jsonify
import redis
import json
from typing import Dict, Any

# Configuration
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
PRESENCE_KEY = "student_presence"

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize Redis connection
try:
    redis_client = redis.Redis(
        host=REDIS_HOST, 
        port=REDIS_PORT, 
        db=REDIS_DB, 
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5
    )
    # Test connection
    redis_client.ping()
    logger.info("Redis connection established successfully")
except Exception as e:
    logger.error(f"Failed to connect to Redis: {e}")
    redis_client = None

@app.route('/api/presence/<student_id>', methods=['GET'])
def get_presence(student_id: str) -> tuple:
    """Get presence status for a specific student"""
    try:
        # Check if Redis is available
        if redis_client is None:
            return jsonify({"error": "Redis connection not available"}), 503
        
        data = redis_client.hget(PRESENCE_KEY, student_id)
        if data:
            try:
                info = json.loads(data) if isinstance(data, str) else {"status": "offline", "last_seen": None}
                return jsonify({
                    "student_id": student_id, 
                    "status": info["status"], 
                    "last_seen": info["last_seen"]
                }), 200
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode presence data for student {student_id}: {e}")
                return jsonify({
                    "student_id": student_id, 
                    "status": "offline", 
                    "last_seen": None
                }), 200
        
        return jsonify({
            "student_id": student_id, 
            "status": "offline", 
            "last_seen": None
        }), 200
        
    except redis.RedisError as e:
        logger.error(f"Redis error while getting presence for student {student_id}: {e}")
        return jsonify({"error": "Service temporarily unavailable"}), 503
    except Exception as e:
        logger.error(f"Unexpected error while getting presence for student {student_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/presence/all', methods=['GET'])
def get_all_presence() -> tuple:
    """Get presence status for all students"""
    try:
        # Check if Redis is available
        if redis_client is None:
            return jsonify({"error": "Redis connection not available"}), 503
        
        all_data = redis_client.hgetall(PRESENCE_KEY)
        result: Dict[str, Dict[str, Any]] = {}
        
        if isinstance(all_data, dict):
            for k, v in all_data.items():
                try:
                    result[k] = json.loads(v) if isinstance(v, str) else {"status": "offline", "last_seen": None}
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode presence data for student {k}: {e}")
                    result[k] = {"status": "offline", "last_seen": None}
        
        return jsonify(result), 200
        
    except redis.RedisError as e:
        logger.error(f"Redis error while getting all presence: {e}")
        return jsonify({"error": "Service temporarily unavailable"}), 503
    except Exception as e:
        logger.error(f"Unexpected error while getting all presence: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/health', methods=['GET'])
def health_check() -> tuple:
    """Health check endpoint"""
    try:
        if redis_client is None:
            return jsonify({
                "status": "unhealthy", 
                "redis": "not connected",
                "message": "Redis client initialization failed"
            }), 503
        
        redis_client.ping()
        return jsonify({
            "status": "healthy", 
            "redis": "connected",
            "message": "Service is running normally"
        }), 200
        
    except redis.RedisError as e:
        logger.error(f"Redis health check failed: {e}")
        return jsonify({
            "status": "unhealthy", 
            "redis": f"disconnected: {str(e)}",
            "message": "Redis connection failed"
        }), 503
    except Exception as e:
        logger.error(f"Unexpected error in health check: {e}")
        return jsonify({
            "status": "unhealthy", 
            "message": "Internal server error"
        }), 500

if __name__ == "__main__":
    logger.info("Starting IntelliAttend Presence API Server on port 5005")
    try:
        app.run(host='0.0.0.0', port=5005, debug=False)
    except Exception as e:
        logger.error(f"Failed to start API server: {e}")
        raise