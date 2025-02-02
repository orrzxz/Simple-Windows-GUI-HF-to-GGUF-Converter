import os
import platform
import subprocess
import sys
from pathlib import Path

def install_dependencies():
    print("Installing Python dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def setup_llamacpp():
    print("\nSetting up llama.cpp...")
    llamadir = Path("llama.cpp").resolve()
    
    # Add safe directory configuration for Git
    if platform.system() == "Windows":
        print("Configuring Git safe directory...")
        subprocess.check_call(["git", "config", "--global", "--add", "safe.directory", str(llamadir)])
    
    # Clone or update repository
    if not llamadir.exists():
        print("Cloning llama.cpp repository...")
        subprocess.check_call(["git", "clone", "https://github.com/ggerganov/llama.cpp.git"])
    else:
        print("Updating existing repository...")
        try:
            subprocess.check_call(["git", "pull"], cwd=llamadir)
        except subprocess.CalledProcessError:
            print("\nWARNING: Could not update existing repository")
            print("Please delete the llama.cpp directory and try again")
            print("or run this command manually:")
            print(f"git config --global --add safe.directory {llamadir}")
            sys.exit(1)
    
    # Build with CMake
    build_dir = llamadir / "build"
    build_dir.mkdir(exist_ok=True)
    
    print("Configuring CMake...")
    cmake_cmd = ["cmake", ".."]
    if platform.system() == "Windows":
        cmake_cmd += ["-G", "Visual Studio 17 2022", "-A", "x64"]
    
    subprocess.check_call(cmake_cmd, cwd=build_dir)
    
    print("Building llama.cpp...")
    subprocess.check_call(["cmake", "--build", ".", "--config", "Release"], cwd=build_dir)

def create_folders():
    print("\nCreating directory structure...")
    Path("Converted").mkdir(exist_ok=True)

def check_prerequisites():
    required = ["git", "cmake"]
    print("Checking prerequisites...")
    
    for tool in required:
        try:
            subprocess.run([tool, "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except (FileNotFoundError, subprocess.CalledProcessError):
            print(f"\nERROR: Missing required tool: {tool}")
            print("Please install:")
            print("- Git: https://git-scm.com/")
            print("- CMake: https://cmake.org/download/")
            if platform.system() == "Windows":
                print("- Visual Studio 2022 Build Tools with C++ workload")
            sys.exit(1)

if __name__ == "__main__":
    check_prerequisites()
    install_dependencies()
    setup_llamacpp()
    create_folders()
    print("\nSetup completed successfully!")
    if platform.system() == "Windows":
        print("NOTE: If you see build errors, ensure you ran this in a Developer Command Prompt for VS 2022")