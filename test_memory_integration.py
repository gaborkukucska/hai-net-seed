#!/usr/bin/env python3
"""
Test script to verify Memory Manager integration with agents
"""

import asyncio
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

async def test_memory_integration():
    print("=" * 60)
    print("Testing HAI-Net Memory Manager Integration")
    print("=" * 60)
    
    # 1. Check server health
    print("\n1. Testing server health...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Health check: {response.json()}")
    
    # 2. Get list of agents
    print("\n2. Getting list of agents...")
    response = requests.get(f"{BASE_URL}/api/agents")
    agents = response.json().get("agents", [])
    print(f"   Found {len(agents)} agent(s)")
    
    if not agents:
        print("   ❌ No agents found! Test cannot continue.")
        return False
    
    admin_agent = agents[0]
    agent_id = admin_agent["agent_id"]
    print(f"   Testing with agent: {agent_id} (role: {admin_agent['role']})")
    
    # 3. Send a chat message to trigger agent processing
    print("\n3. Sending chat message to trigger agent processing...")
    chat_response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "messages": [
                {"role": "user", "content": "Hello! What is your role?"}
            ],
            "user_did": "did:hai:test_user"
        }
    )
    
    if chat_response.status_code == 200:
        print(f"   ✅ Chat response received")
        response_data = chat_response.json()
        print(f"   Response preview: {response_data.get('response', '')[:100]}...")
    else:
        print(f"   ❌ Chat request failed: {chat_response.status_code}")
        return False
    
    # Wait for processing
    print("\n4. Waiting for agent to process message and store memories...")
    await asyncio.sleep(5)
    
    # 5. Query agent memories
    print(f"\n5. Querying memories for agent {agent_id}...")
    try:
        memory_response = requests.get(f"{BASE_URL}/api/memory/{agent_id}")
        
        if memory_response.status_code == 200:
            memory_summary = memory_response.json().get("memory_summary", {})
            print(f"   ✅ Memory summary retrieved:")
            print(f"      - Total memories: {memory_summary.get('total_memories', 0)}")
            print(f"      - By type: {memory_summary.get('memories_by_type', {})}")
            print(f"      - By importance: {memory_summary.get('memories_by_importance', {})}")
            
            if memory_summary.get('total_memories', 0) > 0:
                print("\n   ✅ SUCCESS: Memories are being stored!")
            else:
                print("\n   ⚠️ WARNING: No memories found in storage")
        else:
            print(f"   ❌ Failed to retrieve memory summary: {memory_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error querying memories: {e}")
        return False
    
    # 6. Search agent memories
    print(f"\n6. Searching agent memories...")
    try:
        search_response = requests.post(
            f"{BASE_URL}/api/memory/{agent_id}/search",
            json={"query": "agent", "limit": 5}
        )
        
        if search_response.status_code == 200:
            results = search_response.json().get("results", [])
            print(f"   ✅ Found {len(results)} memory result(s):")
            for i, result in enumerate(results, 1):
                print(f"\n      Memory {i}:")
                print(f"      - ID: {result.get('memory_id', 'N/A')}")
                print(f"      - Type: {result.get('memory_type', 'N/A')}")
                print(f"      - Importance: {result.get('importance', 'N/A')}")
                print(f"      - Content: {result.get('content', 'N/A')[:100]}...")
                print(f"      - Similarity: {result.get('similarity_score', 0):.3f}")
        else:
            print(f"   ⚠️ Memory search returned status: {search_response.status_code}")
            
    except Exception as e:
        print(f"   ⚠️ Error searching memories: {e}")
    
    print("\n" + "=" * 60)
    print("Memory Integration Test Complete!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        asyncio.run(test_memory_integration())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
