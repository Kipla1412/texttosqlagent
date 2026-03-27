from tools.base import Tool, ToolResult, ToolInvocation, ToolKind
from pydantic import BaseModel
from utils.conversation import build_conversation_text


class SummarySchema(BaseModel):
    pass


class GeneratePatientSummaryTool(Tool):

    name = "generate_patient_summary"
    description = "Generate short patient summary"
    kind = ToolKind.READ
    schema = SummarySchema

    async def execute(self, invocation: ToolInvocation) -> ToolResult:

        try:

            session = invocation.metadata["session"]

            messages = session.context_manager.get_messages()

            conversation = build_conversation_text(messages)

            prompt = f"""
                    Summarize the following patient conversation into one clear,
                    human-readable paragraph.

                    Conversation:
                    {conversation}

                    Rules:
                    • Use simple, natural language
                    • No bullet points
                    • No diagnoses
                    • No assumptions
                    • Just describe the main symptoms and context

                    Write ONE short paragraph only.

            Conversation:
            {conversation}
            """

            summary = await session.client.complete(prompt)

            return ToolResult.success_result(summary)

        except Exception as e:
            return ToolResult.error_result(str(e))