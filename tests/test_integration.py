#!/usr/bin/env python3
"""
End-to-end integration tests for Schedule Manager
"""

import json
import os
import sys
import threading
import time
import urllib.request
from urllib.error import HTTPError, URLError

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.views.http_server import main


class IntegrationTestRunner:
    def __init__(self):
        self.server_thread = None
        self.base_url = "http://localhost:6247"

    def start_server(self):
        """Start server in background thread"""
        self.server_thread = threading.Thread(target=main, daemon=True)
        self.server_thread.start()
        time.sleep(3)  # Wait for server startup

    def test_health_endpoint(self):
        """Test /health endpoint"""
        try:
            response = urllib.request.urlopen(f"{self.base_url}/health", timeout=10)
            data = json.loads(response.read().decode())
            assert response.status == 200
            assert data["status"] in ["healthy", "unhealthy"]
            print("✅ Health endpoint test passed")
            return True
        except Exception as e:
            print(f"❌ Health endpoint test failed: {e}")
            return False

    def test_index_page(self):
        """Test / endpoint"""
        try:
            response = urllib.request.urlopen(f"{self.base_url}/", timeout=10)
            html = response.read().decode()
            assert response.status == 200
            assert "4x10 Work Schedule Calendar" in html
            print("✅ Index page test passed")
            return True
        except Exception as e:
            print(f"❌ Index page test failed: {e}")
            return False

    def test_calendar_endpoint(self):
        """Test /calendar.ics endpoint"""
        try:
            response = urllib.request.urlopen(
                f"{self.base_url}/calendar.ics", timeout=10
            )
            content = response.read().decode()
            assert response.status == 200
            assert "BEGIN:VCALENDAR" in content
            print("✅ Calendar endpoint test passed")
            return True
        except Exception as e:
            print(f"❌ Calendar endpoint test failed: {e}")
            return False

    def test_view_endpoint(self):
        """Test /view endpoint"""
        try:
            response = urllib.request.urlopen(f"{self.base_url}/view", timeout=10)
            html = response.read().decode()
            assert response.status == 200
            assert "Schedule" in html or "Calendar" in html
            print("✅ View endpoint test passed")
            return True
        except Exception as e:
            print(f"❌ View endpoint test failed: {e}")
            return False

    def test_login_page(self):
        """Test /login endpoint"""
        try:
            response = urllib.request.urlopen(f"{self.base_url}/login", timeout=10)
            html = response.read().decode()
            assert response.status == 200
            print("✅ Login page test passed")
            return True
        except Exception as e:
            print(f"❌ Login page test failed: {e}")
            return False

    def test_404_handling(self):
        """Test 404 error handling"""
        try:
            urllib.request.urlopen(f"{self.base_url}/nonexistent", timeout=10)
            print("❌ 404 test failed: should have returned 404")
            return False
        except HTTPError as e:
            if e.code == 404:
                print("✅ 404 handling test passed")
                return True
            else:
                print(f"❌ 404 test failed: got {e.code} instead of 404")
                return False
        except Exception as e:
            print(f"❌ 404 test failed: {e}")
            return False

    def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 Starting end-to-end integration tests...")

        # Start server
        print("📡 Starting server...")
        self.start_server()

        # Run tests
        tests = [
            self.test_health_endpoint,
            self.test_index_page,
            self.test_calendar_endpoint,
            self.test_view_endpoint,
            self.test_login_page,
            self.test_404_handling,
        ]

        passed = 0
        total = len(tests)

        for test in tests:
            if test():
                passed += 1
            time.sleep(0.5)  # Brief pause between tests

        print(f"\n📊 Test Results: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All integration tests passed!")
            return True
        else:
            print("💥 Some tests failed!")
            return False


if __name__ == "__main__":
    runner = IntegrationTestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)
