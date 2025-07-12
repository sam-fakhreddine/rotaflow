#!/usr/bin/env python3
"""
4x10 Rotation Manager

Generates rotating schedules for the 4x10 workweek policy.
Usage: python rotation_manager.py --weeks 12
"""

import argparse
import datetime
import json
import os
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Engineer:
    name: str
    letter: str
    seniority: int  # For on-call rotation order
    country: str = "US"
    state_province: str = "CA"  # State/Province code


class RotationManager:
    def __init__(self, config_file: str = None):
        # Load team configuration
        self._load_config(config_file)

        # Generate fair rotation patterns algorithmically
        self.rotation_patterns = self._generate_fair_rotation_patterns()

        # Print config info and validate patterns
        cycle_length = len(self.rotation_patterns)
        print(
            f"Team: {len(self.engineers)} engineers, {len(self.rotation_days)} rotation days"
        )
        print(f"Rotation cycle: {cycle_length} weeks")

        # Validate the patterns
        self._validate_patterns()

    def _load_config(self, config_file: str = None):
        """Load team configuration from JSON file"""
        if config_file is None:
            config_file = os.path.join(
                os.path.dirname(__file__), "../../config/team_config.json"
            )

        try:
            with open(config_file, "r") as f:
                config = json.load(f)

            self.engineers = [Engineer(**eng) for eng in config["engineers"]]
            self.rotation_days = config["rotation_days"]
            self.mandatory_day = config.get("mandatory_day", "Tuesday")
            self.mandatory_dates = config.get("mandatory_dates", [])  # YYYYMMDD format
            self.company_days_off = config.get(
                "company_days_off", []
            )  # YYYYMMDD format

        except FileNotFoundError:
            print(f"Config file {config_file} not found. Using default team.")
            self._load_default_config()
        except Exception as e:
            print(f"Error loading config: {e}. Using default team.")
            self._load_default_config()

    def _load_default_config(self):
        """Load default team configuration"""
        self.engineers = [
            Engineer("Alex", "A", 1),
            Engineer("Blake", "B", 2),
            Engineer("Casey", "C", 3),
            Engineer("Dana", "D", 4),
            Engineer("Evan", "E", 5),
            Engineer("Fiona", "F", 6),
        ]
        self.rotation_days = ["Monday", "Wednesday", "Thursday", "Friday"]
        self.mandatory_day = "Tuesday"
        self.mandatory_dates = []
        self.company_days_off = []

    def get_week_start_date(
        self, week_number: int, start_date: datetime.date = None
    ) -> datetime.date:
        """Get the Monday of the specified week number"""
        if start_date is None:
            # Default to next Monday
            today = datetime.date.today()
            days_until_monday = (7 - today.weekday()) % 7
            start_date = today + datetime.timedelta(days=days_until_monday)

        return start_date + datetime.timedelta(weeks=week_number)

    def get_oncall_engineer(self, week_number: int) -> Engineer:
        """Get on-call engineer for given week (rotates through team)"""
        return self.engineers[week_number % len(self.engineers)]

    def _generate_fair_rotation_patterns(self) -> List[Dict[str, str]]:
        """Generate rotation patterns ensuring at least 1 person off per day (except mandatory day)"""
        num_engineers = len(self.engineers)
        num_days = len(self.rotation_days)

        # Ensure we have enough engineers for the constraint
        if num_engineers < num_days:
            raise ValueError(
                f"Need at least {num_days} engineers for {num_days} rotation days"
            )

        patterns = []
        cycle_length = num_engineers * num_days  # Longer cycle for better fairness

        for week in range(cycle_length):
            pattern = {}
            day_assignments = {day: [] for day in self.rotation_days}

            # First pass: ensure exactly 1 person off per day (minimum coverage)
            used_engineers = set()
            day_counts = {day: 0 for day in self.rotation_days}

            for day_idx, day in enumerate(self.rotation_days):
                engineer_idx = (week + day_idx) % num_engineers
                engineer = self.engineers[engineer_idx]

                # If engineer already used, find next available
                while engineer.name in used_engineers:
                    engineer_idx = (engineer_idx + 1) % num_engineers
                    engineer = self.engineers[engineer_idx]

                pattern[engineer.name] = day
                day_counts[day] += 1
                used_engineers.add(engineer.name)

            # Second pass: distribute remaining engineers to minimize max count per day
            remaining_engineers = [
                eng for eng in self.engineers if eng.name not in used_engineers
            ]

            for engineer in remaining_engineers:
                # Always assign to day with minimum count
                min_count = min(day_counts.values())
                min_days = [
                    day for day in self.rotation_days if day_counts[day] == min_count
                ]

                # Use deterministic selection for consistency
                selected_day = min_days[(week + len(used_engineers)) % len(min_days)]

                pattern[engineer.name] = selected_day
                day_counts[selected_day] += 1
                used_engineers.add(engineer.name)

            patterns.append(pattern)

        return patterns

    def get_rotation_pattern(self, week_number: int) -> Dict[str, str]:
        """Get the rotation pattern for given week"""
        pattern_index = week_number % len(self.rotation_patterns)
        return self.rotation_patterns[pattern_index]

    def _validate_patterns(self):
        """Validate that rotation patterns are well-distributed"""
        print("\nPattern validation:")
        for week_idx, pattern in enumerate(self.rotation_patterns):
            day_counts = {day: 0 for day in self.rotation_days}
            for engineer, day_off in pattern.items():
                day_counts[day_off] += 1

            max_per_day = max(day_counts.values())
            min_per_day = min(day_counts.values())

            print(
                f"Week {week_idx + 1}: {dict(day_counts)} (max: {max_per_day}, min: {min_per_day})"
            )

            if max_per_day > 2:
                print(f"  ⚠️  Warning: {max_per_day} people off on same day")

    def generate_week_schedule(self, week_number: int) -> Dict[str, List[str]]:
        """Generate schedule for a specific week"""
        oncall_engineer = self.get_oncall_engineer(week_number)
        rotation_pattern = self.get_rotation_pattern(week_number)

        # Initialize daily schedule
        schedule = {
            "Monday": [],
            "Tuesday": [],  # Always full team
            "Wednesday": [],
            "Thursday": [],
            "Friday": [],
        }

        # Add all engineers to mandatory day
        for engineer in self.engineers:
            schedule[self.mandatory_day].append(
                engineer.letter + ("*" if engineer == oncall_engineer else "")
            )

        # Add engineers to other days based on rotation pattern
        for engineer in self.engineers:
            day_off = rotation_pattern[engineer.name]

            for day in ["Monday", "Wednesday", "Thursday", "Friday"]:
                if day != day_off:
                    marker = engineer.letter
                    if engineer == oncall_engineer:
                        marker += "*"
                    schedule[day].append(marker)

        return schedule

    def print_week_schedule(self, week_number: int, start_date: datetime.date = None):
        """Print formatted schedule for a single week"""
        week_start = self.get_week_start_date(week_number, start_date)
        oncall_engineer = self.get_oncall_engineer(week_number)
        schedule = self.generate_week_schedule(week_number)

        print(
            f"\nWEEK {week_number + 1} ({oncall_engineer.letter}* on-call) - {week_start.strftime('%Y-%m-%d')}"
        )

        # Print header
        print("Mon  Tue  Wed  Thu  Fri")

        # Print schedule grid
        max_engineers = max(len(schedule[day]) for day in schedule.keys())

        for row in range(max_engineers):
            line = ""
            for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
                if row < len(schedule[day]):
                    line += f"{schedule[day][row]:<4} "
                else:
                    line += "     "
            print(line.rstrip())

        # Print totals
        totals = []
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            totals.append(str(len(schedule[day])))

        print(f"\nTotal: {' '.join(f'{total:>3}' for total in totals)}")

    def print_calendar_view(self, num_weeks: int, start_date: datetime.date = None):
        """Print calendar-style view for multiple weeks"""
        if start_date is None:
            # Default to next Monday
            today = datetime.date.today()
            days_until_monday = (7 - today.weekday()) % 7
            start_date = today + datetime.timedelta(days=days_until_monday)

        print(f"4x10 ROTATION SCHEDULE - Starting {start_date.strftime('%Y-%m-%d')}")
        print("=" * 60)
        print("Legend: A-F = Engineers, * = On-call (5x8), - = Day off")
        print("Tuesday is REQUIRED for all engineers")

        # Print 3 weeks per row for better readability
        for row_start in range(0, num_weeks, 3):
            weeks_in_row = min(3, num_weeks - row_start)

            # Print week headers
            header_line = ""
            for i in range(weeks_in_row):
                week_num = row_start + i
                oncall = self.get_oncall_engineer(week_num)
                week_start = self.get_week_start_date(week_num, start_date)
                header_line += f"WEEK {week_num + 1} ({oncall.letter}* on-call)".ljust(
                    20
                )
            print(f"\n{header_line}")

            # Print day headers
            day_header = ""
            for i in range(weeks_in_row):
                day_header += "Mon  Tue  Wed  Thu  Fri   "
            print(day_header)

            # Print engineer schedules
            for engineer in self.engineers:
                line = ""
                for i in range(weeks_in_row):
                    week_num = row_start + i
                    schedule = self.generate_week_schedule(week_num)
                    oncall = self.get_oncall_engineer(week_num)
                    rotation_pattern = self.get_rotation_pattern(week_num)
                    day_off = rotation_pattern[engineer.name]

                    for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
                        if day == day_off and engineer != oncall:
                            line += "-    "
                        else:
                            marker = engineer.letter
                            if engineer == oncall:
                                marker += "*"
                            line += f"{marker:<4} "
                    line += " "
                print(line.rstrip())

            # Print totals for this row
            print()
            total_line = ""
            for i in range(weeks_in_row):
                week_num = row_start + i
                schedule = self.generate_week_schedule(week_num)
                totals = []
                for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
                    totals.append(str(len(schedule[day])))
                total_line += f"Total: {' '.join(totals)}   "
            print(total_line)

    def export_csv(
        self, num_weeks: int, filename: str = None, start_date: datetime.date = None
    ):
        """Export schedule to CSV file"""
        if filename is None:
            filename = f"4x10_schedule_{num_weeks}weeks.csv"

        if start_date is None:
            today = datetime.date.today()
            days_until_monday = (7 - today.weekday()) % 7
            start_date = today + datetime.timedelta(days=days_until_monday)

        with open(filename, "w") as f:
            f.write(
                "Week,Date,Engineer,Monday,Tuesday,Wednesday,Thursday,Friday,Schedule_Type,Day_Off\n"
            )

            for week_num in range(num_weeks):
                week_start = self.get_week_start_date(week_num, start_date)
                oncall = self.get_oncall_engineer(week_num)
                rotation_pattern = self.get_rotation_pattern(week_num)

                for engineer in self.engineers:
                    day_off = rotation_pattern[engineer.name]
                    schedule_type = "5x8_oncall" if engineer == oncall else "4x10"

                    # Create schedule row
                    row = [
                        str(week_num + 1),
                        week_start.strftime("%Y-%m-%d"),
                        engineer.name,
                        "WORK" if "Monday" != day_off else "OFF",
                        "WORK",  # Tuesday always required
                        "WORK" if "Wednesday" != day_off else "OFF",
                        "WORK" if "Thursday" != day_off else "OFF",
                        "WORK" if "Friday" != day_off else "OFF",
                        schedule_type,
                        day_off if engineer != oncall else "None",
                    ]
                    f.write(",".join(row) + "\n")

        print(f"Schedule exported to {filename}")

    def export_ical(
        self, num_weeks: int, filename: str = None, start_date: datetime.date = None
    ):
        """Export schedule to iCal format for calendar subscriptions"""
        if filename is None:
            filename = f"4x10_schedule_{num_weeks}weeks.ics"

        if start_date is None:
            today = datetime.date.today()
            days_until_monday = (7 - today.weekday()) % 7
            start_date = today + datetime.timedelta(days=days_until_monday)

        with open(filename, "w") as f:
            f.write("BEGIN:VCALENDAR\n")
            f.write("VERSION:2.0\n")
            f.write("PRODID:-//4x10 Rotation Manager//EN\n")
            f.write("CALSCALE:GREGORIAN\n")
            f.write("METHOD:PUBLISH\n")
            f.write("X-WR-CALNAME:4x10 Work Schedule\n")
            f.write("X-WR-CALDESC:4-day work week rotation schedule\n")

            for week_num in range(num_weeks):
                week_start = self.get_week_start_date(week_num, start_date)
                oncall = self.get_oncall_engineer(week_num)
                rotation_pattern = self.get_rotation_pattern(week_num)

                for engineer in self.engineers:
                    day_off = rotation_pattern[engineer.name]
                    is_oncall = engineer == oncall

                    # Create events for work days
                    for day_name, day_offset in [
                        ("Monday", 0),
                        ("Tuesday", 1),
                        ("Wednesday", 2),
                        ("Thursday", 3),
                        ("Friday", 4),
                    ]:
                        event_date = week_start + datetime.timedelta(days=day_offset)

                        if day_name == day_off and not is_oncall:
                            # Day off event
                            f.write("BEGIN:VEVENT\n")
                            f.write(
                                f"UID:{engineer.name}-{event_date.strftime('%Y%m%d')}-dayoff@4x10rotation\n"
                            )
                            f.write(
                                f"DTSTART;VALUE=DATE:{event_date.strftime('%Y%m%d')}\n"
                            )
                            f.write(
                                f"DTEND;VALUE=DATE:{event_date.strftime('%Y%m%d')}\n"
                            )
                            f.write(f"SUMMARY:{engineer.name} - Day Off\n")
                            f.write(
                                f"DESCRIPTION:Scheduled day off for {engineer.name}\n"
                            )
                            f.write("CATEGORIES:Day Off\n")
                            f.write("END:VEVENT\n")
                        else:
                            # Work day event
                            schedule_type = (
                                "On-call (5x8)" if is_oncall else "Regular (4x10)"
                            )
                            f.write("BEGIN:VEVENT\n")
                            f.write(
                                f"UID:{engineer.name}-{event_date.strftime('%Y%m%d')}-work@4x10rotation\n"
                            )
                            f.write(
                                f"DTSTART;VALUE=DATE:{event_date.strftime('%Y%m%d')}\n"
                            )
                            f.write(
                                f"DTEND;VALUE=DATE:{event_date.strftime('%Y%m%d')}\n"
                            )
                            f.write(f"SUMMARY:{engineer.name} - {schedule_type}\n")
                            f.write(
                                f"DESCRIPTION:{engineer.name} working - {schedule_type}\n"
                            )
                            if is_oncall:
                                f.write("CATEGORIES:On-call,Work\n")
                            else:
                                f.write("CATEGORIES:Work\n")
                            f.write("END:VEVENT\n")

            f.write("END:VCALENDAR\n")

        print(f"iCal calendar exported to {filename}")

    def analyze_fairness(self, num_weeks: int, start_date: datetime.date = None):
        """Analyze fairness of day-off distribution across engineers and days"""
        if start_date is None:
            today = datetime.date.today()
            days_until_monday = (7 - today.weekday()) % 7
            start_date = today + datetime.timedelta(days=days_until_monday)

        # Track days off per engineer per day of week
        days_off_count = {
            engineer.name: {"Monday": 0, "Wednesday": 0, "Thursday": 0, "Friday": 0}
            for engineer in self.engineers
        }
        total_days_off = {engineer.name: 0 for engineer in self.engineers}
        oncall_weeks = {engineer.name: 0 for engineer in self.engineers}

        for week_num in range(num_weeks):
            oncall = self.get_oncall_engineer(week_num)
            rotation_pattern = self.get_rotation_pattern(week_num)
            oncall_weeks[oncall.name] += 1

            for engineer in self.engineers:
                if engineer != oncall:  # On-call engineers don't get days off
                    day_off = rotation_pattern[engineer.name]
                    days_off_count[engineer.name][day_off] += 1
                    total_days_off[engineer.name] += 1

        print(f"\nFAIRNESS ANALYSIS - {num_weeks} weeks")
        print("=" * 50)

        # Days off per engineer
        print("\nTotal Days Off per Engineer:")
        for engineer in self.engineers:
            print(f"{engineer.name}: {total_days_off[engineer.name]} days")

        avg_days_off = sum(total_days_off.values()) / len(self.engineers)
        print(f"Average: {avg_days_off:.1f} days")

        # On-call distribution
        print("\nOn-call Weeks per Engineer:")
        for engineer in self.engineers:
            print(f"{engineer.name}: {oncall_weeks[engineer.name]} weeks")

        avg_oncall = sum(oncall_weeks.values()) / len(self.engineers)
        print(f"Average: {avg_oncall:.1f} weeks")

        # Day-of-week distribution
        print("\nDays Off by Day of Week:")
        print("Engineer    Mon  Wed  Thu  Fri")
        for engineer in self.engineers:
            counts = days_off_count[engineer.name]
            print(
                f"{engineer.name:<10} {counts['Monday']:>3}  {counts['Wednesday']:>3}  {counts['Thursday']:>3}  {counts['Friday']:>3}"
            )

        # Calculate fairness metrics
        day_totals = {"Monday": 0, "Wednesday": 0, "Thursday": 0, "Friday": 0}
        for engineer_counts in days_off_count.values():
            for day, count in engineer_counts.items():
                day_totals[day] += count

        print("\nTotal per day:", end="")
        for day, total in day_totals.items():
            print(f" {day[:3]}:{total}", end="")
        print()

        # Fairness score (lower is more fair)
        import statistics

        fairness_scores = []
        for day in ["Monday", "Wednesday", "Thursday", "Friday"]:
            day_counts = [days_off_count[eng.name][day] for eng in self.engineers]
            if max(day_counts) > 0:
                fairness_scores.append(statistics.stdev(day_counts))

        avg_fairness = (
            sum(fairness_scores) / len(fairness_scores) if fairness_scores else 0
        )
        print(f"\nFairness Score: {avg_fairness:.2f} (lower = more fair)")

        if avg_fairness < 0.5:
            print("✓ Very fair distribution")
        elif avg_fairness < 1.0:
            print("~ Reasonably fair distribution")
        else:
            print("! Uneven distribution - consider adjusting rotation")


def main():
    parser = argparse.ArgumentParser(description="Generate 4x10 rotation schedules")
    parser.add_argument(
        "--weeks",
        "-w",
        type=int,
        default=6,
        help="Number of weeks to generate (default: 6)",
    )
    parser.add_argument(
        "--export", "-e", action="store_true", help="Export to CSV file"
    )
    parser.add_argument(
        "--start-date",
        "-s",
        type=str,
        help="Start date (YYYY-MM-DD), defaults to next Monday",
    )
    parser.add_argument(
        "--analyze", "-a", action="store_true", help="Analyze fairness of schedule"
    )
    parser.add_argument(
        "--config", "-c", type=str, help="Path to team config JSON file"
    )
    parser.add_argument(
        "--ical", "-i", action="store_true", help="Export to iCal format"
    )

    args = parser.parse_args()

    # Parse start date if provided
    start_date = None
    if args.start_date:
        try:
            start_date = datetime.datetime.strptime(args.start_date, "%Y-%m-%d").date()
        except ValueError:
            print("Error: Start date must be in YYYY-MM-DD format")
            return

    manager = RotationManager(args.config)

    # Generate and display schedule
    manager.print_calendar_view(args.weeks, start_date)

    # Export if requested
    if args.export:
        manager.export_csv(args.weeks, start_date=start_date)

    if args.ical:
        manager.export_ical(args.weeks, start_date=start_date)

    # Analyze fairness if requested
    if args.analyze:
        manager.analyze_fairness(args.weeks, start_date)


if __name__ == "__main__":
    main()
