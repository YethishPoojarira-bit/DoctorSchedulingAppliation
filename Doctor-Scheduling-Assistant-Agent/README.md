# Study Portal Orchestrator Agent

A multi-agent system built with LangGraph for managing a study portal with intelligent routing and specialized agents.

## Architecture

### Root Agent (Router)
The central traffic controller that analyzes user intent and routes requests to specialized agents.

### Specialized Agents

1. **Assignment Review & Insight Agent**
   - Handles assignment queries (status, grades, feedback)
   - Provides performance insights
   - Role: Consultant

2. **Learning Path Recommendation Agent**
   - Recommends courses and study materials
   - Creates personalized learning paths
   - Tracks learning progress
   - Role: Consultant

3. **Question Generation Agent**
   - Generates practice questions and quizzes
   - Creates assessments on specific topics
   - Role: Admin only

4. **FAQ & Fallback Agent**
   - Handles general queries about portal functionality
   - Acts as fallback for unmatched intents
   - Role: All users

## Features

- ✅ Intelligent intent-based routing
- ✅ Role-based access control
- ✅ Context-aware conversation handling
- ✅ Parameter gathering with clarification loops
- ✅ Conversation history tracking
- ✅ Dynamic agent switching

## Installation

1. Create virtual environment:
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
   - Copy `.env.example` to `.env`
   - Add your Azure OpenAI credentials

## Usage

Run the orchestrator:
```bash
python orchestrator.py
```

## Example Conversations

### Consultant User - Assignment Query
```
You: Hi there! I'd like to check my grades.
Assistant: Hello! Happy to help you with your grades. Which assignment are you interested in?

You: The Python Basics one.
Assistant: Got it. For your 'Python Basics' assignment, your grade is 85%...
```

### Consultant User - Learning Recommendations
```
You: I'd like to learn more about machine learning.
Assistant: Certainly! To recommend the best machine learning courses for you, what would be your target skill level?

You: I'm an intermediate, and I'm interested in NLP.
Assistant: Excellent! For an intermediate skill level in Natural Language Processing (NLP)...
```

### Admin User - Question Generation
```
You: Generate 5 medium difficulty Python questions.
Assistant: I've generated 5 Medium level questions about Python:
1. What is the output of...
```

## Project Structure

```
Doctor-Scheduling-Assistant-Agent/
├── orchestrator.py              # Main orchestrator with LangGraph
├── root_agent.py                # Router agent
├── state.py                     # State definitions
├── agents/
│   ├── assignment_review_agent.py
│   ├── learning_path_agent.py
│   ├── question_generation_agent.py
│   └── faq_fallback_agent.py
├── .env.example                 # Environment template
└── requirements.txt             # Python dependencies
```

## Key Concepts

### State Management
- `RootAgentState`: Shared state across all agents
- Conversation history tracking
- Parameter scratchpad for sub-agents

### Routing Logic
- LLM-based intent classification
- Role-based permissions
- Context-aware agent selection

### Parameter Gathering
- Automatic parameter extraction
- Clarification loops for missing info
- Context preservation during multi-turn conversations
