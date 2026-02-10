# Quick Start Guide - Study Portal Orchestrator

## Architecture Overview

The system consists of:
1. **Root Agent (Router)** - Central traffic controller using LangChain
2. **4 Specialized Sub-Agents** - Handle specific tasks
3. **WebSocket Server** - Real-time communication
4. **Agent Info** - Metadata store for routing decisions

## Starting the System

### Option 1: WebSocket Server (Recommended)

1. Start the WebSocket server:
```bash
python websocket_server.py
```

2. In another terminal, run the test client:
```bash
python test_websocket_client.py
```

### Option 2: Direct Console Interface

```bash
python orchestrator.py
```

## WebSocket Message Format

### Connect
```json
{
  "type": "connect",
  "user_id": "user123",
  "user_role": "Consultant"
}
```

### Send Message
```json
{
  "type": "message",
  "user_id": "user123",
  "user_role": "Consultant",
  "message": "What's my grade on Python Basics?"
}
```

### Clear Current Task
```json
{
  "type": "clear",
  "user_id": "user123"
}
```

## Response Types

### Connected
```json
{
  "type": "connected",
  "user_id": "user123",
  "user_role": "Consultant",
  "message": "Welcome message"
}
```

### Response
```json
{
  "type": "response",
  "message": "Assistant's response",
  "agent": "assignment_review_agent",
  "awaiting_parameters": false,
  "timestamp": "2025-11-07T..."
}
```

### Processing
```json
{
  "type": "processing",
  "message": "Processing your request..."
}
```

### Error
```json
{
  "type": "error",
  "message": "Error description"
}
```

## Routing Logic

The Root Agent makes intelligent routing decisions based on:

1. **User Intent** - Analyzed using LangChain and Azure OpenAI
2. **Conversation Context** - Maintains history and current state
3. **Role Permissions** - Enforces role-based access control
4. **Parameter Status** - Tracks parameter gathering loops

### Routing Priority:
1. Check if continuing parameter gathering
2. Detect task abandonment
3. Validate role permissions
4. Match intent to specialized agent
5. Fallback to FAQ agent

## Available Agents

### 1. Assignment Review & Insight Agent
- **Role**: Consultant
- **Triggers**: "grade", "assignment", "feedback", "status"
- **Parameters**: assignment_id or assignment_title

### 2. Learning Path Recommendation Agent
- **Role**: Consultant
- **Triggers**: "learn", "recommend", "course", "study"
- **Parameters**: topic, skill_level

### 3. Question Generation Agent
- **Role**: Admin only
- **Triggers**: "generate questions", "create quiz"
- **Parameters**: topic, difficulty, question_count

### 4. FAQ & Fallback Agent
- **Role**: All
- **Triggers**: Greetings, general queries, fallback
- **Parameters**: None

## Testing Scenarios

### Scenario 1: Parameter Gathering
```
User: "I'd like to check my grades"
→ Routes to assignment_review_agent
→ Agent asks: "Which assignment?"
User: "Python Basics"
→ Agent provides grade information
```

### Scenario 2: Topic Switch
```
User: "I'd like to check my grades"
→ Routes to assignment_review_agent
User: "Actually, I want to learn machine learning"
→ Clears context, routes to learning_path_agent
```

### Scenario 3: Task Abandonment
```
User: "Generate some questions"
→ Routes to question_generation_agent
→ Agent asks: "What topic?"
User: "Never mind"
→ Clears context, routes to faq_fallback_agent
```

### Scenario 4: Permission Denied
```
User (Consultant): "Generate questions on Python"
→ Routes to question_generation_agent
→ Permission check fails
→ Redirects to faq_fallback_agent with explanation
```

## Key Features

✅ **LangChain-powered routing** - Intelligent intent classification
✅ **WebSocket real-time communication** - Instant responses
✅ **Context-aware conversations** - Maintains conversation history
✅ **Role-based access control** - Enforces permissions
✅ **Parameter gathering loops** - Clarifies missing information
✅ **Dynamic agent switching** - Handles topic changes
✅ **Task abandonment handling** - Clears context gracefully
✅ **Agent metadata store** - Centralized agent information

## Environment Setup

Make sure `.env` file contains:
```
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini
```

## Next Steps

1. Run `python websocket_server.py`
2. Run `python test_websocket_client.py` in another terminal
3. Observe the routing decisions and agent interactions
4. Try different user roles and queries
