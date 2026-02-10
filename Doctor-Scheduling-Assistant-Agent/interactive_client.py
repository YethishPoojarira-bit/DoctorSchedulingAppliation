"""
Interactive WebSocket Client for Study Portal Orchestrator.
Simple client that connects and sends queries directly.
"""
import asyncio
import websockets
import json


async def interactive_client():
    """Interactive client that takes user input and sends to WebSocket server."""
    
    uri = "ws://localhost:8765"
    
    print("=" * 80)
    print("Study Portal - AI Assistant")
    print("=" * 80)
    print("\nConnecting to server...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected!\n")
            print("💡 You can ask about:")
            print("  📝 Assignments and grades")
            print("  📚 Learning recommendations")
            print("  ❓ Question generation")
            print("  💬 General questions")
            print("\nType 'quit' to exit\n")
            print("=" * 80 + "\n")
            
            # Conversation loop
            while True:
                try:
                    # Get user input
                    user_query = input("You: ").strip()
                    
                    if user_query.lower() in ['quit', 'exit', 'bye']:
                        print("\n👋 Goodbye!")
                        break
                    
                    if not user_query:
                        continue
                    
                    # Prepare message (simplified - just send the query)
                    message = {
                        "user_query": user_query
                    }
                    
                    # Send to server
                    await websocket.send(json.dumps(message))
                    
                    # Wait for response
                    response = await websocket.recv()
                    response_data = json.loads(response)
                    
                    # Display response
                    print(f"\n🤖 Assistant: {response_data.get('response', 'No response')}")
                    
                    # Show which agent handled the request
                    if 'agent_used' in response_data:
                        agent_name = response_data['agent_used'].replace('_', ' ').title()
                        print(f"   [Agent: {agent_name}]")
                    
                    print()
                
                except EOFError:
                    print("\n\n❌ Input error detected. Exiting...")
                    break
                except KeyboardInterrupt:
                    print("\n\n👋 Goodbye!")
                    break
    
    except ConnectionRefusedError:
        print("❌ Could not connect to server. Make sure the WebSocket server is running.")
        print("   Run: python websocket_server.py")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        asyncio.run(interactive_client())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
