#!/usr/bin/env python3
"""Calendar-specific HTTP handlers"""

# RotationManager imported in methods where needed
from urllib.parse import parse_qs, urlparse

from ..services.calendar_service import CalendarService
from .base_handler import BaseHandler


class CalendarHandler(BaseHandler):
    def __init__(self):
        super().__init__()
        self.calendar_service = CalendarService()

    def serve_calendar(self):
        """Generate and serve the iCal calendar"""
        try:
            query_params = parse_qs(urlparse(self.path).query)
            weeks = int(query_params.get("weeks", ["52"])[0])
            config = query_params.get("config", [None])[0]

            content = self.calendar_service.generate_team_calendar(weeks, config)

            self.send_response(200)
            self.send_header("Content-Type", "text/calendar; charset=utf-8")
            self.send_header(
                "Content-Disposition", 'attachment; filename="4x10-schedule.ics"'
            )
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(content)

        except Exception as e:
            self.send_error(500, f"Error generating calendar: {str(e)}")

    def serve_engineer_calendar(self):
        """Generate and serve individual engineer calendar"""
        try:
            engineer_name = (
                self.path.split("/engineer/")[1].split("?")[0].split(".ics")[0]
            )
            query_params = parse_qs(urlparse(self.path).query)
            weeks = int(query_params.get("weeks", ["52"])[0])
            config = query_params.get("config", [None])[0]

            content = self.calendar_service.generate_engineer_calendar(
                engineer_name, weeks, config
            )

            if not content:
                self.send_error(404, f"Engineer '{engineer_name}' not found")
                return

            self.send_response(200)
            self.send_header("Content-Type", "text/calendar; charset=utf-8")
            self.send_header(
                "Content-Disposition",
                f'attachment; filename="{engineer_name}-schedule.ics"',
            )
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(content)

        except Exception as e:
            self.send_error(500, f"Error generating engineer calendar: {str(e)}")

    def serve_calendar_view(self):
        """Serve HTML calendar view"""
        try:
            query_params = parse_qs(urlparse(self.path).query)
            weeks = int(query_params.get("weeks", ["52"])[0])
            config = query_params.get("config", [None])[0]
            start_date_str = query_params.get("start_date", [None])[0]

            html = self.calendar_service.generate_calendar_html(
                weeks, config, start_date_str
            )

            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())

        except Exception as e:
            self.send_error(500, f"Error generating calendar view: {str(e)}")
