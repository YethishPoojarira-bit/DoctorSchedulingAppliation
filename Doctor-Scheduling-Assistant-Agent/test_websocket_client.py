"""
WebSocket Test Client for Study Portal Orchestrator.
"""
import asyncio
import json
import websockets


async def test_client():
    """Test client for WebSocket server."""
    uri = "ws://localhost:8765"
    
    print("=" * 80)
    print("Study Portal WebSocket Test Client")
    print("=" * 80)
    print(f"Connecting to {uri}...\n")
    
    async with websockets.connect(uri) as websocket:
        print("✅ Connected to server!\n")
        
        # Send connection message
        connect_msg = {
            "type": "connect",
            "user_id": "test_user_123",
            "user_role": "Consultant"
        }
        await websocket.send(json.dumps(connect_msg))
        response = await websocket.recv()
        print(f"Server: {json.loads(response)}\n")
        
        print("=" * 80)
        print("Test Scenarios")
        print("=" * 80)
        
        # Test 1: Assignment query
        print("\n📝 Test 1: Assignment Query")
        print("-" * 80)
        
        await websocket.send(json.dumps({
            "type": "message",
            "user_id": "test_user_123",
            "user_role": "Consultant",
            "message": "I'd like to check my grades"
        }))
        
        response = await websocket.recv()
        data = json.loads(response)
        print(f"You: I'd like to check my grades")
        if data['type'] == 'processing':
            response = await websocket.recv()
            data = json.loads(response)
        print(f"Assistant: {data.get('message', data)}")
        print(f"Agent: {data.get('agent')}")
        print(f"Awaiting Parameters: {data.get('awaiting_parameters')}")
        
        # Continue conversation
        await websocket.send(json.dumps({
            "type": "message",
            "user_id": "test_user_123",
            "user_role": "Consultant",
            "message": "Python Basics"
        }))
        
        response = await websocket.recv()
        data = json.loads(response)
        if data['type'] == 'processing':
            response = await websocket.recv()
            data = json.loads(response)
        print(f"\nYou: Python Basics")
        print(f"Assistant: {data.get('message', '')[:200]}...")
        
        # Test 2: Clear and switch topic
        print("\n\n📚 Test 2: Clear and Switch to Learning Path")
        print("-" * 80)
        
        await websocket.send(json.dumps({
            "type": "clear",
            "user_id": "test_user_123"
        }))
        
        response = await websocket.recv()
        print(f"Clear Response: {json.loads(response)}")
        
        await websocket.send(json.dumps({
            "type": "message",
            "user_id": "test_user_123",
            "user_role": "Consultant",
            "message": "I want to learn machine learning"
        }))
        
        response = await websocket.recv()
        data = json.loads(response)
        if data['type'] == 'processing':
            response = await websocket.recv()
            data = json.loads(response)
        print(f"\nYou: I want to learn machine learning")
        print(f"Assistant: {data.get('message', '')[:200]}...")
        print(f"Agent: {data.get('agent')}")
        
        # Test 3: Admin trying question generation (should work if role is Admin)
        print("\n\n❓ Test 3: Question Generation (Admin)")
        print("-" * 80)
        
        await websocket.send(json.dumps({
            "type": "connect",
            "user_id": "admin_user",
            "user_role": "Admin"
        }))
        
        response = await websocket.recv()
        print(f"Admin connected: {json.loads(response)}")
        
        await websocket.send(json.dumps({
            "type": "message",
            "user_id": "admin_user",
            "user_role": "Admin",
            "message": "Generate 3 Python questions, medium difficulty"
        }))
        
        response = await websocket.recv()
        data = json.loads(response)
        if data['type'] == 'processing':
            response = await websocket.recv()
            data = json.loads(response)
        print(f"\nYou: Generate 3 Python questions, medium difficulty")
        print(f"Assistant: {data.get('message', '')[:300]}...")
        print(f"Agent: {data.get('agent')}")
        
        print("\n" + "=" * 80)
        print("✅ All tests completed!")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_client())
