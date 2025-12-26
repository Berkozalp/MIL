#!/usr/bin/env python3
"""
Motion Image Learner - Project Launcher
Automatically starts both backend and frontend servers
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

# ANSI color codes for pretty output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}[+] {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}[i] {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}[!] {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}[x] {text}{Colors.ENDC}")

def check_dependencies():
    """Check and install missing required dependencies"""
    print_header("Syncing Dependencies")
    
    # Python checks
    backend_dir = Path(__file__).parent / 'backend'
    req_file = backend_dir / 'requirements.txt'
    
    if req_file.exists():
        print_info("Installing/Updating Python dependencies from requirements.txt...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', str(req_file)], check=True)
            print_success("Python dependencies are up to date")
        except subprocess.CalledProcessError:
            print_error("Failed to install Python dependencies")
            sys.exit(1)
            
    # Check for ML Models
    models = ['yolov8n.pt', 'efficientdet_lite0.tflite']
    for model in models:
        if not (backend_dir / model).exists():
            print_warning(f"Model {model} is missing in background folder.")
            print_info(f"Attempting to download {model}...")
            # For YOLOv8, it downloads automatically on first run, but we can verify it here
            # For MediaPipe, we check if it's there
            if model.endswith('.tflite'):
                print_error(f"Please ensure {model} is placed in the backend/ directory.")
                # sys.exit(1) # Don't exit, might still work if user has their own
    
    # Nuclear Cleanup: Kill all node and uvicorn before starting
    print_info("Performing deep cleanup of existing processes...")
    try:
        if sys.platform == 'win32':
            # Use taskkill to wipe out any hanging instances
            subprocess.run(['taskkill', '/F', '/IM', 'node.exe', '/T'], capture_output=True)
            subprocess.run(['taskkill', '/F', '/IM', 'uvicorn.exe', '/T'], capture_output=True)
        else:
            subprocess.run(['pkill', '-f', 'node'], capture_output=True)
            subprocess.run(['pkill', '-f', 'uvicorn'], capture_output=True)
    except: pass

    # Check Node.js
    try:
        subprocess.run(['node', '--version'], capture_output=True, check=True)
        print_success("Node.js is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("Node.js is NOT installed. Please install it from https://nodejs.org/")
        sys.exit(1)

def start_backend():
    """Start the FastAPI backend server"""
    print_header("Starting Backend Server")
    
    # Kill any existing process on port 8000
    kill_port(8000)
    
    backend_dir = Path(__file__).parent / 'backend'
    
    if not backend_dir.exists():
        print_error(f"Backend directory not found: {backend_dir}")
        sys.exit(1)
    
    print_info(f"Backend directory: {backend_dir}")
    print_info("Starting uvicorn server on http://0.0.0.0:8000")
    
    # Start backend in background without piping (avoids hanging)
    # On Windows, we open a new console window to see the logs
    creation_flags = subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
    backend_process = subprocess.Popen(
        [sys.executable, '-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000'],
        cwd=backend_dir,
        creationflags=creation_flags
    )
    
    # Wait a bit for server to start
    time.sleep(3)
    
    if backend_process.poll() is None:
        print_success("Backend server started successfully")
        return backend_process
    else:
        print_error("Failed to start backend server")
        sys.exit(1)

def kill_port(port):
    """Kill any process listening on the specified port"""
    if sys.platform != 'win32':
        return # Simplified for now
    
    try:
        output = subprocess.check_output(['netstat', '-ano', '-p', 'TCP'], text=True)
        for line in output.splitlines():
            if f':{port}' in line and 'LISTENING' in line:
                pid = line.strip().split()[-1]
                print_info(f"Killing existing process {pid} on port {port}...")
                subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
    except Exception as e:
        print_warning(f"Could not check/kill port {port}: {e}")

def start_frontend():
    """Start the Vite frontend dev server"""
    print_header("Starting Frontend Server")
    
    # Kill any existing Vite process on the new port
    kill_port(5185)
    
    frontend_dir = Path(__file__).parent / 'frontend'
    
    if not frontend_dir.exists():
        print_error(f"Frontend directory not found: {frontend_dir}")
        sys.exit(1)
    
    print_info(f"Frontend directory: {frontend_dir}")
    
    # Check if node_modules exists
    if not (frontend_dir / 'node_modules').exists():
        print_warning("node_modules not found, running npm install...")
        try:
            subprocess.run(['cmd', '/c', 'npm', 'install'] if sys.platform == 'win32' else ['npm', 'install'], 
                           cwd=frontend_dir, check=True)
            print_success("Dependencies installed")
        except Exception as e:
            print_error(f"Failed to install node modules: {e}")
            sys.exit(1)

    # Clear Vite cache to prevent MIME/Syntax errors
    vite_cache = frontend_dir / 'node_modules' / '.vite'
    if vite_cache.exists():
        print_info("Clearing Vite dependency cache...")
        try:
            import shutil
            shutil.rmtree(vite_cache)
            print_success("Vite cache cleared")
        except Exception as e:
            print_warning(f"Could not clear Vite cache: {e}")
    
    print_info("Starting Vite dev server on http://127.0.0.1:5185")
    
    # Environment with explicit PATH and other goodies
    env = os.environ.copy()
    
    # Start frontend in background
    creation_flags = subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
    
    # We use 'npx vite' directly with --force and the new port
    cmd = ['npx', 'vite', '--host', '0.0.0.0', '--port', '5185', '--force']
    if sys.platform == 'win32':
        cmd = ['cmd', '/c'] + cmd
        
    frontend_process = subprocess.Popen(
        cmd,
        cwd=frontend_dir,
        env=env,
        creationflags=creation_flags
    )
    
    # Wait for frontend to be ready
    print_info("Waiting for frontend server to be ready...")
    max_wait = 30
    import urllib.request
    for i in range(max_wait):
        time.sleep(1)
        if frontend_process.poll() is not None:
            print_error("Frontend server failed to start")
            sys.exit(1)
        
        # Deep Health Check: Verify core Vite scripts serve JS, not HTML
        try:
            # Check both the entry point AND the vite client
            checks_passed = True
            for script_path in ['/src/main.jsx', '/@vite/client']:
                with urllib.request.urlopen(f'http://127.0.0.1:5185{script_path}', timeout=1) as response:
                    content_type = response.getheader('Content-Type', '')
                    content = response.read(200).decode('utf-8', errors='ignore')
                    
                    # If it served HTML for a JS path, it's not ready
                    if 'text/html' in content_type.lower() or content.strip().startswith('<!doctype'):
                        checks_passed = False
                        break
                    if response.status != 200:
                        checks_passed = False
                        break
            
            if checks_passed:
                print_success("Frontend server is fully hydrated and serving JavaScript")
                # Extra safety buffer for Windows file system locks / bundle finalization
                time.sleep(3)
                return frontend_process
        except:
            if i % 3 == 0 and i > 0:
                print_info(f"Waiting for Vite to transform scripts... ({i}/{max_wait}s)")
            continue
    
    print_warning("Frontend server started but readiness check timed out")
    return frontend_process

def open_browser():
    """Open the application in default browser"""
    print_header("Opening Application")
    
    url = "http://127.0.0.1:5185"
    print_info(f"Opening {url} in browser...")
    webbrowser.open(url)
    print_success("Browser opened")

def main():
    """Main launcher function"""
    # Force UTF-8 encoding for stdout if possible
    if sys.platform == 'win32':
        import ctypes
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    
    print_header("Motion Image Learner - Launcher")
    print_info("Starting Motion Image Learner application...")
    
    try:
        # Check dependencies
        check_dependencies()
        
        # Start servers
        backend_proc = start_backend()
        
        # Verify Backend Health before starting Frontend
        print_info("Verifying backend health...")
        backend_ok = False
        import urllib.request
        for _ in range(10):
            try:
                with urllib.request.urlopen("http://127.0.0.1:8000/", timeout=1) as r:
                    if r.getcode() == 200:
                        backend_ok = True
                        break
            except: pass
            time.sleep(1)
            
        if not backend_ok:
            print_error("Backend failed health check. Check logs in the second window.")
            backend_proc.terminate()
            sys.exit(1)
            
        frontend_proc = start_frontend()
        
        # Open browser
        open_browser()
        
        # Show status
        print_header("Application Running")
        print_success("Backend:  http://0.0.0.0:8000")
        print_success("Frontend: http://localhost:5185")
        print_info("\nPress Ctrl+C to stop all servers")
        
        # Keep script running
        try:
            while True:
                time.sleep(1)
                # Check if processes are still running
                if backend_proc.poll() is not None:
                    print_error("Backend server stopped unexpectedly")
                    break
                if frontend_proc.poll() is not None:
                    print_error("Frontend server stopped unexpectedly")
                    break
        except KeyboardInterrupt:
            print_info("\n\nShutting down servers...")
            # On Windows, terminating a shell process doesn't always kill children
            # but CREATE_NEW_CONSOLE helps as they are separate.
            backend_proc.terminate()
            frontend_proc.terminate()
            print_success("Servers stopped")
            
    except Exception as e:
        print_error(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
