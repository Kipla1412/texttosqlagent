import asyncio
from typing import Any
from config.config import Config
from tools.base import Tool, ToolInvocation, ToolResult
from dataclasses import dataclass
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

class SubagentParams(BaseModel):
    goal: str = Field(
        ..., description="The specific task or goal for the subagent to accomplish"
    )


@dataclass
class SubagentDefinition:
    name: str
    description: str
    goal_prompt: str
    allowed_tools: list[str] | None = None
    max_turns: int = 20
    timeout_seconds: float = 600


class SubagentTool(Tool):
    def __init__(self, config: Config, definition: SubagentDefinition):
        super().__init__(config)
        self.definition = definition

    @property
    def name(self) -> str:
        return f"subagent_{self.definition.name}"

    @property
    def description(self) -> str:
        return f"subagent_{self.definition.description}"

    schema = SubagentParams

    def is_mutating(self, params: dict[str, Any]) -> bool:
        return True

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        from agent.agent import Agent
        from agent.events import AgentEventType

        params = SubagentParams(**invocation.params)
        if not params.goal:
            return ToolResult.error_result("No goal specified for sub-agent")

        config_dict = self.config.to_dict()
        config_dict["max_turns"] = self.definition.max_turns
        if self.definition.allowed_tools:
            config_dict["allowed_tools"] = self.definition.allowed_tools

        subagent_config = Config(**config_dict)

        prompt = f"""You are a specialized sub-agent with a specific task to complete.

        {self.definition.goal_prompt}

        YOUR TASK:
        {params.goal}

        IMPORTANT:
        - Focus only on completing the specified task
        - Use tools to gather information instead of guessing
        - Do not engage in unrelated actions
        - Once you have completed the task or have the answer, provide your final response
        - Be concise and direct in your output
        """

        tool_calls = []
        final_response = None
        error = None
        terminate_response = "goal"

        try:
            async with Agent(subagent_config) as agent:
                loop = asyncio.get_running_loop()
                deadline = (
                    loop.time() + self.definition.timeout_seconds
                )

                async for event in agent.run(prompt):
                    if loop.time() > deadline:
                        terminate_response = "timeout"
                        final_response = "Sub-agent timed out"
                        break

                    if event.type == AgentEventType.TOOL_CALL_START:
                        tool_name = event.data.get("name")
                        if tool_name and tool_name not in tool_calls:
                            tool_calls.append(tool_name)

                    elif event.type == AgentEventType.TEXT_COMPLETE:
                        final_response = event.data.get("content")
                    
                    elif event.type == AgentEventType.AGENT_END:
                        if final_response is None:
                            final_response = event.data.get("response")
                    
                    elif event.type == AgentEventType.AGENT_ERROR:
                        terminate_response = "error"
                        error = event.data.get("error", "Unknown")
                        final_response = f"Sub-agent error: {error}"
                        break

        except Exception as e:
            logger.exception("Sub-agent execution failed")
            terminate_response = "error"
            error = str(e)
            final_response = f"Sub-agent failed: {e}"
        
        if not final_response:
            final_response = "Sub-agent completed but returned no textual response."
        
        result = f"""Sub-agent '{self.definition.name}' completed. 
        Termination: {terminate_response}
        Tools called: {', '.join(tool_calls) if tool_calls else 'None'}

        Result:
        {final_response or 'No response'}
        """

        if error:
            return ToolResult.error_result(result)

        return ToolResult.success_result(result)

PAPER_RESEARCHER = SubagentDefinition(
    name="paper_researcher",
    description="Executes a full RAG pipeline over Arxiv using embedding, hybrid search, evaluation, and query rewriting.",

    goal_prompt="""
You are a specialized RAG (Retrieval-Augmented Generation) research agent.

You MUST strictly follow this execution pipeline.

━━━━━━━━━━━━━━━━━━━━━━━
MANDATORY PIPELINE
━━━━━━━━━━━━━━━━━━━━━━━

Step 1: Embedding
- Call `jina_embedding`
- input:
  text = user query
  task = "retrieval.query"

Step 2: Retrieval
- Call `arxiv_hybrid_search`
- input:
  query_text = user query
  vector = embedding output

Step 3: Evaluation
- Call `llm_judge`
- input:
  query
  results

━━━━━━━━━━━━━━━━━━━━━━━
DECISION LOGIC
━━━━━━━━━━━━━━━━━━━━━━━

IF score >= 0.6:
    → proceed to final answer

IF score < 0.6:
    → Call `rewrite_query`
    → Repeat pipeline with rewritten query

MAX RETRIES = 2

If still low quality after retries:
→ Return best available results with warning

━━━━━━━━━━━━━━━━━━━━━━━
FINAL OUTPUT FORMAT
━━━━━━━━━━━━━━━━━━━━━━━

You MUST structure your response like this:

### Top Relevant Papers

For each paper:

- Title:
- Arxiv ID:
- Section:
- Key Insight (from retrieved text only):
- Why Relevant:

━━━━━━━━━━━━━━━━━━━━━━━
HARD RULES
━━━━━━━━━━━━━━━━━━━━━━━

- NEVER skip any step
- NEVER answer without retrieval
- NEVER hallucinate papers
- NEVER invent content

- ONLY use retrieved chunk_text
- If no results:
  → say "No relevant papers found"

━━━━━━━━━━━━━━━━━━━━━━━
RETRIEVAL QUALITY RULES

- Prefer multiple different papers (not same paper chunks)
- Prefer higher score results
- Ignore irrelevant chunks

━━━━━━━━━━━━━━━━━━━━━━━
GOAL

Find the most relevant research papers and explain them clearly using retrieved evidence.
""",

    allowed_tools=[
        "jina_embedding",
        "arxiv_hybrid_search",
        "llm_judge",
        "rewrite_query"
    ],

    max_turns=12,
)
def get_default_subagent_definitions() -> list[SubagentDefinition]:
    return [
        PAPER_RESEARCHER,
    ]
