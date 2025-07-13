#!/usr/bin/env python3
"""Authentication HTML templates"""

import os
from .renderers.template_renderer import TemplateRenderer


class AuthTemplates:
    def __init__(self):
        template_dir = os.path.join(os.path.dirname(__file__), "html")
        self.renderer = TemplateRenderer(template_dir)

    def render_login_page(self, error_msg=""):
        """Render login page"""
        error_html = f'<div class="error">{error_msg}</div>' if error_msg else ""

        return self.renderer.render("login.html", error_html=error_html)
