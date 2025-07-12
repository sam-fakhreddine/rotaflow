"""Calendar service following Single Responsibility Principle."""

import datetime
from typing import Optional
from ..models.rotation import RotationManager
from ..core.constants import TEMP_DIR


class CalendarService:
    """Service responsible for calendar generation and export."""
    
    def __init__(self, rotation_manager: RotationManager):
        self._rotation_manager = rotation_manager
    
    def generate_ical(self, weeks: int, filename: Optional[str] = None) -> str:
        """Generate iCal file and return filename."""
        if filename is None:
            filename = f"{TEMP_DIR}/schedule.ics"
        
        self._rotation_manager.export_ical(weeks, filename)
        return filename
    
    def generate_engineer_ical(self, engineer_name: str, weeks: int) -> str:
        """Generate individual engineer iCal file."""
        engineer = self._find_engineer(engineer_name)
        if not engineer:
            raise ValueError(f"Engineer '{engineer_name}' not found")
        
        filename = f"{TEMP_DIR}/{engineer_name}_schedule.ics"
        self._export_engineer_ical(engineer, weeks, filename)
        return filename
    
    def _find_engineer(self, engineer_name: str):
        """Find engineer by name (case-insensitive)."""
        for engineer in self._rotation_manager.engineers:
            if engineer.name.lower() == engineer_name.lower():
                return engineer
        return None
    
    def _export_engineer_ical(self, engineer, num_weeks: int, filename: str):
        """Export individual engineer schedule to iCal."""
        today = datetime.date.today()
        days_until_monday = (7 - today.weekday()) % 7
        start_date = today + datetime.timedelta(days=days_until_monday)

        with open(filename, "w") as f:
            self._write_ical_header(f, engineer)
            self._write_engineer_events(f, engineer, num_weeks, start_date)
            f.write("END:VCALENDAR\\n")
    
    def _write_ical_header(self, f, engineer):
        """Write iCal header information."""
        f.write("BEGIN:VCALENDAR\\n")
        f.write("VERSION:2.0\\n")
        f.write("PRODID:-//4x10 Rotation Manager//EN\\n")
        f.write("CALSCALE:GREGORIAN\\n")
        f.write("METHOD:PUBLISH\\n")
        f.write(f"X-WR-CALNAME:{engineer.name} - 4x10 Schedule\\n")
        f.write(f"X-WR-CALDESC:Personal 4x10 work schedule for {engineer.name}\\n")
    
    def _write_engineer_events(self, f, engineer, num_weeks: int, start_date: datetime.date):
        """Write engineer events to iCal file."""
        for week_num in range(num_weeks):
            week_start = self._rotation_manager.get_week_start_date(week_num, start_date)
            oncall = self._rotation_manager.get_oncall_engineer(week_num)
            rotation_pattern = self._rotation_manager.get_rotation_pattern(week_num)

            day_off = rotation_pattern[engineer.name]
            is_oncall = engineer == oncall

            for day_name, day_offset in [
                ("Monday", 0), ("Tuesday", 1), ("Wednesday", 2), 
                ("Thursday", 3), ("Friday", 4)
            ]:
                event_date = week_start + datetime.timedelta(days=day_offset)
                
                if day_name == day_off and not is_oncall:
                    self._write_day_off_event(f, engineer, event_date)
                else:
                    self._write_work_event(f, engineer, event_date, is_oncall)
    
    def _write_day_off_event(self, f, engineer, event_date: datetime.date):
        """Write day off event to iCal."""
        f.write("BEGIN:VEVENT\\n")
        f.write(f"UID:{engineer.name}-{event_date.strftime('%Y%m%d')}-dayoff@4x10rotation\\n")
        f.write(f"DTSTART;VALUE=DATE:{event_date.strftime('%Y%m%d')}\\n")
        f.write(f"DTEND;VALUE=DATE:{event_date.strftime('%Y%m%d')}\\n")
        f.write("SUMMARY:Day Off\\n")
        f.write("DESCRIPTION:Scheduled day off\\n")
        f.write("CATEGORIES:Day Off\\n")
        f.write("END:VEVENT\\n")
    
    def _write_work_event(self, f, engineer, event_date: datetime.date, is_oncall: bool):
        """Write work event to iCal."""
        schedule_type = "On-call" if is_oncall else "Work"
        f.write("BEGIN:VEVENT\\n")
        f.write(f"UID:{engineer.name}-{event_date.strftime('%Y%m%d')}-work@4x10rotation\\n")
        f.write(f"DTSTART;VALUE=DATE:{event_date.strftime('%Y%m%d')}\\n")
        f.write(f"DTEND;VALUE=DATE:{event_date.strftime('%Y%m%d')}\\n")
        f.write(f"SUMMARY:{schedule_type}\\n")
        f.write(f"DESCRIPTION:{'On-call duty' if is_oncall else 'Regular work day'}\\n")
        f.write(f"CATEGORIES:{'On-call,Work' if is_oncall else 'Work'}\\n")
        f.write("END:VEVENT\\n")