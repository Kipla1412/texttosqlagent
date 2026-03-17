from __future__ import annotations
import asyncio
import time
from typing import Any, List, Dict
from pydantic import BaseModel, Field
from tools.base import Tool, ToolInvocation, ToolKind, ToolResult
from client.llm_client import LLMClient
from knowledgebase.opensearch import OpenSearchConnector
from knowledgebase.embedding import EmbeddingConnector
from config.config import Config
import json
import logging

logger = logging.getLogger(__name__)

class QueryJudgeParams(BaseModel):
    """Parameters for the LLM Judge tool."""
    query: str = Field(..., description="The original query to be judged and potentially rewritten")
    max_retries: int = Field(default=3, description="Maximum number of query rewrite attempts")
    break_time: int = Field(default=5, description="Break time in seconds between retries")
    context_threshold: float = Field(default=0.3, description="Minimum relevance score threshold (0-1)")

class LLMJudgeTool(Tool):
    """
    LLM Judge Tool that analyzes retrieved data and rewrites queries if results are poor.
    
    This tool:
    1. Retrieves initial results from knowledge base
    2. Uses LLM to judge result quality
    3. Rewrites query if results are poor
    4. Retries up to max_retries times with breaks
    """
    name = "llm_judge"
    description = "Analyzes knowledge base results and rewrites queries if needed, with retry logic."
    kind = ToolKind.NETWORK

    @property
    def schema(self) -> type[BaseModel]:
        return QueryJudgeParams

    def __init__(self, config: Config):
        super().__init__(config)
        self.llm_client = LLMClient(config)
        self.opensearch = OpenSearchConnector(config)
        self.embedding = EmbeddingConnector(config)

    async def _judge_results(self, query: str, results: List[Dict]) -> tuple[bool, str]:
        """
        Use LLM to judge if results are relevant to the query.
        
        Returns:
            tuple: (is_good, judgment_reason)
        """
        if not results:
            return False, "No results found"
        
        results_summary = json.dumps(results[:3], indent=2)  # First 3 results for context
        
        judge_prompt = f"""You are a query result judge. Analyze if these search results are relevant and helpful for the user's query.

Original Query: "{query}"

Search Results:
{results_summary}

Judge the results based on:
1. Relevance to the query
2. Quality and completeness of information
3. Whether results actually answer what the user is asking

Respond with exactly one word: either "GOOD" or "BAD"
If BAD, provide a brief reason after a pipe character: "BAD|reason"

Examples:
- GOOD
- BAD|Results are about different topic
- BAD|Results are too generic and don't answer the specific question"""

        try:
            response = await self.llm_client.chat_completion(
                messages=[{"role": "user", "content": judge_prompt}],
                temperature=0.1
            )
            
            judgment = response.content.strip().upper()
            
            if "|" in judgment:
                is_good, reason = judgment.split("|", 1)
                return is_good == "GOOD", reason
            else:
                return judgment == "GOOD", ""
                
        except Exception as e:
            logger.error(f"Error judging results: {e}")
            return False, f"Judgment error: {str(e)}"

    async def _rewrite_query(self, original_query: str, judgment_reason: str, attempt: int) -> str:
        """
        Use LLM to rewrite the query based on why previous results were bad.
        """
        rewrite_prompt = f"""You are a query optimization expert. The previous search query gave poor results.

Original Query: "{original_query}"
Problem with results: {judgment_reason}
Attempt number: {attempt} of 3

Rewrite the query to be more specific and effective. Consider:
1. Using more precise terminology
2. Adding context or constraints
3. Being more specific about what information is needed
4. Using different phrasing or synonyms

Return ONLY the rewritten query, nothing else.

Examples:
Original: "machine learning" -> Rewritten: "supervised machine learning algorithms for classification"
Original: "python error" -> Rewritten: "Python TypeError list object is not callable fix" """

        try:
            response = await self.llm_client.chat_completion(
                messages=[{"role": "user", "content": rewrite_prompt}],
                temperature=0.3
            )
            
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"Error rewriting query: {e}")
            return original_query  # Return original if rewrite fails

    async def _search_knowledge_base(self, query: str) -> List[Dict]:
        """
        Search the knowledge base using the query.
        """
        try:
            # Get embedding for the query
            async with self.embedding as client:
                embedding_response = await client.post(
                    self.config.jina_api_url,
                    json={
                        "model": self.config.jina_model,
                        "task": "retrieval.query",
                        "dimensions": self.config.jina_dimensions,
                        "input": [query]
                    }
                )
                embedding_response.raise_for_status()
                vector = embedding_response.json()["data"][0]["embedding"]

            # Search OpenSearch with the vector
            with self.opensearch as client:
                search_body = {
                    "size": 5,
                    "_source": ["title", "content", "score"],
                    "query": {
                        "knn": {
                            "embedding": {
                                "vector": vector,
                                "k": 5
                            }
                        }
                    }
                }
                
                response = client.search(
                    index="knowledge-base",
                    body=search_body
                )
                
                hits = response["hits"]["hits"]
                results = []
                for hit in hits:
                    source = hit["_source"]
                    results.append({
                        "title": source.get("title", ""),
                        "content": source.get("content", ""),
                        "score": hit["_score"]
                    })
                
                return results
                
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return []

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        """
        Execute the LLM Judge workflow with retry logic.
        """
        try:
            params = QueryJudgeParams(**invocation.params)
            current_query = params.query
            attempt = 1
            
            while attempt <= params.max_retries:
                logger.info(f"LLM Judge: Attempt {attempt}/{params.max_retries} for query: '{current_query}'")
                
                # Search knowledge base
                results = await self._search_knowledge_base(current_query)
                
                # Judge the results
                is_good, reason = await self._judge_results(current_query, results)
                
                if is_good:
                    logger.info(f"LLM Judge: Results are GOOD on attempt {attempt}")
                    return ToolResult.success_result(
                        output=json.dumps({
                            "status": "success",
                            "query": current_query,
                            "attempt": attempt,
                            "results": results,
                            "judgment": "Results are relevant and helpful"
                        }, indent=2),
                        metadata={
                            "attempt": attempt,
                            "results_count": len(results),
                            "final_query": current_query
                        }
                    )
                
                # Results are bad, rewrite query
                logger.warning(f"LLM Judge: Results are BAD on attempt {attempt}: {reason}")
                
                if attempt < params.max_retries:
                    # Take a break before retrying
                    logger.info(f"LLM Judge: Taking {params.break_time}s break before retry...")
                    await asyncio.sleep(params.break_time)
                    
                    # Rewrite the query
                    current_query = await self._rewrite_query(current_query, reason, attempt)
                    logger.info(f"LLM Judge: Rewritten query for attempt {attempt + 1}: '{current_query}'")
                
                attempt += 1
            
            # All attempts failed
            logger.error(f"LLM Judge: All {params.max_retries} attempts failed")
            return ToolResult.error_result(
                error=f"All {params.max_retries} attempts failed. Last query: '{current_query}'"
            )
            
        except Exception as e:
            logger.error(f"LLM Judge execution error: {e}")
            return ToolResult.error_result(error=f"LLM Judge failed: {str(e)}")
