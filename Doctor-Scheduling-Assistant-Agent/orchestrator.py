"""
Main Orchestrator - LangGraph workflow that coordinates all agents.
"""
from langgraph.graph import StateGraph, END
from state import RootAgentState, Message
from root_agent import router_node
from agents.assignment_review_agent import assignment_review_node
from agents.learning_path_agent import learning_path_node
from agents.question_generation_agent import question_generation_node
from agents.faq_fallback_agent import faq_fallback_node
from datetime import datetime
from typing import Literal
import os
from dotenv import load_dotenv

load_dotenv()


def create_orchestrator_graph():
    """
    Create the LangGraph orchestrator with all agents.
    
    Returns:
        Compiled StateGraph
    """
    # Create graph
    workflow = StateGraph(RootAgentState)
    
    # Add nodes
    workflow.add_node("router", router_node)
    workflow.add_node("assignment_review_agent", assignment_review_node)
    workflow.add_node("learning_path_agent", learning_path_node)
    workflow.add_node("question_generation_agent", question_generation_node)
    workflow.add_node("faq_fallback_agent", faq_fallback_node)
    
    # Define routing logic
    def route_to_agent(state: RootAgentState) -> Literal[
        "assignment_review_agent",
        "learning_path_agent", 
        "question_generation_agent",
        "faq_fallback_agent"
    ]:
        """Route to the appropriate agent based on router decision."""
        return state['current_agent']
    
    # Set entry point
    workflow.set_entry_point("router")
    
    # Add conditional edges from router to agents
    workflow.add_conditional_edges(
        "router",
        route_to_agent,
        {
            "assignment_review_agent": "assignment_review_agent",
            "learning_path_agent": "learning_path_agent",
            "question_generation_agent": "question_generation_agent",
            "faq_fallback_agent": "faq_fallback_agent"
        }
    )
    
    # All agents end after execution
    workflow.add_edge("assignment_review_agent", END)
    workflow.add_edge("learning_path_agent", END)
    workflow.add_edge("question_generation_agent", END)
    workflow.add_edge("faq_fallback_agent", END)
    
    return workflow.compile()


class StudyPortalOrchestrator:
    """Main orchestrator for the study portal agent system."""
    
    def __init__(self):
        """Initialize the orchestrator."""
        self.graph = create_orchestrator_graph()
    
    def process_message(self, state: RootAgentState) -> RootAgentState:
        """
        Process a user message through the agent system.
        
        Args:
            state: Current conversation state
            
        Returns:
            Updated state with system response
        """
        # Add timestamp to user message
        user_message: Message = {
            'role': 'user',
            'content': state['user_query'],
            'timestamp': datetime.now().isoformat()
        }
        
        # Add to conversation history
        if 'conversation_history' not in state:
            state['conversation_history'] = []
        state['conversation_history'].append(user_message)
        
        # Process through graph
        result = self.graph.invoke(state)
        
        # Add system response to conversation history
        system_message: Message = {
            'role': 'assistant',
            'content': result['system_response'],
            'timestamp': datetime.now().isoformat()
        }
        result['conversation_history'].append(system_message)
        
        return result


def main():
    """
    Main function to run the orchestrator in interactive mode.
    """
    print("=" * 80)
    print("Study Portal Orchestrator Agent")
    print("=" * 80)
    print("\nWelcome! I can help you with:")
    print("  📝 Assignment reviews and grades (Consultant)")
    print("  📚 Learning path recommendations (Consultant)")
    print("  ❓ Question generation (Admin only)")
    print("  💬 General questions and FAQs (All users)")
    print("\nType 'quit' to exit\n")
    print("=" * 80)
    
    # Get user information
    print("\n🔐 Login:")
    user_id = input("Enter user ID: ").strip() or "user123"
    print("\nSelect your role:")
    print("  1. Consultant")
    print("  2. Admin")
    print("  3. SME")
    role_choice = input("Enter choice (1-3): ").strip()
    
    role_map = {'1': 'Consultant', '2': 'Admin', '3': 'SME'}
    user_role = role_map.get(role_choice, 'Consultant')
    
    print(f"\n✅ Logged in as: {user_id} ({user_role})")
    print("=" * 80 + "\n")
    
    # Initialize orchestrator
    orchestrator = StudyPortalOrchestrator()
    
    # Initialize state
    state: RootAgentState = {
        'user_id': user_id,
        'user_role': user_role,
        'user_query': '',
        'conversation_history': [],
        'current_agent': None,
        'current_agent_awaiting_parameters': None,
        'sub_agent_scratchpad': {},
        'system_response': '',
        'error': None,
        'current_assignment_id': None,
        'current_topic': None
    }
    
    # Conversation loop
    while True:
        # Get user input
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("\n👋 Goodbye! Happy learning!")
            break
        
        if not user_input:
            continue
        
        # Update state with new query
        state['user_query'] = user_input
        
        # Process through orchestrator
        try:
            state = orchestrator.process_message(state)
            print(f"\nAssistant: {state['system_response']}\n")
            
            if state.get('error'):
                print(f"⚠️ Error: {state['error']}\n")
        
        except Exception as e:
            print(f"\n❌ Error processing request: {e}\n")
            # Reset state on error
            state['current_agent_awaiting_parameters'] = None
            state['sub_agent_scratchpad'] = {}


if __name__ == "__main__":
    main()
