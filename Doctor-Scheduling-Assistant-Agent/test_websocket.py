"""
Simple WebSocket test client that sends test queries.
"""
import asyncio
import json
import websockets


async def test_websocket():
    """Test the WebSocket server with automated queries."""
    uri = "ws://localhost:8765"
    
    test_queries = [
        "How did I do on my Python assignment?",
        "Python Assignment 1",
        "I want to learn machine learning",
        "Beginner",
        "Hello!",
        "What are office hours?"
    ]
    
    print("=" * 80)
    print("WebSocket Test Client")
    print("=" * 80)
    print(f"Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected!\n")
            
            for i, query in enumerate(test_queries, 1):
                print(f"📤 Test {i}: Sending: '{query}'")
                
                # Send query
                message = {"user_query": query}
                await websocket.send(json.dumps(message))
                
                # Receive response
                response = await websocket.recv()
                data = json.loads(response)
                
                print(f"📥 Response:")
                print(f"   Agent: {data.get('agent_used', 'unknown')}")
                print(f"   Response: {data.get('response', '')[:150]}...")
                print(f"   Awaiting Parameters: {data.get('awaiting_parameters', False)}")
                print()
                
                await asyncio.sleep(0.5)  # Small delay between messages
            
            print("=" * 80)
            print("✅ All tests completed successfully!")
            print("=" * 80)
    
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_websocket())
