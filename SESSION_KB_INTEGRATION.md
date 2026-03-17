# Knowledge Base Integration in Sessions

Your knowledge base clients (OpenSearchConnector and EmbeddingConnector) are now integrated into the Session class, just like the LLM client.

## What's Been Added

### Session Class Updates
```python
class Session:
    def __init__(self, config: Config):
        # ... existing clients ...
        self.client = LLMClient(config=config)
        self.tool_registry = create_default_registry(config=config)
        
        # NEW: Knowledge base clients
        self.opensearch_connector = OpenSearchConnector(config)
        self.embedding_connector = EmbeddingConnector(config)
```

### New Session Methods

#### `get_knowledge_base_clients()`
Get direct access to knowledge base clients:
```python
opensearch, embedding = session.get_knowledge_base_clients()
```

#### `search_knowledge_base(query, limit=5)`
Convenience method for quick knowledge base searches:
```python
results = await session.search_knowledge_base("machine learning", limit=10)
```

## Usage Examples

### In Custom Tools
Access knowledge base clients from within any tool:
```python
from tools.base import Tool, ToolResult

class MyTool(Tool):
    async def execute(self, invocation):
        # Access session's knowledge base clients
        opensearch, embedding = self.session.get_knowledge_base_clients()
        
        # Use them directly
        with opensearch as client:
            results = client.search(index="my-data", body={...})
```

### In Agent Code
Use the convenience method:
```python
# In your agent or custom code
async def process_query(session, query):
    results = await session.search_knowledge_base(query)
    
    # Process results
    for result in results:
        print(f"Title: {result['title']}")
        print(f"Content: {result['content'][:100]}...")
```

## Available Tools

### New: `knowledge_search` Tool
Demonstrates knowledge base integration:
```python
> using knowledge_search with query "python debugging", limit=3
```

### Updated: `llm_judge` Tool
Now uses the new LLM session infrastructure for better query judgment and rewriting.

## Benefits

### Unified Access
- All clients available through one session object
- Consistent configuration and error handling
- Easy resource management

### Convenience Methods
- Quick access without importing multiple modules
- Built-in error handling and logging
- Standardized search patterns

### Session Integration
- Knowledge base state managed with session lifecycle
- Available throughout agent runtime
- Consistent with existing patterns

## Architecture

```
Session
├── LLM Client (existing)
├── Tool Registry (existing)
├── Context Manager (existing)
├── OpenSearchConnector (NEW)
├── EmbeddingConnector (NEW)
└── MCP Manager (existing)
```

## Migration Guide

### Before (Separate Clients)
```python
from knowledgebase.opensearch import OpenSearchConnector
from knowledgebase.embedding import EmbeddingConnector

# Manual setup
opensearch = OpenSearchConnector(config)
embedding = EmbeddingConnector(config)

# Manual resource management
with opensearch as client:
    # use client
    pass

async with embedding as client:
    # use client
    pass
```

### After (Session Integration)
```python
# Get clients from session
opensearch, embedding = session.get_knowledge_base_clients()

# Or use convenience method
results = await session.search_knowledge_base("my query")
```

## Configuration

Same environment variables as before:
- `OPENSEARCH_HOST`, `OPENSEARCH_PORT`, `OPENSEARCH_SSL`
- `OPENSEARCH_USER`, `OPENSEARCH_PASSWORD`
- `JINA_API_KEY`, `JINA_BASE_URL`
- `JINA_MODEL`, `JINA_DIMENSIONS`

## Error Handling

All knowledge base operations include:
- Automatic retry logic
- Graceful degradation
- Detailed logging
- Resource cleanup

## Best Practices

1. **Use session methods** when possible for consistency
2. **Access clients directly** only for custom operations
3. **Handle exceptions** - knowledge base may be unavailable
4. **Use context managers** for resource safety
5. **Monitor performance** through session stats

Your knowledge base is now fully integrated into the session infrastructure!
