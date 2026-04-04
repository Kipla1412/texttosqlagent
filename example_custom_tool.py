from tools.base import Tool, ToolResult, ToolInvocation, ToolKind, ToolConfirmation
from pydantic import BaseModel
from pathlib import Path

class CustomToolSchema(BaseModel):
    file_path: str
    action: str = "read"  # read, write, delete

class CustomToolWithApproval(Tool):
    name = "custom_file_tool"
    description = "Custom tool with approval control"
    kind = ToolKind.WRITE  # This triggers approval system
    
    def get_confirmation(self, invocation: ToolInvocation) -> ToolConfirmation | None:
        """Custom approval logic"""
        params = invocation.params
        action = params.get("action", "read")
        file_path = params.get("file_path", "")
        
        # Auto-approve read operations
        if action == "read":
            return None
            
        # Require confirmation for write/delete operations
        if action in ["write", "delete"]:
            return ToolConfirmation(
                tool_name=self.name,
                params=params,
                description=f"⚠️ {action.upper()} file: {file_path}",
                is_dangerous=action == "delete",  # Mark as dangerous
                affected_paths=[Path(file_path)]  # Track affected files
            )
            
        return None
    
    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        try:
            params = invocation.params
            file_path = params.get("file_path", "")
            action = params.get("action", "read")
            
            if action == "read":
                # Read operation (auto-approved)
                if Path(file_path).exists():
                    content = Path(file_path).read_text()
                    return ToolResult.success_result(f"File content:\n{content}")
                else:
                    return ToolResult.error_result("File not found")
                    
            elif action == "write":
                # Write operation (requires approval)
                content = params.get("content", "")
                Path(file_path).write_text(content)
                return ToolResult.success_result(f"Written to {file_path}")
                
            elif action == "delete":
                # Delete operation (requires approval + marked dangerous)
                if Path(file_path).exists():
                    Path(file_path).unlink()
                    return ToolResult.success_result(f"Deleted {file_path}")
                else:
                    return ToolResult.error_result("File not found")
                    
            else:
                return ToolResult.error_result(f"Unknown action: {action}")
                
        except Exception as e:
            return ToolResult.error_result(str(e))
    
    @property
    def schema(self) -> type[CustomToolSchema]:
        return CustomToolSchema
