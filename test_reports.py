import asyncio
import os
from pathlib import Path
from config.config import Config
from agent.session import Session
from tools.discovery import ToolDiscoveryManager
from tools.registry import create_default_registry
from tools.base import ToolInvocation

async def run_direct_tool_test():
    # Setup
    config = Config()
    # Force cwd to be a Path object to prevent the error
    config.cwd = Path(os.getcwd()) 
    
    session = Session(config)
    await session.initialize()
    
    # Discover tools
    registry = create_default_registry(config)
    discovery = ToolDiscoveryManager(config, registry)
    discovery.discover_all()
    
    # Mock some clinical data in session memory
    config._session_memory = {
        "patient_info": {"patient_id": "ALEE_404", "name": "Alees"},
        "conversation": "Patient reports severe migraine for 4 hours. No medications. No allergies."
    }
    
    # Get the assessment tool from registry
    tool = registry.get("generate_assessment_report")
    if not tool:
        print("❌ Assessment tool not found!")
        return
    
    # Create invocation (Exactly as other agents do)
    invocation = ToolInvocation(
        params={},
        cwd=config.cwd
    )
    
    print("🛠️  Executing tool...")
    result = await tool.execute(invocation)
    
    if result.success:
        print(f"🎉 Success! Plan at: {result.output}")
    else:
        print(f"❌ Failed: {result.error}")

if __name__ == "__main__":
    asyncio.run(run_direct_tool_test())