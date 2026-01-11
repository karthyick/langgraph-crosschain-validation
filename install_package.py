#!/usr/bin/env python3
"""
Installation script for langgraph-crosschain from pypi
"""

import subprocess
import sys
from pathlib import Path

def install_package():
    """Install the langgraph-crosschain package from pypi"""
    print("=" * 60)
    print("Installing langgraph-crosschain from pypi...")
    print("=" * 60)
    
    try:
        # Install from pypi
        cmd = [
            sys.executable, "-m", "pip", "install",
            "-i", "https://pypi.org/simple/",
            "langgraph-crosschain==0.1.2",
            "--extra-index-url", "https://pypi.org/simple/"  # For dependencies
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Successfully installed langgraph-crosschain 0.1.2")
            print(result.stdout)
            
            # Verify installation
            verify_cmd = [sys.executable, "-c", "import langgraph_crosschain; print(f'Version: {langgraph_crosschain.__version__}')"]
            verify_result = subprocess.run(verify_cmd, capture_output=True, text=True)
            
            if verify_result.returncode == 0:
                print("\n✅ Package imported successfully!")
                print(verify_result.stdout)
            else:
                print("\n⚠️ Warning: Could not verify import")
                print(verify_result.stderr)
                
        else:
            print("❌ Installation failed")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error during installation: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = install_package()
    sys.exit(0 if success else 1)