#!/usr/bin/env python3
"""
Simple session-based authentication
"""

import secrets
from typing import Dict, Optional
from .user_manager import UserManager, User


class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, str] = {}  # session_id -> username
        self.user_manager = UserManager()

    def create_session(self, username: str) -> str:
        session_id = secrets.token_urlsafe(32)
        self.sessions[session_id] = username
        return session_id

    def get_user_from_session(self, session_id: str) -> Optional[User]:
        username = self.sessions.get(session_id)
        if username:
            return self.user_manager.users.get(username)
        return None

    def destroy_session(self, session_id: str):
        self.sessions.pop(session_id, None)

    def login(self, username: str, password: str) -> Optional[str]:
        user = self.user_manager.authenticate(username, password)
        if user:
            return self.create_session(username)
        return None
