"""
Quick test script to verify the agent system works without WebSocket.
"""
from orchestrator import StudyPortalOrchestrator
from state import RootAgentState


def test_agent():
    """Test the agent system directly."""
    orchestrator = StudyPortalOrchestrator()
    
    # Create initial state
    state: RootAgentState = {
        'user_id': 'test_user',
        'user_role': 'Consultant',
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
    
    print("=" * 80)
    print("Testing Study Portal Agent System")
    print("=" * 80)
    
    # Test 1: Assignment query
    print("\n🧪 Test 1: Assignment Query")
    state['user_query'] = "How did I do on my Python assignment?"
    result = orchestrator.process_message(state)
    print(f"Agent Used: {result['current_agent']}")
    print(f"Response: {result['system_response']}")
    print(f"Awaiting Parameters: {result.get('current_agent_awaiting_parameters')}")
    
    # Test 2: Follow-up with assignment name
    if result.get('current_agent_awaiting_parameters'):
        print("\n🧪 Test 2: Providing Assignment Name")
        state = result
        state['user_query'] = "Python Assignment 1"
        result = orchestrator.process_message(state)
        print(f"Agent Used: {result['current_agent']}")
        print(f"Response: {result['system_response'][:200]}...")
        print(f"Awaiting Parameters: {result.get('current_agent_awaiting_parameters')}")
    
    # Reset state for new test
    state = {
        'user_id': 'test_user',
        'user_role': 'Consultant',
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
    
    # Test 3: Learning path query
    print("\n🧪 Test 3: Learning Path Query")
    state['user_query'] = "I want to learn machine learning"
    result = orchestrator.process_message(state)
    print(f"Agent Used: {result['current_agent']}")
    print(f"Response: {result['system_response'][:200]}...")
    
    # Test 4: FAQ query
    print("\n🧪 Test 4: FAQ Query")
    state['user_query'] = "What are office hours?"
    result = orchestrator.process_message(state)
    print(f"Agent Used: {result['current_agent']}")
    print(f"Response: {result['system_response']}")
    
    # Test 5: Greeting
    print("\n🧪 Test 5: Greeting")
    state['user_query'] = "Hello!"
    result = orchestrator.process_message(state)
    print(f"Agent Used: {result['current_agent']}")
    print(f"Response: {result['system_response']}")
    
    print("\n" + "=" * 80)
    print("✅ All tests completed!")
    print("=" * 80)


if __name__ == "__main__":
    test_agent()
