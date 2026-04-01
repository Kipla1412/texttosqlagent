#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from ai_agent.tools.soapnote import GenerateSOAPReportTool
    print("✅ SOAP tool imported successfully")
except Exception as e:
    print(f"❌ SOAP tool import failed: {e}")

try:
    from ai_agent.tools.assesmentplan import GenerateAssessmentReportTool
    print("✅ Assessment tool imported successfully")
except Exception as e:
    print(f"❌ Assessment tool import failed: {e}")

try:
    from ai_agent.tools.summary import GeneratePatientSummaryTool
    print("✅ Summary tool imported successfully")
except Exception as e:
    print(f"❌ Summary tool import failed: {e}")

try:
    from ai_agent.tools.patientinfo import SavePatientInfoTool
    print("✅ Patient info tool imported successfully")
except Exception as e:
    print(f"❌ Patient info tool import failed: {e}")

print("\nTesting tool instantiation...")
try:
    from config.config import Config
    config = Config()
    
    soap_tool = GenerateSOAPReportTool(config)
    print(f"✅ SOAP tool created: {soap_tool.name}")
    
    assessment_tool = GenerateAssessmentReportTool(config)
    print(f"✅ Assessment tool created: {assessment_tool.name}")
    
    summary_tool = GeneratePatientSummaryTool(config)
    print(f"✅ Summary tool created: {summary_tool.name}")
    
    patient_tool = SavePatientInfoTool(config)
    print(f"✅ Patient tool created: {patient_tool.name}")
    
except Exception as e:
    print(f"❌ Tool instantiation failed: {e}")
