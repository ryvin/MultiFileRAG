#!/usr/bin/env python3
"""
Restart Web UI

This script restarts the web UI by restarting the MultiFileRAG server.
"""

import os
import sys
import time
import logging
import subprocess
import requests
import signal
import psutil

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_server_url():
    """Get the server URL."""
    return "http://localhost:9621"

def check_server_running():
    """Check if the server is running."""
    try:
        response = requests.get(f"{get_server_url()}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def find_server_process():
    """Find the server process."""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and 'multifilerag_server.py' in ' '.join(cmdline):
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return None

def kill_server_process():
    """Kill the server process."""
    proc = find_server_process()
    if proc:
        logger.info(f"Killing server process (PID: {proc.pid})...")
        try:
            proc.terminate()
            proc.wait(timeout=10)
            logger.info("Server process terminated.")
            return True
        except:
            try:
                proc.kill()
                proc.wait(timeout=10)
                logger.info("Server process killed.")
                return True
            except:
                logger.error("Failed to kill server process.")
                return False
    else:
        logger.info("No server process found.")
        return True

def restart_server():
    """Restart the server."""
    # Kill the server process
    if not kill_server_process():
        logger.error("Failed to kill server process.")
        return False
    
    # Start the server
    logger.info("Starting server...")
    try:
        subprocess.Popen(["python", "multifilerag_server.py"], 
                         cwd=os.path.dirname(os.path.abspath(__file__)),
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
        
        # Wait for the server to start
        for _ in range(30):
            if check_server_running():
                logger.info("Server started successfully.")
                return True
            time.sleep(1)
        
        logger.error("Server failed to start within the timeout period.")
        return False
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        return False

def main():
    """Main function."""
    logger.info("Restarting web UI...")
    
    # Check if the server is running
    if check_server_running():
        logger.info("Server is running.")
    else:
        logger.info("Server is not running.")
    
    # Restart the server
    if restart_server():
        logger.info("Web UI restarted successfully.")
    else:
        logger.error("Failed to restart web UI.")
        sys.exit(1)

if __name__ == "__main__":
    main()
