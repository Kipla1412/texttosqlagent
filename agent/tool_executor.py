from tools.base import ToolInvocation, ToolResult


class ToolExecutor:

    def __init__(self, session):
        self.session = session


    async def run_tool(self, tool, params):

        invocation = ToolInvocation(
            params=params,
            cwd=self.session.config.cwd,
        )

        # Validate params
        errors = tool.validate_params(params)
        if errors:
            return ToolResult.error_result("\n".join(errors))

        # Handle approval
        confirmation = await tool.get_confirmation(invocation)

        if confirmation:
            approved = await self.session.approval_manager.request_confirmation(
                confirmation
            )

            if not approved:
                return ToolResult.error_result("Tool execution rejected.")

        # MLflow tracing
        with self.session.mlflow.start_span(
            name=tool.name,
            attributes={
                "span_type": "tool",
                "tool.name": tool.name,
                "tool.kind": str(tool.kind),
            },
        ):
            return await tool.execute(invocation)