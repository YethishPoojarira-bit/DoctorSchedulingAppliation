"""
Quick test to verify routing decisions.
"""
from orchestrator import StudyPortalOrchestrator
from state import RootAgentState


def test_routing():
    """Test routing with various queries."""
    orchestrator = StudyPortalOrchestrator()
    
    test_queries = [
        "i want info on my past reports",
        "How did I do on my Python assignment?",
        "Show me my assignment history",
        "What's my grade?",
        "I want to learn machine learning",
        "Generate some Python questions",
        "Hello",
        "What are office hours?"
    ]
    
    print("=" * 80)
    print("Testing Routing Decisions")
    print("=" * 80)
    
    for query in test_queries:
        # Create fresh state
        state: RootAgentState = {
            'user_id': 'test_user',
            'user_role': 'Consultant',
            'user_query': query,
            'conversation_history': [],
            'current_agent': None,
            'current_agent_awaiting_parameters': None,
            'sub_agent_scratchpad': {},
            'system_response': '',
            'error': None,
            'current_assignment_id': None,
            'current_topic': None
        }
        
        result = orchestrator.process_message(state)
        agent = result['current_agent'].replace('_', ' ').title()
        
        print(f"\n📝 Query: {query}")
        print(f"   ➡️  Agent: {agent}")


if __name__ == "__main__":
    test_routing()
