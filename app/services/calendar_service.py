#!/usr/bin/env python3
"""Calendar generation service"""

import datetime
import os
import tempfile

from ..models.rotation import RotationManager
from ..models.swap_manager import SwapManager
from ..services.coverage_service import CoverageService
from ..templates.calendar_templates import CalendarTemplates
from ..utils.holidays import HolidayManager


class CalendarService:
    def __init__(self):
        self.coverage_service = CoverageService()
        self.templates = CalendarTemplates()

    def generate_team_calendar(self, weeks=52, config=None):
        """Generate team iCal calendar"""
        manager = RotationManager(config)
        filename = self._create_temp_file("schedule.ics")

        try:
            manager.export_ical(weeks, filename)
            with open(filename, "rb") as f:
                return f.read()
        finally:
            self._cleanup_temp_file(filename)

    def generate_engineer_calendar(self, engineer_name, weeks=52, config=None):
        """Generate individual engineer iCal calendar"""
        manager = RotationManager(config)

        engineer = self._find_engineer(manager, engineer_name)
        if not engineer:
            return None

        filename = self._create_temp_file(f"{engineer_name}_schedule.ics")

        try:
            self._export_engineer_ical(manager, engineer, weeks, filename)
            with open(filename, "rb") as f:
                return f.read()
        finally:
            self._cleanup_temp_file(filename)

    def generate_calendar_html(self, weeks=52, config=None, start_date_str=None):
        """Generate HTML calendar view"""
        manager = RotationManager(config)
        start_date = self._parse_start_date(start_date_str)

        calendar_data = self._build_calendar_data(manager, weeks, start_date)
        return self.templates.render_calendar_view(calendar_data)

    def _find_engineer(self, manager, engineer_name):
        """Find engineer by name"""
        for eng in manager.engineers:
            if eng.name.lower() == engineer_name.lower():
                return eng
        return None

    def _parse_start_date(self, start_date_str):
        """Parse start date string or use default"""
        if start_date_str:
            try:
                return datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
            except ValueError:
                pass

        today = datetime.date.today()
        days_until_monday = (7 - today.weekday()) % 7
        return today + datetime.timedelta(days=days_until_monday)

    def _build_calendar_data(self, manager, weeks, start_date):
        """Build calendar data structure for template"""
        swap_manager = SwapManager()

        return {
            "manager": manager,
            "weeks": weeks,
            "start_date": start_date,
            "coverage_service": self.coverage_service,
            "swap_manager": swap_manager,
            "holiday_manager": HolidayManager,
        }

    def _export_engineer_ical(self, manager, engineer, num_weeks, filename):
        """Export individual engineer schedule to iCal"""
        today = datetime.date.today()
        days_until_monday = (7 - today.weekday()) % 7
        start_date = today + datetime.timedelta(days=days_until_monday)

        with open(filename, "w") as f:
            self._write_ical_header(f, engineer)

            for week_num in range(num_weeks):
                self._write_engineer_week(f, manager, engineer, week_num, start_date)

            f.write("END:VCALENDAR\n")

    def _write_ical_header(self, f, engineer):
        """Write iCal header"""
        f.write("BEGIN:VCALENDAR\n")
        f.write("VERSION:2.0\n")
        f.write("PRODID:-//4x10 Rotation Manager//EN\n")
        f.write("CALSCALE:GREGORIAN\n")
        f.write("METHOD:PUBLISH\n")
        f.write(f"X-WR-CALNAME:{engineer.name} - 4x10 Schedule\n")
        f.write(f"X-WR-CALDESC:Personal 4x10 work schedule for {engineer.name}\n")

    def _write_engineer_week(self, f, manager, engineer, week_num, start_date):
        """Write one week of engineer schedule"""
        week_start = manager.get_week_start_date(week_num, start_date)
        oncall = manager.get_oncall_engineer(week_num)
        rotation_pattern = manager.get_rotation_pattern(week_num)

        day_off = rotation_pattern[engineer.name]
        is_oncall = engineer == oncall

        for day_name, day_offset in [
            ("Monday", 0),
            ("Tuesday", 1),
            ("Wednesday", 2),
            ("Thursday", 3),
            ("Friday", 4),
        ]:
            event_date = week_start + datetime.timedelta(days=day_offset)

            if day_name == day_off and not is_oncall:
                self._write_day_off_event(f, engineer, event_date)
            else:
                self._write_work_event(f, engineer, event_date, is_oncall)

    def _write_day_off_event(self, f, engineer, event_date):
        """Write day off event"""
        f.write("BEGIN:VEVENT\n")
        f.write(
            f"UID:{engineer.name}-{event_date.strftime('%Y%m%d')}-dayoff@4x10rotation\n"
        )
        f.write(f"DTSTART;VALUE=DATE:{event_date.strftime('%Y%m%d')}\n")
        f.write(f"DTEND;VALUE=DATE:{event_date.strftime('%Y%m%d')}\n")
        f.write("SUMMARY:Day Off\n")
        f.write("DESCRIPTION:Scheduled day off\n")
        f.write("CATEGORIES:Day Off\n")
        f.write("END:VEVENT\n")

    def _write_work_event(self, f, engineer, event_date, is_oncall):
        """Write work day event"""
        schedule_type = "On-call" if is_oncall else "Work"
        f.write("BEGIN:VEVENT\n")
        f.write(
            f"UID:{engineer.name}-{event_date.strftime('%Y%m%d')}-work@4x10rotation\n"
        )
        f.write(f"DTSTART;VALUE=DATE:{event_date.strftime('%Y%m%d')}\n")
        f.write(f"DTEND;VALUE=DATE:{event_date.strftime('%Y%m%d')}\n")
        f.write(f"SUMMARY:{schedule_type}\n")
        f.write(f"DESCRIPTION:{'On-call duty' if is_oncall else 'Regular work day'}\n")
        f.write(f"CATEGORIES:{'On-call,Work' if is_oncall else 'Work'}\n")
        f.write("END:VEVENT\n")

    def _create_temp_file(self, filename):
        """Create temporary file"""
        return os.path.join(tempfile.gettempdir(), filename)

    def _cleanup_temp_file(self, filename):
        """Clean up temporary file"""
        try:
            os.remove(filename)
        except OSError:
            pass
