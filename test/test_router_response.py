#!/usr/bin/env python3
"""
Test script to verify router returns assistant messages instead of raw events
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'texttosqlagent'))

import asyncio
from agent.agent import Agent
from config.config import Config
import json

async def test_router_response():
    """Test that router collects and returns assistant messages"""
    
    config = Config()
    
    test_questions = [
        "Show me all patients",
        "How many patients are there?"
    ]
    
    print("Testing router response format...")
    print("=" * 50)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\nTest {i}: {question}")
        print("-" * 30)
        
        try:
            async with Agent(config) as agent:
                # Simulate router logic
                assistant_messages = []
                query_results = []
                
                async for event in agent.run(question):
                    if hasattr(event, 'type'):
                        if event.type.value == 'text_complete':
                            # Collect complete assistant messages
                            assistant_messages.append(event.data.get('content', ''))
                        elif event.type.value == 'tool_call_complete':
                            # Collect query results for context
                            tool_name = event.data.get('tool_name', '')
                            result = event.data.get('result', {})
                            if tool_name == 'postgres_query' and result.get('success'):
                                query_results.append(result.get('output', []))
                
                # Simulate router response format
                response_data = {
                    "assistant_messages": assistant_messages,
                    "query_results": query_results,
                    "message_count": len(assistant_messages)
                }
                
                print(f"Router Response Format:")
                print(json.dumps(response_data, indent=2, default=str))
                
                # Verify we have assistant messages
                if assistant_messages:
                    print(f"\n✅ SUCCESS: Found {len(assistant_messages)} assistant messages")
                    for j, msg in enumerate(assistant_messages, 1):
                        print(f"   Message {j}: {msg[:100]}..." if len(msg) > 100 else f"   Message {j}: {msg}")
                else:
                    print("\n❌ ISSUE: No assistant messages found")
                
                if query_results:
                    print(f"✅ Query results: {len(query_results)} queries executed")
                else:
                    print("⚠️  No query results (may be normal if no SQL was needed)")
                
        except Exception as e:
            print(f"Error testing question '{question}': {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 50)

if __name__ == "__main__":
    asyncio.run(test_router_response())
