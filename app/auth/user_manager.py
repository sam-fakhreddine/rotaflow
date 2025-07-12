#!/usr/bin/env python3
"""
User management system
"""

import json
import bcrypt
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class User:
    username: str
    password_hash: str
    role: str  # 'admin', 'manager', 'engineer'
    engineer_name: Optional[str] = None  # Links to engineer in rotation


class UserManager:
    def __init__(self, users_file: str = None):
        if users_file is None:
            users_file = os.path.join(
                os.path.dirname(__file__), "../../data/users.json"
            )
        self.users_file = users_file
        os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
        self.users = self._load_users()

    def _load_users(self) -> Dict[str, User]:
        try:
            with open(self.users_file, "r") as f:
                data = json.load(f)
                return {k: User(**v) for k, v in data.items()}
        except FileNotFoundError:
            # Create default admin user
            default_users = {
                "admin": User("admin", self._hash_password("admin123"), "admin"),
                "manager": User(
                    "manager", self._hash_password("manager123"), "manager"
                ),
            }
            self._save_users(default_users)
            return default_users

    def _save_users(self, users: Dict[str, User] = None):
        if users is None:
            users = self.users
        with open(self.users_file, "w") as f:
            data = {k: asdict(v) for k, v in users.items()}
            json.dump(data, f, indent=2)

    def _hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def _verify_password(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

    def create_user(
        self, username: str, password: str, role: str, engineer_name: str = None
    ) -> bool:
        if username in self.users:
            return False

        self.users[username] = User(
            username=username,
            password_hash=self._hash_password(password),
            role=role,
            engineer_name=engineer_name,
        )
        self._save_users()
        return True

    def authenticate(self, username: str, password: str) -> Optional[User]:
        user = self.users.get(username)
        if user and self._verify_password(password, user.password_hash):
            return user
        return None

    def get_users(self) -> List[User]:
        return list(self.users.values())

    def delete_user(self, username: str) -> bool:
        if username in self.users and username != "admin":  # Protect admin
            del self.users[username]
            self._save_users()
            return True
        return False
