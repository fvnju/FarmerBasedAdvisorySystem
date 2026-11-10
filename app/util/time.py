"""Date and time helpers."""

import datetime


def utc_now() -> datetime.datetime:  # Current UTC time without a time zone, as the DateTime columns keep it
    return datetime.datetime.now(datetime.UTC).replace(tzinfo=None)


def utc_today() -> datetime.date:  # Current UTC date
    return utc_now().date()
