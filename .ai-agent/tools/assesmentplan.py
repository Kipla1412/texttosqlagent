from __future__ import annotations
import os
from pathlib import Path
from pydantic import BaseModel
from tools.base import Tool, ToolResult, ToolInvocation, ToolKind, ToolConfirmation
from utils.conversation import build_conversation_text
from utils.patientstorage import get_patient_folder
from utils.assesmentplan import AssessmentPlanReportGenerator
from client.response import StreamEventType

class AssessmentReportSchema(BaseModel):
    patient_id: str | None = None

class GenerateAssessmentReportTool(Tool):
    name = "generate_assessment_report"
    description = "Generate a structured doctor-facing Assessment & Plan PDF"
    kind = ToolKind.WRITE
    
    # We add this so we can inject the session manually 
    # without changing the base Tool class
    session = None 

    @property
    def schema(self):
        return AssessmentReportSchema

    async def get_confirmation(self, invocation: ToolInvocation) -> ToolConfirmation | None:

        # Resolve patient_id
        patient_info = getattr(self.session, "patient_info", {}) if self.session else {}
        patient_id = invocation.params.get("patient_id") or patient_info.get("patient_id")

        # Determine output path
        base_cwd = Path(str(self.config.cwd))
        patient_dir = get_patient_folder(base_cwd, patient_id) if patient_id else base_cwd / "patients"
        output_file = patient_dir / f"assessment_{patient_id}.pdf"

        return ToolConfirmation(
            tool_name=self.name,
            params=invocation.params,
            description=f"Generate clinical Assessment & Plan PDF for patient '{patient_id}'.",
            affected_paths=[output_file],
            is_dangerous=False,
        )

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        try:
            # 1. Validation: Ensure session was injected
            if not self.session:
                return ToolResult.error_result("Tool Error: Session context not linked.")
            
            params = AssessmentReportSchema(**invocation.params)
            patient_info = getattr(self.session, "patient_info", {})
            patient_id = params.patient_id or patient_info.get("patient_id")

            if not patient_id:
                return ToolResult.error_result("Missing patient_id in tool parameters.")

            # 2. Extract Data from Session
            messages = self.session.context_manager.get_messages()
            conversation = build_conversation_text(messages)

            if not conversation:
                return ToolResult.error_result("Conversation is empty. Cannot generate assessment.")

            # 3. Generate Clinical Text via LLM
            assessment_text = await self._generate_clinical_text(conversation)

            # 4. Path Handling (Fixing the TypeError for WSL)
            # Convert str to Path locally so it doesn't break other agents
            base_cwd = Path(str(self.config.cwd))
            patient_dir = get_patient_folder(base_cwd, patient_id)
            os.makedirs(patient_dir, exist_ok=True)
            
            output_file = patient_dir / f"assessment_{patient_id}.pdf"

            # 5. PDF Generation
            generator = AssessmentPlanReportGenerator(patient_info)
            generator.generate(assessment_text, str(output_file))

            return ToolResult.success_result(f"Clinical report generated: {output_file}")

        except Exception as e:
            return ToolResult.error_result(f"Tool Execution Failed: {str(e)}")

    async def _generate_clinical_text(self, conversation: str) -> str:
        """Helper method to generate assessment text using your strict prompt"""
        
        prompt = f"""
You are a clinical Assessment & Plan generation agent.
Analyze the following patient conversation and generate a doctor-facing Assessment & Plan.

Conversation:
{conversation}

--------------------------------------------------
Assessment & Plan
--------------------------------------------------

A. Clinical Overview
Briefly summarize key symptoms, duration, severity, and risk factors.

B. Differential Diagnosis
List the TOP 3-5 diagnoses in descending likelihood.
For each diagnosis include:
- Diagnosis name
- Estimated likelihood percentage (total ~100%)
- Clear clinical rationale
Use this exact format:
1. Diagnosis Name - ~XX% Likelihood
• Rationale: ...

C. Diagnostic Plan
Group tests under:
- Laboratory Tests
- Imaging Studies (only if indicated)
- Other Diagnostics
For each test include:
- Test name
- Sample/source
- Purpose

D. Treatment Plan (Conditional)
ONLY conditional recommendations.
Use format:
- If Diagnosis X is confirmed:
• Medication
• Example adult dose
• Route
• Duration
• Rationale

E. Procedures / Interventions
Clearly state if none are indicated.

F. Risk & Urgency Assessment
- Urgency level: LOW / MODERATE / HIGH
- Red-flag symptoms requiring escalation

--------------------------------------------------
STRICT RULES:
- Plain text only
- No markdown symbols
- No patient-facing language
- No definitive diagnosis
- Output ONLY the Assessment & Plan document
"""
        response_text = ""
        # Use the session's existing client
        async for event in self.session.client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        ):
            if event.type == StreamEventType.TEXT_DELTA and event.text_delta:
                response_text += event.text_delta.content
        
        return response_text.strip()


