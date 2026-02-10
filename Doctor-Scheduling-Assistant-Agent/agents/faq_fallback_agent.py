"""
FAQ & Fallback Agent
Handles general queries, FAQs, and acts as fallback for unmatched intents.
"""
from typing import Dict, Any
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from state import RootAgentState
import os


class FAQFallbackAgent:
    """Agent for handling general queries and fallback scenarios."""
    
    def __init__(self):
        """Initialize the agent."""
        self.llm = AzureChatOpenAI(
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini"),
            api_version="2024-02-01",
            temperature=0.7,
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        )
        
        # FAQ database (simplified)
        self.faq_db = {
            'how to submit assignment': 'To submit an assignment, log into the portal, navigate to your Assignments section, select the assignment, and click the "Submit" button. You can upload files or paste your work directly.',
            'how to check grades': 'You can check your grades by going to the Assignments section and clicking on any completed assignment. Your grade and feedback will be displayed.',
            'forgot password': 'To reset your password, click on "Forgot Password" on the login page. Enter your email, and you\'ll receive a password reset link.',
            'portal features': 'The portal offers assignment tracking, grade viewing, learning path recommendations, and practice question generation (for admins). You can also view your performance insights.',
            'contact support': 'You can contact support by emailing support@studyportal.com or using the "Contact Us" form in the Help section.'
        }
    
    def search_faq(self, user_query: str) -> str:
        """Search FAQ database for relevant answer."""
        user_query_lower = user_query.lower()
        
        # Simple keyword matching
        for key, answer in self.faq_db.items():
            if any(word in user_query_lower for word in key.split()):
                return answer
        
        return None
    
    def handle_greeting(self, user_query: str) -> str:
        """Check if query is a greeting."""
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        user_query_lower = user_query.lower()
        
        if any(greeting in user_query_lower for greeting in greetings):
            return True
        return False
    
    def handle_thanks(self, user_query: str) -> bool:
        """Check if query is a thank you."""
        thanks = ['thank', 'thanks', 'appreciate', 'grateful']
        user_query_lower = user_query.lower()
        
        return any(thank in user_query_lower for thank in thanks)
    
    def generate_response(self, state: RootAgentState) -> str:
        """Generate appropriate response."""
        user_query = state['user_query']
        
        # Check for greeting
        if self.handle_greeting(user_query):
            return f"Hello! I'm here to help you with your study portal. You can ask me about:\n- Your assignments and grades\n- Learning recommendations\n- General questions about the portal\n\nWhat would you like to know?"
        
        # Check for thanks
        if self.handle_thanks(user_query):
            return "You're welcome! Feel free to ask if you need anything else. Happy learning! 😊"
        
        # Search FAQ
        faq_answer = self.search_faq(user_query)
        if faq_answer:
            return faq_answer
        
        # General fallback with LLM
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful assistant for a study portal. Handle general queries, out-of-scope questions, and provide guidance.

If the question is about:
- Assignments or grades: Suggest asking specifically about an assignment
- Learning: Suggest exploring learning path recommendations
- Questions/quizzes: Mention that admins can generate practice questions
- Something completely unrelated: Politely explain you're focused on the study portal

Always be friendly and helpful."""),
            ("human", "User query: {user_query}\n\nProvide a helpful response.")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({'user_query': user_query})
        
        return response.content


def faq_fallback_node(state: RootAgentState) -> RootAgentState:
    """
    FAQ & Fallback Agent node for LangGraph.
    
    Args:
        state: Current state
        
    Returns:
        Updated state with response
    """
    print("\n💬 FAQ & Fallback Agent activated")
    
    agent = FAQFallbackAgent()
    
    # Generate response
    state['system_response'] = agent.generate_response(state)
    state['current_agent_awaiting_parameters'] = None
    state['sub_agent_scratchpad'] = {}
    
    print("✅ Response generated")
    
    return state
