#!/usr/bin/env python3
"""Swap management service"""

from ..models.rotation import RotationManager
from ..models.swap_manager import SwapManager


class SwapService:
    def __init__(self):
        self.rotation_manager = RotationManager()
        self.swap_manager = SwapManager()

    def get_swap_data(self):
        """Get all swap-related data for UI"""
        return {
            "pending_swaps": self.swap_manager.get_pending_swaps(),
            "approved_swaps": self.swap_manager.get_approved_swaps(),
            "available_users": self.swap_manager.get_available_users(
                self.rotation_manager
            ),
        }

    def create_swap_request(self, form_data):
        """Create a new swap request"""
        requester = form_data.get("requester", [""])[0]
        target = form_data.get("target", [""])[0]
        date = form_data.get("date", [""])[0]
        reason = form_data.get("reason", [""])[0]

        swap_id, error = self.swap_manager.request_swap(
            requester, target, date, reason, self.rotation_manager
        )

        if error:
            return {"success": False, "message": error}
        else:
            return {"success": True, "message": "Swap request submitted successfully"}

    def approve_swap(self, form_data):
        """Approve a swap request"""
        swap_id = form_data.get("swap_id", [""])[0]
        approver = form_data.get("approver", [""])[0]

        success = self.swap_manager.approve_swap(swap_id, approver)

        if success:
            return {"success": True, "message": "Swap approved successfully"}
        else:
            return {"success": False, "message": "Failed to approve swap"}

    def reject_swap(self, form_data):
        """Reject a swap request"""
        swap_id = form_data.get("swap_id", [""])[0]
        approver = form_data.get("approver", [""])[0]

        success = self.swap_manager.reject_swap(swap_id, approver)

        if success:
            return {"success": True, "message": "Swap rejected successfully"}
        else:
            return {"success": False, "message": "Failed to reject swap"}
