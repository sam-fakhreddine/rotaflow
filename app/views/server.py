#!/usr/bin/env python3
"""
Simple HTTP server to serve iCal calendar files for webcal subscriptions
"""

import http.server
import socketserver
import os
import datetime
from urllib.parse import urlparse, parse_qs
import sys
import json
import logging

sys.path.append(".")
from ..models.rotation import RotationManager
from ..models.swap_manager import SwapManager
from ..auth.user_manager import UserManager
from ..auth.auth import SessionManager
from ..multi_tenant import TenantManager
from ..utils.holidays import HolidayManager
from ..services.coverage_service import CoverageService

# Setup JSON logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Global coverage service
coverage_service = CoverageService()


class CalendarHandler(http.server.BaseHTTPRequestHandler):
    session_manager = SessionManager()
    tenant_manager = TenantManager()

    def get_tenant_context(self):
        """Get tenant-specific configuration from host header"""
        host = self.headers.get("Host", "localhost").split(":")[0]
        tenant_id = self.tenant_manager.get_tenant_from_host(host)
        return tenant_id, self.tenant_manager.get_tenant_config(tenant_id)

    def do_GET(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path == "/calendar.ics":
            self.serve_calendar()
        elif parsed_path.path.startswith("/engineer/"):
            self.serve_engineer_calendar()
        elif parsed_path.path == "/view":
            self.serve_calendar_view()
        elif parsed_path.path == "/swaps":
            self.serve_swap_management()
        elif parsed_path.path == "/users":
            self.serve_user_management()
        elif parsed_path.path == "/login":
            self.serve_login()
        elif parsed_path.path == "/logout":
            self.handle_logout()
        elif parsed_path.path == "/health":
            self.serve_health_check()
        elif parsed_path.path == "/analytics":
            self.serve_analytics()
        elif parsed_path.path == "/":
            self.serve_index()
        else:
            self.send_error(404)

    def do_POST(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path == "/api/swap":
            self.handle_swap_request()
        elif parsed_path.path == "/api/user":
            self.handle_user_request()
        elif parsed_path.path == "/api/login":
            self.handle_login()
        else:
            self.send_error(404)

    def serve_calendar(self):
        """Generate and serve the iCal calendar"""
        try:
            # Parse query parameters
            query_params = parse_qs(urlparse(self.path).query)
            weeks = int(query_params.get("weeks", ["52"])[0])  # Default 1 year
            config = query_params.get("config", [None])[0]

            # Generate calendar
            manager = RotationManager(config)
            filename = "/tmp/schedule.ics"
            manager.export_ical(weeks, filename)

            # Serve the file
            with open(filename, "rb") as f:
                content = f.read()

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
            # Extract engineer name from path
            engineer_name = (
                self.path.split("/engineer/")[1].split("?")[0].split(".ics")[0]
            )

            # Parse query parameters
            query_params = parse_qs(urlparse(self.path).query)
            weeks = int(query_params.get("weeks", ["52"])[0])
            config = query_params.get("config", [None])[0]

            # Generate individual calendar
            manager = RotationManager(config)

            # Find engineer
            engineer = None
            for eng in manager.engineers:
                if eng.name.lower() == engineer_name.lower():
                    engineer = eng
                    break

            if not engineer:
                self.send_error(404, f"Engineer '{engineer_name}' not found")
                return

            filename = f"/tmp/{engineer_name}_schedule.ics"
            self._export_engineer_ical(manager, engineer, weeks, filename)

            # Serve the file
            with open(filename, "rb") as f:
                content = f.read()

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

    def _export_engineer_ical(self, manager, engineer, num_weeks, filename):
        """Export individual engineer schedule to iCal"""
        today = datetime.date.today()
        days_until_monday = (7 - today.weekday()) % 7
        start_date = today + datetime.timedelta(days=days_until_monday)

        with open(filename, "w") as f:
            f.write("BEGIN:VCALENDAR\n")
            f.write("VERSION:2.0\n")
            f.write("PRODID:-//4x10 Rotation Manager//EN\n")
            f.write("CALSCALE:GREGORIAN\n")
            f.write("METHOD:PUBLISH\n")
            f.write(f"X-WR-CALNAME:{engineer.name} - 4x10 Schedule\n")
            f.write(f"X-WR-CALDESC:Personal 4x10 work schedule for {engineer.name}\n")

            for week_num in range(num_weeks):
                week_start = manager.get_week_start_date(week_num, start_date)
                oncall = manager.get_oncall_engineer(week_num)
                rotation_pattern = manager.get_rotation_pattern(week_num)

                day_off = rotation_pattern[engineer.name]
                is_oncall = engineer == oncall

                # Create events for work days and day off
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
                        f.write(f"DTSTART;VALUE=DATE:{event_date.strftime('%Y%m%d')}\n")
                        f.write(f"DTEND;VALUE=DATE:{event_date.strftime('%Y%m%d')}\n")
                        f.write(f"SUMMARY:Day Off\n")
                        f.write(f"DESCRIPTION:Scheduled day off\n")
                        f.write("CATEGORIES:Day Off\n")
                        f.write("END:VEVENT\n")
                    else:
                        # Work day event
                        schedule_type = "On-call" if is_oncall else "Work"
                        f.write("BEGIN:VEVENT\n")
                        f.write(
                            f"UID:{engineer.name}-{event_date.strftime('%Y%m%d')}-work@4x10rotation\n"
                        )
                        f.write(f"DTSTART;VALUE=DATE:{event_date.strftime('%Y%m%d')}\n")
                        f.write(f"DTEND;VALUE=DATE:{event_date.strftime('%Y%m%d')}\n")
                        f.write(f"SUMMARY:{schedule_type}\n")
                        f.write(
                            f"DESCRIPTION:{'On-call duty' if is_oncall else 'Regular work day'}\n"
                        )
                        f.write(
                            f"CATEGORIES:{'On-call,Work' if is_oncall else 'Work'}\n"
                        )
                        f.write("END:VEVENT\n")

            f.write("END:VCALENDAR\n")

    def serve_swap_management(self):
        """Serve swap management interface"""
        try:
            rotation_manager = RotationManager()
            swap_manager = SwapManager()
            pending_swaps = swap_manager.get_pending_swaps()
            approved_swaps = swap_manager.get_approved_swaps()
            available_users = swap_manager.get_available_users(rotation_manager)

            # Get error message from query params if any
            query_params = parse_qs(urlparse(self.path).query)
            error_msg = query_params.get("error", [""])[0]
            success_msg = query_params.get("success", [""])[0]

            user_options = "".join(
                [f'<option value="{user}">{user}</option>' for user in available_users]
            )

            error_html = (
                f'<div style="background: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px; margin: 10px 0;">{error_msg}</div>'
                if error_msg
                else ""
            )
            success_html = (
                f'<div style="background: #d4edda; color: #155724; padding: 10px; border-radius: 5px; margin: 10px 0;">{success_msg}</div>'
                if success_msg
                else ""
            )

            html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Shift Swap Management</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        .form {{ background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .swap-list {{ margin: 20px 0; }}
        .swap-item {{ background: white; border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .pending {{ border-left: 4px solid #ffc107; }}
        .approved {{ border-left: 4px solid #28a745; }}
        .rejected {{ border-left: 4px solid #dc3545; }}
        .button {{ background: #007cba; color: white; padding: 8px 15px; border: none; border-radius: 3px; margin: 5px; cursor: pointer; }}
        .approve {{ background: #28a745; }}
        .reject {{ background: #dc3545; }}
        input, select {{ margin: 5px; padding: 8px; border: 1px solid #ddd; border-radius: 3px; }}
        .form-row {{ margin: 10px 0; }}
        .form-row label {{ display: inline-block; width: 120px; font-weight: bold; }}
        .rules {{ background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #007cba; }}
        .rules h4 {{ margin-top: 0; color: #007cba; }}
        .rules ul {{ margin: 5px 0; padding-left: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Shift Swap Management</h1>
        
        <div class="rules">
            <h4>Swap Rules:</h4>
            <ul>
                <li>Only <strong>Off</strong> and <strong>On</strong> people can swap (not on-call engineers)</li>
                <li>Swaps are for <strong>days off only</strong> - you cannot swap on-call duties</li>
                <li>Tuesday is required for everyone and cannot be swapped</li>
                <li>Approved swaps do <strong>not</strong> change the base rotation schedule</li>
                <li>One person must be scheduled off and the other on for the swap date</li>
            </ul>
        </div>
        
        {error_html}
        {success_html}
        
        <div class="form">
            <h3>Request Shift Swap</h3>
            <form method="post" action="/api/swap">
                <input type="hidden" name="action" value="request">
                <div class="form-row">
                    <label>Your Name:</label>
                    <select name="requester" required>
                        <option value="">Select your name...</option>
                        {user_options}
                    </select>
                </div>
                <div class="form-row">
                    <label>Swap With:</label>
                    <select name="target" required>
                        <option value="">Select person to swap with...</option>
                        {user_options}
                    </select>
                </div>
                <div class="form-row">
                    <label>Date:</label>
                    <input type="date" name="date" required min="{datetime.date.today().strftime('%Y-%m-%d')}">
                </div>
                <div class="form-row">
                    <label>Reason:</label>
                    <input type="text" name="reason" required placeholder="Brief reason for swap request" style="width: 300px;">
                </div>
                <div class="form-row">
                    <button type="submit" class="button">Request Swap</button>
                </div>
            </form>
        </div>
        
        <div class="swap-list">
            <h3>Pending Swaps ({len(pending_swaps)})</h3>
            {self._render_swaps(pending_swaps, show_actions=True)}
        </div>
        
        <div class="swap-list">
            <h3>Approved Swaps ({len(approved_swaps)})</h3>
            {self._render_swaps(approved_swaps, show_actions=False)}
        </div>
        
        <p><a href="/view" class="button">Back to Calendar</a></p>
    </div>
    
    <script>
        // Prevent selecting the same person for both requester and target
        document.querySelector('select[name="requester"]').addEventListener('change', function() {{
            const targetSelect = document.querySelector('select[name="target"]');
            const selectedValue = this.value;
            
            // Reset target selection if it matches requester
            if (targetSelect.value === selectedValue) {{
                targetSelect.value = '';
            }}
            
            // Disable the selected option in target dropdown
            Array.from(targetSelect.options).forEach(option => {{
                option.disabled = option.value === selectedValue && option.value !== '';
            }});
        }});
        
        document.querySelector('select[name="target"]').addEventListener('change', function() {{
            const requesterSelect = document.querySelector('select[name="requester"]');
            const selectedValue = this.value;
            
            // Reset requester selection if it matches target
            if (requesterSelect.value === selectedValue) {{
                requesterSelect.value = '';
            }}
            
            // Disable the selected option in requester dropdown
            Array.from(requesterSelect.options).forEach(option => {{
                option.disabled = option.value === selectedValue && option.value !== '';
            }});
        }});
    </script>
</body>
</html>
            """

            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())

        except Exception as e:
            self.send_error(500, f"Error loading swaps: {str(e)}")

    def _render_swaps(self, swaps, show_actions=False):
        if not swaps:
            return "<p>No swaps found.</p>"

        html = ""
        for swap in swaps:
            actions = ""
            if show_actions:
                actions = f"""
                <form method="post" action="/api/swap" style="display: inline;">
                    <input type="hidden" name="action" value="approve">
                    <input type="hidden" name="swap_id" value="{swap.id}">
                    <input type="hidden" name="approver" value="manager">
                    <button type="submit" class="button approve">Approve</button>
                </form>
                <form method="post" action="/api/swap" style="display: inline;">
                    <input type="hidden" name="action" value="reject">
                    <input type="hidden" name="swap_id" value="{swap.id}">
                    <input type="hidden" name="approver" value="manager">
                    <button type="submit" class="button reject">Reject</button>
                </form>
                """

            html += f"""
            <div class="swap-item {swap.status}">
                <strong>{swap.requester}</strong> wants to swap with <strong>{swap.target}</strong> on <strong>{swap.date}</strong><br>
                <em>Reason:</em> {swap.reason}<br>
                <small>Requested: {swap.created_at[:19]}</small>
                {actions}
            </div>
            """
        return html

    def handle_swap_request(self):
        """Handle POST requests for swap operations"""
        try:
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length).decode("utf-8")

            # Parse form data
            from urllib.parse import parse_qs

            form_data = parse_qs(post_data)

            action = form_data.get("action", [""])[0]
            rotation_manager = RotationManager()
            swap_manager = SwapManager()

            redirect_url = "/swaps"

            if action == "request":
                requester = form_data.get("requester", [""])[0]
                target = form_data.get("target", [""])[0]
                date = form_data.get("date", [""])[0]
                reason = form_data.get("reason", [""])[0]

                # Validate and create swap request
                swap_id, error = swap_manager.request_swap(
                    requester, target, date, reason, rotation_manager
                )

                if error:
                    redirect_url = f'/swaps?error={error.replace(" ", "%20")}'
                else:
                    redirect_url = (
                        f"/swaps?success=Swap%20request%20submitted%20successfully"
                    )

            elif action == "approve":
                swap_id = form_data.get("swap_id", [""])[0]
                approver = form_data.get("approver", [""])[0]
                success = swap_manager.approve_swap(swap_id, approver)

                if success:
                    redirect_url = "/swaps?success=Swap%20approved%20successfully"
                else:
                    redirect_url = "/swaps?error=Failed%20to%20approve%20swap"

            elif action == "reject":
                swap_id = form_data.get("swap_id", [""])[0]
                approver = form_data.get("approver", [""])[0]
                success = swap_manager.reject_swap(swap_id, approver)

                if success:
                    redirect_url = "/swaps?success=Swap%20rejected%20successfully"
                else:
                    redirect_url = "/swaps?error=Failed%20to%20reject%20swap"

            # Redirect back to swaps page with status
            self.send_response(302)
            self.send_header("Location", redirect_url)
            self.end_headers()

        except Exception as e:
            self.send_error(500, f"Error handling swap request: {str(e)}")

    def serve_user_management(self):
        """Serve user management interface"""
        if not self.require_auth("admin"):
            return

        try:
            user_manager = UserManager()
            rotation_manager = RotationManager()
            users = user_manager.get_users()
            engineers = [eng.name for eng in rotation_manager.engineers]

            query_params = parse_qs(urlparse(self.path).query)
            error_msg = query_params.get("error", [""])[0]
            success_msg = query_params.get("success", [""])[0]

            error_html = (
                f'<div style="background: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px; margin: 10px 0;">{error_msg}</div>'
                if error_msg
                else ""
            )
            success_html = (
                f'<div style="background: #d4edda; color: #155724; padding: 10px; border-radius: 5px; margin: 10px 0;">{success_msg}</div>'
                if success_msg
                else ""
            )

            engineer_options = "".join(
                [f'<option value="{eng}">{eng}</option>' for eng in engineers]
            )

            html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>User Management</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        .form {{ background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .user-list {{ margin: 20px 0; }}
        .user-item {{ background: white; border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .admin {{ border-left: 4px solid #dc3545; }}
        .manager {{ border-left: 4px solid #ffc107; }}
        .engineer {{ border-left: 4px solid #28a745; }}
        .button {{ background: #007cba; color: white; padding: 8px 15px; border: none; border-radius: 3px; margin: 5px; cursor: pointer; }}
        .delete {{ background: #dc3545; }}
        input, select {{ margin: 5px; padding: 8px; border: 1px solid #ddd; border-radius: 3px; }}
        .form-row {{ margin: 10px 0; }}
        .form-row label {{ display: inline-block; width: 120px; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>User Management</h1>
        
        {error_html}
        {success_html}
        
        <div class="form">
            <h3>Create New User</h3>
            <form method="post" action="/api/user">
                <input type="hidden" name="action" value="create">
                <div class="form-row">
                    <label>Username:</label>
                    <input type="text" name="username" required>
                </div>
                <div class="form-row">
                    <label>Password:</label>
                    <input type="password" name="password" required>
                </div>
                <div class="form-row">
                    <label>Role:</label>
                    <select name="role" required>
                        <option value="">Select role...</option>
                        <option value="admin">Admin</option>
                        <option value="manager">Manager</option>
                        <option value="engineer">Engineer</option>
                    </select>
                </div>
                <div class="form-row">
                    <label>Engineer Name:</label>
                    <select name="engineer_name">
                        <option value="">None (for admin/manager)</option>
                        {engineer_options}
                    </select>
                </div>
                <div class="form-row">
                    <button type="submit" class="button">Create User</button>
                </div>
            </form>
        </div>
        
        <div class="user-list">
            <h3>Current Users ({len(users)})</h3>
            {self._render_users(users)}
        </div>
        
        <p><a href="/" class="button">Back to Home</a></p>
    </div>
</body>
</html>
            """

            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())

        except Exception as e:
            self.send_error(500, f"Error loading users: {str(e)}")

    def _render_users(self, users):
        if not users:
            return "<p>No users found.</p>"

        html = ""
        for user in users:
            actions = ""
            if user.username != "admin":  # Protect admin user
                actions = f"""
                <form method="post" action="/api/user" style="display: inline;">
                    <input type="hidden" name="action" value="delete">
                    <input type="hidden" name="username" value="{user.username}">
                    <button type="submit" class="button delete" onclick="return confirm('Delete user {user.username}?')">Delete</button>
                </form>
                """

            engineer_info = (
                f" (Engineer: {user.engineer_name})" if user.engineer_name else ""
            )

            html += f"""
            <div class="user-item {user.role}">
                <strong>{user.username}</strong> - {user.role.title()}{engineer_info}<br>
                <small>Role: {user.role}</small>
                {actions}
            </div>
            """
        return html

    def handle_user_request(self):
        """Handle POST requests for user operations"""
        try:
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length).decode("utf-8")

            from urllib.parse import parse_qs

            form_data = parse_qs(post_data)

            action = form_data.get("action", [""])[0]
            user_manager = UserManager()

            redirect_url = "/users"

            if action == "create":
                username = form_data.get("username", [""])[0]
                password = form_data.get("password", [""])[0]
                role = form_data.get("role", [""])[0]
                engineer_name = form_data.get("engineer_name", [""])[0] or None

                if user_manager.create_user(username, password, role, engineer_name):
                    redirect_url = "/users?success=User%20created%20successfully"
                else:
                    redirect_url = "/users?error=Username%20already%20exists"

            elif action == "delete":
                username = form_data.get("username", [""])[0]

                if user_manager.delete_user(username):
                    redirect_url = "/users?success=User%20deleted%20successfully"
                else:
                    redirect_url = "/users?error=Failed%20to%20delete%20user"

            self.send_response(302)
            self.send_header("Location", redirect_url)
            self.end_headers()

        except Exception as e:
            self.send_error(500, f"Error handling user request: {str(e)}")

    def get_current_user(self):
        """Get current user from session cookie"""
        cookies = self.headers.get("Cookie", "")
        for cookie in cookies.split(";"):
            if cookie.strip().startswith("session="):
                session_id = cookie.split("=")[1]
                return self.session_manager.get_user_from_session(session_id)
        return None

    def require_auth(self, required_role=None):
        """Check if user is authenticated and has required role"""
        user = self.get_current_user()
        if not user:
            self.send_response(302)
            self.send_header("Location", "/login")
            self.end_headers()
            return False

        if required_role and user.role not in ["admin"] and user.role != required_role:
            self.send_error(403, "Insufficient permissions")
            return False

        return True

    def serve_login(self):
        """Serve login page"""
        query_params = parse_qs(urlparse(self.path).query)
        error_msg = query_params.get("error", [""])[0]

        error_html = (
            f'<div style="background: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px; margin: 10px 0;">{error_msg}</div>'
            if error_msg
            else ""
        )

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Login - 4x10 Schedule</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f8f9fa; }}
        .login-container {{ max-width: 400px; margin: 100px auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .form-row {{ margin: 15px 0; }}
        .form-row label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
        .form-row input {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }}
        .button {{ background: #007cba; color: white; padding: 12px 20px; border: none; border-radius: 5px; cursor: pointer; width: 100%; font-size: 16px; }}
        .button:hover {{ background: #005a8b; }}
        h1 {{ text-align: center; color: #333; }}
    </style>
</head>
<body>
    <div class="login-container">
        <h1>Login</h1>
        {error_html}
        <form method="post" action="/api/login">
            <div class="form-row">
                <label>Username:</label>
                <input type="text" name="username" required>
            </div>
            <div class="form-row">
                <label>Password:</label>
                <input type="password" name="password" required>
            </div>
            <div class="form-row">
                <button type="submit" class="button">Login</button>
            </div>
        </form>
        <p style="text-align: center; margin-top: 20px; color: #666; font-size: 14px;">
            Default: admin/admin123 or manager/manager123
        </p>
    </div>
</body>
</html>
        """

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def handle_login(self):
        """Handle login POST request"""
        try:
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length).decode("utf-8")

            from urllib.parse import parse_qs

            form_data = parse_qs(post_data)

            username = form_data.get("username", [""])[0]
            password = form_data.get("password", [""])[0]

            session_id = self.session_manager.login(username, password)

            if session_id:
                self.send_response(302)
                self.send_header("Location", "/")
                self.send_header(
                    "Set-Cookie", f"session={session_id}; Path=/; HttpOnly"
                )
                self.end_headers()
            else:
                self.send_response(302)
                self.send_header("Location", "/login?error=Invalid%20credentials")
                self.end_headers()

        except Exception as e:
            self.send_error(500, f"Login error: {str(e)}")

    def handle_logout(self):
        """Handle logout"""
        cookies = self.headers.get("Cookie", "")
        for cookie in cookies.split(";"):
            if cookie.strip().startswith("session="):
                session_id = cookie.split("=")[1]
                self.session_manager.destroy_session(session_id)

        self.send_response(302)
        self.send_header("Location", "/login")
        self.send_header(
            "Set-Cookie",
            "session=; Path=/; HttpOnly; Expires=Thu, 01 Jan 1970 00:00:00 GMT",
        )
        self.end_headers()

    def serve_calendar_view(self):
        """Serve HTML calendar view"""
        try:
            query_params = parse_qs(urlparse(self.path).query)
            weeks = int(query_params.get("weeks", ["52"])[0])
            config = query_params.get("config", [None])[0]
            start_date_str = query_params.get("start_date", [None])[0]

            # Parse custom start date if provided
            start_date = None
            if start_date_str:
                try:
                    start_date = datetime.datetime.strptime(
                        start_date_str, "%Y-%m-%d"
                    ).date()
                except ValueError:
                    pass

            manager = RotationManager(config)

            # Generate HTML calendar
            html = self._generate_calendar_html(manager, weeks, start_date)

            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())

        except Exception as e:
            self.send_error(500, f"Error generating calendar view: {str(e)}")

    def _generate_calendar_html(self, manager, weeks, custom_start_date=None):
        """Generate HTML calendar view"""
        if custom_start_date:
            start_date = custom_start_date
        else:
            today = datetime.date.today()
            days_until_monday = (7 - today.weekday()) % 7
            start_date = today + datetime.timedelta(days=days_until_monday)

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>4x10 Work Schedule</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 10px; font-size: 13px; }}
        .header {{ text-align: center; margin-bottom: 15px; }}
        .week {{ margin-bottom: 15px; border: 1px solid #ddd; border-radius: 4px; overflow: hidden; }}
        .week-header {{ background: #f8f9fa; padding: 6px; font-weight: bold; text-align: center; font-size: 14px; }}
        .days {{ display: flex; }}
        .day {{ flex: 1; border-right: 1px solid #ddd; }}
        .day:last-child {{ border-right: none; }}
        .day-header {{ background: #e9ecef; padding: 4px; text-align: center; font-weight: bold; font-size: 12px; }}
        .engineers {{ padding: 6px; min-height: 80px; }}
        .engineer {{ margin: 1px 0; padding: 2px 6px; border-radius: 3px; font-size: 12px; }}
        .working {{ background: #d4edda; color: #155724; }}
        .oncall {{ background: #fd7e14; color: white; font-weight: bold; }}
        .dayoff {{ background: #dc3545; color: white; }}
        .required {{ background: #cce5ff; color: #004085; }}
        .swapped {{ border: 2px dashed #6f42c1; background: #e2d9f3; color: #4a148c; font-weight: bold; }}
        .holiday {{ background: #9932cc; color: white; font-weight: bold; }}
        .legend {{ margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 4px; }}
        .legend-item {{ display: inline-block; margin: 3px 10px 3px 0; font-size: 12px; }}
        .legend-color {{ display: inline-block; width: 16px; height: 12px; margin-right: 4px; border-radius: 2px; vertical-align: middle; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>4x10 Work Schedule</h1>
        <p>Team: {len(manager.engineers)} engineers | Starting: {start_date.strftime('%Y-%m-%d')}</p>
        
        <form method="get" style="margin: 15px 0; padding: 15px; background: #f8f9fa; border-radius: 5px;">
            <label>Weeks: <input type="number" name="weeks" value="{weeks}" min="1" max="104" style="width: 60px; margin: 0 10px;"></label>
            <label>Config: 
                <select name="config" style="margin: 0 10px;">
                    <option value="">Default (6 engineers)</option>
                    <option value="team_5.json">5 Engineers</option>
                    <option value="team_7.json">7 Engineers</option>
                </select>
            </label>
            <label>Start Date: <input type="date" name="start_date" style="margin: 0 10px;"></label>
            <button type="submit" style="background: #007cba; color: white; padding: 5px 15px; border: none; border-radius: 3px; margin: 0 5px;">Update</button>
        </form>
    </div>
    
    <div class="legend">
        <div class="legend-item"><span class="legend-color working"></span>Regular Work (4x10)</div>
        <div class="legend-item"><span class="legend-color oncall" style="background: #fd7e14;"></span>On-call (5x8)</div>
        <div class="legend-item"><span class="legend-color required"></span>Required Day (Tuesday)</div>
        <div class="legend-item"><span class="legend-color dayoff" style="background: #dc3545;"></span>Day Off</div>
        <div class="legend-item"><span class="legend-color holiday" style="background: #9932cc;"></span>Stat Holiday</div>
        <div class="legend-item"><span class="legend-color" style="background: #e2d9f3; border: 2px dashed #6f42c1;"></span>Swapped Schedule</div>
    </div>
"""

        for week_num in range(weeks):
            week_start = manager.get_week_start_date(week_num, start_date)
            oncall = manager.get_oncall_engineer(week_num)
            rotation_pattern = manager.get_rotation_pattern(week_num)
            
            # Calculate coverage adjustments for this week
            coverage_adjustments = coverage_service.calculate_coverage_adjustments(manager, week_num, week_start)

            html += f"""
    <div class="week">
        <div class="week-header">Week {week_num + 1} - {week_start.strftime('%B %d, %Y')} ({oncall.letter}* on-call)</div>
        <div class="days">
"""

            for day_name in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
                day_date = week_start + datetime.timedelta(
                    days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"].index(
                        day_name
                    )
                )

                # Get holiday names for this date (check all locations)
                holiday_names = set()
                for engineer in manager.engineers:
                    if HolidayManager.is_holiday(day_date, engineer.country, engineer.state_province):
                        try:
                            import holidays
                            if engineer.country == "US":
                                country_holidays = holidays.US(state=engineer.state_province, years=day_date.year)
                            elif engineer.country == "CA":
                                country_holidays = holidays.Canada(state=engineer.state_province, years=day_date.year)
                            else:
                                continue
                            if day_date in country_holidays:
                                holiday_names.add(country_holidays[day_date])
                        except:
                            pass

                holiday_text = ", ".join(sorted(holiday_names)) if holiday_names else ""
                holiday_display = f"<br><small style='color: #9932cc; font-weight: bold;'>{holiday_text}</small>" if holiday_names else ""

                html += f"""
            <div class="day">
                <div class="day-header">{day_name}<br><small>{day_date.strftime('%m/%d')}</small>{holiday_display}</div>
                <div class="engineers">
"""

                # Check for approved swaps on this specific date
                day_date = week_start + datetime.timedelta(
                    days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"].index(
                        day_name
                    )
                )
                swap_manager = SwapManager()
                swaps_for_date = swap_manager.get_swaps_for_date(day_date)

                # Sort engineers to show on-call first
                engineers_sorted = sorted(
                    manager.engineers, key=lambda e: (e != oncall, e.name)
                )


                
                # Check if engineer has any holidays this week
                engineer_has_holiday_this_week = {}
                for engineer in engineers_sorted:
                    has_holiday = False
                    for day_offset in range(5):  # Mon-Fri
                        check_date = week_start + datetime.timedelta(days=day_offset)
                        if HolidayManager.is_holiday(check_date, engineer.country, engineer.state_province):
                            has_holiday = True
                            break
                    engineer_has_holiday_this_week[engineer.name] = has_holiday

                for engineer in engineers_sorted:
                    # Get actual day off (may be adjusted for coverage)
                    original_day_off = rotation_pattern[engineer.name]
                    actual_day_off = coverage_service.get_engineer_day_off(engineer.name, week_num, original_day_off)
                    is_coverage_adjusted = coverage_service.is_coverage_adjustment(engineer.name, week_num)
                    
                    is_oncall = engineer == oncall
                    has_holiday_this_week = engineer_has_holiday_this_week[engineer.name]

                    # Check if this engineer is affected by a swap on this date
                    swap_status = ""
                    original_status = ""
                    for swap in swaps_for_date:
                        if (
                            swap.requester == engineer.name
                            or swap.target == engineer.name
                        ):
                            # This engineer is involved in a swap
                            if day_name == day_off:
                                # Engineer was originally off but is now working due to swap
                                if swap.requester == engineer.name:
                                    swap_status = " (Swapped - Working)"
                                    original_status = "Work"
                                else:
                                    swap_status = " (Swapped - Working)"
                                    original_status = "Work"
                            else:
                                # Engineer was originally working but is now off due to swap
                                if (
                                    swap.target == engineer.name
                                    and swap.requester != engineer.name
                                ):
                                    # Target gets the day off
                                    requester_day_off = rotation_pattern[swap.requester]
                                    if requester_day_off == day_name:
                                        swap_status = " (Swapped - Off)"
                                        original_status = "Day Off"
                                elif swap.requester == engineer.name:
                                    # Requester gets to work (giving up their day off)
                                    target_day_off = rotation_pattern[swap.target]
                                    if target_day_off == day_name:
                                        swap_status = " (Swapped - Off)"
                                        original_status = "Day Off"
                            break

                    # Check if this is a holiday for this specific engineer (but not if on-call)
                    is_engineer_holiday = (not is_oncall and 
                                         HolidayManager.is_holiday(day_date, engineer.country, engineer.state_province))
                    
                    # Log holiday check
                    logger.info(json.dumps({
                        "event": "holiday_check",
                        "engineer": engineer.name,
                        "date": day_date.isoformat(),
                        "country": engineer.country,
                        "state_province": engineer.state_province,
                        "is_holiday": is_engineer_holiday,
                        "has_holiday_this_week": has_holiday_this_week
                    }))
                    
                    if is_engineer_holiday:
                        css_class = "holiday"
                        status = "Stat Holiday"
                    elif day_name == "Tuesday":
                        # Tuesday is required for everyone
                        css_class = "oncall" if is_oncall else "required"
                        status = "On-call" if is_oncall else "Required"
                    elif swap_status:
                        # Show swapped status
                        if "Off" in swap_status:
                            css_class = "dayoff"
                            status = f"Day Off{swap_status}"
                        else:
                            css_class = "oncall" if is_oncall else "working"
                            status = (
                                f"{'On-call' if is_oncall else 'Work'}{swap_status}"
                            )
                    elif day_name == actual_day_off and not is_oncall and not has_holiday_this_week:
                        # Day off (possibly moved for coverage)
                        css_class = "dayoff"
                        if is_coverage_adjusted and day_name != original_day_off:
                            status = "Day Off (Moved)"
                        else:
                            status = "Day Off"
                    else:
                        css_class = "oncall" if is_oncall else "working"
                        status = "On-call" if is_oncall else "Work"

                    html += f'<div class="engineer {css_class}">{engineer.name} ({engineer.letter}) - {status}</div>'
                    
                    # Log final status
                    logger.info(json.dumps({
                        "event": "engineer_status",
                        "engineer": engineer.name,
                        "date": day_date.isoformat(),
                        "css_class": css_class,
                        "status": status,
                        "coverage_adjusted": is_coverage_adjusted,
                        "original_day_off": original_day_off,
                        "actual_day_off": actual_day_off
                    }))

                html += """
                </div>
            </div>
"""

            html += """
        </div>
    </div>
"""

        html += """
    <div style="text-align: center; margin-top: 30px;">
        <a href="/calendar.ics{self._build_query_string(weeks, config, start_date)}" style="background: #007cba; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 5px;">Download iCal</a>
        <a href="/" style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 5px;">Subscription Info</a>
    </div>
    
    <script>
        // Set form values from current URL
        const params = new URLSearchParams(window.location.search);
        if (params.get('config')) {{
            document.querySelector('select[name="config"]').value = params.get('config');
        }}
        if (params.get('start_date')) {{
            document.querySelector('input[name="start_date"]').value = params.get('start_date');
        }}
    </script>
</body>
</html>
"""
        return html

    def _build_query_string(self, weeks, config, start_date):
        """Build query string for links"""
        params = []
        if weeks != 52:
            params.append(f"weeks={weeks}")
        if config:
            params.append(f"config={config}")
        if start_date:
            params.append(f'start_date={start_date.strftime("%Y-%m-%d")}')
        return "?" + "&".join(params) if params else ""

    def serve_health_check(self):
        """Simple health check endpoint for Docker"""
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status":"healthy"}')

    def serve_analytics(self):
        """Serve analytics dashboard"""
        try:
            from ..views.analytics import ScheduleAnalytics, generate_analytics_html

            rotation_manager = RotationManager()
            swap_manager = SwapManager()

            analytics = ScheduleAnalytics(rotation_manager, swap_manager)
            data = analytics.generate_dashboard_data(weeks=12)
            html = generate_analytics_html(data)

            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())

        except Exception as e:
            self.send_error(500, f"Analytics error: {str(e)}")

    def serve_index(self):
        """Serve a simple index page with subscription instructions"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>4x10 Work Schedule Calendar</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; }
        .url { background: #f5f5f5; padding: 10px; border-radius: 5px; font-family: monospace; word-break: break-all; }
        .button { background: #007cba; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 5px; display: inline-block; }
        .green { background: #28a745; }
    </style>
</head>
<body>
    <div class="container">
        <h1>4x10 Work Schedule Calendar</h1>
        <p>Subscribe to your team's 4-day work week rotation schedule.</p>
        
        <p><a href="/view" class="button green">View Schedule</a> <a href="/swaps" class="button" style="background: #ffc107; color: black;">Manage Swaps</a> <a href="/analytics" class="button" style="background: #17a2b8; color: white;">📊 Analytics</a> <a href="/users" class="button" style="background: #6c757d; color: white;">Manage Users</a> <a href="/logout" class="button" style="background: #dc3545;">Logout</a> <a href="/calendar.ics" class="button">Download Calendar</a></p>
        
        <h2>Individual Engineer Calendars:</h2>
        <p>Each engineer gets their personal calendar with only their schedule:</p>
        <ul>
            <li><strong>Alex:</strong> <div class="url">webcal://localhost:8433/engineer/alex.ics</div></li>
            <li><strong>Blake:</strong> <div class="url">webcal://localhost:8433/engineer/blake.ics</div></li>
            <li><strong>Casey:</strong> <div class="url">webcal://localhost:8433/engineer/casey.ics</div></li>
            <li><strong>Dana:</strong> <div class="url">webcal://localhost:8433/engineer/dana.ics</div></li>
            <li><strong>Evan:</strong> <div class="url">webcal://localhost:8433/engineer/evan.ics</div></li>
            <li><strong>Fiona:</strong> <div class="url">webcal://localhost:8433/engineer/fiona.ics</div></li>
        </ul>
        
        <h2>Team Calendar Subscription URLs:</h2>
        <p><strong>Full Team (52 weeks):</strong></p>
        <div class="url">webcal://localhost:8433/calendar.ics</div>
        
        <p><strong>Custom weeks:</strong></p>
        <div class="url">webcal://localhost:8433/calendar.ics?weeks=24</div>
        
        <p><strong>Custom config:</strong></p>
        <div class="url">webcal://localhost:8433/calendar.ics?config=team_5.json</div>
        
        <h2>How to Subscribe:</h2>
        <ul>
            <li><strong>iPhone/iPad:</strong> Settings → Calendar → Accounts → Add Account → Other → Add Subscribed Calendar</li>
            <li><strong>Google Calendar:</strong> Settings → Add calendar → From URL</li>
            <li><strong>Outlook:</strong> File → Account Settings → Internet Calendars → New</li>
            <li><strong>Apple Calendar:</strong> File → New Calendar Subscription</li>
        </ul>
    </div>
</body>
</html>
        """

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())


def main():
    PORT = int(os.environ.get("PORT", 6247))

    with socketserver.TCPServer(("", PORT), CalendarHandler) as httpd:
        print(f"Serving 4x10 calendar at http://localhost:{PORT}")
        print(f"Calendar view: http://localhost:{PORT}/view")
        print(f"Calendar subscription URL: webcal://localhost:{PORT}/calendar.ics")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
