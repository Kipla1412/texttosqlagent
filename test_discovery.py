#!/usr/bin/env python3

import sys
import os
import importlib.util
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_tool_file_loading():
    """Test if tool files can be loaded using the same method as discovery"""
    
    tool_dir = Path.cwd() / ".ai-agent" / "tools"
    
    print(f"Looking for tools in: {tool_dir}")
    print(f"Directory exists: {tool_dir.exists()}")
    
    if tool_dir.exists():
        for py_file in tool_dir.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
                
            print(f"\n🔍 Testing: {py_file.name}")
            
            try:
                # Use same method as tool discovery
                module_name = f"test_tool_{py_file.stem}"
                spec = importlib.util.spec_from_file_location(module_name, py_file)
                
                if spec is None or spec.loader is None:
                    print(f"❌ Could not create spec for {py_file.name}")
                    continue
                
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                
                # Try to execute the module
                spec.loader.exec_module(module)
                print(f"✅ Module {py_file.name} loaded successfully")
                
                # Look for Tool classes
                for name in dir(module):
                    obj = getattr(module, name)
                    if hasattr(obj, '__bases__') and hasattr(obj, '__module__'):
                        if obj.__module__ == module_name and hasattr(obj, 'name'):
                            print(f"  📋 Found tool class: {name} (name: {getattr(obj, 'name', 'N/A')})")
                
            except Exception as e:
                print(f"❌ Failed to load {py_file.name}: {e}")
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    test_tool_file_loading()
