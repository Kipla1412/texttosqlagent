from __future__ import annotations
from typing import List, Dict
from pydantic import BaseModel, Field
from tools.base import Tool, ToolInvocation, ToolKind, ToolResult
from client.llm_client import LLMClient
from config.config import Config
import json
import logging

logger = logging.getLogger(__name__)


class LLMJudgeParams(BaseModel):
    """Parameters for LLM Judge tool."""

    query: str = Field(..., description="The original query to judge")
    results: List[Dict] = Field(..., description="Search results to judge")
    judgment_criteria: str = Field(
        default="relevance and quality",
        description="Criteria for judging results",
    )


class LLMJudgeTool(Tool):

    name = "llm_judge"
    description = "MANDATORY evaluation step. Scores retrieval quality. Determines whether query rewriting is needed."
    kind = ToolKind.NETWORK
    # allowed_tools = ["jina_embedding", "arxiv_hybrid_search", "paper_researcher"]

    def __init__(self, config: Config):
        super().__init__(config)
        self.llm_client = LLMClient(config)

    @property
    def schema(self) -> type[BaseModel]:
        return LLMJudgeParams

    async def execute(self, invocation: ToolInvocation) -> ToolResult:

        try:
            params = LLMJudgeParams(**invocation.params)

            if not params.results:
                return ToolResult.success_result(
                    output=json.dumps(
                        {
                            "score": 0.0,
                            "reasoning": "No results found",
                            "issues": ["No retrieval results"],
                            "recommendations": ["Try broader search terms"],
                        },
                        indent=2,
                    ),
                    metadata={"score": 0.0},
                )

            results_summary = json.dumps(params.results[:3], indent=2)

            judge_prompt = f"""
You are an expert information retrieval evaluator.

Your task is to evaluate the quality of search results for a user query.

USER QUERY:
{params.query}

EVALUATION CRITERIA:
{params.judgment_criteria}

SEARCH RESULTS (top results):
{results_summary}

Evaluate how well these results answer the query.

Consider the following factors carefully:
1. Relevance — do the results directly match the query intent?
2. Coverage — do the results contain enough useful information?
3. Specificity — are the results specific or too generic?
4. Accuracy — are the results clearly related to the query topic?

SCORING SCALE (0.0 - 1.0):

0.90 - 1.00 → Perfect results (highly relevant and complete)  
0.70 - 0.89 → Very good results (mostly relevant)  
0.50 - 0.69 → Moderate relevance (partially useful)  
0.30 - 0.49 → Weak results (low relevance)  
0.00 - 0.29 → Irrelevant results  

IMPORTANT RULES:
- Output must be valid JSON
- Score must be a float between 0.0 and 1.0
- Do not include explanations outside JSON
- Be strict and realistic when scoring

Return ONLY JSON in this format:

{{
  "score": 0.0,
  "reasoning": "brief explanation of why this score was given",
  "issues": [
    "problem with the results"
  ],
  "recommendations": [
    "how the query could be improved"
  ]
}}
"""

            response_text = ""
            async for event in self.llm_client.chat_completion(
                messages=[{"role": "user", "content": judge_prompt}],
                temperature=0.2
            ):
                if event.type == "text_complete":
                    response_text = event.data.get("content", "")
                    break

            judgment_text = response_text.strip()

            if judgment_text.startswith("```"):
                judgment_text = judgment_text.replace("```json", "")
                judgment_text = judgment_text.replace("```", "")
                judgment_text = judgment_text.strip()


            try:
                judgment = json.loads(judgment_text)

            except json.JSONDecodeError:
                return ToolResult.success_result(
                    output=json.dumps(
                        {
                            "score": 0.5,
                            "reasoning": "Could not parse LLM judgment",
                            "issues": ["Parsing error"],
                            "recommendations": ["Manual review needed"],
                        },
                        indent=2,
                    ),
                    metadata={"score": 0.5, "parsing_error": True},
                )

            score = float(judgment.get("score", 0.0))
            score = max(0.0, min(score, 1.0))
            judgment["score"] = score
            
            return ToolResult.success_result(
                output=json.dumps(judgment, indent=2),
                metadata={
                    "score": score,
                    "result_count": len(params.results),
                },
            )

        except Exception as e:
            logger.error(f"LLM Judge failed: {e}")
            return ToolResult.error_result(
                error=f"LLM Judge failed: {str(e)}"
            )