"""
Phase 2: Message Handler System
Processes and routes messages between agents
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from uuid import UUID

from .protocol import (
    AgentMessage, MessageType, MessageStatus, MessagePriority,
    TaskDelegationMessage, StatusUpdateMessage, CapabilityInquiryMessage,
    CapabilityResponseMessage, MessageValidator
)

logger = logging.getLogger(__name__)


class MessageHandler:
    """Handles message processing, routing, and delivery"""
    
    def __init__(self):
        self.message_handlers: Dict[MessageType, Callable] = {}
        self.pending_messages: Dict[UUID, AgentMessage] = {}
        self.message_history: List[AgentMessage] = []
        self.delivery_callbacks: Dict[UUID, Callable] = {}
        
    def register_handler(self, message_type: MessageType, handler: Callable):
        """Register a handler function for a specific message type"""
        self.message_handlers[message_type] = handler
        logger.info(f"Registered handler for {message_type}")
    
    async def process_message(self, message: AgentMessage) -> bool:
        """Process an incoming message"""
        try:
            # Validate message
            is_valid, error = MessageValidator.validate_message(message)
            if not is_valid:
                logger.error(f"Invalid message {message.message_id}: {error}")
                await self._mark_message_failed(message, error)
                return False
            
            # Update message status
            message.status = MessageStatus.DELIVERED
            message.delivered_at = datetime.utcnow()
            
            # Route to appropriate handler
            if message.message_type in self.message_handlers:
                handler = self.message_handlers[message.message_type]
                success = await handler(message)
                
                if success:
                    message.status = MessageStatus.ACKNOWLEDGED
                    message.acknowledged_at = datetime.utcnow()
                    logger.info(f"Successfully processed message {message.message_id}")
                else:
                    await self._mark_message_failed(message, "Handler returned False")
                    return False
            else:
                logger.warning(f"No handler registered for {message.message_type}")
                await self._mark_message_failed(message, "No handler available")
                return False
            
            # Store in history
            self.message_history.append(message)
            
            # Execute delivery callback if exists
            if message.message_id in self.delivery_callbacks:
                callback = self.delivery_callbacks[message.message_id]
                await callback(message)
                del self.delivery_callbacks[message.message_id]
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing message {message.message_id}: {str(e)}")
            await self._mark_message_failed(message, str(e))
            return False
    
    async def send_message(self, message: AgentMessage, 
                          delivery_callback: Optional[Callable] = None) -> bool:
        """Send a message to another agent"""
        try:
            # Validate message before sending
            is_valid, error = MessageValidator.validate_message(message)
            if not is_valid:
                logger.error(f"Cannot send invalid message: {error}")
                return False
            
            # Update message status
            message.status = MessageStatus.SENT
            message.created_at = datetime.utcnow()
            
            # Store pending message
            self.pending_messages[message.message_id] = message
            
            # Register delivery callback
            if delivery_callback:
                self.delivery_callbacks[message.message_id] = delivery_callback
            
            # TODO: Integrate with Redis message queue for actual delivery
            # For now, simulate message delivery
            await self._simulate_message_delivery(message)
            
            logger.info(f"Sent message {message.message_id} from {message.sender_id} to {message.recipient_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return False
    
    async def _simulate_message_delivery(self, message: AgentMessage):
        """Simulate message delivery (replace with Redis integration)"""
        # Simulate network delay
        await asyncio.sleep(0.1)
        
        # For now, just mark as delivered
        # In real implementation, this would push to Redis queue
        message.status = MessageStatus.DELIVERED
        message.delivered_at = datetime.utcnow()
    
    async def _mark_message_failed(self, message: AgentMessage, error: str):
        """Mark a message as failed"""
        message.status = MessageStatus.FAILED
        logger.error(f"Message {message.message_id} failed: {error}")
        
        # Retry logic
        if message.retry_count < message.max_retries:
            message.retry_count += 1
            logger.info(f"Retrying message {message.message_id} (attempt {message.retry_count})")
            await asyncio.sleep(2 ** message.retry_count)  # Exponential backoff
            await self.send_message(message)
    
    def get_message_history(self, agent_id: UUID, limit: int = 100) -> List[AgentMessage]:
        """Get message history for an agent"""
        agent_messages = [
            msg for msg in self.message_history
            if msg.sender_id == agent_id or msg.recipient_id == agent_id
        ]
        return sorted(agent_messages, key=lambda x: x.created_at, reverse=True)[:limit]
    
    def get_pending_messages(self, agent_id: UUID) -> List[AgentMessage]:
        """Get pending messages for an agent"""
        return [
            msg for msg in self.pending_messages.values()
            if msg.recipient_id == agent_id and msg.status in [MessageStatus.PENDING, MessageStatus.SENT]
        ]


class AgentCommunicationManager:
    """Manages communication between agents"""
    
    def __init__(self):
        self.message_handler = MessageHandler()
        self.agent_connections: Dict[UUID, bool] = {}  # Track agent online status
        self.setup_default_handlers()
    
    def setup_default_handlers(self):
        """Set up default message handlers"""
        self.message_handler.register_handler(
            MessageType.TASK_DELEGATION, 
            self._handle_task_delegation
        )
        self.message_handler.register_handler(
            MessageType.STATUS_UPDATE, 
            self._handle_status_update
        )
        self.message_handler.register_handler(
            MessageType.CAPABILITY_INQUIRY, 
            self._handle_capability_inquiry
        )
        self.message_handler.register_handler(
            MessageType.CAPABILITY_RESPONSE, 
            self._handle_capability_response
        )
        self.message_handler.register_handler(
            MessageType.HEARTBEAT, 
            self._handle_heartbeat
        )
    
    async def _handle_task_delegation(self, message: AgentMessage) -> bool:
        """Handle task delegation messages"""
        try:
            task_data = TaskDelegationMessage(**message.payload)
            logger.info(f"Task delegation: {task_data.task_title} to agent {message.recipient_id}")
            
            # TODO: Integrate with task management system
            # - Create task in database
            # - Assign to recipient agent
            # - Update agent status
            
            return True
        except Exception as e:
            logger.error(f"Error handling task delegation: {str(e)}")
            return False
    
    async def _handle_status_update(self, message: AgentMessage) -> bool:
        """Handle status update messages"""
        try:
            status_data = StatusUpdateMessage(**message.payload)
            logger.info(f"Status update from agent {message.sender_id}: {status_data.agent_status}")
            
            # TODO: Update agent status in database
            # - Update agent record
            # - Notify interested parties
            # - Update metrics
            
            return True
        except Exception as e:
            logger.error(f"Error handling status update: {str(e)}")
            return False
    
    async def _handle_capability_inquiry(self, message: AgentMessage) -> bool:
        """Handle capability inquiry messages"""
        try:
            inquiry_data = CapabilityInquiryMessage(**message.payload)
            logger.info(f"Capability inquiry from agent {message.sender_id}")
            
            # TODO: Query agent capabilities and respond
            # - Check agent capabilities
            # - Calculate availability
            # - Send response message
            
            return True
        except Exception as e:
            logger.error(f"Error handling capability inquiry: {str(e)}")
            return False
    
    async def _handle_capability_response(self, message: AgentMessage) -> bool:
        """Handle capability response messages"""
        try:
            response_data = CapabilityResponseMessage(**message.payload)
            logger.info(f"Capability response from agent {message.sender_id}")
            
            # TODO: Process capability response
            # - Update agent capability cache
            # - Make task assignment decisions
            # - Notify requesting agent
            
            return True
        except Exception as e:
            logger.error(f"Error handling capability response: {str(e)}")
            return False
    
    async def _handle_heartbeat(self, message: AgentMessage) -> bool:
        """Handle heartbeat messages"""
        try:
            self.agent_connections[message.sender_id] = True
            logger.debug(f"Heartbeat from agent {message.sender_id}")
            return True
        except Exception as e:
            logger.error(f"Error handling heartbeat: {str(e)}")
            return False
    
    async def send_message_to_agent(self, sender_id: UUID, recipient_id: UUID,
                                   message_type: MessageType, payload: Dict,
                                   priority: MessagePriority = MessagePriority.NORMAL) -> bool:
        """Send a message from one agent to another"""
        message = AgentMessage(
            sender_id=sender_id,
            recipient_id=recipient_id,
            sender_type="unknown",  # TODO: Get from agent registry
            recipient_type="unknown",  # TODO: Get from agent registry
            message_type=message_type,
            priority=priority,
            payload=payload
        )
        
        return await self.message_handler.send_message(message)
    
    def is_agent_online(self, agent_id: UUID) -> bool:
        """Check if an agent is currently online"""
        return self.agent_connections.get(agent_id, False)
    
    async def broadcast_message(self, sender_id: UUID, message_type: MessageType,
                               payload: Dict, agent_filter: Optional[Callable] = None) -> int:
        """Broadcast a message to multiple agents"""
        sent_count = 0
        
        # TODO: Get list of active agents from database
        # For now, use connected agents
        for agent_id in self.agent_connections.keys():
            if agent_id != sender_id:  # Don't send to self
                if agent_filter is None or agent_filter(agent_id):
                    success = await self.send_message_to_agent(
                        sender_id, agent_id, message_type, payload
                    )
                    if success:
                        sent_count += 1
        
        return sent_count


# Global communication manager instance
communication_manager = AgentCommunicationManager()
