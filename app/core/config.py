#!/usr/bin/env python3
"""Configuration constants and settings"""

import os


class Config:
    """Application configuration constants"""

    # Server settings
    DEFAULT_PORT = 6247
    DEFAULT_WEEKS = 52
    MAX_WEEKS = 104

    # File paths
    TEMP_DIR = "/tmp"

    # Calendar settings
    CALENDAR_FILENAME = "schedule.ics"
    CALENDAR_CONTENT_TYPE = "text/calendar; charset=utf-8"

    # HTTP settings
    CACHE_CONTROL = "no-cache"

    # Session settings
    SESSION_COOKIE_NAME = "session"
    SESSION_COOKIE_PATH = "/"
    SESSION_COOKIE_HTTPONLY = True

    # Form validation
    MIN_PASSWORD_LENGTH = 8
    MAX_REASON_LENGTH = 200

    # UI settings
    ENGINEERS_PER_TEAM_DEFAULT = 6
    REQUIRED_DAY = "Tuesday"

    @classmethod
    def get_port(cls):
        """Get server port from environment or default"""
        return int(os.environ.get("PORT", cls.DEFAULT_PORT))

    @classmethod
    def get_temp_file_path(cls, filename):
        """Get full path for temporary file"""
        return os.path.join(cls.TEMP_DIR, filename)
