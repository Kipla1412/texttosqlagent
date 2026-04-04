
from __future__ import annotations
import os
import sys
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel
from tools.base import Tool, ToolResult, ToolInvocation, ToolKind, ToolConfirmation
from utils.conversation import build_conversation_text
from utils.patientstorage import get_patient_folder
from utils.soapreport import SOAPReportGenerator
from utils.soapparser import parse_soap_note
import os

class SOAPReportSchema(BaseModel):
    # If the LLM doesn't know the ID, we can make this optional 
    # and pull it from the session instead
    patient_id: str | None = None

class GenerateSOAPReportTool(Tool):
    name = "generate_soap_report"
    description = "Generate a structured clinical SOAP report PDF"
    kind = ToolKind.WRITE
    
    # Non-breaking session injection
    session = None 

    @property
    def schema(self):
        return SOAPReportSchema

    async def get_confirmation(self, invocation: ToolInvocation) -> ToolConfirmation | None:
        try:
            if not self.session:
                return None

            # Resolve patient id
            patient_info = getattr(self.session, "patient_info", {})
            patient_id = invocation.params.get("patient_id") or patient_info.get("patient_id")

            # Build output path
            base_cwd = Path(str(self.config.cwd))
            patient_dir = get_patient_folder(base_cwd, patient_id) if patient_id else base_cwd / "patients"
            output_file = patient_dir / "soap_report.pdf"

            return ToolConfirmation(
                tool_name=self.name,
                params=invocation.params,
                description=f"Generate clinical SOAP report PDF for patient '{patient_id}'.",
                affected_paths=[output_file],
                is_dangerous=True,
            )

        except Exception:
            return None

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        try:
            # 1. Validation: Ensure session is linked
            if not self.session:
                return ToolResult.error_result("Tool Error: Session not linked.")

            # 2. Get Patient Info (Priority: Session > Params > File)
            patient_info = getattr(self.session, "patient_info", {})
            patient_id = invocation.params.get("patient_id") or patient_info.get("patient_id")
            
            if not patient_id:
                return ToolResult.error_result("No patient ID found. Please complete intake first.")

            # 3. Get Conversation from Session Context
            messages = self.session.context_manager.get_messages()
            conversation = build_conversation_text(messages)

            if not conversation:
                return ToolResult.error_result("No conversation history found to generate report.")

            # 4. Generate & Parse SOAP Note
            soap_text = await self._generate_soap(conversation)
            parsed = parse_soap_note(soap_text)
            parsed["date"] = datetime.now().strftime("%Y-%m-%d %H:%M")

            # 5. Path Handling (WSL Safe)
            base_cwd = Path(str(self.config.cwd))
            patient_dir = get_patient_folder(base_cwd, patient_id)
            os.makedirs(patient_dir, exist_ok=True)
            
            output_file = patient_dir / "soap_report.pdf"

            # 6. PDF Generation
            generator = SOAPReportGenerator(patient_info)
            generator.generate(parsed, str(output_file))

            return ToolResult.success_result(f"SOAP report saved at {output_file}")

        except Exception as e:
            return ToolResult.error_result(f"SOAP Tool Failed: {str(e)}")

    async def _generate_soap(self, conversation: str) -> str:
        """Calls the LLM via the session client to generate the SOAP text"""
        prompt = f"""
Convert the following patient conversation into a structured SOAP Note.
Conversation:
{conversation}

Follow this exact format:
SOAP Note
Subjective
• List symptoms...
Objective
• Measurable details...
Assessment
• Clinical impressions...
Plan
• Steps and follow-up...

STRICT RULES: No markdown, plain text only.
"""
        response_text = ""
        # Using the active session's client
        async for event in self.session.client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        ):
            from client.response import StreamEventType
            if event.type == StreamEventType.TEXT_DELTA and event.text_delta:
                response_text += event.text_delta.content
        
        return response_text.strip()