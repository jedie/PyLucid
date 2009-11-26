# coding:utf-8

"""
    small utils around timezone
"""

from datetime import datetime, timedelta


def utc_offset():
    """
    returns the offset between datetime.now() and datetime.utcnow() as a datetime.timedelta
    from contrib/syndication/feeds.py
    """
    now = datetime.now()
    utcnow = datetime.utcnow()

    # Must always subtract smaller time from larger time here.
    if utcnow > now:
        sign = -1
        tzDifference = (utcnow - now)
    else:
        sign = 1
        tzDifference = (now - utcnow)

    # Round the timezone offset to the nearest half hour.
    tzOffsetMinutes = sign * ((tzDifference.seconds / 60 + 15) / 30) * 30
    tzOffset = timedelta(minutes=tzOffsetMinutes)
    return tzOffset
