#!/usr/bin/env python3
"""
Simple test script to verify MLflow trace logging works.
"""

import os
import sys
import time
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment variables for MLflow
os.environ["MLFLOW_ENABLED"] = "true"
os.environ["MLFLOW_TRACKING_URI"] = "http://localhost:5000"
os.environ["MLFLOW_EXPERIMENT_NAME"] = "TraceTest"

try:
    import mlflow
    from mlflow.tracking import MlflowClient
    
    print("🧪 Testing MLflow Trace Logging")
    print("=" * 40)
    
    # Set up MLflow
    mlflow.set_tracking_uri("http://localhost:5000")
    mlflow.set_experiment("TraceTest")
    
    print("✅ MLflow tracking initialized")
    
    # Start a run
    with mlflow.start_run(run_name="Trace Test Run") as run:
        print(f"✅ Started run: {run.info.run_id}")
        
        # Create trace data
        timestamp_ms = int(time.time() * 1000)
        trace_id = f"test_trace_{timestamp_ms}"
        
        trace_data = {
            "trace_id": trace_id,
            "session_id": "test_session",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "execution_time_ms": 5000,
            "status": "OK",
            "agent_interaction": {
                "user_message": "Hello, this is a test message",
                "agent_response": "I received your test message and am responding accordingly",
                "success": True,
                "duration_seconds": 5.0,
                "message_lengths": {
                    "user": 27,
                    "agent": 59
                }
            },
            "tools_used": ["search", "code_analysis"],
            "tool_count": 2,
            "token_usage": {
                "prompt_tokens": 15,
                "completion_tokens": 20,
                "total_tokens": 35
            },
            "spans": []
        }
        
        # Add spans
        base_time = timestamp_ms
        
        # Agent processing span
        trace_data["spans"].append({
            "span_id": f"agent_{timestamp_ms}",
            "parent_id": None,
            "name": "Agent Processing",
            "type": "CHAIN",
            "start_time_ms": base_time,
            "end_time_ms": base_time + 5000,
            "duration_ms": 5000,
            "status": "OK",
            "inputs": {"user_message": "Hello, this is a test message"},
            "outputs": {"agent_response": "I received your test message and am responding accordingly"},
            "metadata": {
                "component": "ai_agent",
                "model": "test-model",
                "temperature": 0.7
            }
        })
        
        # Tool spans
        for i, tool_name in enumerate(["search", "code_analysis"]):
            tool_start = base_time + i * 100
            tool_end = tool_start + 50
            
            trace_data["spans"].append({
                "span_id": f"tool_{tool_name}_{timestamp_ms}",
                "parent_id": f"agent_{timestamp_ms}",
                "name": f"Tool: {tool_name}",
                "type": "TOOL",
                "start_time_ms": tool_start,
                "end_time_ms": tool_end,
                "duration_ms": 50,
                "status": "OK",
                "inputs": {"tool_name": tool_name},
                "outputs": {"executed": True},
                "metadata": {
                    "component": "tool_execution",
                    "tool_index": i
                }
            })
        
        # Create trace directory
        trace_dir = Path("mlruns") / "trace_artifacts" / "traces"
        trace_dir.mkdir(parents=True, exist_ok=True)
        
        # Save trace file
        trace_file = trace_dir / f"{trace_id}.json"
        import json
        with open(trace_file, 'w') as f:
            json.dump(trace_data, f, indent=2)
        
        # Save summary file
        summary_file = trace_dir / f"summary_{trace_id}.json"
        summary_data = {
            "trace_id": trace_id,
            "session_id": "test_session",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "duration_seconds": 5.0,
            "success": True,
            "tools_used": ["search", "code_analysis"],
            "token_usage": {
                "prompt_tokens": 15,
                "completion_tokens": 20,
                "total_tokens": 35
            },
            "message_preview": {
                "user": "Hello, this is a test message",
                "agent": "I received your test message and am responding accordingly"
            }
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary_data, f, indent=2)
        
        # Log to MLflow
        mlflow.log_artifact(str(trace_file), artifact_path="traces")
        mlflow.log_artifact(str(summary_file), artifact_path="trace_summaries")
        
        # Log metrics
        mlflow.log_metrics({
            "session_duration_seconds": 5.0,
            "user_message_length": 27,
            "agent_response_length": 59,
            "tools_used_count": 2,
            "success": 1,
            "prompt_tokens": 15,
            "completion_tokens": 20,
            "total_tokens": 35
        })
        
        # Log parameters
        mlflow.log_param("tools_used", "search,code_analysis")
        mlflow.log_param("trace_id", trace_id)
        
        print(f"✅ Trace logged: {trace_id}")
        print(f"📁 Run ID: {run.info.run_id}")
        print(f"🌐 View at: http://localhost:5000/#/experiments/")
    
    print("\n🎉 Trace test completed!")
    print("📁 Check the 'traces' and 'trace_summaries' folders in the artifacts section")
    print("🌐 MLflow UI: http://localhost:5000")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure MLflow is installed: pip install mlflow")
except Exception as e:
    print(f"❌ Error: {e}")
    print("💡 Make sure MLflow server is running: mlflow ui --port 5000")
