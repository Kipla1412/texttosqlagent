from tools.base import Tool, ToolResult, ToolInvocation, ToolKind
from pydantic import BaseModel
from utils.conversation import build_conversation_text
from utils.patient_storage import get_patient_folder
from utils.soapreport import SOAPReportGenerator
from utils.soapparser import parse_soap_note
import os


class SOAPReportSchema(BaseModel):
    patient_id: str


class GenerateSOAPReportTool(Tool):

    name = "generate_soap_report"
    description = "Generate SOAP report PDF for patient"
    kind = ToolKind.WRITE
    schema = SOAPReportSchema

    async def execute(self, invocation: ToolInvocation) -> ToolResult:

        try:

            session = invocation.metadata["session"]

            patient_id = invocation.params["patient_id"]

            messages = session.context_manager.get_messages()

            conversation = build_conversation_text(messages)

            prompt = f"""

Convert the following patient conversation into a structured SOAP Note.

Conversation:
{conversation}

Follow this exact format:

SOAP Note

Subjective
• List all symptoms reported by the patient.

Objective
• Include only measurable or observable details mentioned.

Assessment
• Provide 2-4 possible clinical impressions.
• Label each as High / Moderate / Low likelihood.
• Add 1-2 lines of reasoning.

Plan
• Supportive care steps
• Home instructions
• Monitoring advice
• Red flags for urgent care
• Follow-up guidance
"""

            soap_text = await session.client.complete(prompt)

            parsed = parse_soap_note(soap_text)

            patient_dir = get_patient_folder(self.config.cwd, patient_id)

            output_file = patient_dir / "soap_report.pdf"

            patient_info = {
                "patient_id": patient_id
            }

            generator = SOAPReportGenerator(patient_info)

            generator.generate(parsed, str(output_file))

            return ToolResult.success_result(
                f"SOAP report saved at {output_file}"
            )

        except Exception as e:
            return ToolResult.error_result(str(e))