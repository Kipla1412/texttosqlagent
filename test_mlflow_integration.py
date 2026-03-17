#!/usr/bin/env python3
"""
Test script to verify MLflow integration with the AI Agent.
"""

import os
import sys
import time
import asyncio
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.config import Config
from utils.mlflow_tracker import MLflowTracker


def test_mlflow_tracker():
    """Test the MLflow tracker functionality."""
    print("🧪 Testing MLflow Integration")
    print("=" * 40)
    
    # Create a test config
    config = Config()
    
    # Test MLflow tracker initialization
    print("1. Initializing MLflow tracker...")
    tracker = MLflowTracker(config)
    
    if not tracker.enabled:
        print("❌ MLflow is disabled")
        return False
    
    print("✅ MLflow tracker initialized successfully")
    
    # Test starting a run
    print("\n2. Starting MLflow run...")
    session_id = "test_session_123"
    run_id = tracker.start_run(session_id, "Test Run")
    
    if run_id:
        print(f"✅ MLflow run started: {run_id}")
    else:
        print("❌ Failed to start MLflow run")
        return False
    
    # Test logging agent interaction
    print("\n3. Logging agent interaction...")
    tracker.log_agent_interaction(
        user_message="Hello, how can you help me?",
        agent_response="I'm an AI assistant that can help you with various tasks.",
        tools_used=["search", "code_analysis"],
        session_duration=5.2,
        token_usage={"prompt_tokens": 20, "completion_tokens": 15, "total_tokens": 35},
        success=True
    )
    print("✅ Agent interaction logged")
    
    # Test logging tool execution
    print("\n4. Logging tool execution...")
    tracker.log_tool_execution(
        tool_name="search",
        tool_args={"query": "MLflow integration"},
        execution_time=1.5,
        success=True
    )
    print("✅ Tool execution logged")
    
    # Test logging session summary
    print("\n5. Logging session summary...")
    tracker.log_session_summary(
        session_id=session_id,
        total_interactions=3,
        total_duration=15.7,
        total_tools_used=5,
        success_rate=1.0
    )
    print("✅ Session summary logged")
    
    # Test getting experiment stats
    print("\n6. Getting experiment stats...")
    stats = tracker.get_experiment_stats()
    if stats:
        print(f"✅ Experiment stats: {stats}")
    else:
        print("⚠️  Could not retrieve experiment stats")
    
    # End the run
    print("\n7. Ending MLflow run...")
    tracker.end_run()
    print("✅ MLflow run ended")
    
    print("\n🎉 MLflow integration test completed successfully!")
    return True


async def test_agent_integration():
    """Test MLflow integration with the Agent class."""
    print("\n🤖 Testing Agent MLflow Integration")
    print("=" * 40)
    
    try:
        from agent.agent import Agent
        
        # Create agent with test config
        config = Config()
        async with Agent(config) as agent:
            print("✅ Agent initialized with MLflow tracking")
            
            # Run a simple test message
            print("🔄 Running test interaction...")
            async for event in agent.run("Hello, this is a test message"):
                if event.type.value == "agent_start":
                    print("✅ Agent started")
                elif event.type.value == "text_complete":
                    print(f"✅ Agent response: {event.data.get('content', '')[:100]}...")
                elif event.type.value == "agent_end":
                    print("✅ Agent completed")
                    break
            
        print("✅ Agent MLflow integration test completed")
        return True
        
    except Exception as e:
        print(f"❌ Agent integration test failed: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 AI Agent MLflow Integration Test")
    print("=" * 50)
    
    # Check if MLflow server is running
    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000")
    print(f"📍 MLflow Tracking URI: {tracking_uri}")
    
    # Test basic MLflow tracker
    tracker_success = test_mlflow_tracker()
    
    # Test agent integration (only if tracker test passed)
    agent_success = False
    if tracker_success:
        try:
            agent_success = asyncio.run(test_agent_integration())
        except Exception as e:
            print(f"❌ Agent test failed: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   MLflow Tracker: {'✅ PASS' if tracker_success else '❌ FAIL'}")
    print(f"   Agent Integration: {'✅ PASS' if agent_success else '❌ FAIL'}")
    
    if tracker_success and agent_success:
        print("\n🎉 All tests passed! MLflow integration is working correctly.")
        print(f"🌐 View your experiments at: {tracking_uri}")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")
        print("\n💡 Make sure:")
        print("   - MLflow is installed: pip install mlflow")
        print("   - MLflow server is running: mlflow ui --port 5000")
        print("   - Environment variables are set correctly")


if __name__ == "__main__":
    main()
