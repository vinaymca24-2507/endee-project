
import sys
import importlib.util
import subprocess
import os
import time

def check_package(package_name):
    if importlib.util.find_spec(package_name) is None:
        print(f"[MISSING] {package_name} not found")
        return False
    print(f"[OK] {package_name} found")
    return True

def check_command(command):
    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[OK] Command '{command[0]}' is available")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"[MISSING] Command '{command[0]}' failed or not found")
        return False

def check_service(url):
    try:
        import requests
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
             print(f"[OK] Service at {url} is running")
             return True
        else:
             print(f"[WARN] Service at {url} returned {response.status_code}")
             return False
    except Exception as e:
        print(f"[FAIL] Service at {url} is not reachable: {e}")
        return False

def main():
    print("--- Environment Check ---")
    
    # Python Version
    print(f"Python: {sys.version.split()[0]}")
    
    # Dependencies
    required_packages = [
        "fastapi", "uvicorn", "streamlit", "sentence_transformers", "langchain", "requests"
    ]
    all_packages = True
    for pkg in required_packages:
        if not check_package(pkg):
            all_packages = False
            
    # Ollama
    ollama_ok = check_command(["ollama", "--version"])
    
    # Endee (assuming we need to import it or run it)
    # If Endee is a service, we should check if it's running.
    # If it's a library, we check import.
    # For now, let's check if the directory exists since we cloned it.
    if os.path.exists("../endee"):
        print("[OK] Endee directory found at ../endee")
    else:
        print("[MISSING] Endee directory NOT found at ../endee")

    # Build Tools / Docker
    print("\n--- System Capabilities ---")
    check_command(["docker", "--version"])
    check_command(["cmake", "--version"])
    check_command(["cl"]) # MSVC
    check_command(["g++", "--version"]) # MinGW/GCC

    # Service Checks (optional, if we expect them to be running already, which we don't yet)
    check_service("http://localhost:11434") # Ollama
    check_service("http://localhost:8000/docs") # Backend API Docs
    check_service("http://localhost:8501") # Frontend UI
    
    if not all_packages:
        print("\n[MISSING] Some Python packages are missing. Run: pip install -r requirements.txt")
    
    if not ollama_ok:
        print("\n[WARN] Ollama is creating issues. The app might not work fully without it.")

if __name__ == "__main__":
    main()
