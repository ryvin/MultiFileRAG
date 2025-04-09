#!/usr/bin/env python3
"""
Database Management Script for MultiFileRAG.

This script provides a command-line interface for managing the database services.
"""

import sys
import argparse
import logging
from database_manager import get_database_manager

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the database management script."""
    parser = argparse.ArgumentParser(description="MultiFileRAG Database Manager")
    parser.add_argument("action", choices=["start", "stop", "restart", "status"],
                       help="Action to perform")
    parser.add_argument("--force", action="store_true",
                       help="Force the action even if services are already running")
    
    args = parser.parse_args()
    
    db_manager = get_database_manager()
    
    if args.action == "start":
        logger.info("Starting database services...")
        success = db_manager.start_services(force=args.force)
        if success:
            logger.info("Database services started successfully.")
        else:
            logger.error("Failed to start database services.")
        sys.exit(0 if success else 1)
    
    elif args.action == "stop":
        logger.info("Stopping database services...")
        success = db_manager.stop_services()
        if success:
            logger.info("Database services stopped successfully.")
        else:
            logger.error("Failed to stop database services.")
        sys.exit(0 if success else 1)
    
    elif args.action == "restart":
        logger.info("Restarting database services...")
        success = db_manager.restart_services()
        if success:
            logger.info("Database services restarted successfully.")
        else:
            logger.error("Failed to restart database services.")
        sys.exit(0 if success else 1)
    
    elif args.action == "status":
        logger.info("Checking database services status...")
        status = db_manager.check_all_services()
        
        print("\nDatabase Services Status:")
        for service, running in status.items():
            print(f"  {service}: {'✅ Running' if running else '❌ Not running'}")
        
        all_running = all(status.values())
        if all_running:
            print("\nAll database services are running.")
        else:
            print("\nSome database services are not running.")
        
        sys.exit(0 if all_running else 1)

if __name__ == "__main__":
    main()
