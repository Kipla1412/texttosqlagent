from __future__ import annotations
from typing import Any, List
from pydantic import BaseModel, Field
from opensearchpy import OpenSearch
from tools.base import Tool, ToolConfirmation, ToolKind, ToolResult
from config.config import Config 
import json

from knowledgebase.opensearch import OpenSearchConnector

ARXIV_INDEX = "arxiv-papers-chunks"

class HybridSearchParams(BaseModel):
    """
    Parameters for hybrid search combining keyword and vector search.
    
    This tool performs a hybrid search that:
    1. Uses keyword search to find papers with relevant titles/abstracts
    2. Uses vector search to find semantically similar papers
    3. Combines and re-ranks results for better recall and precision
    """
    query_text: str = Field(..., description="The original keyword search text.")
    vector: List[float] = Field(..., description="The 1024-dimension vector from the jina_embedding tool.")
    limit: int = Field(default=5, description="Number of results to return.")


class ArxivHybridSearchTool(Tool):
    name = "arxiv_hybrid_search"
    description = f"Searches the '{ARXIV_INDEX}' index using hybrid BM25 and Vector RRF ranking."
    kind = ToolKind.NETWORK

    def __init__(self, config: Config):
        super().__init__(config)
        self.opensearch_connector = OpenSearchConnector(config)
        self.opensearch = self.opensearch_connector.connect()

    @property
    def schema(self) -> type[BaseModel]:
        return HybridSearchParams

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        try:
            params = HybridSearchParams(**invocation.params)

            # Constructing the Hybrid Query DSL
            search_body = {
                "size": params.limit,
                "_source": ["title", "chunk_text", "arxiv_id", "section_title"],
                "query": {
                    "hybrid": {
                        "queries": [
                            {
                                "match": {
                                    "chunk_text": {
                                        "query": params.query_text,
                                        "boost": 1.0
                                    }
                                }
                            },
                            {
                                "knn": {
                                    "embedding": {
                                        "vector": params.vector,
                                        "k": params.limit
                                    }
                                }
                            }
                        ]
                    }
                }
            }

            # Triggering your 'hybrid-rrf-pipeline'
            response = self.opensearch.search(
                index=ARXIV_INDEX,
                body=search_body,
                params={"search_pipeline": "hybrid-rrf-pipeline"}
            )

            hits = response["hits"]["hits"]
            results = []
            for hit in hits:
                source = hit["_source"]
                results.append({
                    "score": hit["_score"],
                    "title": source.get("title"),
                    "text": source.get("chunk_text"),
                    "arxiv_id": source.get("arxiv_id"),
                    "section": source.get("section_title")
                })

            return ToolResult.success_result(
                output=json.dumps(results, indent=2),
                metadata={"total_hits": response["hits"]["total"]["value"]}
            )
        except Exception as e:
            return ToolResult.error_result(error=f"Arxiv Hybrid Search failed: {str(e)}")