"""Coverage service for managing day-off adjustments."""

import datetime
from typing import Dict, List, Tuple

from ..utils.holidays import HolidayManager


class CoverageService:
    """Service responsible for managing coverage and day-off adjustments."""

    def __init__(self):
        self.coverage_adjustments = (
            {}
        )  # week_num -> {engineer: {original_day: new_day}}

    def calculate_coverage_adjustments(
        self, manager, week_num: int, week_start: datetime.date
    ) -> Dict[str, str]:
        """Calculate if any engineers need their day off moved for coverage."""
        oncall = manager.get_oncall_engineer(week_num)
        rotation_pattern = manager.get_rotation_pattern(week_num)

        # Check each day for coverage issues
        adjustments = {}

        for day_name in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            if day_name == "Tuesday":  # Skip mandatory day
                continue

            day_date = week_start + datetime.timedelta(
                days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"].index(
                    day_name
                )
            )

            engineers_with_holidays = []
            engineers_with_scheduled_off = []

            for engineer in manager.engineers:
                if engineer != oncall:
                    day_off = rotation_pattern[engineer.name]
                    is_holiday = HolidayManager.is_holiday(
                        day_date, engineer.country, engineer.state_province
                    )

                    if is_holiday:
                        engineers_with_holidays.append(engineer.name)
                    elif day_name == day_off:
                        engineers_with_scheduled_off.append(engineer.name)

            # Check if we need coverage adjustment
            total_off = len(engineers_with_holidays) + len(engineers_with_scheduled_off)
            max_allowed_off = len(manager.engineers) - 2  # Keep at least 2 working

            if total_off > max_allowed_off:
                override_count = total_off - max_allowed_off
                engineers_to_move = engineers_with_scheduled_off[:override_count]

                # Find alternative days for these engineers
                for engineer_name in engineers_to_move:
                    new_day = self._find_alternative_day(
                        engineer_name, day_name, week_start, manager, week_num
                    )
                    if new_day:
                        adjustments[engineer_name] = new_day

        # Store adjustments for this week
        if adjustments:
            self.coverage_adjustments[week_num] = adjustments

        return adjustments

    def _find_alternative_day(
        self,
        engineer_name: str,
        original_day: str,
        week_start: datetime.date,
        manager,
        week_num: int,
    ) -> str:
        """Find an alternative day off for an engineer."""
        oncall = manager.get_oncall_engineer(week_num)
        rotation_pattern = manager.get_rotation_pattern(week_num)

        # Try other days in order of preference
        alternative_days = ["Monday", "Wednesday", "Thursday", "Friday"]
        alternative_days.remove(original_day)  # Remove the original day

        for alt_day in alternative_days:
            alt_date = week_start + datetime.timedelta(
                days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"].index(
                    alt_day
                )
            )

            # Check if this engineer has a holiday on the alternative day
            engineer = next(e for e in manager.engineers if e.name == engineer_name)
            if HolidayManager.is_holiday(
                alt_date, engineer.country, engineer.state_province
            ):
                continue

            # Check if moving here would cause coverage issues
            engineers_off_alt_day = 0
            for eng in manager.engineers:
                if eng != oncall:
                    eng_day_off = rotation_pattern[eng.name]
                    is_holiday_alt = HolidayManager.is_holiday(
                        alt_date, eng.country, eng.state_province
                    )

                    if is_holiday_alt or eng_day_off == alt_day:
                        engineers_off_alt_day += 1

            # If adding this engineer won't cause coverage issues, use this day
            max_allowed = len(manager.engineers) - 2
            if engineers_off_alt_day + 1 <= max_allowed:
                return alt_day

        return None  # No suitable alternative found

    def get_engineer_day_off(
        self, engineer_name: str, week_num: int, original_day: str
    ) -> str:
        """Get the actual day off for an engineer, considering adjustments."""
        if week_num in self.coverage_adjustments:
            if engineer_name in self.coverage_adjustments[week_num]:
                return self.coverage_adjustments[week_num][engineer_name]
        return original_day

    def is_coverage_adjustment(self, engineer_name: str, week_num: int) -> bool:
        """Check if an engineer has a coverage adjustment for this week."""
        return (
            week_num in self.coverage_adjustments
            and engineer_name in self.coverage_adjustments[week_num]
        )
