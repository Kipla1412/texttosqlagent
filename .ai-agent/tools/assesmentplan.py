from tools.base import Tool, ToolResult, ToolInvocation, ToolKind
from pydantic import BaseModel
from utils.conversation import build_conversation_text
from utils.patientstorage import get_patient_folder
from utils.assesmentplan import AssessmentPlanReportGenerator

class AssessmentReportSchema(BaseModel):
    patient_id: str

class GenerateAssessmentReportTool(Tool):

    name = "generate_assessment_report"
    description = "Generate Assessment & Plan PDF for patient"
    kind = ToolKind.WRITE
    schema = AssessmentReportSchema

    async def execute(self, invocation: ToolInvocation) -> ToolResult:

        try:

            patient_id = invocation.params["patient_id"]

            # Get conversation from memory
            conversation = ""
            if "conversation" in self.config.memory:
                conversation = self.config.memory["conversation"]
            else:
                # Try to get from messages if available
                messages = self.config.memory.get("messages", [])
                if messages:
                    conversation = build_conversation_text(messages)     

            assessment_text = await self._generate_assessment(conversation)

            patient_dir = get_patient_folder(self.config.cwd, patient_id)

            output_file = patient_dir / "assessment_plan_report.pdf"

            patient_info = {
                "patient_id": patient_id
            }

            generator = AssessmentPlanReportGenerator(patient_info)

            generator.generate(assessment_text, str(output_file))

            return ToolResult.success_result(
                f"Assessment report saved at {output_file}"
            )

        except Exception as e:
            return ToolResult.error_result(str(e))

    async def _generate_assessment(self, conversation: str) -> str:
        """Helper method to generate assessment text"""
        # This is a placeholder - you'll need to implement the actual
        # LLM call here based on your system's client interface
        
        prompt = f"""

You are a clinical Assessment & Plan generation agent.

Analyze the following patient conversation and generate a
doctor-facing Assessment & Plan.

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
        
        # Placeholder implementation
        # You'll need to replace this with your actual LLM client call
        return """
Assessment & Plan

A. Clinical Overview
Patient presents with symptoms requiring further evaluation.

B. Differential Diagnosis
1. Common Condition - ~60% Likelihood
• Rationale: Based on reported symptoms

2. Less Common Condition - ~30% Likelihood
• Rationale: Alternative explanation for symptoms

3. Rare Condition - ~10% Likelihood
• Rationale: Cannot be ruled out without further testing

C. Diagnostic Plan
- Laboratory Tests
• Complete blood count
• Basic metabolic panel

D. Treatment Plan (Conditional)
- If Condition X is confirmed:
• Symptomatic treatment
• Follow-up in 1-2 weeks

E. Procedures / Interventions
None indicated at this time.

F. Risk & Urgency Assessment
- Urgency level: LOW
- No immediate red-flag symptoms identified
"""