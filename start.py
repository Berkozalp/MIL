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
    """Check if required dependencies are installed"""
    print_header("Checking Dependencies")
    
    # Check Python packages
    required_packages = {'fastapi': 'fastapi', 'uvicorn': 'uvicorn', 'mediapipe': 'mediapipe', 'opencv-python': 'cv2', 'ultralytics': 'ultralytics'}
    missing_packages = []
    
    for package, import_name in required_packages.items():
        try:
            __import__(import_name)
            print_success(f"{package} is installed")
        except ImportError:
            missing_packages.append(package)
            print_error(f"{package} is NOT installed")
    
    if missing_packages:
        print_warning(f"\nMissing packages: {', '.join(missing_packages)}")
        response = input("Would you like to install them now? (y/n): ")
        if response.lower() == 'y':
            print_info("Installing missing packages...")
            subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print_success("Packages installed successfully")
        else:
            print_error("Cannot start without required packages")
            sys.exit(1)
    
    # Check Node.js
    try:
        subprocess.run(['node', '--version'], capture_output=True, check=True)
        print_success("Node.js is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("Node.js is NOT installed")
        print_warning("Please install Node.js from https://nodejs.org/")
        sys.exit(1)

def start_backend():
    """Start the FastAPI backend server"""
    print_header("Starting Backend Server")
    
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
    
    # Kill any existing Vite process
    kill_port(5173)
    
    frontend_dir = Path(__file__).parent / 'frontend'
    
    if not frontend_dir.exists():
        print_error(f"Frontend directory not found: {frontend_dir}")
        sys.exit(1)
    
    print_info(f"Frontend directory: {frontend_dir}")
    
    # Check if node_modules exists
    if not (frontend_dir / 'node_modules').exists():
        print_warning("node_modules not found, running npm install...")
        subprocess.run(['cmd', '/c', 'npm', 'install'] if sys.platform == 'win32' else ['npm', 'install'], 
                       cwd=frontend_dir, check=True)
        print_success("Dependencies installed")
    
    print_info("Starting Vite dev server on http://127.0.0.1:5173")
    
    # Start frontend in background without piping
    creation_flags = subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
    if sys.platform == 'win32':
        frontend_process = subprocess.Popen(
            ['cmd', '/c', 'npm', 'run', 'dev', '--', '--host', '127.0.0.1'],
            cwd=frontend_dir,
            creationflags=creation_flags
        )
    else:
        frontend_process = subprocess.Popen(
            ['npm', 'run', 'dev', '--', '--host', '127.0.0.1'],
            cwd=frontend_dir
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
        
        # Check if server is responding
        try:
            with urllib.request.urlopen('http://127.0.0.1:5173', timeout=1) as response:
                if response.status == 200:
                    print_success("Frontend server is ready")
                    # Extra sleep to ensure Vite handles initial module resolution
                    time.sleep(3)
                    return frontend_process
        except:
            if i % 5 == 0 and i > 0:
                print_info(f"Still waiting... ({i}/{max_wait}s)")
            continue
    
    print_warning("Frontend server started but readiness check timed out")
    return frontend_process

def open_browser():
    """Open the application in default browser"""
    print_header("Opening Application")
    
    url = "http://127.0.0.1:5173"
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
        frontend_proc = start_frontend()
        
        # Open browser
        open_browser()
        
        # Show status
        print_header("Application Running")
        print_success("Backend:  http://0.0.0.0:8000")
        print_success("Frontend: http://localhost:5173")
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
