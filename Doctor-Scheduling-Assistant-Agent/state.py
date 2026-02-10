"""
State management for the Orchestrator Agent system.
Defines the shared state structure used across all agents.
"""
from typing import List, Dict, Any, Optional, Literal
from typing_extensions import TypedDict


class Message(TypedDict):
    """Represents a single message in the conversation."""
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: Optional[str]


class RootAgentState(TypedDict):
    """
    Root Agent State - shared across all agents in the graph.
    
    This state maintains the conversation context, user information,
    and routing information for the orchestrator system.
    """
    # User Information
    user_id: str
    user_role: Literal["Consultant", "Admin", "SME"]
    
    # Conversation Context
    user_query: str
    conversation_history: List[Message]
    
    # Routing & Control
    current_agent: Optional[str]  # Which agent is currently handling the request
    current_agent_awaiting_parameters: Optional[str]  # Agent waiting for user input
    
    # Sub-Agent Communication
    sub_agent_scratchpad: Dict[str, Any]  # Temporary storage for sub-agent context
    
    # Response Management
    system_response: str
    
    # Error Handling
    error: Optional[str]
    
    # Additional Context (for specific agents)
    current_assignment_id: Optional[str]
    current_topic: Optional[str]
