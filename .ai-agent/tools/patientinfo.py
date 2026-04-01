# from pydantic import BaseModel
# from tools.base import Tool, ToolResult, ToolInvocation, ToolKind
# import uuid
# from datetime import datetime

# class SavePatientInfo(BaseModel):
#     name: str
#     age: int
#     gender: str

# class SavePatientInfoTool(Tool):
#     name = "save_patient_info"
#     description = "Store patient basic information and generate patient ID"
#     kind = ToolKind.MEMORY
#     schema = SavePatientInfo

#     async def execute(self, invocation: ToolInvocation) -> ToolResult:

#         params = invocation.params

#         name = params["name"]
#         age = params["age"]
#         gender = params["gender"]

#         # Generate unique patient ID
#         patient_id = f"patient_{datetime.now().strftime('%Y%m%d')}_{str(uuid.uuid4())[:8]}"
        
#         # Store patient info using the memory system
#         # This will be stored in the persistent memory file
#         patient_data = {
#             "patient_id": patient_id,
#             "name": name,
#             "age": age,
#             "gender": gender,
#             "created_at": datetime.now().isoformat()
#         }

#         # Store in memory using a simple approach
#         # We'll use a file-based storage since memory tool isn't directly accessible here
#         try:
#             import json
#             from pathlib import Path
            
#             # Create patient data file and folder
#             patients_dir = Path.cwd() / "patients"
#             patients_dir.mkdir(exist_ok=True)
            
#             # Create patient folder for reports
#             patient_folder = patients_dir / patient_id
#             patient_folder.mkdir(exist_ok=True)
            
#             patient_file = patients_dir / f"{patient_id}_info.json"
#             patient_file.write_text(json.dumps(patient_data, indent=2))
            
#             # Also store in a simple memory dict for current session
#             if not hasattr(self.config, '_session_memory'):
#                 self.config._session_memory = {}
#             self.config._session_memory["patient_info"] = patient_data

#         except Exception as e:
#             return ToolResult.error_result(f"Failed to save patient info: {str(e)}")

#         return ToolResult.success_result(
#             f"Patient info saved. Patient ID: {patient_id}. Name: {name}, {age}, {gender}"
#         )

from __future__ import annotations
import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel

from tools.base import Tool, ToolResult, ToolInvocation, ToolKind

class SavePatientInfoSchema(BaseModel):
    name: str
    age: int
    gender: str

class SavePatientInfoTool(Tool):
    name = "save_patient_info"
    description = "Store patient basic information and generate a unique clinical Patient ID"
    kind = ToolKind.MEMORY
    
    # Injection point for the session
    session = None 

    @property
    def schema(self):
        return SavePatientInfoSchema

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        try:
            # 1. Validation: Ensure session is linked
            if not self.session:
                return ToolResult.error_result("Tool Error: Session not linked.")

            params = invocation.params
            name = params.get("name")
            age = params.get("age")
            gender = params.get("gender")

            # 2. Generate unique patient ID
            # Using a prefix like 'PAT-' makes it look more professional in the PDF
            timestamp = datetime.now().strftime('%Y%m%d')
            unique_suffix = str(uuid.uuid4())[:6].upper()
            patient_id = f"PAT-{timestamp}-{unique_suffix}"
            
            patient_data = {
                "patient_id": patient_id,
                "name": name,
                "age": age,
                "gender": gender,
                "created_at": datetime.now().isoformat()
            }

            # 3. Path Handling (WSL Safe)
            # Use Path(str(...)) to avoid the TypeError we saw earlier
            base_cwd = Path(str(self.config.cwd))
            patients_dir = base_cwd / "patients"
            patients_dir.mkdir(exist_ok=True)
            
            # Create a dedicated folder for this specific patient's files
            patient_folder = patients_dir / patient_id
            patient_folder.mkdir(parents=True, exist_ok=True)
            
            # Save the JSON record
            info_file = patients_dir / f"{patient_id}_info.json"
            info_file.write_text(json.dumps(patient_data, indent=2))

            # 4. STORE IN SESSION (Crucial for the other tools!)
            # This makes session.patient_info accessible to SOAP, Summary, and Assessment tools
            self.session.patient_info = patient_data

            # # 5. Optional: Track in MLflow if your session supports it
            # if hasattr(self.session, "mlflow_tracker"):
            #     self.session.mlflow_tracker.log_param("patient_id", patient_id)

            return ToolResult.success_result(
                f"Successfully registered patient {name} (ID: {patient_id}). "
                f"Folders created in {patients_dir}."
            )

        except Exception as e:
            return ToolResult.error_result(f"Failed to save patient info: {str(e)}")