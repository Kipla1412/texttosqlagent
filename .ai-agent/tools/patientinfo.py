from pydantic import BaseModel
from tools.base import Tool, ToolResult, ToolInvocation, ToolKind

class SavePatientInfo(BaseModel):
    name: str
    age: int
    gender: str

class SavePatientInfoTool(Tool):
    name = "save_patient_info"
    description = "Store patient basic information"
    kind = ToolKind.MEMORY
    schema = SavePatientInfo

    async def execute(self, invocation: ToolInvocation) -> ToolResult:

        params = invocation.params

        name = params["name"]
        age = params["age"]
        gender = params["gender"]

        # # Example storage (you can replace with DB)
        # self.config.memory["patient_info"] = {
        #     "name": name,
        #     "age": age,
        #     "gender": gender,
        # }

        return ToolResult.success_result(
            f"Patient info saved: {name}, {age}, {gender}"
        )