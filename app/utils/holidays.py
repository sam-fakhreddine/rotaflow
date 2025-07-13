#!/usr/bin/env python3
"""
Holiday detection based on engineer location
"""

import datetime
import logging
from typing import List, Set, Optional

try:
    import holidays

    HAS_HOLIDAYS = True
except ImportError:
    HAS_HOLIDAYS = False

logger = logging.getLogger(__name__)


class HolidayManager:
    # Cache for holiday objects to avoid repeated instantiation
    _holiday_cache = {}

    @classmethod
    def _get_holiday_object(
        cls, country: str, state_province: Optional[str], years: range
    ):
        """Get holiday object for a country/state combination with caching"""
        cache_key = (country.upper(), state_province, tuple(years))

        if cache_key in cls._holiday_cache:
            return cls._holiday_cache[cache_key]

        try:
            # Convert country code to uppercase for consistency
            country_upper = country.upper()

            # Get the holiday class for the country
            if hasattr(holidays, country_upper):
                holiday_class = getattr(holidays, country_upper)

                # Create holiday object with or without state/province
                if state_province:
                    # Try with state/province parameter
                    try:
                        holiday_obj = holiday_class(state=state_province, years=years)
                    except (TypeError, ValueError):
                        # Some countries don't support state/province, fallback to country only
                        logger.warning(
                            f"State/province '{state_province}' not supported for {country_upper}, "
                            f"using country-level holidays only"
                        )
                        holiday_obj = holiday_class(years=years)
                else:
                    holiday_obj = holiday_class(years=years)

                cls._holiday_cache[cache_key] = holiday_obj
                return holiday_obj
            else:
                logger.warning(
                    f"Country '{country_upper}' not supported by holidays library"
                )
                return None

        except Exception as e:
            logger.error(f"Error creating holiday object for {country_upper}: {e}")
            return None

    @classmethod
    def get_holidays_for_date_range(
        cls,
        start_date: datetime.date,
        end_date: datetime.date,
        country: str,
        state_province: Optional[str] = None,
    ) -> Set[datetime.date]:
        """Get all holidays in date range for location"""
        if not HAS_HOLIDAYS:
            logger.warning("holidays library not available")
            return set()

        if not country:
            logger.warning("No country specified")
            return set()

        holiday_dates = set()

        try:
            # Get years covered by the date range
            years = range(start_date.year, end_date.year + 1)

            # Get holiday object for this country/state combination
            country_holidays = cls._get_holiday_object(country, state_province, years)

            if country_holidays is None:
                return set()

            # Filter to date range
            for date in country_holidays:
                if start_date <= date <= end_date:
                    holiday_dates.add(date)

        except Exception as e:
            # Fallback to empty set if holidays library fails
            logger.error(f"Error getting holidays for {country}/{state_province}: {e}")

        return holiday_dates

    @classmethod
    def is_holiday(
        cls, date: datetime.date, country: str, state_province: Optional[str] = None
    ) -> bool:
        """Check if specific date is a holiday"""
        holiday_dates = cls.get_holidays_for_date_range(
            date, date, country, state_province
        )
        return date in holiday_dates

    @classmethod
    def get_supported_countries(cls) -> Set[str]:
        """Get list of countries supported by the holidays library"""
        if not HAS_HOLIDAYS:
            return set()

        supported = set()
        for attr_name in dir(holidays):
            attr = getattr(holidays, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, holidays.HolidayBase)
                and attr != holidays.HolidayBase
            ):
                supported.add(attr_name)

        return supported

    @classmethod
    def clear_cache(cls):
        """Clear the holiday object cache"""
        cls._holiday_cache.clear()
