"""
Phase 2: Agent Communication Protocol
Inter-agent messaging system for coordination and task delegation
"""

from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """Types of messages that can be sent between agents"""
    TASK_DELEGATION = "task_delegation"
    STATUS_UPDATE = "status_update"
    COORDINATION_REQUEST = "coordination_request"
    COORDINATION_RESPONSE = "coordination_response"
    CAPABILITY_INQUIRY = "capability_inquiry"
    CAPABILITY_RESPONSE = "capability_response"
    HEARTBEAT = "heartbeat"
    ERROR_REPORT = "error_report"
    WORKFLOW_STEP = "workflow_step"
    RESOURCE_REQUEST = "resource_request"


class MessagePriority(str, Enum):
    """Message priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class MessageStatus(str, Enum):
    """Message delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    ACKNOWLEDGED = "acknowledged"
    FAILED = "failed"
    EXPIRED = "expired"


class AgentMessage(BaseModel):
    """Core message structure for agent-to-agent communication"""
    
    # Message identification
    message_id: UUID = Field(default_factory=uuid4)
    correlation_id: Optional[UUID] = None
    conversation_id: Optional[UUID] = None
    
    # Routing information
    sender_id: UUID
    recipient_id: UUID
    sender_type: str
    recipient_type: str
    
    # Message metadata
    message_type: MessageType
    priority: MessagePriority = MessagePriority.NORMAL
    status: MessageStatus = MessageStatus.PENDING
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    
    # Content
    subject: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    
    # Delivery tracking
    retry_count: int = 0
    max_retries: int = 3
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class TaskDelegationMessage(BaseModel):
    """Specific payload for task delegation messages"""
    task_id: UUID
    task_title: str
    task_description: str
    task_priority: str
    required_capabilities: List[str] = Field(default_factory=list)
    deadline: Optional[datetime] = None
    context: Dict[str, Any] = Field(default_factory=dict)


class StatusUpdateMessage(BaseModel):
    """Specific payload for status update messages"""
    agent_status: str  # idle, busy, error, offline
    current_task_id: Optional[UUID] = None
    task_progress: Optional[float] = None  # 0.0 to 1.0
    message: Optional[str] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)


class CoordinationRequestMessage(BaseModel):
    """Specific payload for coordination requests"""
    request_type: str  # "resource_allocation", "task_priority", "capability_check"
    request_data: Dict[str, Any] = Field(default_factory=dict)
    requires_response: bool = True
    response_deadline: Optional[datetime] = None


class CapabilityInquiryMessage(BaseModel):
    """Specific payload for capability inquiries"""
    required_capabilities: List[str]
    task_context: Optional[str] = None
    urgency_level: str = "normal"


class CapabilityResponseMessage(BaseModel):
    """Specific payload for capability responses"""
    available_capabilities: List[str]
    confidence_scores: Dict[str, float] = Field(default_factory=dict)
    current_load: float = 0.0  # 0.0 to 1.0
    estimated_availability: Optional[datetime] = None


# Message routing and delivery system
class MessageRouter:
    """Routes messages between agents based on type and priority"""
    
    def __init__(self):
        self.routing_rules: Dict[MessageType, callable] = {}
        self.priority_queues: Dict[MessagePriority, List[AgentMessage]] = {
            MessagePriority.URGENT: [],
            MessagePriority.HIGH: [],
            MessagePriority.NORMAL: [],
            MessagePriority.LOW: []
        }
    
    def register_route(self, message_type: MessageType, handler: callable):
        """Register a handler for a specific message type"""
        self.routing_rules[message_type] = handler
    
    def route_message(self, message: AgentMessage) -> bool:
        """Route a message to the appropriate handler"""
        if message.message_type in self.routing_rules:
            handler = self.routing_rules[message.message_type]
            return handler(message)
        return False
    
    def queue_message(self, message: AgentMessage):
        """Add message to priority queue"""
        self.priority_queues[message.priority].append(message)
    
    def get_next_message(self) -> Optional[AgentMessage]:
        """Get the next highest priority message"""
        for priority in [MessagePriority.URGENT, MessagePriority.HIGH, 
                        MessagePriority.NORMAL, MessagePriority.LOW]:
            if self.priority_queues[priority]:
                return self.priority_queues[priority].pop(0)
        return None


# Communication protocols for different agent types
class ChiefOfStaffProtocol:
    """Communication protocol for Chief of Staff agents"""
    
    @staticmethod
    def delegate_task(cos_agent_id: UUID, mo_agent_id: UUID, 
                     task_data: TaskDelegationMessage) -> AgentMessage:
        """Create a task delegation message from CoS to MO"""
        return AgentMessage(
            sender_id=cos_agent_id,
            recipient_id=mo_agent_id,
            sender_type="chief_of_staff",
            recipient_type="master_operator",
            message_type=MessageType.TASK_DELEGATION,
            priority=MessagePriority.HIGH,
            subject=f"Task Delegation: {task_data.task_title}",
            payload=task_data.dict()
        )
    
    @staticmethod
    def request_capabilities(cos_agent_id: UUID, mo_agent_id: UUID,
                           capability_inquiry: CapabilityInquiryMessage) -> AgentMessage:
        """Request capability information from MO agent"""
        return AgentMessage(
            sender_id=cos_agent_id,
            recipient_id=mo_agent_id,
            sender_type="chief_of_staff",
            recipient_type="master_operator",
            message_type=MessageType.CAPABILITY_INQUIRY,
            priority=MessagePriority.NORMAL,
            subject="Capability Inquiry",
            payload=capability_inquiry.dict()
        )


class MasterOperatorProtocol:
    """Communication protocol for Master Operator agents"""
    
    @staticmethod
    def send_status_update(mo_agent_id: UUID, cos_agent_id: UUID,
                          status_data: StatusUpdateMessage) -> AgentMessage:
        """Send status update from MO to CoS"""
        return AgentMessage(
            sender_id=mo_agent_id,
            recipient_id=cos_agent_id,
            sender_type="master_operator",
            recipient_type="chief_of_staff",
            message_type=MessageType.STATUS_UPDATE,
            priority=MessagePriority.NORMAL,
            subject=f"Status Update: {status_data.agent_status}",
            payload=status_data.dict()
        )
    
    @staticmethod
    def respond_to_capability_inquiry(mo_agent_id: UUID, cos_agent_id: UUID,
                                    capability_response: CapabilityResponseMessage,
                                    correlation_id: UUID) -> AgentMessage:
        """Respond to capability inquiry from CoS"""
        return AgentMessage(
            sender_id=mo_agent_id,
            recipient_id=cos_agent_id,
            sender_type="master_operator",
            recipient_type="chief_of_staff",
            message_type=MessageType.CAPABILITY_RESPONSE,
            priority=MessagePriority.NORMAL,
            correlation_id=correlation_id,
            subject="Capability Response",
            payload=capability_response.dict()
        )


# Message validation and serialization
class MessageValidator:
    """Validates message structure and content"""
    
    @staticmethod
    def validate_message(message: AgentMessage) -> tuple[bool, Optional[str]]:
        """Validate message structure and required fields"""
        try:
            # Check required fields
            if not message.sender_id or not message.recipient_id:
                return False, "Missing sender_id or recipient_id"
            
            if not message.message_type:
                return False, "Missing message_type"
            
            # Check expiration
            if message.expires_at and message.expires_at < datetime.utcnow():
                return False, "Message has expired"
            
            # Validate payload based on message type
            if message.message_type == MessageType.TASK_DELEGATION:
                if not message.payload.get('task_id'):
                    return False, "Task delegation missing task_id"
            
            return True, None
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    @staticmethod
    def serialize_message(message: AgentMessage) -> Dict[str, Any]:
        """Serialize message for transmission"""
        return message.dict()
    
    @staticmethod
    def deserialize_message(data: Dict[str, Any]) -> AgentMessage:
        """Deserialize message from transmission data"""
        return AgentMessage(**data)
