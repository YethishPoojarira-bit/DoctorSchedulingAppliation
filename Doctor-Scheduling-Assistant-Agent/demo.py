"""
Demo script to showcase the Orchestrator Agent system.
"""
from orchestrator import StudyPortalOrchestrator
from state import RootAgentState


def run_demo_conversation(user_role='Consultant'):
    """Run a demo conversation to showcase the orchestrator."""
    
    print("=" * 80)
    print(f"DEMO: Study Portal Orchestrator ({user_role} User)")
    print("=" * 80)
    
    # Initialize orchestrator
    orchestrator = StudyPortalOrchestrator()
    
    # Initialize state
    state: RootAgentState = {
        'user_id': 'demo_user',
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
    
    # Define conversation scenarios
    if user_role == 'Consultant':
        conversations = [
            "Hi there! I'd like to check my grades.",
            "The Python Basics one.",
            "Thanks! I'd like to learn more about machine learning.",
            "I'm an intermediate, and I'm interested in NLP.",
            "Thank you!"
        ]
    elif user_role == 'Admin':
        conversations = [
            "Generate practice questions on Python.",
            "Make them medium difficulty, 5 questions.",
            "Thanks!"
        ]
    else:
        conversations = [
            "Hello!",
            "How do I submit an assignment?",
            "Thank you!"
        ]
    
    # Run conversation
    for i, user_input in enumerate(conversations, 1):
        print(f"\n[Turn {i}]")
        print(f"You: {user_input}")
        
        # Update state
        state['user_query'] = user_input
        
        # Process
        try:
            state = orchestrator.process_message(state)
            print(f"\nAssistant: {state['system_response']}")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            break
        
        print("-" * 80)
    
    print("\n" + "=" * 80)
    print("Demo completed!")
    print("=" * 80)


if __name__ == "__main__":
    print("\nRunning demos for different user roles...\n")
    
    # Demo 1: Consultant user
    run_demo_conversation('Consultant')
    
    print("\n\n")
    input("Press Enter to see Admin user demo...")
    print("\n")
    
    # Demo 2: Admin user
    run_demo_conversation('Admin')
    
    print("\n\n")
    input("Press Enter to see general FAQ demo...")
    print("\n")
    
    # Demo 3: SME user (fallback scenarios)
    run_demo_conversation('SME')
