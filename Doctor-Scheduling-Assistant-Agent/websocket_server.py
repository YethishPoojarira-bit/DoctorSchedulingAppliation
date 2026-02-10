"""
WebSocket Server for Study Portal Orchestrator.
Simplified version - directly connects user queries to agents.
"""
import asyncio
import json
from datetime import datetime
from typing import Set, Any
import websockets
from orchestrator import StudyPortalOrchestrator
from state import RootAgentState


class WebSocketHandler:
    """Handles WebSocket connections and message routing."""
    
    def __init__(self):
        """Initialize the WebSocket handler."""
        self.orchestrator = StudyPortalOrchestrator()
        self.active_connections: Set[Any] = set()
        self.session_state: RootAgentState = {
            'user_id': 'websocket_user',
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
    
    async def register(self, websocket: Any):
        """Register a new WebSocket connection."""
        self.active_connections.add(websocket)
        print(f"✅ Client connected. Total connections: {len(self.active_connections)}")
    
    async def unregister(self, websocket: Any):
        """Unregister a WebSocket connection."""
        self.active_connections.discard(websocket)
        print(f"❌ Client disconnected. Total connections: {len(self.active_connections)}")
    
    def get_or_create_session(self, user_id: str, user_role: str) -> RootAgentState:
        """Get existing session or create new one."""
        if user_id not in self.user_sessions:
            return self.create_session(user_id, user_role)
        return self.user_sessions[user_id]
    
    async def send_message(self, websocket: Any, message: dict):
        """Send a message through WebSocket."""
        try:
            await websocket.send(json.dumps(message))
        except Exception as e:
            print(f"Error sending message: {e}")
    
    async def handle_message(self, websocket: Any, message: str):
        """Handle incoming WebSocket message."""
        try:
            data = json.loads(message)
            
            # Get the user query
            user_query = data.get('user_query', '').strip()
            
            if not user_query:
                await self.send_message(websocket, {
                    'type': 'error',
                    'message': 'No query provided'
                })
                return
            
            # Update session state with new query
            self.session_state['user_query'] = user_query
            
            print(f"\n📩 Query: {user_query}")
            
            # Process through orchestrator
            result = self.orchestrator.process_message(self.session_state)
            
            # Update session state
            self.session_state = result
            
            # Send response
            response_message = {
                'type': 'response',
                'response': result['system_response'],
                'agent_used': result.get('current_agent', 'unknown'),
                'awaiting_parameters': result.get('current_agent_awaiting_parameters') is not None,
                'timestamp': datetime.now().isoformat()
            }
            
            if result.get('error'):
                response_message['error'] = result['error']
            
            await self.send_message(websocket, response_message)
            
            agent_name = result.get('current_agent', 'unknown').replace('_', ' ').title()
            print(f"📤 Response sent via {agent_name}")
        
        except json.JSONDecodeError:
            await self.send_message(websocket, {
                'type': 'error',
                'message': 'Invalid JSON format'
            })
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            await self.send_message(websocket, {
                'type': 'error',
                'message': f'Error processing message: {str(e)}'
            })
    
    async def handler(self, websocket: Any):
        """Main WebSocket handler."""
        await self.register(websocket)
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed by client")
        finally:
            await self.unregister(websocket)


async def start_server(host: str = "localhost", port: int = 8765):
    """Start the WebSocket server."""
    handler = WebSocketHandler()
    
    print("=" * 80)
    print("Study Portal WebSocket Server")
    print("=" * 80)
    print(f"🚀 Server starting on ws://{host}:{port}")
    print("\nMessage format:")
    print('  {"user_query": "your question here"}')
    print("\nReady to handle requests from agents:")
    print("  • Assignment Review & Insight Agent")
    print("  • Learning Path Recommendation Agent")
    print("  • Question Generation Agent")
    print("  • FAQ & Fallback Agent")
    print("=" * 80 + "\n")
    
    async with websockets.serve(handler.handler, host, port):
        print("✅ Server is running and waiting for connections...\n")
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")

