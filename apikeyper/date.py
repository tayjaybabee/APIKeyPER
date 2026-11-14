from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime, time, timezone
from typing import TypeAlias

from apikeyper.log_engine import Loggable, ROOT_LOGGER


DateInput: TypeAlias = "Date | datetime | date | str | None"

_DATE_FORMATS = (
    "%m/%d/%Y", "%d/%m/%Y", "%m/%d/%y", "%d/%m/%y",
    "%Y-%m-%d", "%m-%d-%Y", "%d-%m-%Y", "%Y/%m/%d", "%d.%m.%Y", "%Y.%m.%d",
    "%b %d %Y", "%B %d %Y", "%d %b %Y", "%d %B %Y", "%d-%b-%Y",
)
_TIME_FORMATS = (
    "%H:%M", "%H:%M:%S", "%H:%M:%S.%f",
    "%I:%M %p", "%I:%M:%S %p", "%I:%M%p", "%I:%M:%S%p",
)
_TIMESTAMP_FORMATS = (
    "%a %d %b %Y %H:%M:%S %z",
    "%a %b %d %H:%M:%S %Y",
    *_DATE_FORMATS,
    *(
        f"{date_format} {time_format}{offset_format}"
        for date_format in _DATE_FORMATS
        for time_format in _TIME_FORMATS
        for offset_format in ("", "%z", " %z")
    ),
)


def _parse_date(value: str) -> datetime:
    value = value.strip()
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        pass

    cleaned = re.sub(r"\s+", " ", value.replace(",", " "))
    cleaned = re.sub(r"\s+(?:UTC|GMT)$", " +0000", cleaned, flags=re.IGNORECASE)
    for stamp_format in _TIMESTAMP_FORMATS:
        try:
            return datetime.strptime(cleaned, stamp_format)
        except ValueError:
            continue
    raise ValueError("Unsupported date or time format")


@dataclass(order=True, init=False)
class Date(Loggable):
    """A UTC timestamp ordered by its instant, with read-only default metadata."""

    _value: datetime
    _was_defaulted: bool = field(compare=False, repr=False)

    def __init__(self, value: DateInput = None, *, was_defaulted: bool = False):
        super().__init__(parent_log_device=ROOT_LOGGER)
        if isinstance(value, Date):
            was_defaulted = was_defaulted or value.was_defaulted
            timestamp = value.value
        elif value is None or isinstance(value, str) and not value.strip():
            was_defaulted = True
            timestamp = datetime.now(timezone.utc)
        elif isinstance(value, datetime):
            timestamp = value
        elif isinstance(value, date):
            timestamp = datetime.combine(value, time.min)
        elif isinstance(value, str):
            timestamp = _parse_date(value)
        else:
            raise TypeError("Date expects a date, datetime, string, or None")

        if timestamp.utcoffset() is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        self._value = timestamp.astimezone(timezone.utc)
        self._was_defaulted = was_defaulted

    @property
    def value(self) -> datetime:
        return self._value

    @property
    def was_defaulted(self) -> bool:
        return self._was_defaulted

    def isoformat(self) -> str:
        return self.value.isoformat(timespec="microseconds")

    def __str__(self) -> str:
        return self.isoformat()
