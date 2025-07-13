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

        # Database/Storage check
        try:
            from ..models.swap_manager import SwapManager

            swap_manager = SwapManager()
            swap_manager.get_pending_swaps()
            checks["storage"] = {"status": "healthy", "message": "Storage accessible"}
        except Exception as e:
            checks["storage"] = {"status": "unhealthy", "error": str(e)}
            overall_healthy = False

        # Authentication check
        try:
            from ..auth.auth import SessionManager

            session_manager = SessionManager()
            checks["auth"] = {"status": "healthy", "message": "Auth system operational"}
        except Exception as e:
            checks["auth"] = {"status": "unhealthy", "error": str(e)}
            overall_healthy = False

        # Calendar generation check
        try:
            from ..models.rotation import RotationManager

            rotation_manager = RotationManager()
            rotation_manager.generate_week_schedule(0)
            checks["calendar"] = {
                "status": "healthy",
                "message": "Calendar generation working",
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
