#!/usr/bin/env python3
"""
Refactored HTTP server following SOLID principles and best practices
"""

import http.server
import os
import socketserver
from urllib.parse import urlparse

from ..handlers.auth_handler import AuthHandler
from ..handlers.base_handler import BaseHandler
from ..handlers.calendar_handler import CalendarHandler
from ..handlers.swap_handler import SwapHandler
from ..multi_tenant import TenantManager


class MainHandler(BaseHandler):
    """Main HTTP request handler that delegates to specialized handlers"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.calendar_handler = CalendarHandler()
        self.swap_handler = SwapHandler()
        self.auth_handler = AuthHandler()
        self.tenant_manager = TenantManager()

    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)

        # Route to appropriate handler
        if parsed_path.path == "/calendar.ics":
            self._delegate_to_handler(self.calendar_handler.serve_calendar)
        elif parsed_path.path.startswith("/engineer/"):
            self._delegate_to_handler(self.calendar_handler.serve_engineer_calendar)
        elif parsed_path.path == "/view":
            self._delegate_to_handler(self.calendar_handler.serve_calendar_view)
        elif parsed_path.path == "/swaps":
            self._delegate_to_handler(self.swap_handler.serve_swap_management)
        elif parsed_path.path == "/login":
            self._delegate_to_handler(self.auth_handler.serve_login)
        elif parsed_path.path == "/logout":
            self._delegate_to_handler(self.auth_handler.handle_logout)
        elif parsed_path.path == "/health":
            self._serve_health_check()
        elif parsed_path.path == "/":
            self._serve_index()
        else:
            self.send_error(404)

    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)

        if parsed_path.path == "/api/swap":
            self._delegate_to_handler(self.swap_handler.handle_swap_request)
        elif parsed_path.path == "/api/login":
            self._delegate_to_handler(self.auth_handler.handle_login)
        else:
            self.send_error(404)

    def _delegate_to_handler(self, handler_method):
        """Delegate request to specialized handler"""
        # Copy request context to handler
        handler = handler_method.__self__
        handler.path = self.path
        handler.headers = self.headers
        handler.rfile = self.rfile
        handler.wfile = self.wfile
        handler.send_response = self.send_response
        handler.send_header = self.send_header
        handler.send_error = self.send_error
        handler.end_headers = self.end_headers

        # Execute handler method
        handler_method()

    def _serve_health_check(self):
        """Simple health check endpoint"""
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status":"healthy"}')

    def _serve_index(self):
        """Serve index page with navigation"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>4x10 Work Schedule Calendar</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; }
        .button { background: #007cba; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 5px; display: inline-block; }
        .green { background: #28a745; }
    </style>
</head>
<body>
    <div class="container">
        <h1>4x10 Work Schedule Calendar</h1>
        <p>Subscribe to your team's 4-day work week rotation schedule.</p>
        
        <p>
            <a href="/view" class="button green">View Schedule</a>
            <a href="/swaps" class="button" style="background: #ffc107; color: black;">Manage Swaps</a>
            <a href="/logout" class="button" style="background: #dc3545;">Logout</a>
            <a href="/calendar.ics" class="button">Download Calendar</a>
        </p>
        
        <h2>How to Subscribe:</h2>
        <ul>
            <li><strong>iPhone/iPad:</strong> Settings → Calendar → Accounts → Add Account → Other → Add Subscribed Calendar</li>
            <li><strong>Google Calendar:</strong> Settings → Add calendar → From URL</li>
            <li><strong>Outlook:</strong> File → Account Settings → Internet Calendars → New</li>
            <li><strong>Apple Calendar:</strong> File → New Calendar Subscription</li>
        </ul>
    </div>
</body>
</html>
        """

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())


def main():
    """Start the server"""
    PORT = int(os.environ.get("PORT", 6247))

    with socketserver.TCPServer(("", PORT), MainHandler) as httpd:
        print(f"Serving 4x10 calendar at http://localhost:{PORT}")
        print(f"Calendar view: http://localhost:{PORT}/view")
        print(f"Calendar subscription URL: webcal://localhost:{PORT}/calendar.ics")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
