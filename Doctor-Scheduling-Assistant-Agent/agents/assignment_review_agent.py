"""
Assignment Review & Insight Agent
Handles queries about assignments, grades, feedback, and performance insights.
"""
from typing import Dict, Any
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from state import RootAgentState, Message
import os
from datetime import datetime


class AssignmentReviewAgent:
    """Agent for handling assignment-related queries and insights."""
    
    def __init__(self):
        """Initialize the agent."""
        self.llm = AzureChatOpenAI(
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini"),
            api_version="2024-02-01",
            temperature=0.7,
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        )
    
    def validate_parameters(self, state: RootAgentState) -> Dict[str, Any]:
        """
        Check if all required parameters are present.
        
        Returns:
            Dict with 'complete' boolean and 'missing' list
        """
        scratchpad = state.get('sub_agent_scratchpad', {})
        
        # For assignment queries, we need assignment_id or assignment_title
        has_assignment = scratchpad.get('assignment_id') or scratchpad.get('assignment_title')
        
        if not has_assignment:
            return {
                'complete': False,
                'missing': ['assignment_id or assignment_title'],
                'clarification': "Which assignment are you interested in? Please provide the assignment name or ID."
            }
        
        return {'complete': True, 'missing': []}
    
    def extract_parameters(self, state: RootAgentState) -> RootAgentState:
        """Extract assignment-related parameters from user query."""
        user_query = state['user_query'].lower()
        scratchpad = state.get('sub_agent_scratchpad', {})
        
        # Simple parameter extraction (in production, use NER or more sophisticated methods)
        # Check for common assignment-related terms
        if 'python' in user_query and 'basic' in user_query:
            scratchpad['assignment_title'] = 'Python Basics'
        elif 'assignment' in user_query:
            # Extract potential assignment name (simplified)
            words = state['user_query'].split()
            for i, word in enumerate(words):
                if word.lower() in ['assignment', 'task', 'homework']:
                    if i + 1 < len(words):
                        scratchpad['assignment_title'] = ' '.join(words[i+1:i+3])
        
        state['sub_agent_scratchpad'] = scratchpad
        return state
    
    def get_assignment_results(self, assignment_title: str, user_id: str) -> Dict[str, Any]:
        """
        Mock function to retrieve assignment results.
        In production, this would query a database.
        """
        # Mock data
        mock_assignments = {
            'Python Basics': {
                'grade': '85%',
                'feedback': 'Good understanding of core concepts, but consider reviewing list comprehensions for efficiency.',
                'due_date': '2025-11-15',
                'status': 'Completed',
                'submission_date': '2025-11-10'
            },
            'Data Structures': {
                'grade': '92%',
                'feedback': 'Excellent work on implementing binary trees. Great optimization!',
                'due_date': '2025-11-20',
                'status': 'Completed',
                'submission_date': '2025-11-18'
            }
        }
        
        return mock_assignments.get(assignment_title, {
            'grade': 'Not available',
            'feedback': 'Assignment not found or not yet graded.',
            'due_date': 'N/A',
            'status': 'Unknown'
        })
    
    def generate_response(self, state: RootAgentState) -> str:
        """Generate response with assignment information."""
        scratchpad = state['sub_agent_scratchpad']
        assignment_title = scratchpad.get('assignment_title', 'Unknown')
        
        # Get assignment results
        results = self.get_assignment_results(assignment_title, state['user_id'])
        
        # Generate natural language response
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant providing information about student assignments. Be concise and friendly."),
            ("human", """Generate a response about the following assignment:

Assignment: {assignment_title}
Grade: {grade}
Status: {status}
Feedback: {feedback}
Due Date: {due_date}

User Query: {user_query}

Provide a natural, conversational response.""")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            'assignment_title': assignment_title,
            'grade': results.get('grade'),
            'status': results.get('status'),
            'feedback': results.get('feedback'),
            'due_date': results.get('due_date'),
            'user_query': state['user_query']
        })
        
        return response.content


def assignment_review_node(state: RootAgentState) -> RootAgentState:
    """
    Assignment Review Agent node for LangGraph.
    
    Args:
        state: Current state
        
    Returns:
        Updated state with response
    """
    print("\n📝 Assignment Review Agent activated")
    
    agent = AssignmentReviewAgent()
    
    # Extract parameters from query
    state = agent.extract_parameters(state)
    
    # Validate parameters
    validation = agent.validate_parameters(state)
    
    if not validation['complete']:
        # Need more information from user
        state['system_response'] = validation['clarification']
        state['current_agent_awaiting_parameters'] = 'assignment_review_agent'
        print(f"⏳ Waiting for parameters: {validation['missing']}")
    else:
        # Generate response
        state['system_response'] = agent.generate_response(state)
        state['current_agent_awaiting_parameters'] = None
        state['sub_agent_scratchpad'] = {}
        print("✅ Response generated")
    
    return state
