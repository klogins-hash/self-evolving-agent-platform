"""
Phase 2: Redis Message Queue Integration
High-performance message queuing and caching for agent communication
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from uuid import UUID
import redis.asyncio as redis
from redis.asyncio import Redis
from pydantic import BaseSettings

from .protocol import AgentMessage, MessageType, MessageStatus, MessagePriority

logger = logging.getLogger(__name__)


class RedisSettings(BaseSettings):
    """Redis configuration settings"""
    redis_url: str = "redis://localhost:6379"
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_max_connections: int = 20
    redis_retry_on_timeout: bool = True
    redis_socket_timeout: int = 5
    redis_socket_connect_timeout: int = 5
    
    # Message queue settings
    message_queue_prefix: str = "agent_messages"
    priority_queue_prefix: str = "priority_queue"
    dead_letter_queue: str = "dead_letter_queue"
    
    # Caching settings
    cache_prefix: str = "agent_cache"
    default_cache_ttl: int = 3600  # 1 hour
    
    class Config:
        env_file = ".env"


class RedisMessageQueue:
    """Redis-based message queue for agent communication"""
    
    def __init__(self, settings: RedisSettings):
        self.settings = settings
        self.redis: Optional[Redis] = None
        self.subscribers: Dict[str, Callable] = {}
        self.running = False
        
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis = redis.from_url(
                self.settings.redis_url,
                db=self.settings.redis_db,
                password=self.settings.redis_password,
                max_connections=self.settings.redis_max_connections,
                retry_on_timeout=self.settings.redis_retry_on_timeout,
                socket_timeout=self.settings.redis_socket_timeout,
                socket_connect_timeout=self.settings.redis_socket_connect_timeout,
                decode_responses=True
            )
            
            # Test connection
            await self.redis.ping()
            logger.info("Redis connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise
    
    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            logger.info("Redis connection closed")
    
    async def enqueue_message(self, message: AgentMessage) -> bool:
        """Add message to the appropriate priority queue"""
        try:
            if not self.redis:
                raise RuntimeError("Redis not initialized")
            
            # Serialize message
            message_data = {
                "message": message.json(),
                "enqueued_at": datetime.utcnow().isoformat(),
                "attempts": 0
            }
            
            # Determine queue based on priority
            queue_name = self._get_queue_name(message.priority)
            
            # Add to queue with score based on priority and timestamp
            score = self._calculate_priority_score(message)
            
            await self.redis.zadd(
                queue_name,
                {json.dumps(message_data): score}
            )
            
            # Set expiration if specified
            if message.expires_at:
                ttl = int((message.expires_at - datetime.utcnow()).total_seconds())
                if ttl > 0:
                    await self.redis.expire(queue_name, ttl)
            
            # Publish notification for real-time processing
            await self.redis.publish(
                f"{self.settings.message_queue_prefix}:notifications",
                json.dumps({
                    "action": "new_message",
                    "queue": queue_name,
                    "message_id": str(message.message_id),
                    "recipient_id": str(message.recipient_id)
                })
            )
            
            logger.debug(f"Enqueued message {message.message_id} to {queue_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to enqueue message {message.message_id}: {str(e)}")
            return False
    
    async def dequeue_message(self, agent_id: UUID, timeout: int = 10) -> Optional[AgentMessage]:
        """Dequeue the highest priority message for an agent"""
        try:
            if not self.redis:
                raise RuntimeError("Redis not initialized")
            
            # Check all priority queues in order
            for priority in [MessagePriority.URGENT, MessagePriority.HIGH, 
                           MessagePriority.NORMAL, MessagePriority.LOW]:
                queue_name = self._get_queue_name(priority)
                
                # Get messages for this agent
                messages = await self.redis.zrange(queue_name, 0, -1, withscores=True)
                
                for message_json, score in messages:
                    message_data = json.loads(message_json)
                    message = AgentMessage.parse_raw(message_data["message"])
                    
                    # Check if message is for this agent
                    if message.recipient_id == agent_id:
                        # Remove from queue
                        await self.redis.zrem(queue_name, message_json)
                        
                        # Update message status
                        message.status = MessageStatus.DELIVERED
                        message.delivered_at = datetime.utcnow()
                        
                        logger.debug(f"Dequeued message {message.message_id} for agent {agent_id}")
                        return message
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to dequeue message for agent {agent_id}: {str(e)}")
            return None
    
    async def get_queue_size(self, priority: MessagePriority) -> int:
        """Get the size of a priority queue"""
        try:
            if not self.redis:
                return 0
            
            queue_name = self._get_queue_name(priority)
            return await self.redis.zcard(queue_name)
            
        except Exception as e:
            logger.error(f"Failed to get queue size for {priority}: {str(e)}")
            return 0
    
    async def get_pending_messages(self, agent_id: UUID) -> List[AgentMessage]:
        """Get all pending messages for an agent"""
        try:
            if not self.redis:
                return []
            
            pending_messages = []
            
            # Check all priority queues
            for priority in MessagePriority:
                queue_name = self._get_queue_name(priority)
                messages = await self.redis.zrange(queue_name, 0, -1)
                
                for message_json in messages:
                    message_data = json.loads(message_json)
                    message = AgentMessage.parse_raw(message_data["message"])
                    
                    if message.recipient_id == agent_id:
                        pending_messages.append(message)
            
            # Sort by priority and timestamp
            pending_messages.sort(
                key=lambda m: (m.priority.value, m.created_at),
                reverse=True
            )
            
            return pending_messages
            
        except Exception as e:
            logger.error(f"Failed to get pending messages for agent {agent_id}: {str(e)}")
            return []
    
    async def move_to_dead_letter_queue(self, message: AgentMessage, error: str):
        """Move failed message to dead letter queue"""
        try:
            if not self.redis:
                return
            
            dead_letter_data = {
                "message": message.json(),
                "error": error,
                "failed_at": datetime.utcnow().isoformat(),
                "original_queue": self._get_queue_name(message.priority)
            }
            
            await self.redis.lpush(
                self.settings.dead_letter_queue,
                json.dumps(dead_letter_data)
            )
            
            logger.warning(f"Moved message {message.message_id} to dead letter queue: {error}")
            
        except Exception as e:
            logger.error(f"Failed to move message to dead letter queue: {str(e)}")
    
    def _get_queue_name(self, priority: MessagePriority) -> str:
        """Get queue name for priority level"""
        return f"{self.settings.priority_queue_prefix}:{priority.value}"
    
    def _calculate_priority_score(self, message: AgentMessage) -> float:
        """Calculate priority score for message ordering"""
        # Higher score = higher priority
        priority_scores = {
            MessagePriority.URGENT: 1000,
            MessagePriority.HIGH: 100,
            MessagePriority.NORMAL: 10,
            MessagePriority.LOW: 1
        }
        
        base_score = priority_scores.get(message.priority, 10)
        
        # Add timestamp component (newer messages get slightly higher score)
        timestamp_score = message.created_at.timestamp() / 1000000
        
        return base_score + timestamp_score


class RedisCache:
    """Redis-based caching for agent data and performance optimization"""
    
    def __init__(self, redis_client: Redis, settings: RedisSettings):
        self.redis = redis_client
        self.settings = settings
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value in cache"""
        try:
            cache_key = f"{self.settings.cache_prefix}:{key}"
            ttl = ttl or self.settings.default_cache_ttl
            
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            await self.redis.setex(cache_key, ttl, str(value))
            return True
            
        except Exception as e:
            logger.error(f"Failed to set cache key {key}: {str(e)}")
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache"""
        try:
            cache_key = f"{self.settings.cache_prefix}:{key}"
            value = await self.redis.get(cache_key)
            
            if value is None:
                return None
            
            # Try to parse as JSON, fallback to string
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
                
        except Exception as e:
            logger.error(f"Failed to get cache key {key}: {str(e)}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete a value from cache"""
        try:
            cache_key = f"{self.settings.cache_prefix}:{key}"
            result = await self.redis.delete(cache_key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Failed to delete cache key {key}: {str(e)}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            cache_key = f"{self.settings.cache_prefix}:{key}"
            return await self.redis.exists(cache_key) > 0
            
        except Exception as e:
            logger.error(f"Failed to check cache key {key}: {str(e)}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a numeric value in cache"""
        try:
            cache_key = f"{self.settings.cache_prefix}:{key}"
            return await self.redis.incrby(cache_key, amount)
            
        except Exception as e:
            logger.error(f"Failed to increment cache key {key}: {str(e)}")
            return None


class RedisMessageBroker:
    """High-level message broker combining queue and cache functionality"""
    
    def __init__(self, settings: Optional[RedisSettings] = None):
        self.settings = settings or RedisSettings()
        self.queue: Optional[RedisMessageQueue] = None
        self.cache: Optional[RedisCache] = None
        self.pubsub: Optional[redis.client.PubSub] = None
        
    async def initialize(self):
        """Initialize message broker"""
        self.queue = RedisMessageQueue(self.settings)
        await self.queue.initialize()
        
        self.cache = RedisCache(self.queue.redis, self.settings)
        
        logger.info("Redis message broker initialized successfully")
    
    async def close(self):
        """Close message broker"""
        if self.queue:
            await self.queue.close()
        
        if self.pubsub:
            await self.pubsub.close()
    
    async def send_message(self, message: AgentMessage) -> bool:
        """Send a message through the queue"""
        if not self.queue:
            raise RuntimeError("Message broker not initialized")
        
        success = await self.queue.enqueue_message(message)
        
        if success:
            # Cache message for quick retrieval
            await self.cache.set(
                f"message:{message.message_id}",
                message.dict(),
                ttl=3600  # 1 hour
            )
        
        return success
    
    async def receive_message(self, agent_id: UUID) -> Optional[AgentMessage]:
        """Receive a message from the queue"""
        if not self.queue:
            raise RuntimeError("Message broker not initialized")
        
        return await self.queue.dequeue_message(agent_id)
    
    async def get_agent_status(self, agent_id: UUID) -> Optional[Dict[str, Any]]:
        """Get cached agent status"""
        if not self.cache:
            return None
        
        return await self.cache.get(f"agent_status:{agent_id}")
    
    async def set_agent_status(self, agent_id: UUID, status: Dict[str, Any], ttl: int = 300):
        """Cache agent status"""
        if not self.cache:
            return False
        
        return await self.cache.set(f"agent_status:{agent_id}", status, ttl)
    
    async def get_queue_stats(self) -> Dict[str, int]:
        """Get queue statistics"""
        if not self.queue:
            return {}
        
        stats = {}
        for priority in MessagePriority:
            stats[priority.value] = await self.queue.get_queue_size(priority)
        
        return stats


# Global message broker instance
message_broker = RedisMessageBroker()
