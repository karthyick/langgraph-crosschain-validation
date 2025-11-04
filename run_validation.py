#!/usr/bin/env python3
"""
Main validation runner for langgraph-crosschain package
"""

import sys
import subprocess
import time
from pathlib import Path
from colorama import init, Fore, Style
from tabulate import tabulate

# Initialize colorama
init(autoreset=True)

def print_banner():
    """Print validation banner"""
    banner = f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║      LangGraph CrossChain Communication Framework Validation         ║
║                          Version 0.1.2                               ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
    """
    print(banner)

def run_script(script_name, description):
    """Run a validation script and capture results"""
    print(f"\n{Fore.YELLOW}▶ Running: {description}")
    print(f"\n{Fore.YELLOW}{'-'*60}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=False,
            text=True,
            timeout=60
        )
        
        elapsed_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f"{Fore.GREEN}✓ {description} completed successfully ({elapsed_time:.2f}s)")
            return True, elapsed_time
        else:
            print(f"{Fore.RED}✗ {description} failed (exit code: {result.returncode})")
            return False, elapsed_time
            
    except subprocess.TimeoutExpired:
        print(f"{Fore.RED}✗ {description} timed out after 60 seconds")
        return False, 60.0
    except Exception as e:
        print(f"{Fore.RED}✗ Error running {description}: {e}")
        return False, 0.0

def main():
    """Main validation runner"""
    print_banner()
    
    # Change to validation directory
    validation_dir = Path(__file__).parent
    
    # Define test scripts
    test_scripts = [
        ("install_package.py", "Package Installation"),
        ("test_core_components.py", "Core Components Validation"),
        ("test_cross_chain_communication.py", "Cross-Chain Communication Tests"),
    ]
    
    # Run all tests
    results = []
    total_start = time.time()
    
    for script, description in test_scripts:
        success, elapsed = run_script(script, description)
        results.append([description, "✅ PASS" if success else "❌ FAIL", f"{elapsed:.2f}s"])
        
        if not success and script == "install_package.py":
            print(f"\n{Fore.RED}⚠️ Installation failed. Cannot continue with validation.")
            break
    
    total_time = time.time() - total_start
    
    # Print summary table
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}VALIDATION SUMMARY")
    print(f"{Fore.CYAN}{'='*70}")
    
    print(tabulate(
        results,
        headers=["Test Suite", "Status", "Time"],
        tablefmt="grid",
        colalign=("left", "center", "right")
    ))
    
    # Overall result
    all_passed = all("✅" in result[1] for result in results)
    
    print(f"\n{Fore.CYAN}Total Execution Time: {total_time:.2f} seconds")
    
    if all_passed:
        print(f"\n{Fore.GREEN}{'='*70}")
        print(f"{Fore.GREEN}🎉 VALIDATION SUCCESSFUL! 🎉")
        print(f"{Fore.GREEN}All tests passed. The package is working correctly.")
        print(f"{Fore.GREEN}{'='*70}")
    else:
        print(f"\n{Fore.YELLOW}{'='*70}")
        print(f"{Fore.YELLOW}⚠️ VALIDATION INCOMPLETE")
        print(f"{Fore.YELLOW}Some tests failed. Please review the output above.")
        print(f"{Fore.YELLOW}{'='*70}")
    
    # Provide next steps
    print(f"\n{Fore.CYAN}Next Steps:")
    print(f"  1. Review any failed tests in detail")
    print(f"  2. Check the package implementation for missing components")
    print(f"  3. Verify all dependencies are correctly installed")
    print(f"  4. Run individual test files for detailed debugging")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())