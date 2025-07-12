"""Application constants following DRY principle."""

# HTTP Status Codes
HTTP_OK = 200
HTTP_FOUND = 302
HTTP_NOT_FOUND = 404
HTTP_INTERNAL_ERROR = 500

# Default Values
DEFAULT_WEEKS = 52
DEFAULT_PORT = 6247
MAX_WEEKS = 104

# File Paths
TEMP_DIR = "/tmp"
CONFIG_DIR = "config"

# Date Formats
DATE_FORMAT = "%Y-%m-%d"
DISPLAY_DATE_FORMAT = "%B %d, %Y"
SHORT_DATE_FORMAT = "%m/%d"

# CSS Classes
CSS_WORKING = "working"
CSS_ONCALL = "oncall"
CSS_DAYOFF = "dayoff"
CSS_REQUIRED = "required"
CSS_HOLIDAY = "holiday"
CSS_SWAPPED = "swapped"

# Days of Week
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
MANDATORY_DAY = "Tuesday"

# Content Types
CONTENT_TYPE_HTML = "text/html"
CONTENT_TYPE_CALENDAR = "text/calendar; charset=utf-8"
CONTENT_TYPE_JSON = "application/json"

# Cache Control
NO_CACHE = "no-cache"