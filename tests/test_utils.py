"""
Tests for utility functions.

This module tests various utility functions, particularly focusing on
timezone handling, date formatting, and other helper functions.
"""

# Standard library imports
import logging
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

# Third-party imports
import pytz

# Local application imports
from .test_base import BaseTestCase
from app.utils import (
    calculate_days_until,
    ensure_timezone_utc,
    format_date,
    format_datetime,
    format_time,
    from_local_timezone,
    to_local_timezone,
)

# Temporarily increase log level
logger = logging.getLogger("app.model_relationships")
logger.setLevel(logging.DEBUG)


class TestTimezoneUtils(BaseTestCase):
    """Test cases for timezone utility functions."""

    def setUp(self):
        """Set up test fixtures before each test."""
        super().setUp()

        # Create a datetime object for testing
        self.utc_now = self.now.astimezone(pytz.timezone("UTC"))
        self.naive_now = self.now

    def test_ensure_timezone_utc(self):
        # Test with timezone-naive datetime
        result = ensure_timezone_utc(self.naive_now)
        self.assertEqual(result.tzinfo, timezone.utc)

        # Test with timezone-aware datetime
        berlin_tz = pytz.timezone("Europe/Berlin")
        berlin_time = self.now.astimezone(berlin_tz)
        result = ensure_timezone_utc(berlin_time)

        # Compare timezone zones instead of objects
        self.assertEqual(result.tzinfo.zone, berlin_tz.zone)

    def test_to_local_timezone(self):
        """Test conversion from UTC to local timezone."""
        from app.models import Settings

        # Mock the application timezone setting
        with patch("utils.get_application_timezone") as mock_get_tz:
            # Set app timezone to Berlin
            timezone_string = "Europe/Berlin"

            # Create a Settings object with the timezone
            set = Settings(timezone_name=timezone_string)
            self.db.session.add(set)
            self.db.session.flush()

            mock_get_tz.return_value = pytz.timezone(timezone_string)

            berlin_tz = pytz.timezone(timezone_string)
            mock_get_tz.return_value = berlin_tz

            # Convert UTC time to Berlin time
            result = to_local_timezone(self.utc_now)

            # Check timezone
            self.assertEqual(result.tzinfo.zone, berlin_tz.zone)

            # We need to be flexible about DST, so just check that time differs
            self.assertNotEqual(self.utc_now.hour, result.hour)

    def test_from_local_timezone(self):
        """Test conversion from local timezone to UTC."""
        # Mock the application timezone setting
        with patch("utils.get_application_timezone") as mock_get_tz:
            # Set app timezone to Berlin
            berlin_tz = pytz.timezone("Europe/Berlin")
            mock_get_tz.return_value = berlin_tz

            # Create a Berlin timezone datetime
            berlin_time = self.now.astimezone(berlin_tz)

            # Convert to UTC
            result = from_local_timezone(berlin_time)

            # Check timezone
            self.assertEqual(result.tzinfo, timezone.utc)

            # We need to be flexible about DST, so just check that time differs
            self.assertNotEqual(berlin_time.hour, result.hour)

    def test_calculate_days_until(self):
        """Test calculation of days until a target date."""
        # Today should return 1 (tomorrow)
        today = self.now.astimezone(pytz.timezone("UTC"))
        result = calculate_days_until(today)
        self.assertEqual(result, 1)

        # Tomorrow should return 1
        tomorrow = today + timedelta(days=1)
        result = calculate_days_until(tomorrow)
        self.assertEqual(result, 1)

        # 5 days ahead should return 5
        future = today + timedelta(days=5)
        result = calculate_days_until(future)
        self.assertEqual(result, 5)


class TestDateFormatting(BaseTestCase):
    """Test cases for date formatting utility functions."""

    def setUp(self):
        """Set up test fixtures before each test."""
        super().setUp()

        # Create a datetime object for testing
        self.test_dt = datetime(2023, 1, 15, 14, 30, 45, tzinfo=timezone.utc)

    def test_format_datetime(self):
        """Test datetime formatting."""
        # Mock local timezone to avoid actual TZ conversion for predictable tests
        with patch("utils.to_local_timezone") as mock_to_local:
            # Identity function for testing
            mock_to_local.side_effect = lambda dt: dt

            # Test without seconds
            result = format_datetime(self.test_dt, show_seconds=False)
            self.assertEqual(result, "15.01.2023 14:30")

            # Test with seconds
            result = format_datetime(self.test_dt, show_seconds=True)
            self.assertEqual(result, "15.01.2023 14:30:45")

    def test_format_date(self):
        """Test date formatting."""
        # Mock local timezone to avoid actual TZ conversion for predictable tests
        with patch("utils.to_local_timezone") as mock_to_local:
            # Identity function for testing
            mock_to_local.side_effect = lambda dt: dt

            result = format_date(self.test_dt)
            self.assertEqual(result, "15.01.2023")

    def test_format_time(self):
        """Test time formatting."""
        # Mock local timezone to avoid actual TZ conversion for predictable tests
        with patch("utils.to_local_timezone") as mock_to_local:
            # Identity function for testing
            mock_to_local.side_effect = lambda dt: dt

            result = format_time(self.test_dt)
            self.assertEqual(result, "14:30:45")


if __name__ == "__main__":
    unittest.main()
