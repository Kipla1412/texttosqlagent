from __future__ import annotations
import json
import httpx
from typing import Any, Literal, List
from pydantic import BaseModel, Field
from tools.base import Tool, ToolInvocation, ToolKind, ToolResult
from config.config import Config
from knowledgebase.embedding import EmbeddingConnector

class JinaEmbeddingParams(BaseModel):
    
    text: str = Field(..., description="The text string to convert into a vector.")
    task: Literal["retrieval.query", "retrieval.passage"] = Field(
        default="retrieval.query", 
        description="Task type: 'retrieval.query' for searching, 'retrieval.passage' for saving data."
    )

class JinaEmbeddingTool(Tool):
    name = "jina_embedding"
    description = "Generates a 1024-dimension vector using Jina AI v3 API for semantic search."
    kind = ToolKind.NETWORK

    def __init__(self, config: Config):
        super().__init__(config)

        self.embedding_connector = EmbeddingConnector(config)
      

    @property
    def schema(self) -> type[BaseModel]:
        return JinaEmbeddingParams

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        try:
            params = JinaEmbeddingParams(**invocation.params)
            client = self.embedding_connector.connect()
            
            response = await client.post(
                self.config.jina_api_url,
                json={
                    "model": self.config.jina_model,
                    "task": params.task,
                    "dimensions": self.config.jina_dimensions,
                    "input": [params.text]
                }
            )
            
            response.raise_for_status()
            data = response.json()
            vector = data["data"][0]["embedding"]
                
            return ToolResult.success_result(
                output=json.dumps({"vector": vector}),
                metadata={
                    "model": self.config.jina_model,
                    "dimensions": self.config.jina_dimensions,
                    "task": params.task
                }
            )

        except Exception as e:
            return ToolResult.error_result(error=f"Jina Embedding failed: {str(e)}")