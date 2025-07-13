#!/usr/bin/env python3
"""Authentication HTTP handlers"""

from .base_handler import BaseHandler
from ..services.auth_service import AuthService
from ..templates.auth_templates import AuthTemplates
from urllib.parse import urlparse, parse_qs


class AuthHandler(BaseHandler):
    def __init__(self):
        super().__init__()
        self.auth_service = AuthService()
        self.templates = AuthTemplates()

    def serve_login(self):
        """Serve login page"""
        query_params = parse_qs(urlparse(self.path).query)
        error_msg = query_params.get("error", [""])[0]

        html = self.templates.render_login_page(error_msg)

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def handle_login(self):
        """Handle login POST request"""
        try:
            form_data = self._parse_form_data()
            username = form_data.get("username", [""])[0]
            password = form_data.get("password", [""])[0]

            session_id = self.auth_service.authenticate(username, password)

            if session_id:
                self.send_response(302)
                self.send_header("Location", "/")
                self.send_header(
                    "Set-Cookie", f"session={session_id}; Path=/; HttpOnly"
                )
                self.end_headers()
            else:
                self.send_response(302)
                self.send_header("Location", "/login?error=Invalid%20credentials")
                self.end_headers()

        except Exception as e:
            self.send_error(500, f"Login error: {str(e)}")

    def handle_logout(self):
        """Handle logout"""
        session_id = self._get_session_id()
        if session_id:
            self.auth_service.destroy_session(session_id)

        self.send_response(302)
        self.send_header("Location", "/login")
        self.send_header(
            "Set-Cookie",
            "session=; Path=/; HttpOnly; Expires=Thu, 01 Jan 1970 00:00:00 GMT",
        )
        self.end_headers()

    def get_current_user(self):
        """Get current user from session"""
        session_id = self._get_session_id()
        return (
            self.auth_service.get_user_from_session(session_id) if session_id else None
        )

    def require_auth(self, required_role=None):
        """Check authentication and authorization"""
        user = self.get_current_user()
        if not user:
            self.send_response(302)
            self.send_header("Location", "/login")
            self.end_headers()
            return False

        if required_role and not self.auth_service.has_permission(user, required_role):
            self.send_error(403, "Insufficient permissions")
            return False

        return True

    def _get_session_id(self):
        """Extract session ID from cookies"""
        cookies = self.headers.get("Cookie", "")
        for cookie in cookies.split(";"):
            if cookie.strip().startswith("session="):
                return cookie.split("=")[1]
        return None
