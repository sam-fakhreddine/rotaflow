#!/usr/bin/env python3
"""
Clean, refactored HTTP server following SOLID principles
"""

import socketserver
from urllib.parse import urlparse

from ..handlers.calendar_handler import CalendarHandler
from ..handlers.swap_handler import SwapHandler
from ..handlers.auth_handler import AuthHandler
from ..handlers.base_handler import BaseHandler
from ..core.router import Router
from ..core.config import Config


class CleanHandler(BaseHandler):
    """Clean HTTP handler using router pattern"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.calendar_handler = CalendarHandler()
        self.swap_handler = SwapHandler()
        self.auth_handler = AuthHandler()
        self.router = self._setup_routes()

    def _setup_routes(self):
        """Setup URL routes"""
        router = Router()
        
        # Calendar routes
        router.get(r"^/calendar\.ics$", self.calendar_handler.serve_calendar)
        router.get(r"^/engineer/.*\.ics$", self.calendar_handler.serve_engineer_calendar)
        router.get(r"^/view$", self.calendar_handler.serve_calendar_view)
        
        # Swap routes
        router.get(r"^/swaps$", self.swap_handler.serve_swap_management)
        router.post(r"^/api/swap$", self.swap_handler.handle_swap_request)
        
        # Auth routes
        router.get(r"^/login$", self.auth_handler.serve_login)
        router.post(r"^/api/login$", self.auth_handler.handle_login)
        router.get(r"^/logout$", self.auth_handler.handle_logout)
        
        # System routes
        router.get(r"^/health$", self._serve_health_check)
        router.get(r"^/$", self._serve_index)
        
        return router

    def do_GET(self):
        """Handle GET requests"""
        self._handle_request("GET")

    def do_POST(self):
        """Handle POST requests"""
        self._handle_request("POST")

    def _handle_request(self, method):
        """Handle HTTP request using router"""
        parsed_path = urlparse(self.path)
        handler = self.router.route(parsed_path.path, method)
        
        if handler:
            self._delegate_to_handler(handler)
        else:
            self.send_error(404)

    def _delegate_to_handler(self, handler_method):
        """Delegate request to handler"""
        if hasattr(handler_method, '__self__'):
            # Instance method - copy context
            handler = handler_method.__self__
            handler.path = self.path
            handler.headers = self.headers
            handler.rfile = self.rfile
            handler.wfile = self.wfile
            handler.send_response = self.send_response
            handler.send_header = self.send_header
            handler.send_error = self.send_error
            handler.end_headers = self.end_headers
        
        handler_method()

    def _serve_health_check(self):
        """Health check endpoint"""
        self._send_json_response({"status": "healthy"})

    def _serve_index(self):
        """Index page"""
        from ..templates.renderers.template_renderer import TemplateRenderer
        import os
        
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates', 'html')
        renderer = TemplateRenderer(template_dir)
        html = renderer.render('index.html')
        
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())


def main():
    """Start the clean server"""
    port = Config.get_port()

    with socketserver.TCPServer(("", port), CleanHandler) as httpd:
        print(f"Clean server running at http://localhost:{port}")
        httpd.serve_forever()


if __name__ == "__main__":
    main()