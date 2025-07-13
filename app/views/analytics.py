#!/usr/bin/env python3
"""
Analytics dashboard for schedule management
"""

import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(__file__))


class ScheduleAnalytics:
    def __init__(self, rotation_manager, swap_manager):
        self.rotation_manager = rotation_manager
        self.swap_manager = swap_manager

    def generate_dashboard_data(self, weeks=12):
        """Generate analytics data for dashboard"""

        # Basic metrics
        total_engineers = len(self.rotation_manager.engineers)
        total_swaps = len(self.swap_manager.get_all_swaps())
        pending_swaps = len(self.swap_manager.get_pending_swaps())

        # Days off distribution
        days_off_stats = self._analyze_days_off_distribution(weeks)

        # On-call distribution
        oncall_stats = self._analyze_oncall_distribution(weeks)

        # Swap statistics
        swap_stats = self._analyze_swap_patterns()

        # Holiday impact
        holiday_stats = self._analyze_holiday_impact(weeks)

        return {
            "summary": {
                "total_engineers": total_engineers,
                "total_swaps": total_swaps,
                "pending_swaps": pending_swaps,
                "rotation_cycle": len(self.rotation_manager.rotation_patterns),
            },
            "days_off_distribution": days_off_stats,
            "oncall_distribution": oncall_stats,
            "swap_patterns": swap_stats,
            "holiday_impact": holiday_stats,
            "generated_at": datetime.now().isoformat(),
        }

    def _analyze_days_off_distribution(self, weeks):
        """Analyze fairness of days off distribution"""
        engineer_stats = defaultdict(
            lambda: {
                "Monday": 0,
                "Wednesday": 0,
                "Thursday": 0,
                "Friday": 0,
                "total": 0,
            }
        )

        for week in range(weeks):
            pattern = self.rotation_manager.get_rotation_pattern(week)
            oncall = self.rotation_manager.get_oncall_engineer(week)

            for engineer in self.rotation_manager.engineers:
                if engineer != oncall:  # On-call engineers don't get days off
                    day_off = pattern[engineer.name]
                    engineer_stats[engineer.name][day_off] += 1
                    engineer_stats[engineer.name]["total"] += 1

        return dict(engineer_stats)

    def _analyze_oncall_distribution(self, weeks):
        """Analyze on-call duty distribution"""
        oncall_counts = defaultdict(int)

        for week in range(weeks):
            oncall = self.rotation_manager.get_oncall_engineer(week)
            oncall_counts[oncall.name] += 1

        return dict(oncall_counts)

    def _analyze_swap_patterns(self):
        """Analyze swap request patterns"""
        all_swaps = self.swap_manager.get_all_swaps()

        # Swap counts by engineer
        requester_counts = defaultdict(int)
        target_counts = defaultdict(int)

        # Swap success rates
        approved = 0
        rejected = 0
        pending = 0

        for swap in all_swaps:
            requester_counts[swap.requester] += 1
            target_counts[swap.target] += 1

            if swap.status == "approved":
                approved += 1
            elif swap.status == "rejected":
                rejected += 1
            else:
                pending += 1

        return {
            "requester_counts": dict(requester_counts),
            "target_counts": dict(target_counts),
            "approval_rate": approved / max(1, approved + rejected) * 100,
            "status_breakdown": {
                "approved": approved,
                "rejected": rejected,
                "pending": pending,
            },
        }

    def _analyze_holiday_impact(self, weeks):
        """Analyze impact of holidays on scheduling"""
        from ..utils.holidays import HolidayManager

        # Get date range
        start_date = self.rotation_manager.get_week_start_date(0)
        end_date = start_date + timedelta(weeks=weeks)

        # Count holidays by location
        location_holidays = defaultdict(int)

        for engineer in self.rotation_manager.engineers:
            holidays = HolidayManager.get_holidays_for_date_range(
                start_date, end_date, engineer.country, engineer.state_province
            )
            location_key = f"{engineer.country}-{engineer.state_province}"
            location_holidays[location_key] = len(holidays)

        return dict(location_holidays)


def generate_analytics_html(analytics_data):
    """Generate HTML dashboard"""
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Schedule Analytics Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .card {{ background: white; padding: 20px; margin: 15px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
        .metric {{ text-align: center; padding: 15px; background: #007cba; color: white; border-radius: 5px; }}
        .metric h3 {{ margin: 0; font-size: 2em; }}
        .metric p {{ margin: 5px 0 0 0; }}
        .chart-container {{ width: 100%; height: 400px; margin: 20px 0; }}
        canvas {{ max-height: 400px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Schedule Analytics Dashboard</h1>
        
        <div class="card">
            <h2>Summary Metrics</h2>
            <div class="metrics">
                <div class="metric">
                    <h3>{analytics_data['summary']['total_engineers']}</h3>
                    <p>Engineers</p>
                </div>
                <div class="metric">
                    <h3>{analytics_data['summary']['total_swaps']}</h3>
                    <p>Total Swaps</p>
                </div>
                <div class="metric">
                    <h3>{analytics_data['summary']['pending_swaps']}</h3>
                    <p>Pending Swaps</p>
                </div>
                <div class="metric">
                    <h3>{analytics_data['summary']['rotation_cycle']}</h3>
                    <p>Week Cycle</p>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>Days Off Distribution</h2>
            <div class="chart-container">
                <canvas id="daysOffChart"></canvas>
            </div>
        </div>
        
        <div class="card">
            <h2>On-Call Distribution</h2>
            <div class="chart-container">
                <canvas id="oncallChart"></canvas>
            </div>
        </div>
        
        <div class="card">
            <h2>Swap Patterns</h2>
            <div class="chart-container">
                <canvas id="swapChart"></canvas>
            </div>
            <p>Approval Rate: {analytics_data['swap_patterns']['approval_rate']:.1f}%</p>
        </div>
        
        <p><a href="/view" style="background: #007cba; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Back to Calendar</a></p>
    </div>
    
    <script>
        // Days Off Chart
        const daysOffData = {json.dumps(analytics_data['days_off_distribution'])};
        const engineers = Object.keys(daysOffData);
        const days = ['Monday', 'Wednesday', 'Thursday', 'Friday'];
        
        new Chart(document.getElementById('daysOffChart'), {{
            type: 'bar',
            data: {{
                labels: engineers,
                datasets: days.map((day, i) => ({{
                    label: day,
                    data: engineers.map(eng => daysOffData[eng][day]),
                    backgroundColor: ['#ff6384', '#36a2eb', '#ffce56', '#4bc0c0'][i]
                }}))
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{ y: {{ beginAtZero: true }} }}
            }}
        }});
        
        // On-Call Chart
        const oncallData = {json.dumps(analytics_data['oncall_distribution'])};
        new Chart(document.getElementById('oncallChart'), {{
            type: 'doughnut',
            data: {{
                labels: Object.keys(oncallData),
                datasets: [{{
                    data: Object.values(oncallData),
                    backgroundColor: ['#ff6384', '#36a2eb', '#ffce56', '#4bc0c0', '#9966ff', '#ff9f40']
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false
            }}
        }});
        
        // Swap Chart
        const swapData = {json.dumps(analytics_data['swap_patterns']['status_breakdown'])};
        new Chart(document.getElementById('swapChart'), {{
            type: 'pie',
            data: {{
                labels: Object.keys(swapData),
                datasets: [{{
                    data: Object.values(swapData),
                    backgroundColor: ['#28a745', '#dc3545', '#ffc107']
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false
            }}
        }});
    </script>
</body>
</html>
    """
