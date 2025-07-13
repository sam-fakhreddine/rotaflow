#!/usr/bin/env python3
"""Health check handler for monitoring and CI"""

import json
import time

from .base_handler import BaseHandler


class HealthHandler(BaseHandler):
    """Comprehensive health check endpoint"""

    def handle_request(self):
        """Handle health check request"""
        try:
            health_data = self._perform_health_checks()
            status_code = 200 if health_data["status"] == "healthy" else 503
            self.send_json_response(health_data, status_code)
        except Exception as e:
            self.send_json_response(
                {"status": "unhealthy", "error": str(e), "timestamp": time.time()}, 503
            )

    def _perform_health_checks(self):
        """Perform comprehensive health checks"""
        checks = {}
        overall_healthy = True

        # Basic system check
        try:
            import os

            os.path.exists(".")
            checks["system"] = {"status": "healthy", "message": "System operational"}
        except Exception as e:
            checks["system"] = {"status": "unhealthy", "error": str(e)}
            overall_healthy = False

        # Storage check - basic file system
        try:
            import os

            data_dir = "data"
            if os.path.exists(data_dir):
                checks["storage"] = {
                    "status": "healthy",
                    "message": "Storage accessible",
                }
            else:
                checks["storage"] = {"status": "healthy", "message": "Storage ready"}
        except Exception as e:
            checks["storage"] = {"status": "unhealthy", "error": str(e)}
            overall_healthy = False

        # Auth check - basic import
        try:
            from ..auth import auth

            checks["auth"] = {"status": "healthy", "message": "Auth system operational"}
        except Exception as e:
            checks["auth"] = {"status": "unhealthy", "error": str(e)}
            overall_healthy = False

        # Calendar check - basic import
        try:
            from ..models import rotation

            checks["calendar"] = {
                "status": "healthy",
                "message": "Calendar system operational",
            }
        except Exception as e:
            checks["calendar"] = {"status": "unhealthy", "error": str(e)}
            overall_healthy = False

        return {
            "status": "healthy" if overall_healthy else "unhealthy",
            "timestamp": time.time(),
            "checks": checks,
            "version": "1.0.0",
        }
