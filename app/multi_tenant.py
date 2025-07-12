import os
from urllib.parse import urlparse


class TenantManager:
    def __init__(self):
        self.data_root = os.path.join(os.path.dirname(__file__), "../data")

    def get_tenant_from_host(self, host):
        """Extract tenant from subdomain: customer1.app.com -> customer1"""
        if "." in host:
            return host.split(".")[0]
        return "default"

    def get_tenant_data_path(self, tenant_id):
        """Get isolated data directory for tenant"""
        tenant_dir = os.path.join(self.data_root, f"tenant_{tenant_id}")
        os.makedirs(tenant_dir, exist_ok=True)
        return tenant_dir

    def get_tenant_config(self, tenant_id):
        """Get tenant-specific configuration"""
        return {
            "users_file": os.path.join(
                self.get_tenant_data_path(tenant_id), "users.json"
            ),
            "swaps_file": os.path.join(
                self.get_tenant_data_path(tenant_id), "swaps.json"
            ),
            "config_file": os.path.join(
                self.get_tenant_data_path(tenant_id), "rotation.json"
            ),
        }
