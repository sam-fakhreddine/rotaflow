#!/usr/bin/env python3
"""Authentication service"""

from ..auth.user_manager import UserManager
from ..auth.auth import SessionManager


class AuthService:
    def __init__(self):
        self.user_manager = UserManager()
        self.session_manager = SessionManager()

    def authenticate(self, username, password):
        """Authenticate user and create session"""
        return self.session_manager.login(username, password)

    def get_user_from_session(self, session_id):
        """Get user from session ID"""
        return self.session_manager.get_user_from_session(session_id)

    def destroy_session(self, session_id):
        """Destroy user session"""
        self.session_manager.destroy_session(session_id)

    def has_permission(self, user, required_role):
        """Check if user has required permission"""
        if user.role == "admin":
            return True
        return user.role == required_role