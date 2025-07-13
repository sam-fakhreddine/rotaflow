#!/usr/bin/env python3
"""
Docker integration tests for Schedule Manager
"""

import json
import subprocess
import time
import urllib.request
from urllib.error import HTTPError


class DockerTestRunner:
    def __init__(self):
        self.container_name = "schedule-manager-test"
        self.base_url = "http://localhost:6247"

    def build_image(self):
        """Build Docker image"""
        try:
            result = subprocess.run(
                ["docker", "build", "-t", "schedule-manager:test", "."],
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                print("✅ Docker image built successfully")
                return True
            else:
                print(f"❌ Docker build failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Docker build error: {e}")
            return False

    def start_container(self):
        """Start Docker container"""
        try:
            # Stop any existing container
            subprocess.run(["docker", "stop", self.container_name], capture_output=True)

            subprocess.run(["docker", "rm", self.container_name], capture_output=True)

            # Start new container
            result = subprocess.run(
                [
                    "docker",
                    "run",
                    "-d",
                    "--name",
                    self.container_name,
                    "-p",
                    "6247:6247",
                    "schedule-manager:test",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print("✅ Docker container started")
                time.sleep(5)  # Wait for startup
                return True
            else:
                print(f"❌ Container start failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Container start error: {e}")
            return False

    def test_container_health(self):
        """Test container health endpoint"""
        try:
            response = urllib.request.urlopen(f"{self.base_url}/health", timeout=15)
            data = json.loads(response.read().decode())

            if response.status == 200 and data.get("status"):
                print("✅ Container health check passed")
                return True
            else:
                print(f"❌ Container health check failed: {data}")
                return False
        except Exception as e:
            print(f"❌ Container health check error: {e}")
            return False

    def test_container_endpoints(self):
        """Test key endpoints in container"""
        endpoints = [
            ("/", "4x10 Work Schedule Calendar"),
            ("/calendar.ics", "BEGIN:VCALENDAR"),
            ("/view", "Schedule"),
        ]

        passed = 0
        for endpoint, expected in endpoints:
            try:
                response = urllib.request.urlopen(
                    f"{self.base_url}{endpoint}", timeout=10
                )
                content = response.read().decode()

                if response.status == 200 and expected in content:
                    print(f"✅ Container endpoint {endpoint} passed")
                    passed += 1
                else:
                    print(f"❌ Container endpoint {endpoint} failed")
            except Exception as e:
                print(f"❌ Container endpoint {endpoint} error: {e}")

        return passed == len(endpoints)

    def cleanup(self):
        """Clean up Docker resources"""
        try:
            subprocess.run(["docker", "stop", self.container_name], capture_output=True)
            subprocess.run(["docker", "rm", self.container_name], capture_output=True)
            print("✅ Docker cleanup completed")
        except Exception as e:
            print(f"❌ Docker cleanup error: {e}")

    def run_all_tests(self):
        """Run all Docker tests"""
        print("🐳 Starting Docker integration tests...")

        try:
            if not self.build_image():
                return False

            if not self.start_container():
                return False

            if not self.test_container_health():
                return False

            if not self.test_container_endpoints():
                return False

            print("🎉 All Docker tests passed!")
            return True

        finally:
            self.cleanup()


if __name__ == "__main__":
    runner = DockerTestRunner()
    success = runner.run_all_tests()
    exit(0 if success else 1)
