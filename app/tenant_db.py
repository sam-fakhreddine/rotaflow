import os
import sqlite3


class TenantDatabase:
    def __init__(self, tenant_id):
        self.tenant_id = tenant_id
        self.db_path = f"data/tenant_{tenant_id}.db"
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password_hash TEXT,
                    role TEXT,
                    engineer_name TEXT
                )
            """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS swaps (
                    id TEXT PRIMARY KEY,
                    requester TEXT,
                    target TEXT,
                    date TEXT,
                    status TEXT,
                    created_at TEXT
                )
            """
            )

    def get_connection(self):
        return sqlite3.connect(self.db_path)
