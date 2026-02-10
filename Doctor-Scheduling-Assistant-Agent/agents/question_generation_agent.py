"""
Question Generation Agent
Generates practice questions, quizzes, and assessments (Admin only).
"""
from typing import Dict, Any, List
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from state import RootAgentState
import os


class QuestionGenerationAgent:
    """Agent for generating questions and assessments."""
    
    def __init__(self):
        """Initialize the agent."""
        self.llm = AzureChatOpenAI(
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini"),
            api_version="2024-02-01",
            temperature=0.8,
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        )
    
    def check_permissions(self, state: RootAgentState) -> bool:
        """Check if user has admin permissions."""
        return state['user_role'] == 'Admin'
    
    def validate_parameters(self, state: RootAgentState) -> Dict[str, Any]:
        """Check if all required parameters are present."""
        scratchpad = state.get('sub_agent_scratchpad', {})
        
        missing = []
        if not scratchpad.get('topic'):
            missing.append('topic')
        if not scratchpad.get('difficulty'):
            missing.append('difficulty')
        if not scratchpad.get('question_count'):
            scratchpad['question_count'] = 5  # Default
        
        if missing:
            clarification = "To generate questions, I need:\n"
            if 'topic' in missing:
                clarification += "- What topic should the questions cover?\n"
            if 'difficulty' in missing:
                clarification += "- What difficulty level? (Easy/Medium/Hard)\n"
            
            return {
                'complete': False,
                'missing': missing,
                'clarification': clarification.strip()
            }
        
        return {'complete': True, 'missing': []}
    
    def extract_parameters(self, state: RootAgentState) -> RootAgentState:
        """Extract question generation parameters from user query."""
        user_query = state['user_query'].lower()
        scratchpad = state.get('sub_agent_scratchpad', {})
        
        # Extract topic
        topics = ['python', 'machine learning', 'data science', 'sql', 'javascript', 
                  'algorithms', 'data structures', 'web development']
        
        for topic in topics:
            if topic in user_query:
                scratchpad['topic'] = topic.title()
                break
        
        # Extract difficulty
        if 'easy' in user_query or 'beginner' in user_query:
            scratchpad['difficulty'] = 'Easy'
        elif 'medium' in user_query or 'intermediate' in user_query:
            scratchpad['difficulty'] = 'Medium'
        elif 'hard' in user_query or 'advanced' in user_query or 'difficult' in user_query:
            scratchpad['difficulty'] = 'Hard'
        
        # Extract question count
        import re
        numbers = re.findall(r'\d+', user_query)
        if numbers:
            scratchpad['question_count'] = int(numbers[0])
        
        state['sub_agent_scratchpad'] = scratchpad
        return state
    
    def generate_questions(self, topic: str, difficulty: str, count: int) -> List[Dict[str, Any]]:
        """Generate questions using LLM."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert educator creating assessment questions. Generate high-quality, varied question types (multiple choice, true/false, short answer)."),
            ("human", """Generate {count} {difficulty} level questions about {topic}.

For each question, provide:
1. The question text
2. Question type (multiple_choice, true_false, or short_answer)
3. For multiple choice: 4 options (A, B, C, D) and the correct answer
4. For true/false: the correct answer
5. For short answer: a sample correct answer

Format as a numbered list.""")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({
            'count': count,
            'difficulty': difficulty,
            'topic': topic
        })
        
        return response.content
    
    def generate_response(self, state: RootAgentState) -> str:
        """Generate questions and format response."""
        scratchpad = state['sub_agent_scratchpad']
        topic = scratchpad.get('topic', 'Unknown')
        difficulty = scratchpad.get('difficulty', 'Medium')
        count = scratchpad.get('question_count', 5)
        
        # Generate questions
        questions = self.generate_questions(topic, difficulty, count)
        
        response = f"I've generated {count} {difficulty} level questions about {topic}:\n\n{questions}"
        response += "\n\nWould you like me to generate more questions or modify these?"
        
        return response


def question_generation_node(state: RootAgentState) -> RootAgentState:
    """
    Question Generation Agent node for LangGraph.
    
    Args:
        state: Current state
        
    Returns:
        Updated state with response
    """
    print("\n❓ Question Generation Agent activated")
    
    agent = QuestionGenerationAgent()
    
    # Check permissions
    if not agent.check_permissions(state):
        state['system_response'] = "I'm sorry, but question generation is only available to Admin users. You are currently logged in as a Consultant."
        state['current_agent_awaiting_parameters'] = None
        state['sub_agent_scratchpad'] = {}
        print("❌ Permission denied: User is not Admin")
        return state
    
    # Extract parameters from query
    state = agent.extract_parameters(state)
    
    # Validate parameters
    validation = agent.validate_parameters(state)
    
    if not validation['complete']:
        # Need more information from user
        state['system_response'] = validation['clarification']
        state['current_agent_awaiting_parameters'] = 'question_generation_agent'
        print(f"⏳ Waiting for parameters: {validation['missing']}")
    else:
        # Generate questions
        state['system_response'] = agent.generate_response(state)
        state['current_agent_awaiting_parameters'] = None
        state['sub_agent_scratchpad'] = {}
        print("✅ Questions generated")
    
    return state
