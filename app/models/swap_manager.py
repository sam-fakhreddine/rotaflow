#!/usr/bin/env python3
"""
Shift Swap Management for 4x10 schedules
"""

import datetime
import json
import sys
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional

from .rotation import RotationManager

sys.path.append(".")


@dataclass
class SwapRequest:
    id: str
    requester: str
    target: str
    date: str
    reason: str
    status: str  # pending, approved, rejected
    created_at: str
    approved_by: Optional[str] = None


class SwapManager:
    def __init__(self, swap_file: str = "swaps.json"):
        self.swap_file = swap_file
        self.swaps = self._load_swaps()

    def _load_swaps(self) -> List[SwapRequest]:
        try:
            with open(self.swap_file, "r") as f:
                data = json.load(f)
                return [SwapRequest(**swap) for swap in data]
        except FileNotFoundError:
            return []

    def _save_swaps(self):
        with open(self.swap_file, "w") as f:
            json.dump([asdict(swap) for swap in self.swaps], f, indent=2)

    def request_swap(
        self, requester: str, target: str, date: str, reason: str, rotation_manager
    ) -> tuple[str, str]:
        """Request a swap with validation. Returns (swap_id, error_message)"""
        # Validate swap request
        error = self._validate_swap_request(requester, target, date, rotation_manager)
        if error:
            return None, error

        swap_id = f"{requester}-{target}-{date}"
        swap = SwapRequest(
            id=swap_id,
            requester=requester,
            target=target,
            date=date,
            reason=reason,
            status="pending",
            created_at=datetime.datetime.now().isoformat(),
        )
        self.swaps.append(swap)
        self._save_swaps()
        return swap_id, None

    def _validate_swap_request(
        self, requester: str, target: str, date: str, rotation_manager
    ) -> str:
        """Validate swap request according to business rules"""
        try:
            swap_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            return "Invalid date format"

        # Find the week containing the swap date
        week_num = self._find_week_for_date(swap_date, rotation_manager)
        if week_num is None:
            return "Date is too far in the past or future"

        # Get the rotation pattern for that week
        rotation_pattern = rotation_manager.get_rotation_pattern(week_num)
        oncall_engineer = rotation_manager.get_oncall_engineer(week_num)

        # Check if requester and target are valid engineers
        engineer_names = [eng.name for eng in rotation_manager.engineers]
        if requester not in engineer_names:
            return f"Requester '{requester}' is not a valid engineer"
        if target not in engineer_names:
            return f"Target '{target}' is not a valid engineer"

        # Check if either person is on-call (on-call can't swap)
        if requester == oncall_engineer.name:
            return f"{requester} is on-call this week and cannot participate in swaps"
        if target == oncall_engineer.name:
            return f"{target} is on-call this week and cannot participate in swaps"

        # Get the day of week for the swap date
        day_names = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        day_of_week = day_names[swap_date.weekday()]

        # Only allow swaps for rotation days (not Tuesday which is required for all)
        if day_of_week == "Tuesday":
            return "Cannot swap Tuesday - it's required for all engineers"

        if day_of_week not in rotation_manager.rotation_days:
            return f"Cannot swap {day_of_week} - only rotation days ({', '.join(rotation_manager.rotation_days)}) can be swapped"

        # Don't allow weekend swaps
        if day_of_week in ["Saturday", "Sunday"]:
            return "Cannot swap weekend days"

        # Check if this is a valid swap (one person off, one person on)
        requester_day_off = rotation_pattern[requester]
        target_day_off = rotation_pattern[target]

        # For a valid swap on the requested date:
        # - One person should have that day off (requester or target)
        # - The other person should be working that day
        requester_off_on_date = requester_day_off == day_of_week
        target_off_on_date = target_day_off == day_of_week

        if requester_off_on_date and target_off_on_date:
            return f"Both {requester} and {target} are already off on {day_of_week} - no swap needed"

        if not requester_off_on_date and not target_off_on_date:
            return f"Both {requester} and {target} are working on {day_of_week} - no swap possible"

        # Valid swap: one person off, one person on
        return None

    def _find_week_for_date(self, target_date: datetime.date, rotation_manager) -> int:
        """Find which week number contains the target date"""
        # Use the same start date logic as the rotation manager
        today = datetime.date.today()
        days_until_monday = (7 - today.weekday()) % 7
        base_start_date = today + datetime.timedelta(days=days_until_monday)

        # Search within reasonable range (52 weeks forward, 4 weeks back)
        for week_offset in range(-4, 52):
            week_start = rotation_manager.get_week_start_date(
                week_offset, base_start_date
            )
            week_end = week_start + datetime.timedelta(days=6)

            if week_start <= target_date <= week_end:
                return week_offset

        return None

    def get_available_users(self, rotation_manager) -> list[str]:
        """Get list of all engineers for dropdown"""
        return [eng.name for eng in rotation_manager.engineers]

    def approve_swap(self, swap_id: str, approver: str) -> bool:
        for swap in self.swaps:
            if swap.id == swap_id:
                swap.status = "approved"
                swap.approved_by = approver
                self._save_swaps()
                return True
        return False

    def reject_swap(self, swap_id: str, approver: str) -> bool:
        for swap in self.swaps:
            if swap.id == swap_id:
                swap.status = "rejected"
                swap.approved_by = approver
                self._save_swaps()
                return True
        return False

    def get_pending_swaps(self) -> List[SwapRequest]:
        return [swap for swap in self.swaps if swap.status == "pending"]

    def get_approved_swaps(self) -> List[SwapRequest]:
        return [swap for swap in self.swaps if swap.status == "approved"]

    def apply_swaps_to_schedule(
        self, rotation_manager: RotationManager, week_num: int
    ) -> Dict[str, str]:
        """Apply approved swaps to a week's rotation pattern - NOTE: This does NOT change the base rotation"""
        base_pattern = rotation_manager.get_rotation_pattern(week_num).copy()
        week_start = rotation_manager.get_week_start_date(week_num)

        # Check for approved swaps in this week
        for swap in self.get_approved_swaps():
            swap_date = datetime.datetime.strptime(swap.date, "%Y-%m-%d").date()
            if week_start <= swap_date < week_start + datetime.timedelta(days=7):
                # Get the day of week for the swap
                day_names = [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ]
                day_of_week = day_names[swap_date.weekday()]

                # Full week swap: they exchange their day-off assignments for this week
                requester_day_off = base_pattern[swap.requester]
                target_day_off = base_pattern[swap.target]

                # Swap their days off for the entire week
                base_pattern[swap.requester] = target_day_off
                base_pattern[swap.target] = requester_day_off

        return base_pattern

    def get_swaps_for_date(self, date: datetime.date) -> List[SwapRequest]:
        """Get all approved swaps for a specific date"""
        date_str = date.strftime("%Y-%m-%d")
        return [swap for swap in self.get_approved_swaps() if swap.date == date_str]

    def get_all_swaps(self) -> List[SwapRequest]:
        """Get all swaps regardless of status"""
        return self.swaps
