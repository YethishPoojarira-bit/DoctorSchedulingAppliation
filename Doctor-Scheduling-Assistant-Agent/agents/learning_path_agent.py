"""
Learning Path Recommendation Agent
Handles learning recommendations, course suggestions, and study plans.
"""
from typing import Dict, Any, List
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from state import RootAgentState
import os


class LearningPathAgent:
    """Agent for handling learning path recommendations."""
    
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
        """Check if all required parameters are present."""
        scratchpad = state.get('sub_agent_scratchpad', {})
        
        missing = []
        if not scratchpad.get('topic'):
            missing.append('topic')
        if not scratchpad.get('skill_level'):
            missing.append('skill_level')
        
        if missing:
            clarification = "To recommend the best learning resources for you, I need:\n"
            if 'topic' in missing:
                clarification += "- What topic would you like to learn?\n"
            if 'skill_level' in missing:
                clarification += "- What is your current skill level? (Beginner/Intermediate/Advanced)\n"
            
            return {
                'complete': False,
                'missing': missing,
                'clarification': clarification.strip()
            }
        
        return {'complete': True, 'missing': []}
    
    def extract_parameters(self, state: RootAgentState) -> RootAgentState:
        """Extract learning-related parameters from user query."""
        user_query = state['user_query'].lower()
        scratchpad = state.get('sub_agent_scratchpad', {})
        
        # Extract topic
        topics = ['machine learning', 'python', 'data science', 'nlp', 'natural language processing',
                  'deep learning', 'web development', 'javascript', 'react', 'sql', 'databases']
        
        for topic in topics:
            if topic in user_query:
                scratchpad['topic'] = topic.title()
                if topic == 'nlp':
                    scratchpad['topic'] = 'Natural Language Processing'
                break
        
        # Extract skill level
        if 'beginner' in user_query or 'new to' in user_query or 'starting' in user_query:
            scratchpad['skill_level'] = 'Beginner'
        elif 'intermediate' in user_query or 'some experience' in user_query:
            scratchpad['skill_level'] = 'Intermediate'
        elif 'advanced' in user_query or 'expert' in user_query:
            scratchpad['skill_level'] = 'Advanced'
        
        state['sub_agent_scratchpad'] = scratchpad
        return state
    
    def recommend_learning_resources(self, topic: str, skill_level: str) -> List[Dict[str, str]]:
        """
        Mock function to get learning resources.
        In production, this would query a database or API.
        """
        resources = {
            'Machine Learning': {
                'Beginner': [
                    {'type': 'Course', 'title': 'Machine Learning Basics', 'platform': 'Coursera'},
                    {'type': 'Book', 'title': 'Hands-On Machine Learning', 'author': 'Aurélien Géron'},
                    {'type': 'Project', 'title': 'Build a simple linear regression model'}
                ],
                'Intermediate': [
                    {'type': 'Course', 'title': 'Advanced ML Techniques', 'platform': 'edX'},
                    {'type': 'Book', 'title': 'Pattern Recognition and Machine Learning', 'author': 'Bishop'},
                    {'type': 'Project', 'title': 'Create an image classifier using CNNs'}
                ]
            },
            'Natural Language Processing': {
                'Intermediate': [
                    {'type': 'Course', 'title': 'Introduction to NLP with Python', 'platform': 'Coursera'},
                    {'type': 'Book', 'title': 'Speech and Language Processing', 'author': 'Jurafsky & Martin'},
                    {'type': 'Project', 'title': 'Build a sentiment analysis model using NLTK'}
                ]
            }
        }
        
        return resources.get(topic, {}).get(skill_level, [
            {'type': 'General', 'title': f'Start with foundational courses in {topic}'}
        ])
    
    def generate_response(self, state: RootAgentState) -> str:
        """Generate learning path recommendation response."""
        scratchpad = state['sub_agent_scratchpad']
        topic = scratchpad.get('topic', 'Unknown')
        skill_level = scratchpad.get('skill_level', 'Beginner')
        
        # Get recommendations
        resources = self.recommend_learning_resources(topic, skill_level)
        
        # Format resources
        resources_list = []
        for r in resources:
            platform_or_author = r.get('platform') or r.get('author', '')
            suffix = f" ({platform_or_author})" if platform_or_author else ""
            resources_list.append(f"- {r['type']}: '{r.get('title', 'N/A')}'{suffix}")
        resources_text = "\n".join(resources_list)
        
        # Generate natural language response
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful learning advisor. Provide encouraging and structured learning recommendations."),
            ("human", """Generate a response for learning path recommendations:

Topic: {topic}
Skill Level: {skill_level}
Resources:
{resources}

User Query: {user_query}

Provide a natural, encouraging response with these recommendations.""")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            'topic': topic,
            'skill_level': skill_level,
            'resources': resources_text,
            'user_query': state['user_query']
        })
        
        return response.content


def learning_path_node(state: RootAgentState) -> RootAgentState:
    """
    Learning Path Agent node for LangGraph.
    
    Args:
        state: Current state
        
    Returns:
        Updated state with response
    """
    print("\n📚 Learning Path Agent activated")
    
    agent = LearningPathAgent()
    
    # Extract parameters from query
    state = agent.extract_parameters(state)
    
    # Validate parameters
    validation = agent.validate_parameters(state)
    
    if not validation['complete']:
        # Need more information from user
        state['system_response'] = validation['clarification']
        state['current_agent_awaiting_parameters'] = 'learning_path_agent'
        print(f"⏳ Waiting for parameters: {validation['missing']}")
    else:
        # Generate response
        state['system_response'] = agent.generate_response(state)
        state['current_agent_awaiting_parameters'] = None
        state['sub_agent_scratchpad'] = {}
        print("✅ Response generated")
    
    return state
