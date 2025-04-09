#!/usr/bin/env python3
"""
Database Manager for MultiFileRAG.

This module handles database initialization, checking, and startup.
It automatically starts the required databases if they are not already running.
"""

import os
import sys
import subprocess
import time
import logging
import socket
import requests
from pathlib import Path
import platform

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database services for MultiFileRAG."""

    def __init__(self):
        """Initialize the database manager."""
        self.is_windows = platform.system() == "Windows"
        self.docker_compose_file = "docker-compose.yml"
        self.services = {
            "postgres": {"port": 5432, "check_method": "socket"},
            "neo4j": {"port": 7474, "check_method": "http", "url": "http://localhost:7474"},
            "redis": {"port": 6379, "check_method": "socket"},
            "nodejs": {"port": 3000, "check_method": "http", "url": "http://localhost:3000"}
        }

        # Check if Docker is available
        self.docker_available = self._check_docker()

    def _check_docker(self):
        """Check if Docker is available."""
        try:
            result = subprocess.run(
                ["docker", "info"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            return result.returncode == 0
        except Exception as e:
            logger.warning(f"Docker check failed: {e}")
            return False

    def _check_service_socket(self, host, port, timeout=1):
        """Check if a service is running by attempting to connect to its socket."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception as e:
            logger.debug(f"Socket check failed for {host}:{port}: {e}")
            return False

    def _check_redis(self, host, port, timeout=1):
        """Check if Redis is running by attempting to ping it."""
        try:
            import redis
            r = redis.Redis(host=host, port=port, socket_timeout=timeout)
            return r.ping()
        except ImportError:
            logger.debug("Redis package not installed. Using socket check instead.")
            return self._check_service_socket(host, port, timeout)
        except Exception as e:
            logger.debug(f"Redis check failed for {host}:{port}: {e}")
            return False

    def _check_service_http(self, url, timeout=1):
        """Check if a service is running by making an HTTP request."""
        try:
            response = requests.get(url, timeout=timeout)
            return response.status_code < 400  # Any successful response
        except Exception as e:
            logger.debug(f"HTTP check failed for {url}: {e}")
            return False

    def check_service(self, service_name):
        """Check if a service is running."""
        if service_name not in self.services:
            logger.warning(f"Unknown service: {service_name}")
            return False

        service = self.services[service_name]

        if service_name == "redis":
            return self._check_redis("localhost", service["port"])
        elif service["check_method"] == "socket":
            return self._check_service_socket("localhost", service["port"])
        elif service["check_method"] == "http":
            return self._check_service_http(service["url"])
        else:
            logger.warning(f"Unknown check method for service: {service_name}")
            return False

    def check_all_services(self):
        """Check if all services are running."""
        results = {}
        for service_name in self.services:
            results[service_name] = self.check_service(service_name)

        return results

    def start_services(self, force=False):
        """Start all database services using Docker Compose."""
        if not self.docker_available:
            logger.error("Docker is not available. Cannot start database services.")
            return False

        # Check if services are already running
        if not force:
            service_status = self.check_all_services()
            all_running = all(service_status.values())

            if all_running:
                logger.info("All database services are already running.")
                return True

            # Log which services are not running
            for service, running in service_status.items():
                if not running:
                    logger.info(f"Service {service} is not running.")

        # Start the services using Docker Compose
        try:
            logger.info("Starting database services with Docker Compose...")

            # Make sure the required directories exist
            os.makedirs("docker/postgres", exist_ok=True)
            os.makedirs("docker/neo4j", exist_ok=True)
            os.makedirs("docker/nodejs", exist_ok=True)

            # Start the services
            result = subprocess.run(
                ["docker-compose", "up", "-d"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )

            if result.returncode != 0:
                logger.error(f"Failed to start database services: {result.stderr.decode()}")
                return False

            logger.info("Database services started successfully.")

            # Wait for services to be ready
            self._wait_for_services()

            return True

        except Exception as e:
            logger.error(f"Error starting database services: {e}")
            return False

    def _wait_for_services(self, timeout=120):
        """Wait for all services to be ready."""
        logger.info("Waiting for database services to be ready...")

        start_time = time.time()
        services_ready = {service: False for service in self.services}

        while time.time() - start_time < timeout:
            # Check each service
            for service in self.services:
                if not services_ready[service]:
                    services_ready[service] = self.check_service(service)
                    if services_ready[service]:
                        logger.info(f"Service {service} is ready.")

            # If all services are ready, we're done
            if all(services_ready.values()):
                logger.info("All database services are ready.")
                return True

            # Wait a bit before checking again
            time.sleep(2)

        # Log which services are not ready
        for service, ready in services_ready.items():
            if not ready:
                logger.warning(f"Service {service} is not ready after {timeout} seconds.")

        return False

    def stop_services(self):
        """Stop all database services using Docker Compose."""
        if not self.docker_available:
            logger.error("Docker is not available. Cannot stop database services.")
            return False

        try:
            logger.info("Stopping database services...")

            result = subprocess.run(
                ["docker-compose", "down"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )

            if result.returncode != 0:
                logger.error(f"Failed to stop database services: {result.stderr.decode()}")
                return False

            logger.info("Database services stopped successfully.")
            return True

        except Exception as e:
            logger.error(f"Error stopping database services: {e}")
            return False

    def restart_services(self):
        """Restart all database services."""
        self.stop_services()
        return self.start_services(force=True)


# Singleton instance
_instance = None

def get_database_manager():
    """Get the singleton instance of the database manager."""
    global _instance
    if _instance is None:
        _instance = DatabaseManager()
    return _instance


if __name__ == "__main__":
    """Command-line interface for the database manager."""
    import argparse

    parser = argparse.ArgumentParser(description="MultiFileRAG Database Manager")
    parser.add_argument("action", choices=["start", "stop", "restart", "status"],
                       help="Action to perform")
    parser.add_argument("--force", action="store_true",
                       help="Force the action even if services are already running")

    args = parser.parse_args()

    db_manager = get_database_manager()

    if args.action == "start":
        success = db_manager.start_services(force=args.force)
        sys.exit(0 if success else 1)

    elif args.action == "stop":
        success = db_manager.stop_services()
        sys.exit(0 if success else 1)

    elif args.action == "restart":
        success = db_manager.restart_services()
        sys.exit(0 if success else 1)

    elif args.action == "status":
        status = db_manager.check_all_services()
        print("Database Services Status:")
        for service, running in status.items():
            print(f"  {service}: {'Running' if running else 'Not running'}")

        all_running = all(status.values())
        sys.exit(0 if all_running else 1)
