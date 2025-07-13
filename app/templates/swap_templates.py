#!/usr/bin/env python3
"""Swap management HTML templates"""

import datetime
import os

from .renderers.template_renderer import TemplateRenderer


class SwapTemplates:
    def __init__(self):
        template_dir = os.path.join(os.path.dirname(__file__), "html")
        self.renderer = TemplateRenderer(template_dir)

    def render_swap_page(self, data, error_msg="", success_msg=""):
        """Render swap management page"""
        pending_swaps = data["pending_swaps"]
        approved_swaps = data["approved_swaps"]
        available_users = data["available_users"]

        user_options = "".join(
            [f'<option value="{user}">{user}</option>' for user in available_users]
        )

        messages = ""
        if error_msg:
            messages += f'<div class="error">{error_msg}</div>'
        if success_msg:
            messages += f'<div class="success">{success_msg}</div>'

        return self.renderer.render(
            "swaps.html",
            messages=messages,
            user_options=user_options,
            today=datetime.date.today().strftime("%Y-%m-%d"),
            pending_count=len(pending_swaps),
            approved_count=len(approved_swaps),
            pending_swaps=self._render_swaps(pending_swaps, show_actions=True),
            approved_swaps=self._render_swaps(approved_swaps, show_actions=False),
        )

    def _render_rules(self):
        """Render swap rules section"""
        return """
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
"""

    def _render_request_form(self, user_options):
        """Render swap request form"""
        return f"""
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
"""

    def _render_swaps(self, swaps, show_actions=False):
        """Render list of swaps"""
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

    def _render_message(self, message, msg_type):
        """Render error or success message"""
        if msg_type == "error":
            bg_color = "#f8d7da"
            text_color = "#721c24"
        else:  # success
            bg_color = "#d4edda"
            text_color = "#155724"

        return f'<div style="background: {bg_color}; color: {text_color}; padding: 10px; border-radius: 5px; margin: 10px 0;">{message}</div>'

    def _render_javascript(self):
        """Render JavaScript for form validation"""
        return """
    <script>
        // Prevent selecting the same person for both requester and target
        document.querySelector('select[name="requester"]').addEventListener('change', function() {
            const targetSelect = document.querySelector('select[name="target"]');
            const selectedValue = this.value;

            if (targetSelect.value === selectedValue) {
                targetSelect.value = '';
            }

            Array.from(targetSelect.options).forEach(option => {
                option.disabled = option.value === selectedValue && option.value !== '';
            });
        });

        document.querySelector('select[name="target"]').addEventListener('change', function() {
            const requesterSelect = document.querySelector('select[name="requester"]');
            const selectedValue = this.value;

            if (requesterSelect.value === selectedValue) {
                requesterSelect.value = '';
            }

            Array.from(requesterSelect.options).forEach(option => {
                option.disabled = option.value === selectedValue && option.value !== '';
            });
        });
    </script>
"""

    def _get_css(self):
        """Get CSS styles"""
        return """
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 1000px; margin: 0 auto; }
        .form { background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }
        .swap-list { margin: 20px 0; }
        .swap-item { background: white; border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .pending { border-left: 4px solid #ffc107; }
        .approved { border-left: 4px solid #28a745; }
        .rejected { border-left: 4px solid #dc3545; }
        .button { background: #007cba; color: white; padding: 8px 15px; border: none; border-radius: 3px; margin: 5px; cursor: pointer; }
        .approve { background: #28a745; }
        .reject { background: #dc3545; }
        input, select { margin: 5px; padding: 8px; border: 1px solid #ddd; border-radius: 3px; }
        .form-row { margin: 10px 0; }
        .form-row label { display: inline-block; width: 120px; font-weight: bold; }
        .rules { background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #007cba; }
        .rules h4 { margin-top: 0; color: #007cba; }
        .rules ul { margin: 5px 0; padding-left: 20px; }
        """
