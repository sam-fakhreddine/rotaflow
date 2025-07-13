#!/usr/bin/env python3
"""
Unit tests for core Schedule Manager components
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.config import Config
from app.core.router import Router
from app.services.calendar_service import CalendarService


class TestConfig(unittest.TestCase):
    def test_get_port_default(self):
        """Test default port configuration"""
        with patch.dict(os.environ, {}, clear=True):
            port = Config.get_port()
            self.assertEqual(port, 6247)

    def test_get_port_from_env(self):
        """Test port from environment variable"""
        with patch.dict(os.environ, {"PORT": "8080"}):
            port = Config.get_port()
            self.assertEqual(port, 8080)


class TestRouter(unittest.TestCase):
    def setUp(self):
        self.router = Router()
        self.mock_handler = Mock()

    def test_add_get_route(self):
        """Test adding GET route"""
        self.router.get(r"^/test$", self.mock_handler)
        handler = self.router.route("/test", "GET")
        self.assertEqual(handler, self.mock_handler)

    def test_add_post_route(self):
        """Test adding POST route"""
        self.router.post(r"^/api/test$", self.mock_handler)
        handler = self.router.route("/api/test", "POST")
        self.assertEqual(handler, self.mock_handler)

    def test_route_not_found(self):
        """Test route not found"""
        handler = self.router.route("/nonexistent", "GET")
        self.assertIsNone(handler)

    def test_method_not_allowed(self):
        """Test method not allowed"""
        self.router.get(r"^/test$", self.mock_handler)
        handler = self.router.route("/test", "POST")
        self.assertIsNone(handler)


class TestCalendarService(unittest.TestCase):
    def setUp(self):
        self.service = CalendarService()

    def test_generate_team_calendar(self):
        """Test team calendar generation"""
        calendar_data = self.service.generate_team_calendar(weeks=1)
        self.assertIsInstance(calendar_data, bytes)
        calendar_str = calendar_data.decode()
        self.assertIn("BEGIN:VCALENDAR", calendar_str)
        self.assertIn("END:VCALENDAR", calendar_str)

    def test_generate_engineer_calendar(self):
        """Test individual engineer calendar"""
        # This should return None for non-existent engineer
        calendar_data = self.service.generate_engineer_calendar("NonExistent", weeks=1)
        self.assertIsNone(calendar_data)

    def test_generate_calendar_html(self):
        """Test HTML calendar generation"""
        html = self.service.generate_calendar_html(weeks=1)
        self.assertIsInstance(html, str)
        self.assertIn("Schedule", html)


class TestIntegration(unittest.TestCase):
    def test_server_imports(self):
        """Test that server modules import correctly"""
        try:
            from app.views.http_server import HttpRequestHandler

            self.assertTrue(hasattr(HttpRequestHandler, "do_GET"))
            self.assertTrue(hasattr(HttpRequestHandler, "do_POST"))
        except ImportError as e:
            self.fail(f"Server import failed: {e}")

    def test_handler_imports(self):
        """Test that handlers import correctly"""
        try:
            from app.handlers.auth_handler import AuthHandler
            from app.handlers.calendar_handler import CalendarHandler
            from app.handlers.swap_handler import SwapHandler

            # Test instantiation
            calendar_handler = CalendarHandler()
            auth_handler = AuthHandler()
            swap_handler = SwapHandler()

            self.assertIsNotNone(calendar_handler)
            self.assertIsNotNone(auth_handler)
            self.assertIsNotNone(swap_handler)
        except ImportError as e:
            self.fail(f"Handler import failed: {e}")


def run_unit_tests():
    """Run all unit tests"""
    print("🧪 Running unit tests...")

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestRouter))
    suite.addTests(loader.loadTestsFromTestCase(TestCalendarService))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    total = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total - failures - errors

    print(f"\n📊 Unit Test Results: {passed}/{total} tests passed")

    if failures:
        print(f"❌ {failures} failures")
    if errors:
        print(f"💥 {errors} errors")

    if passed == total:
        print("🎉 All unit tests passed!")
        return True
    else:
        print("💥 Some unit tests failed!")
        return False


if __name__ == "__main__":
    success = run_unit_tests()
    sys.exit(0 if success else 1)
