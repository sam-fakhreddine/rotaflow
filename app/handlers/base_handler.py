"""Base handler following Open/Closed Principle."""

import http.server
import json
import logging
from abc import ABC, abstractmethod
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, Optional

from ..auth.auth import SessionManager
from ..multi_tenant import TenantManager

# Constants imported inline to avoid star import


class BaseHandler(http.server.BaseHTTPRequestHandler, ABC):
    """Base handler providing common functionality."""

    def __init__(self, *args, **kwargs):
        self.session_manager = SessionManager()
        self.tenant_manager = TenantManager()
        self.logger = logging.getLogger(self.__class__.__name__)
        super().__init__(*args, **kwargs)

    def get_tenant_context(self) -> tuple:
        """Get tenant-specific configuration from host header."""
        host = self.headers.get("Host", "localhost").split(":")[0]
        tenant_id = self.tenant_manager.get_tenant_from_host(host)
        return tenant_id, self.tenant_manager.get_tenant_config(tenant_id)

    def parse_query_params(self) -> Dict[str, Any]:
        """Parse query parameters from request."""
        return parse_qs(urlparse(self.path).query)

    def get_current_user(self):
        """Get current user from session cookie."""
        cookies = self.headers.get("Cookie", "")
        for cookie in cookies.split(";"):
            if cookie.strip().startswith("session="):
                session_id = cookie.split("=")[1]
                return self.session_manager.get_user_from_session(session_id)
        return None

    def require_auth(self, required_role: Optional[str] = None) -> bool:
        """Check if user is authenticated and has required role."""
        user = self.get_current_user()
        if not user:
            self.send_response(302)
            self.send_header("Location", "/login")
            self.end_headers()
            return False

        if required_role and user.role not in ["admin"] and user.role != required_role:
            self.send_error(403, "Insufficient permissions")
            return False

        return True

    def send_json_response(self, data: Dict[str, Any], status_code: int = 200):
        """Send JSON response."""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def send_html_response(self, html: str, status_code: int = 200):
        """Send HTML response."""
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def send_file_response(self, content: bytes, content_type: str, filename: str):
        """Send file response with appropriate headers."""
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(content)

    def redirect(self, location: str):
        """Send redirect response."""
        self.send_response(302)
        self.send_header("Location", location)
        self.end_headers()

    def log_event(self, event_type: str, data: Dict[str, Any]):
        """Log structured event data."""
        log_data = {"event": event_type, **data}
        self.logger.info(json.dumps(log_data))

    @abstractmethod
    def handle_request(self):
        """Handle the specific request - to be implemented by subclasses."""
        pass
