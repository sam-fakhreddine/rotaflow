#!/usr/bin/env python3
"""
Comprehensive test runner for Schedule Manager
"""

import subprocess
import sys

from test_docker import DockerTestRunner
from test_integration import IntegrationTestRunner
from test_units import run_unit_tests


def main():
    """Run all test suites"""
    print("🚀 Starting comprehensive test suite...")
    print("=" * 60)

    results = []

    # 1. Unit Tests
    print("\n1️⃣ UNIT TESTS")
    print("-" * 30)
    unit_success = run_unit_tests()
    results.append(("Unit Tests", unit_success))

    # 2. Integration Tests
    print("\n2️⃣ INTEGRATION TESTS")
    print("-" * 30)
    integration_runner = IntegrationTestRunner()
    integration_success = integration_runner.run_all_tests()
    results.append(("Integration Tests", integration_success))

    # 3. Docker Tests
    print("\n3️⃣ DOCKER TESTS")
    print("-" * 30)
    docker_runner = DockerTestRunner()
    docker_success = docker_runner.run_all_tests()
    results.append(("Docker Tests", docker_success))

    # Summary
    print("\n" + "=" * 60)
    print("📊 FINAL TEST RESULTS")
    print("=" * 60)

    total_suites = len(results)
    passed_suites = sum(1 for _, success in results if success)

    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:<20} {status}")

    print("-" * 60)
    print(f"Test Suites: {passed_suites}/{total_suites} passed")

    if passed_suites == total_suites:
        print("🎉 ALL TESTS PASSED! System is ready for production.")
        return True
    else:
        print("💥 SOME TESTS FAILED! Please review and fix issues.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
