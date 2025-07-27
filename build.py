#!/usr/bin/env python3
"""
Build script for NextGenPaint C++ bindings
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return success status"""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, check=True, 
                              capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"stderr: {e.stderr}")
        return False

def main():
    """Main build function"""
    # Get the project root directory
    project_root = Path(__file__).parent
    build_dir = project_root / "build"
    
    # Create build directory
    build_dir.mkdir(exist_ok=True)
    
    # Determine the Python module extension
    if platform.system() == "Windows":
        module_ext = ".pyd"
    else:
        module_ext = ".so"
    
    # Check if the module already exists
    module_path = project_root / "src" / "python" / "ngpaint" / f"ngp_core_python{module_ext}"
    
    if module_path.exists():
        print(f"Module already exists at {module_path}")
        response = input("Rebuild? (y/N): ").strip().lower()
        if response != 'y':
            print("Skipping build.")
            return True
    
    # Configure with CMake
    print("Configuring with CMake...")
    if not run_command("cmake ..", cwd=build_dir):
        print("CMake configuration failed!")
        return False
    
    # Build the project
    print("Building project...")
    if platform.system() == "Windows":
        if not run_command("cmake --build . --config Release", cwd=build_dir):
            print("Build failed!")
            return False
    else:
        if not run_command("make", cwd=build_dir):
            print("Build failed!")
            return False
    
    # Check if the module was created
    if module_path.exists():
        print(f"Successfully built module: {module_path}")
        return True
    else:
        print(f"Module not found at expected location: {module_path}")
        print("Build may have succeeded but module is in a different location.")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 