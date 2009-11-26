
from pylucid_project.utils import timezone

from datetime import datetime


TZ_OFFSET = timezone.utc_offset()


def to_utc(value, arg=None):
    """Formats a date as the time since that date (i.e. "4 days, 6 hours")."""
    assert isinstance(value, datetime)

    value = value - TZ_OFFSET
    return value

