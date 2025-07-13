#!/usr/bin/env python3
"""Calendar HTML templates"""

import datetime
import json
import logging

logger = logging.getLogger(__name__)


class CalendarTemplates:
    def render_calendar_view(self, data):
        """Render calendar HTML view"""
        manager = data["manager"]
        weeks = data["weeks"]
        start_date = data["start_date"]
        coverage_service = data["coverage_service"]
        swap_manager = data["swap_manager"]
        holiday_manager = data["holiday_manager"]

        html = self._render_header(manager, weeks, start_date)
        html += self._render_legend()

        for week_num in range(weeks):
            html += self._render_week(
                manager,
                week_num,
                start_date,
                coverage_service,
                swap_manager,
                holiday_manager,
            )

        html += self._render_footer(weeks, start_date)
        return html

    def _render_header(self, manager, weeks, start_date):
        """Render page header"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>4x10 Work Schedule</title>
    <style>
        {self._get_css()}
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
"""

    def _render_legend(self):
        """Render color legend"""
        return """
    <div class="legend">
        <div class="legend-item"><span class="legend-color working"></span>Regular Work (4x10)</div>
        <div class="legend-item"><span class="legend-color oncall" style="background: #fd7e14;"></span>On-call (5x8)</div>
        <div class="legend-item"><span class="legend-color required"></span>Required Day (Tuesday)</div>
        <div class="legend-item"><span class="legend-color dayoff" style="background: #dc3545;"></span>Day Off</div>
        <div class="legend-item"><span class="legend-color holiday" style="background: #9932cc;"></span>Stat Holiday</div>
        <div class="legend-item"><span class="legend-color" style="background: #e2d9f3; border: 2px dashed #6f42c1;"></span>Swapped Schedule</div>
    </div>
"""

    def _render_week(
        self,
        manager,
        week_num,
        start_date,
        coverage_service,
        swap_manager,
        holiday_manager,
    ):
        """Render a single week"""
        week_start = manager.get_week_start_date(week_num, start_date)
        oncall = manager.get_oncall_engineer(week_num)
        rotation_pattern = manager.get_rotation_pattern(week_num)
        coverage_adjustments = coverage_service.calculate_coverage_adjustments(
            manager, week_num, week_start
        )

        html = f"""
    <div class="week">
        <div class="week-header">Week {week_num + 1} - {week_start.strftime('%B %d, %Y')} ({oncall.letter}* on-call)</div>
        <div class="days">
"""

        for day_name in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            html += self._render_day(
                day_name,
                week_start,
                manager,
                oncall,
                rotation_pattern,
                coverage_service,
                swap_manager,
                holiday_manager,
                week_num,
            )

        html += """
        </div>
    </div>
"""
        return html

    def _render_day(
        self,
        day_name,
        week_start,
        manager,
        oncall,
        rotation_pattern,
        coverage_service,
        swap_manager,
        holiday_manager,
        week_num,
    ):
        """Render a single day"""
        day_offset = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"].index(
            day_name
        )
        day_date = week_start + datetime.timedelta(days=day_offset)

        # Get holiday info
        holiday_names = self._get_holiday_names(
            day_date, manager.engineers, holiday_manager
        )
        holiday_display = (
            f"<br><small style='color: #9932cc; font-weight: bold;'>{', '.join(sorted(holiday_names))}</small>"
            if holiday_names
            else ""
        )

        html = f"""
            <div class="day">
                <div class="day-header">{day_name}<br><small>{day_date.strftime('%m/%d')}</small>{holiday_display}</div>
                <div class="engineers">
"""

        # Get swaps for this date
        swaps_for_date = swap_manager.get_swaps_for_date(day_date)

        # Sort engineers (on-call first)
        engineers_sorted = sorted(
            manager.engineers, key=lambda e: (e != oncall, e.name)
        )

        for engineer in engineers_sorted:
            html += self._render_engineer_status(
                engineer,
                day_name,
                day_date,
                oncall,
                rotation_pattern,
                coverage_service,
                swaps_for_date,
                holiday_manager,
                week_num,
            )

        html += """
                </div>
            </div>
"""
        return html

    def _render_engineer_status(
        self,
        engineer,
        day_name,
        day_date,
        oncall,
        rotation_pattern,
        coverage_service,
        swaps_for_date,
        holiday_manager,
        week_num,
    ):
        """Render individual engineer status"""
        original_day_off = rotation_pattern[engineer.name]
        actual_day_off = coverage_service.get_engineer_day_off(
            engineer.name, week_num, original_day_off
        )
        is_coverage_adjusted = coverage_service.is_coverage_adjustment(
            engineer.name, week_num
        )
        is_oncall = engineer == oncall

        # Check for holidays and swaps
        is_engineer_holiday = not is_oncall and holiday_manager.is_holiday(
            day_date, engineer.country, engineer.state_province
        )

        swap_status = self._get_swap_status(
            engineer, day_name, swaps_for_date, rotation_pattern
        )

        # Determine CSS class and status text
        css_class, status = self._determine_status(
            day_name,
            actual_day_off,
            original_day_off,
            is_oncall,
            is_engineer_holiday,
            is_coverage_adjusted,
            swap_status,
        )

        # Log status for debugging
        logger.info(
            json.dumps(
                {
                    "event": "engineer_status",
                    "engineer": engineer.name,
                    "date": day_date.isoformat(),
                    "css_class": css_class,
                    "status": status,
                    "coverage_adjusted": is_coverage_adjusted,
                    "original_day_off": original_day_off,
                    "actual_day_off": actual_day_off,
                }
            )
        )

        return f'<div class="engineer {css_class}">{engineer.name} ({engineer.letter}) - {status}</div>'

    def _get_holiday_names(self, day_date, engineers, holiday_manager):
        """Get holiday names for a date"""
        holiday_names = set()
        for engineer in engineers:
            if holiday_manager.is_holiday(
                day_date, engineer.country, engineer.state_province
            ):
                try:
                    import holidays

                    if engineer.country == "US":
                        country_holidays = holidays.US(
                            state=engineer.state_province, years=day_date.year
                        )
                    elif engineer.country == "CA":
                        country_holidays = holidays.Canada(
                            state=engineer.state_province, years=day_date.year
                        )
                    else:
                        continue
                    if day_date in country_holidays:
                        holiday_names.add(country_holidays[day_date])
                except:
                    pass
        return holiday_names

    def _get_swap_status(self, engineer, day_name, swaps_for_date, rotation_pattern):
        """Get swap status for engineer on specific day"""
        for swap in swaps_for_date:
            if swap.requester == engineer.name or swap.target == engineer.name:
                day_off = rotation_pattern[engineer.name]
                if day_name == day_off:
                    return " (Swapped - Working)"
                else:
                    # Check if this engineer gets the day off due to swap
                    if swap.target == engineer.name and swap.requester != engineer.name:
                        requester_day_off = rotation_pattern[swap.requester]
                        if requester_day_off == day_name:
                            return " (Swapped - Off)"
                    elif swap.requester == engineer.name:
                        target_day_off = rotation_pattern[swap.target]
                        if target_day_off == day_name:
                            return " (Swapped - Off)"
        return ""

    def _determine_status(
        self,
        day_name,
        actual_day_off,
        original_day_off,
        is_oncall,
        is_engineer_holiday,
        is_coverage_adjusted,
        swap_status,
    ):
        """Determine CSS class and status text"""
        if is_engineer_holiday:
            return "holiday", "Stat Holiday"
        elif day_name == "Tuesday":
            css_class = "oncall" if is_oncall else "required"
            status = "On-call" if is_oncall else "Required"
            return css_class, status
        elif swap_status:
            if "Off" in swap_status:
                return "dayoff", f"Day Off{swap_status}"
            else:
                css_class = "oncall" if is_oncall else "working"
                status = f"{'On-call' if is_oncall else 'Work'}{swap_status}"
                return css_class, status
        elif day_name == actual_day_off and not is_oncall:
            css_class = "dayoff"
            if is_coverage_adjusted and day_name != original_day_off:
                status = "Day Off (Moved)"
            else:
                status = "Day Off"
            return css_class, status
        else:
            css_class = "oncall" if is_oncall else "working"
            status = "On-call" if is_oncall else "Work"
            return css_class, status

    def _render_footer(self, weeks, start_date):
        """Render page footer"""
        return f"""
    <div style="text-align: center; margin-top: 30px;">
        <a href="/calendar.ics{self._build_query_string(weeks, None, start_date)}" style="background: #007cba; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 5px;">Download iCal</a>
        <a href="/" style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 5px;">Subscription Info</a>
    </div>

    <script>
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

    def _get_css(self):
        """Get CSS styles"""
        return """
        body { font-family: Arial, sans-serif; margin: 10px; font-size: 13px; }
        .header { text-align: center; margin-bottom: 15px; }
        .week { margin-bottom: 15px; border: 1px solid #ddd; border-radius: 4px; overflow: hidden; }
        .week-header { background: #f8f9fa; padding: 6px; font-weight: bold; text-align: center; font-size: 14px; }
        .days { display: flex; }
        .day { flex: 1; border-right: 1px solid #ddd; }
        .day:last-child { border-right: none; }
        .day-header { background: #e9ecef; padding: 4px; text-align: center; font-weight: bold; font-size: 12px; }
        .engineers { padding: 6px; min-height: 80px; }
        .engineer { margin: 1px 0; padding: 2px 6px; border-radius: 3px; font-size: 12px; }
        .working { background: #d4edda; color: #155724; }
        .oncall { background: #fd7e14; color: white; font-weight: bold; }
        .dayoff { background: #dc3545; color: white; }
        .required { background: #cce5ff; color: #004085; }
        .swapped { border: 2px dashed #6f42c1; background: #e2d9f3; color: #4a148c; font-weight: bold; }
        .holiday { background: #9932cc; color: white; font-weight: bold; }
        .legend { margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 4px; }
        .legend-item { display: inline-block; margin: 3px 10px 3px 0; font-size: 12px; }
        .legend-color { display: inline-block; width: 16px; height: 12px; margin-right: 4px; border-radius: 2px; vertical-align: middle; }
        """
