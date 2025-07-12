#!/usr/bin/env python3
"""Simple URL router for HTTP handlers"""

from urllib.parse import urlparse
import re


class Route:
    """Represents a single route"""
    
    def __init__(self, pattern, handler, methods=None):
        self.pattern = re.compile(pattern)
        self.handler = handler
        self.methods = methods or ["GET"]
    
    def matches(self, path, method):
        """Check if route matches path and method"""
        return method in self.methods and self.pattern.match(path)


class Router:
    """Simple HTTP router"""
    
    def __init__(self):
        self.routes = []
    
    def add_route(self, pattern, handler, methods=None):
        """Add a route"""
        self.routes.append(Route(pattern, handler, methods))
    
    def route(self, path, method):
        """Find handler for path and method"""
        for route in self.routes:
            if route.matches(path, method):
                return route.handler
        return None
    
    def get(self, pattern, handler):
        """Add GET route"""
        self.add_route(pattern, handler, ["GET"])
    
    def post(self, pattern, handler):
        """Add POST route"""
        self.add_route(pattern, handler, ["POST"])