#!/usr/bin/env python3
"""Simple template renderer for HTML files"""

import os
import re


class TemplateRenderer:
    """Simple template renderer with variable substitution"""
    
    def __init__(self, template_dir):
        self.template_dir = template_dir
    
    def render(self, template_name, **context):
        """Render template with context variables"""
        template_path = os.path.join(self.template_dir, template_name)
        
        with open(template_path, 'r') as f:
            template = f.read()
        
        return self._substitute_variables(template, context)
    
    def _substitute_variables(self, template, context):
        """Replace {{variable}} placeholders with context values"""
        def replace_var(match):
            var_name = match.group(1)
            return str(context.get(var_name, ''))
        
        return re.sub(r'\{\{(\w+)\}\}', replace_var, template)