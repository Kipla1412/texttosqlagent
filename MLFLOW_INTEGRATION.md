# MLflow Integration for AI Agent

This document describes the MLflow integration that has been implemented to track experiments, metrics, and performance of the AI Agent.

## Overview

The MLflow integration provides comprehensive tracking for:
- Agent interactions and conversations
- Tool usage and execution metrics
- Session performance and statistics
- Token usage and costs
- Error tracking and debugging

## Features

### 📊 Experiment Tracking
- Automatic experiment creation and management
- Session-based run tracking
- Parameter logging (model config, temperature, etc.)
- Metric collection (duration, success rates, token usage)

### 🛠️ Tool Execution Tracking
- Individual tool execution metrics
- Performance timing analysis
- Error logging and debugging
- Tool usage patterns

### 📈 Session Analytics
- Interaction-level metrics
- Session summaries and statistics
- Success rate tracking
- Performance trends

## Configuration

### Environment Variables

Set these environment variables to configure MLflow:

```bash
# Enable/disable MLflow tracking (default: true)
export MLFLOW_ENABLED=true

# MLflow tracking server URI (default: http://localhost:5000)
export MLFLOW_TRACKING_URI=http://localhost:5000

# Experiment name (default: AIAgent)
export MLFLOW_EXPERIMENT_NAME=AIAgent
```

### Configuration in Code

The MLflow configuration is automatically loaded from the `Config` class:

```python
from config.config import Config

config = Config()
print(f"MLflow enabled: {config.mlflow_enabled}")
print(f"Tracking URI: {config.mlflow_tracking_uri}")
print(f"Experiment: {config.mlflow_experiment_name}")
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirement.txt
```

### 2. Start MLflow Server

```bash
# Using the provided setup script
chmod +x setup_mlflow.sh
./setup_mlflow.sh

# Or manually
mlflow ui --port 5000 --backend-store-uri sqlite:///mlflow.db
```

### 3. Verify Installation

```bash
python test_mlflow_integration.py
```

## Usage

### Automatic Tracking

The MLflow integration is automatically enabled when you use the `Agent` class:

```python
from agent.agent import Agent
from config.config import Config

async def main():
    config = Config()
    async with Agent(config) as agent:
        # Your agent interactions here
        async for event in agent.run("Hello, how can you help me?"):
            # Process events...
            pass
```

### Manual Tracking

You can also use the MLflow tracker directly:

```python
from utils.mlflow_tracker import get_mlflow_tracker
from config.config import Config

config = Config()
tracker = get_mlflow_tracker(config)

# Start a run
run_id = tracker.start_run("session_123")

# Log interactions
tracker.log_agent_interaction(
    user_message="Hello",
    agent_response="Hi there!",
    tools_used=["search"],
    session_duration=2.5,
    token_usage={"total_tokens": 50},
    success=True
)

# End the run
tracker.end_run()
```

## Tracked Metrics

### Agent Interaction Metrics
- `session_duration_seconds`: Time taken for the interaction
- `user_message_length`: Length of user input
- `agent_response_length`: Length of agent response
- `tools_used_count`: Number of tools used
- `success`: Whether the interaction was successful (1/0)
- `prompt_tokens`: Number of prompt tokens used
- `completion_tokens`: Number of completion tokens used
- `total_tokens`: Total tokens used

### Tool Execution Metrics
- `{tool_name}_execution_time`: Time taken for tool execution
- `{tool_name}_success`: Whether tool execution succeeded (1/0)

### Session Summary Metrics
- `total_interactions`: Total number of interactions in session
- `total_duration_seconds`: Total session duration
- `total_tools_used`: Total number of tools used
- `success_rate`: Overall success rate (0.0-1.0)
- `avg_interaction_duration`: Average duration per interaction

## Artifacts

The integration automatically saves artifacts for:

### Interaction Logs
Detailed JSON logs of each interaction including:
- Timestamp
- User message and agent response
- Tools used and their arguments
- Token usage
- Success status

### Error Logs
When tools fail, detailed error information is saved:
- Tool name and arguments
- Error message
- Timestamp

### Session Summaries
Complete session summaries with:
- Session ID and duration
- Total interactions and tools used
- Success rates and performance metrics

## Viewing Results

### MLflow UI

Access the MLflow UI at `http://localhost:5000` to view:
- Experiment overview
- Run comparisons
- Metric charts
- Artifact downloads

### Programmatic Access

```python
from utils.mlflow_tracker import get_mlflow_tracker
from config.config import Config

config = Config()
tracker = get_mlflow_tracker(config)

# Get experiment statistics
stats = tracker.get_experiment_stats()
print(f"Total runs: {stats['total_runs']}")
print(f"Success rate: {stats['success_rate']}")
```

## Troubleshooting

### Common Issues

1. **MLflow server not running**
   ```bash
   mlflow ui --port 5000 --backend-store-uri sqlite:///mlflow.db
   ```

2. **Connection refused**
   - Check if MLflow server is running on the correct port
   - Verify `MLFLOW_TRACKING_URI` environment variable

3. **Permission errors**
   - Ensure the `mlruns` directory is writable
   - Check database file permissions

4. **Missing dependencies**
   ```bash
   pip install mlflow pydantic
   ```

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Testing

Run the integration test to verify everything works:

```bash
python test_mlflow_integration.py
```

## Best Practices

### 1. Environment Configuration
- Use environment variables for configuration
- Separate development and production experiments
- Use meaningful experiment names

### 2. Metric Naming
- Use consistent naming conventions
- Include units in metric names when applicable
- Use hierarchical naming for related metrics

### 3. Artifact Management
- Regularly clean up old artifacts
- Use descriptive artifact names
- Compress large artifacts when possible

### 4. Performance Considerations
- Batch logging operations when possible
- Use asynchronous logging for high-throughput scenarios
- Monitor MLflow server performance

## Advanced Usage

### Custom Metrics

Add custom metrics to track domain-specific information:

```python
# In your agent code
self.session.mlflow_tracker.log_metrics({
    "custom_metric_1": value1,
    "custom_metric_2": value2
})
```

### Experiment Comparison

Use MLflow's comparison features to analyze different configurations:

```python
# Compare runs with different temperatures
# Run 1: temperature=0.1
# Run 2: temperature=0.7
# Run 3: temperature=1.0
```

### Integration with CI/CD

Include MLflow tracking in your CI/CD pipeline:

```yaml
# GitHub Actions example
- name: Run MLflow tests
  run: |
    python test_mlflow_integration.py
    # Upload results to MLflow server
```

## API Reference

### MLflowTracker Class

#### Methods

- `start_run(session_id, run_name=None)`: Start a new MLflow run
- `end_run()`: End the current run
- `log_agent_interaction(...)`: Log agent interaction metrics
- `log_tool_execution(...)`: Log tool execution metrics
- `log_session_summary(...)`: Log session summary metrics
- `get_experiment_stats()`: Get experiment statistics

### Session Integration

The `Session` class automatically integrates MLflow tracking:

- `track_agent_interaction(...)`: Track agent interactions
- `track_tool_execution(...)`: Track tool usage
- `track_session_summary(...)`: Track session summaries
- `cleanup()`: Clean up MLflow resources

## Contributing

When contributing to the MLflow integration:

1. Add tests for new features
2. Update documentation
3. Follow existing code patterns
4. Test with different MLflow versions
5. Consider backward compatibility

## License

This MLflow integration follows the same license as the AI Agent project.
