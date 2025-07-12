from flask import Flask, request, session, redirect, url_for, render_template_string
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from flask_bcrypt import Bcrypt
import json
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key-change-in-production")
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


class User(UserMixin):
    def __init__(self, username, password_hash, role, engineer_name=None):
        self.id = username
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.engineer_name = engineer_name


@login_manager.user_loader
def load_user(username):
    users = load_users()
    user_data = users.get(username)
    if user_data:
        return User(**user_data)
    return None


def load_users():
    users_file = os.path.join(os.path.dirname(__file__), "../../data/users.json")
    try:
        with open(users_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # Create default users with bcrypt
        default_users = {
            "admin": {
                "username": "admin",
                "password_hash": bcrypt.generate_password_hash("admin123").decode(
                    "utf-8"
                ),
                "role": "admin",
            },
            "manager": {
                "username": "manager",
                "password_hash": bcrypt.generate_password_hash("manager123").decode(
                    "utf-8"
                ),
                "role": "manager",
            },
        }
        os.makedirs(os.path.dirname(users_file), exist_ok=True)
        with open(users_file, "w") as f:
            json.dump(default_users, f, indent=2)
        return default_users


def authenticate_user(username, password):
    users = load_users()
    user_data = users.get(username)
    if user_data and bcrypt.check_password_hash(user_data["password_hash"], password):
        return User(**user_data)
    return None
