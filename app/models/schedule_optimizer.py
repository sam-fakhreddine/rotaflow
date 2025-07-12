#!/usr/bin/env python3
"""
Schedule optimization and validation utilities
"""

from typing import Dict, List
from .rotation import Engineer


class ScheduleOptimizer:
    @staticmethod
    def validate_coverage(
        pattern: Dict[str, str], engineers: List[Engineer], mandatory_day: str
    ) -> Dict[str, any]:
        """Validate schedule meets coverage requirements"""
        rotation_days = ["Monday", "Wednesday", "Thursday", "Friday"]

        # Count people off per day
        day_counts = {day: 0 for day in rotation_days}
        for engineer_name, day_off in pattern.items():
            if day_off in day_counts:
                day_counts[day_off] += 1

        # Check constraints
        issues = []

        # At least 1 person off per rotation day
        for day, count in day_counts.items():
            if count == 0:
                issues.append(f"No one off on {day}")

        # Not too many people off per day (max 50% of team)
        max_off = len(engineers) // 2
        for day, count in day_counts.items():
            if count > max_off:
                issues.append(f"Too many people off on {day}: {count}")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "day_counts": day_counts,
            "coverage_score": min(day_counts.values()) if day_counts else 0,
        }

    @staticmethod
    def suggest_improvements(
        patterns: List[Dict[str, str]], engineers: List[Engineer]
    ) -> List[str]:
        """Suggest improvements to rotation patterns"""
        suggestions = []

        # Analyze fairness across all patterns
        engineer_day_counts = {
            eng.name: {"Monday": 0, "Wednesday": 0, "Thursday": 0, "Friday": 0}
            for eng in engineers
        }

        for pattern in patterns:
            for engineer_name, day_off in pattern.items():
                if day_off in engineer_day_counts[engineer_name]:
                    engineer_day_counts[engineer_name][day_off] += 1

        # Check for imbalances
        for day in ["Monday", "Wednesday", "Thursday", "Friday"]:
            day_totals = [counts[day] for counts in engineer_day_counts.values()]
            if max(day_totals) - min(day_totals) > 1:
                suggestions.append(f"Uneven distribution on {day}s")

        return suggestions
