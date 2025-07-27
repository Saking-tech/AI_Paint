#!/usr/bin/env python3
"""
Build script for NextGenPaint C++ bindings using MSYS2
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(cmd, cwd=None, env=None):
    """Run a command and return success status"""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, check=True, 
                              capture_output=True, text=True, env=env)
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
    
    # Set up MSYS2 environment
    msys2_path = "C:\\msys64"
    mingw64_path = f"{msys2_path}\\mingw64"
    
    # Update PATH to include MSYS2 tools
    env = os.environ.copy()
    env['PATH'] = f"{mingw64_path}\\bin;{env['PATH']}"
    
    # Set compiler and build tools
    env['CC'] = f"{mingw64_path}\\bin\\gcc.exe"
    env['CXX'] = f"{mingw64_path}\\bin\\g++.exe"
    env['CMAKE_GENERATOR'] = "MinGW Makefiles"
    
    print(f"Using MSYS2 MinGW64: {mingw64_path}")
    print(f"CC: {env['CC']}")
    print(f"CXX: {env['CXX']}")
    
    # Check if required packages are installed
    print("\nChecking required packages...")
    
    # Check for OpenCV
    opencv_include = f"{mingw64_path}\\include\\opencv4"
    if not os.path.exists(opencv_include):
        print("⚠️  OpenCV not found. You may need to install it:")
        print("   Open MSYS2 terminal and run: pacman -S mingw-w64-x86_64-opencv")
        print("   Continuing with build anyway...")
    
    # Check for pybind11
    pybind11_include = f"{mingw64_path}\\include\\pybind11"
    if not os.path.exists(pybind11_include):
        print("⚠️  pybind11 not found. You may need to install it:")
        print("   Open MSYS2 terminal and run: pacman -S mingw-w64-x86_64-pybind11")
        print("   Continuing with build anyway...")
    
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
    print("\nConfiguring with CMake...")
    cmake_cmd = f"{mingw64_path}\\bin\\cmake.exe .. -G \"MinGW Makefiles\""
    if not run_command(cmake_cmd, cwd=build_dir, env=env):
        print("CMake configuration failed!")
        return False
    
    # Build the project
    print("\nBuilding project...")
    if not run_command(f"{mingw64_path}\\bin\\mingw32-make.exe", cwd=build_dir, env=env):
        print("Build failed!")
        return False
    
    # Check if the module was created
    if module_path.exists():
        print(f"\n✅ Successfully built module: {module_path}")
        return True
    else:
        print(f"\n⚠️  Module not found at expected location: {module_path}")
        print("Build may have succeeded but module is in a different location.")
        
        # Look for the module in the build directory
        for root, dirs, files in os.walk(build_dir):
            for file in files:
                if file.endswith(module_ext):
                    print(f"Found module at: {os.path.join(root, file)}")
        
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 