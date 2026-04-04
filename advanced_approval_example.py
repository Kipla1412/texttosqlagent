# Example: How to integrate with approval system

from tools.base import Tool, ToolResult, ToolInvocation, ToolKind, ToolConfirmation
from safety.approval import ApprovalManager, ApprovalContext, ApprovalDecision
from config.config import Config, ApprovalPolicy
from pathlib import Path

class AdvancedCustomTool(Tool):
    name = "advanced_file_tool"
    description = "Advanced tool with custom approval logic"
    kind = ToolKind.WRITE
    
    def __init__(self, config: Config):
        super().__init__(config)
        # Create custom approval manager
        self.approval_manager = ApprovalManager(
            approval_policy=ApprovalPolicy.ON_REQUEST,
            cwd=config.cwd
        )
    
    def get_confirmation(self, invocation: ToolInvocation) -> ToolConfirmation | None:
        """Advanced approval with custom logic"""
        params = invocation.params
        
        # Custom safety checks
        if self._is_dangerous_path(params.get("file_path", "")):
            return ToolConfirmation(
                tool_name=self.name,
                params=params,
                description="🚨 DANGEROUS: Attempts to access sensitive path",
                is_dangerous=True
            )
        
        # Use approval manager for complex decisions
        approval_context = ApprovalContext(
            tool_name=self.name,
            params=params,
            is_mutating=self.is_mutating(params),
            affected_paths=[Path(params.get("file_path", ""))],
            is_dangerous=params.get("action") == "delete"
        )
        
        decision = self.approval_manager.check_approval(approval_context)
        
        if decision == ApprovalDecision.APPROVED:
            return None  # No confirmation needed
        
        if decision == ApprovalDecision.REJECTED:
            return ToolConfirmation(
                tool_name=self.name,
                params=params,
                description="❌ REJECTED: Operation not allowed",
                is_dangerous=True
            )
        
        # Needs confirmation
        return ToolConfirmation(
            tool_name=self.name,
            params=params,
            description=f"⚠️ Requires confirmation: {params.get('action', 'unknown')}",
            is_dangerous=params.get("action") == "delete"
        )
    
    def _is_dangerous_path(self, path: str) -> bool:
        """Custom path safety check"""
        dangerous_patterns = [
            "/etc/", "/sys/", "/proc/", "/dev/",
            "~/.ssh/", "~/.aws/", ".env"
        ]
        return any(pattern in path for pattern in dangerous_patterns)
    
    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        # Tool execution logic here
        return ToolResult.success_result("Operation completed")
    
    @property 
    def schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "file_path": {"type": "string"},
                "action": {"type": "string", "enum": ["read", "write", "delete"]}
            }
        }
