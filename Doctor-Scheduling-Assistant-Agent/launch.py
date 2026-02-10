"""
Launcher script to start the WebSocket server and interactive client.
"""
import subprocess
import time
import sys
import os


def get_python_path():
    """Get the path to the Python executable in venv."""
    if sys.platform == "win32":
        return os.path.join("venv", "Scripts", "python.exe")
    else:
        return os.path.join("venv", "bin", "python")


def main():
    """Launch server and client."""
    
    python_path = get_python_path()
    
    print("=" * 80)
    print("Study Portal Orchestrator - Launcher")
    print("=" * 80)
    print("\n🚀 Starting WebSocket server...")
    
    # Start server in background
    if sys.platform == "win32":
        server_process = subprocess.Popen(
            [python_path, "websocket_server.py"],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        server_process = subprocess.Popen(
            [python_path, "websocket_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    print("✅ Server should be running now!\n")
    print("🔌 Starting interactive client...\n")
    print("=" * 80 + "\n")
    
    # Start client
    try:
        subprocess.run([python_path, "interactive_client.py"])
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
    finally:
        # Cleanup
        server_process.terminate()
        print("✅ Server stopped")


if __name__ == "__main__":
    main()
