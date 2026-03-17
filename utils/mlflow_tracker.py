"""
MLflow tracking utility for AI Agent experiments and metrics.
"""

import os
import time
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient

from config.config import Config
from config.loader import get_data_dir


class MLflowTracker:
    """
    Global MLflow tracker for AI Agent sessions and experiments.
    Tracks agent interactions, tool usage, performance metrics, and outcomes.
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.experiment_name = getattr(config, 'mlflow_experiment_name', 'AIAgent')
        self.tracking_uri = getattr(config, 'mlflow_tracking_uri', 'http://localhost:5000')
        self.enabled = getattr(config, 'mlflow_enabled', True)
        
        if self.enabled:
            self._setup_mlflow()
    
    def _setup_mlflow(self):
        """Initialize MLflow tracking."""
        try:
            # Set tracking URI
            mlflow.set_tracking_uri(self.tracking_uri)
            
            # Create or get experiment
            mlflow.set_experiment(self.experiment_name)
            
            # Initialize client
            self.client = MlflowClient()
            
            # print(f"✅ MLflow tracking initialized: {self.tracking_uri}")
            # print(f"📊 Experiment: {self.experiment_name}")
            
        except Exception as e:
            # print(f"⚠️  MLflow initialization failed: {e}")
            self.enabled = False
    
    def start_run(self, session_id: str, run_name: Optional[str] = None) -> Optional[str]:
        """Start a new MLflow run for a session."""
        if not self.enabled:
            return None
            
        try:
            run_name = run_name or f"Session_{session_id[:8]}"
            
            # Start run with session-specific tags
            run = mlflow.start_run(
                run_name=run_name,
                tags={
                    "session_id": session_id,
                    "model": self.config.model_name,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # Log initial parameters
            mlflow.log_params({
                "model_name": self.config.model_name,
                "temperature": self.config.model.temperature,
                "context_window": self.config.model.context_window,
                "session_id": session_id
            })
            
            return run.info.run_id
            
        except Exception as e:
            # print(f"⚠️  Failed to start MLflow run: {e}")
            return None
    
    def end_run(self):
        """End the current MLflow run."""
        if not self.enabled:
            return
            
        try:
            mlflow.end_run()
        except Exception as e:
            # print(f"⚠️  Failed to end MLflow run: {e}")
            pass
    
    def log_agent_interaction(
        self,
        user_message: str,
        agent_response: str,
        tools_used: List[str],
        session_duration: float,
        token_usage: Optional[Dict[str, int]] = None,
        success: bool = True
    ):
        """Log an agent interaction with metrics and visible traces."""
        if not self.enabled:
            return
            
        try:
            timestamp_ms = int(time.time() * 1000)
            trace_id = f"trace_{timestamp_ms}"
            
            # Create a comprehensive trace that will be visible in MLflow UI
            trace_data = {
                "trace_id": trace_id,
                "session_id": getattr(self, 'current_session_id', 'unknown'),
                "timestamp": datetime.now().isoformat(),
                "execution_time_ms": int(session_duration * 1000),
                "status": "OK" if success else "ERROR",
                "agent_interaction": {
                    "user_message": user_message,
                    "agent_response": agent_response,
                    "success": success,
                    "duration_seconds": session_duration,
                    "message_lengths": {
                        "user": len(user_message),
                        "agent": len(agent_response)
                    }
                },
                "tools_used": tools_used,
                "tool_count": len(tools_used),
                "token_usage": token_usage or {},
                "spans": []
            }
            
            # Add detailed spans for each component
            base_time = timestamp_ms
            
            # Agent processing span
            trace_data["spans"].append({
                "span_id": f"agent_{timestamp_ms}",
                "parent_id": None,
                "name": "Agent Processing",
                "type": "CHAIN",
                "start_time_ms": base_time,
                "end_time_ms": base_time + int(session_duration * 1000),
                "duration_ms": int(session_duration * 1000),
                "status": "OK" if success else "ERROR",
                "inputs": {"user_message": user_message},
                "outputs": {"agent_response": agent_response},
                "metadata": {
                    "component": "ai_agent",
                    "model": self.config.model_name,
                    "temperature": self.config.model.temperature
                }
            })
            
            # Add tool spans
            for i, tool_name in enumerate(tools_used):
                tool_start = base_time + i * 100
                tool_end = tool_start + 50  # Assume 50ms per tool
                
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
            
            # Create trace file in a format that MLflow can display
            trace_dir = Path(get_data_dir()) / "mlflow_artifacts" / "traces"
            trace_dir.mkdir(parents=True, exist_ok=True)
            
            # Save the main trace file
            trace_file = trace_dir / f"{trace_id}.json"
            with open(trace_file, 'w') as f:
                json.dump(trace_data, f, indent=2)
            
            # Also create a summary file for easy viewing
            summary_file = trace_dir / f"summary_{trace_id}.json"
            summary_data = {
                "trace_id": trace_id,
                "session_id": getattr(self, 'current_session_id', 'unknown'),
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": session_duration,
                "success": success,
                "tools_used": tools_used,
                "token_usage": token_usage or {},
                "message_preview": {
                    "user": user_message[:100] + "..." if len(user_message) > 100 else user_message,
                    "agent": agent_response[:100] + "..." if len(agent_response) > 100 else agent_response
                }
            }
            
            with open(summary_file, 'w') as f:
                json.dump(summary_data, f, indent=2)
            
            # Log both files to MLflow
            mlflow.log_artifact(str(trace_file), artifact_path="traces")
            mlflow.log_artifact(str(summary_file), artifact_path="trace_summaries")
            
            # Log metrics for charts
            metrics = {
                "session_duration_seconds": session_duration,
                "user_message_length": len(user_message),
                "agent_response_length": len(agent_response),
                "tools_used_count": len(tools_used),
                "success": 1 if success else 0
            }
            
            if token_usage:
                metrics.update({
                    "prompt_tokens": token_usage.get("prompt_tokens", 0),
                    "completion_tokens": token_usage.get("completion_tokens", 0),
                    "total_tokens": token_usage.get("total_tokens", 0)
                })
            
            mlflow.log_metrics(metrics)
            
            # Log tools used as a parameter
            if tools_used:
                mlflow.log_param("tools_used", ",".join(tools_used))
            
            # Log trace ID as a unique parameter with timestamp to avoid conflicts
            mlflow.log_param(f"trace_id_{timestamp_ms}", trace_id)
            
            # print(f"✅ Trace logged: {trace_id}")
            # print(f"📁 View traces at: http://localhost:5000/#/experiments/1/artifacts")
            
        except Exception as e:
            print(f"⚠️  Failed to log agent interaction trace: {e}")
            # Fallback to regular metric logging
            self._log_fallback_metrics(user_message, agent_response, tools_used, session_duration, token_usage, success)
    
    def _log_fallback_metrics(
        self,
        user_message: str,
        agent_response: str,
        tools_used: List[str],
        session_duration: float,
        token_usage: Optional[Dict[str, int]] = None,
        success: bool = True
    ):
        """Fallback method to log metrics when trace logging fails."""
        try:
            metrics = {
                "session_duration_seconds": session_duration,
                "user_message_length": len(user_message),
                "agent_response_length": len(agent_response),
                "tools_used_count": len(tools_used),
                "success": 1 if success else 0
            }
            
            if token_usage:
                metrics.update({
                    "prompt_tokens": token_usage.get("prompt_tokens", 0),
                    "completion_tokens": token_usage.get("completion_tokens", 0),
                    "total_tokens": token_usage.get("total_tokens", 0)
                })
            
            mlflow.log_metrics(metrics)
            
            if tools_used:
                mlflow.log_param("tools_used", ",".join(tools_used))
            
            # print("✅ Fallback metrics logged")
            
        except Exception as e:
            # print(f"⚠️  Failed to log fallback metrics: {e}")
            pass
    
    def log_tool_execution(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        execution_time: float,
        success: bool,
        error_message: Optional[str] = None
    ):
        """Log individual tool execution metrics."""
        if not self.enabled:
            return
            
        try:
            metrics = {
                f"{tool_name}_execution_time": execution_time,
                f"{tool_name}_success": 1 if success else 0
            }
            
            mlflow.log_metrics(metrics, step=int(time.time()))
            
            if not success and error_message:
                # Log error as artifact
                error_data = {
                    "timestamp": datetime.now().isoformat(),
                    "tool_name": tool_name,
                    "tool_args": tool_args,
                    "error_message": error_message
                }
                
                artifact_path = Path(get_data_dir()) / "mlflow_artifacts" / f"error_{int(time.time())}.json"
                artifact_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(artifact_path, 'w') as f:
                    json.dump(error_data, f, indent=2)
                
                mlflow.log_artifact(str(artifact_path))
                
        except Exception as e:
            # print(f"⚠️  Failed to log tool execution: {e}")
            pass
    
    def log_session_summary(
        self,
        session_id: str,
        total_interactions: int,
        total_duration: float,
        total_tools_used: int,
        success_rate: float
    ):
        """Log session-level summary metrics."""
        if not self.enabled:
            return
            
        try:
            summary_metrics = {
                "total_interactions": total_interactions,
                "total_duration_seconds": total_duration,
                "total_tools_used": total_tools_used,
                "success_rate": success_rate,
                "avg_interaction_duration": total_duration / max(total_interactions, 1)
            }
            
            mlflow.log_metrics(summary_metrics)
            
            # Log session summary as artifact
            summary_data = {
                "session_id": session_id,
                "total_interactions": total_interactions,
                "total_duration": total_duration,
                "total_tools_used": total_tools_used,
                "success_rate": success_rate,
                "end_time": datetime.now().isoformat()
            }
            
            artifact_path = Path(get_data_dir()) / "mlflow_artifacts" / f"session_summary_{session_id}.json"
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(artifact_path, 'w') as f:
                json.dump(summary_data, f, indent=2)
            
            mlflow.log_artifact(str(artifact_path))
            
        except Exception as e:
            # print(f"⚠️  Failed to log session summary: {e}")
            pass
    
    def get_experiment_stats(self) -> Dict[str, Any]:
        """Get statistics about the current experiment."""
        if not self.enabled:
            return {}
            
        try:
            experiment = mlflow.get_experiment_by_name(self.experiment_name)
            if not experiment:
                return {}
            
            runs = self.client.search_runs(experiment_ids=[experiment.experiment_id])
            
            stats = {
                "total_runs": len(runs),
                "experiment_name": self.experiment_name,
                "experiment_id": experiment.experiment_id
            }
            
            if runs:
                # Calculate some basic stats
                successful_runs = [r for r in runs if r.data.metrics.get("success", 0) == 1]
                stats["successful_runs"] = len(successful_runs)
                stats["success_rate"] = len(successful_runs) / len(runs)
                
                # Average duration
                durations = [r.data.metrics.get("session_duration_seconds", 0) for r in runs]
                stats["avg_duration"] = sum(durations) / len(durations) if durations else 0
            
            return stats
            
        except Exception as e:
            # print(f"⚠️  Failed to get experiment stats: {e}")
            return {}


# Global tracker instance
_global_tracker: Optional[MLflowTracker] = None


def get_mlflow_tracker(config: Config) -> MLflowTracker:
    """Get or create the global MLflow tracker instance."""
    global _global_tracker
    
    if _global_tracker is None:
        _global_tracker = MLflowTracker(config)
    
    return _global_tracker


def reset_mlflow_tracker():
    """Reset the global MLflow tracker (useful for testing)."""
    global _global_tracker
    _global_tracker = None
