"""
Root Agent Router - The central traffic controller.
Routes user queries to appropriate specialized agents based on intent and context.
Uses LangChain for intelligent routing decisions.
"""
from typing import Dict, Any, List
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from state import RootAgentState
import os
from dotenv import load_dotenv
import json

load_dotenv()


class AgentInfo:
    """Stores information about available agents."""
    
    AGENTS = {
        'assignment_review_agent': {
            'name': 'Assignment Review & Insight Agent',
            'description': 'Handles queries about assignments, grades, feedback, performance insights, and past reports',
            'keywords': ['assignment', 'grade', 'feedback', 'status', 'due date', 'results', 'performance', 'insights', 'score', 'report', 'reports', 'past', 'previous', 'history', 'how did I do', 'my work'],
            'roles': ['Consultant'],
            'parameters': ['assignment_id', 'assignment_title']
        },
        'learning_path_agent': {
            'name': 'Learning Path Recommendation Agent',
            'description': 'Provides learning recommendations, course suggestions, and study plans',
            'keywords': ['learn', 'study', 'recommend', 'course', 'path', 'plan', 'guide', 'resources', 'progress', 'tutorial', 'want to learn', 'teach me', 'improve'],
            'roles': ['Consultant'],
            'parameters': ['topic', 'skill_level']
        },
        'question_generation_agent': {
            'name': 'Question Generation Agent',
            'description': 'Generates practice questions, quizzes, and assessments',
            'keywords': ['generate', 'create', 'quiz', 'questions', 'test', 'practice', 'assessment', 'exam'],
            'roles': ['Admin'],
            'parameters': ['topic', 'difficulty', 'question_count']
        },
        'faq_fallback_agent': {
            'name': 'FAQ & Fallback Agent',
            'description': 'Handles general queries, FAQs, greetings, and fallback scenarios',
            'keywords': ['help', 'how to', 'what is', 'faq', 'hello', 'hi', 'thank', 'general'],
            'roles': ['All'],
            'parameters': []
        }
    }
    
    @classmethod
    def get_agent_info(cls, agent_name: str) -> Dict[str, Any]:
        """Get information about a specific agent."""
        return cls.AGENTS.get(agent_name, {})
    
    @classmethod
    def get_all_agents(cls) -> Dict[str, Dict[str, Any]]:
        """Get all agent information."""
        return cls.AGENTS


class RootAgentRouter:
    """
    Enhanced Root Agent Router with LangChain-powered routing.
    Analyzes user intent, context, and permissions to route to specialized agents.
    """
    
    def __init__(self):
        """Initialize the router with Azure OpenAI LLM."""
        self.llm = AzureChatOpenAI(
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini"),
            api_version="2024-02-01",
            temperature=0.2,  # Lower temperature for more consistent routing
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        )
        
        self.agent_info = AgentInfo()
        
        # Create sophisticated routing prompt
        self.routing_prompt = self._create_routing_prompt()
        
        # Create routing chain
        self.routing_chain = self.routing_prompt | self.llm | StrOutputParser()
    
    def _create_routing_prompt(self) -> ChatPromptTemplate:
        """Create the routing prompt template."""
        agents_info = self.agent_info.get_all_agents()
        
        # Build agent descriptions
        agent_descriptions = []
        for agent_id, info in agents_info.items():
            agent_descriptions.append(
                f"\n{agent_id}:\n"
                f"  Name: {info['name']}\n"
                f"  Description: {info['description']}\n"
                f"  Keywords: {', '.join(info['keywords'])}\n"
                f"  Allowed Roles: {', '.join(info['roles'])}\n"
                f"  Required Parameters: {', '.join(info['parameters']) if info['parameters'] else 'None'}"
            )
        
        agents_text = "\n".join(agent_descriptions)
        
        agents_text = "\n".join(agent_descriptions)
        
        return ChatPromptTemplate.from_messages([
            ("system", f"""You are an intelligent routing agent for a study portal. Your task is to analyze the user's request and select the *most appropriate* specialized agent.

Available Agents:
{agents_text}

Routing Rules:
1. CONTEXT CONTINUATION: If current_agent_awaiting_parameters is set, check if the user is:
   a) Providing the requested information → Return "CONTINUE_CURRENT"
   b) Switching to a new topic → Return appropriate new agent name
   c) Abandoning the task (e.g., "never mind", "cancel") → Return "faq_fallback_agent"

2. KEYWORD MATCHING: Match user query keywords/phrases to agent keywords:
   - Queries about "assignments", "grades", "reports", "performance", "how did I do", "my work", "past work" → assignment_review_agent
   - Queries about "learn", "study", "recommend", "want to learn", "teach me" → learning_path_agent
   - Queries asking to "generate", "create questions/quiz" → question_generation_agent
   - General questions, greetings, "what is", "how to", "help" → faq_fallback_agent

3. ROLE-BASED ACCESS: 
   - question_generation_agent is only for Admin role
   - If user tries to access Admin-only feature but is not Admin → Return "faq_fallback_agent"
   
4. DEFAULT FALLBACK: If truly unclear → return "faq_fallback_agent"

Response Format: Return ONLY the agent name (e.g., "assignment_review_agent") or "CONTINUE_CURRENT"
No explanations, just the agent name."""),
            ("human", """User Role: {user_role}
Current Agent Awaiting Parameters: {current_agent_awaiting_parameters}
Conversation History (last 5 messages):
{conversation_history}

User Query: {user_query}

Which agent should handle this request?""")
        ])
    
    def analyze_context(self, state: RootAgentState) -> Dict[str, Any]:
        """
        Analyze conversation context for routing decision.
        
        Returns:
            Context analysis including topic switches, parameter status, etc.
        """
        analysis = {
            'has_awaiting_parameters': state.get('current_agent_awaiting_parameters') is not None,
            'awaiting_agent': state.get('current_agent_awaiting_parameters'),
            'conversation_length': len(state.get('conversation_history', [])),
            'has_scratchpad_data': bool(state.get('sub_agent_scratchpad', {}))
        }
        
        # Check for abandonment keywords
        user_query_lower = state['user_query'].lower()
        abandonment_keywords = ['never mind', 'cancel', 'forget it', 'stop', 'quit']
        analysis['is_abandonment'] = any(kw in user_query_lower for kw in abandonment_keywords)
        
        return analysis
    
    def check_role_permission(self, agent_name: str, user_role: str) -> bool:
        """
        Check if user role has permission to access the agent.
        
        Args:
            agent_name: Name of the agent
            user_role: User's role
            
        Returns:
            True if user has permission
        """
        agent_info = self.agent_info.get_agent_info(agent_name)
        if not agent_info:
            return False
        
        allowed_roles = agent_info.get('roles', [])
        return 'All' in allowed_roles or user_role in allowed_roles
    
    def route(self, state: RootAgentState) -> str:
        """
        Determine which agent should handle the current request.
        Enhanced with context analysis and permission checking.
        
        Args:
            state: Current state of the conversation
            
        Returns:
            str: Name of the agent to route to
        """
        # Analyze context
        context = self.analyze_context(state)
        
        # Handle abandonment
        if context['is_abandonment'] and context['has_awaiting_parameters']:
            print("  🔄 User abandoned current task")
            return 'faq_fallback_agent'
        
        # Format conversation history for LLM
        conv_history = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in state.get('conversation_history', [])[-5:]
        ])
        
        # Prepare routing input
        routing_input = {
            "user_role": state['user_role'],
            "current_agent_awaiting_parameters": state.get('current_agent_awaiting_parameters', 'None'),
            "conversation_history": conv_history if conv_history else "No previous conversation",
            "user_query": state['user_query']
        }
        
        # Get routing decision from LLM
        agent_name = self.routing_chain.invoke(routing_input).strip()
        
        print(f"  🤖 LLM routing decision: '{agent_name}'")
        
        # Handle CONTINUE_CURRENT directive
        if agent_name == "CONTINUE_CURRENT" and state.get('current_agent_awaiting_parameters'):
            agent_name = state['current_agent_awaiting_parameters']
            print(f"  ↩️  Continuing with {agent_name}")
        
        # Check permissions
        if agent_name != 'faq_fallback_agent':
            if not self.check_role_permission(agent_name, state['user_role']):
                print(f"  ⛔ Permission denied for {agent_name} (Role: {state['user_role']})")
                return 'faq_fallback_agent'
        
        return agent_name


def router_node(state: RootAgentState) -> RootAgentState:
    """
    Enhanced Router node for the LangGraph workflow.
    Determines which agent should handle the request with sophisticated analysis.
    
    Args:
        state: Current state
        
    Returns:
        Updated state with routing decision
    """
    print("\n" + "="*80)
    print("🔀 ROOT AGENT ROUTER")
    print("="*80)
    print(f"  User: {state['user_id']} ({state['user_role']})")
    print(f"  Query: {state['user_query']}")
    
    router = RootAgentRouter()
    agent_name = router.route(state)
    
    # Update state with routing decision
    state['current_agent'] = agent_name
    
    # Get agent info
    agent_info = AgentInfo.get_agent_info(agent_name)
    print(f"  ➡️  Routing to: {agent_info.get('name', agent_name)}")
    print("="*80)
    
    return state
