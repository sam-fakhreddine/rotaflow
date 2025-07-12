#!/usr/bin/env python3
"""Swap management HTTP handlers"""

from .base_handler import BaseHandler
from ..services.swap_service import SwapService
from ..templates.swap_templates import SwapTemplates
from urllib.parse import urlparse, parse_qs


class SwapHandler(BaseHandler):
    def __init__(self):
        super().__init__()
        self.swap_service = SwapService()
        self.templates = SwapTemplates()

    def serve_swap_management(self):
        """Serve swap management interface"""
        try:
            query_params = parse_qs(urlparse(self.path).query)
            error_msg = query_params.get("error", [""])[0]
            success_msg = query_params.get("success", [""])[0]

            data = self.swap_service.get_swap_data()
            html = self.templates.render_swap_page(data, error_msg, success_msg)

            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())

        except Exception as e:
            self.send_error(500, f"Error loading swaps: {str(e)}")

    def handle_swap_request(self):
        """Handle POST requests for swap operations"""
        try:
            form_data = self._parse_form_data()
            action = form_data.get("action", [""])[0]
            
            if action == "request":
                result = self.swap_service.create_swap_request(form_data)
            elif action == "approve":
                result = self.swap_service.approve_swap(form_data)
            elif action == "reject":
                result = self.swap_service.reject_swap(form_data)
            else:
                result = {"success": False, "message": "Invalid action"}

            redirect_url = self._build_redirect_url(result)
            self.send_response(302)
            self.send_header("Location", redirect_url)
            self.end_headers()

        except Exception as e:
            self.send_error(500, f"Error handling swap request: {str(e)}")

    def _build_redirect_url(self, result):
        """Build redirect URL based on operation result"""
        base_url = "/swaps"
        if result["success"]:
            return f"{base_url}?success={result['message'].replace(' ', '%20')}"
        else:
            return f"{base_url}?error={result['message'].replace(' ', '%20')}"