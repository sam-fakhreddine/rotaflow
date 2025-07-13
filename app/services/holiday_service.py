"""Holiday service following Single Responsibility Principle."""

import datetime
from typing import Set, List
from ..utils.holidays import HolidayManager


class HolidayService:
    """Service responsible for holiday detection and management."""

    def get_holiday_names_for_date(
        self, date: datetime.date, engineers: List
    ) -> Set[str]:
        """Get all unique holiday names for a date across all engineer locations."""
        holiday_names = set()

        for engineer in engineers:
            if HolidayManager.is_holiday(
                date, engineer.country, engineer.state_province
            ):
                holiday_name = self._get_holiday_name(
                    date, engineer.country, engineer.state_province
                )
                if holiday_name:
                    holiday_names.add(holiday_name)

        return holiday_names

    def engineer_has_holiday_this_week(
        self, engineer, week_start: datetime.date
    ) -> bool:
        """Check if engineer has any holidays during the work week."""
        for day_offset in range(5):  # Mon-Fri
            check_date = week_start + datetime.timedelta(days=day_offset)
            if HolidayManager.is_holiday(
                check_date, engineer.country, engineer.state_province
            ):
                return True
        return False

    def is_engineer_holiday(
        self, engineer, date: datetime.date, is_oncall: bool
    ) -> bool:
        """Check if date is a holiday for specific engineer (excluding on-call)."""
        if is_oncall:
            return False
        return HolidayManager.is_holiday(
            date, engineer.country, engineer.state_province
        )

    def _get_holiday_name(
        self, date: datetime.date, country: str, state_province: str
    ) -> str:
        """Get the name of the holiday for a specific date and location."""
        try:
            import holidays

            if country == "US":
                country_holidays = holidays.US(state=state_province, years=date.year)
            elif country == "CA":
                country_holidays = holidays.Canada(
                    state=state_province, years=date.year
                )
            else:
                return ""

            return country_holidays.get(date, "")
        except Exception:
            return ""
