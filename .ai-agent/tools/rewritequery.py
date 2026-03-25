from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field
from tools.base import Tool, ToolInvocation, ToolKind, ToolResult
from client.llm_client import LLMClient
from config.config import Config
import json
import logging

logger = logging.getLogger(__name__)


class RewriteQueryParams(BaseModel):
    """Parameters for query rewriting."""

    original_query: str = Field(..., description="Original user query")
    score: float = Field(..., description="Judge score between 0.0 and 1.0")
    issues: List[str] = Field(default_factory=list, description="Problems detected in search results")
    recommendations: List[str] = Field(default_factory=list, description="Suggestions for improving the query")


class RewriteQueryTool(Tool):

    name = "rewrite_query"
    description = "Used ONLY when retrieval quality is low (score < 0.6). Improves the query and retries search."
    kind = ToolKind.NETWORK

    def __init__(self, config: Config):
        super().__init__(config)
        self.llm_client = LLMClient(config)

    @property
    def schema(self) -> type[BaseModel]:
        return RewriteQueryParams

    async def execute(self, invocation: ToolInvocation) -> ToolResult:

        try:
            params = RewriteQueryParams(**invocation.params)

            rewrite_prompt = f"""
You are an expert search query optimizer.

Your task is to improve a search query so that a retrieval system can find better documents.

ORIGINAL QUERY:
{params.original_query}

CURRENT RETRIEVAL SCORE:
{params.score}

ISSUES DETECTED:
{params.issues}

RECOMMENDATIONS:
{params.recommendations}

Rewrite the query to improve retrieval quality.

Guidelines:
- Make the query more specific
- Use better technical terms if necessary
- Include important context
- Avoid vague or generic wording

Return ONLY the improved query text.

Example:

Original Query:
machine learning

Improved Query:
supervised machine learning algorithms for classification tasks
"""

            response_text = ""
            async for event in self.llm_client.chat_completion(
                messages=[{"role": "user", "content": rewrite_prompt}],
                temperature=0.3
            ):
                if event.type == "text_complete":
                    response_text = event.data.get("content", "")
                    break

            rewritten_query = response_text.strip()

            if rewritten_query.startswith("```"):
                rewritten_query = rewritten_query.replace("```", "").strip()

            rewritten_query = rewritten_query.strip('"')

            if not rewritten_query:
                rewritten_query = params.original_query

            return ToolResult.success_result(
                output=json.dumps(
                    {
                        "original_query": params.original_query,
                        "rewritten_query": rewritten_query,
                        "score": params.score
                    },
                    indent=2
                ),
                metadata={
                    "score": params.score,
                    "rewritten_query": rewritten_query
                }
            )

        except Exception as e:
            logger.error(f"Rewrite query failed: {e}")
            return ToolResult.error_result(
                error=f"Rewrite query failed: {str(e)}"
            )