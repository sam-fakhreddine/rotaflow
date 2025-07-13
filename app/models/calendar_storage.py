#!/usr/bin/env python3
"""
Calendar storage system using JSON
"""

import json

# datetime imported where needed
from typing import Dict, List
from dataclasses import dataclass, asdict
from .rotation import RotationManager
from .swap_manager import SwapManager


@dataclass
class WeekSchedule:
    week_num: int
    start_date: str
    oncall_engineer: str
    base_pattern: Dict[str, str]  # engineer -> day_off
    actual_pattern: Dict[str, str]  # after swaps applied


class CalendarStorage:
    def __init__(self, calendar_file: str = "calendar.json"):
        self.calendar_file = calendar_file
        self.calendar = self._load_calendar()

    def _load_calendar(self) -> Dict[str, WeekSchedule]:
        try:
            with open(self.calendar_file, "r") as f:
                data = json.load(f)
                return {k: WeekSchedule(**v) for k, v in data.items()}
        except FileNotFoundError:
            return {}

    def _save_calendar(self):
        with open(self.calendar_file, "w") as f:
            data = {k: asdict(v) for k, v in self.calendar.items()}
            json.dump(data, f, indent=2)

    def generate_calendar(self, weeks: int = 52):
        """Generate calendar from rotation manager"""
        rotation_manager = RotationManager()
        swap_manager = SwapManager()

        for week_num in range(weeks):
            week_key = f"week_{week_num}"
            week_start = rotation_manager.get_week_start_date(week_num)
            oncall = rotation_manager.get_oncall_engineer(week_num)
            base_pattern = rotation_manager.get_rotation_pattern(week_num)
            actual_pattern = swap_manager.apply_swaps_to_schedule(
                rotation_manager, week_num
            )

            self.calendar[week_key] = WeekSchedule(
                week_num=week_num,
                start_date=week_start.strftime("%Y-%m-%d"),
                oncall_engineer=oncall.name,
                base_pattern=base_pattern,
                actual_pattern=actual_pattern,
            )

        self._save_calendar()

    def update_week_with_swaps(self, week_num: int):
        """Update specific week with current swaps"""
        rotation_manager = RotationManager()
        swap_manager = SwapManager()

        week_key = f"week_{week_num}"
        if week_key in self.calendar:
            actual_pattern = swap_manager.apply_swaps_to_schedule(
                rotation_manager, week_num
            )
            self.calendar[week_key].actual_pattern = actual_pattern
            self._save_calendar()

    def get_week(self, week_num: int) -> WeekSchedule:
        """Get week schedule"""
        week_key = f"week_{week_num}"
        return self.calendar.get(week_key)

    def get_engineer_schedule(self, engineer: str, weeks: int = 4) -> List[Dict]:
        """Get schedule for specific engineer"""
        schedule = []
        for week_num in range(weeks):
            week = self.get_week(week_num)
            if week:
                schedule.append(
                    {
                        "week": week_num + 1,
                        "start_date": week.start_date,
                        "day_off": week.actual_pattern.get(engineer),
                        "is_oncall": week.oncall_engineer == engineer,
                        "swapped": week.base_pattern.get(engineer)
                        != week.actual_pattern.get(engineer),
                    }
                )
        return schedule
