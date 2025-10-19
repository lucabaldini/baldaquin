# Copyright (C) 2022 the baldaquin team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Time-related facilities.
"""

from __future__ import annotations

import calendar
import datetime
import time
from dataclasses import dataclass


class tzoffset(datetime.tzinfo):

    # pylint: disable=invalid-name

    """Minimal tzinfo class factory to create time-aware datetime objects.

    See https://docs.python.org/3/library/datetime.html#datetime.tzinfo
    for more details.

    Arguments
    ---------
    name : str
        The tzinfo object name.

    offset : float
        The UTC offset in seconds.
    """

    def __init__(self, name: str, offset: float) -> None:
        """Constructor.
        """
        self.name = name
        self.offset = datetime.timedelta(seconds=offset)

    def utcoffset(self, dt: datetime.datetime) -> float:
        """Overloaded method.
        """
        return self.offset

    def dst(self, dt: datetime.datetime) -> float:
        """Overloaded method.

        According to the documentation, this Return the daylight saving time (DST)
        adjustment, as a timedelta object or None if DST information isn’t known.
        """
        return None

    def tzname(self, dt: datetime.datetime) -> str:
        """Overloaded method.
        """
        return self.name


@dataclass
class Timestamp:

    """Small utility class to represent a timezone-aware timestamp.

    A Timestamp encodes three basic pieces of information:

    * a datetime object in the UTC time zone;
    * a datetime object in the local time zone;
    * a timestamp in seconds, relative to the origin of the parent timeline.

    Timestamp objects support subtraction aritmethics as a handy shortcut
    to calculate time differences.

    Timestamp objects also support serialization/deserialization through the
    :meth:`to_dict() <baldaquin.timeline.Timestamp.to_dict>` and
    :meth:`from_dict() <baldaquin.timeline.Timestamp.from_dict>`, which, in turn, use
    internally a string conversion to ISO format. (``datetime`` objects
    are implemented in C and therefore have no ``__dict__`` slot.)

    Arguments
    ---------
    utc_datetime : datetime.datetime
        The (timezone-aware) UTC datetime object corresponding to the timestamp.

    local_datetime : datetime.datetime
        The (timezone-aware) local datetime object corresponding to the timestamp.

    seconds : float
        The seconds elapsed since the origin of the parent timeline.
    """

    utc_datetime: datetime.datetime
    local_datetime: datetime.datetime
    seconds: float

    # These are the fields that need special handling when serializing/deserializing.
    _DATETIME_FIELDS = ("utc_datetime", "local_datetime")

    def to_dict(self) -> dict:
        """Serialization.
        """
        dict_ = {**self.__dict__}
        for key in self._DATETIME_FIELDS:
            dict_.update({key: dict_[key].isoformat()})
        return dict_

    @classmethod
    def from_dict(cls, **kwargs) -> Timestamp:
        """Deserialization.
        """
        for key in cls._DATETIME_FIELDS:
            kwargs.update({key: datetime.datetime.fromisoformat(kwargs[key])})
        return cls(**kwargs)

    def __sub__(self, other: Timestamp) -> float:
        """Overloaded operator to support timestamp subtraction.
        """
        return self.seconds - other.seconds

    def __str__(self) -> str:
        """String formatting.
        """
        return f"{self.local_datetime} ({self.seconds} s)"


class Timeline:

    # pylint: disable=too-few-public-methods

    """Class representing a continuos timeline referred to a fixed origin.

    Note that, by deafult, the origin of the Timeline is January 1, 1970 00:00:00 UTC,
    and the seconds field in the Timestamp objects that the Timeline returns
    when latched correspond to the standard POSIX time. Setting the origin to a
    different value allow, e.g., to emulate the mission elapsed time (MET)
    concept that is common in space missions.

    Arguments
    ---------
    origin : str
        A string representation (in ISO 8601 format) of the date and time
        corresponding to the origin of the timeline in UTC (without the
        traling +00:00).

        More specifically, according to the datetime documentation, we support
        strings in the format:

        .. code-block::

           YYYY-MM-DD[*HH[:MM[:SS[.fff[fff]]]]

        where * can match any single character.
    """

    _POSIX_ORIGIN = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)

    def __init__(self, origin: str = "1970-01-01") -> None:
        """Constructor.
        """
        self.origin = datetime.datetime.fromisoformat(f"{origin}")
        self.origin = self.origin.replace(tzinfo=datetime.timezone.utc)
        self._timestamp_offset = (self.origin - self._POSIX_ORIGIN).total_seconds()

    @staticmethod
    def _utc_offset() -> int:
        """Return the local UTC offset in s, considering the DST---note this has
        to be calculated every time the timeline is latched, as one doesn't know
        if a DST change has happened between two successive calls.

        See https://stackoverflow.com/questions/3168096 for more details on why
        this is a sensible way to calculate this.
        """
        return calendar.timegm(time.localtime()) - calendar.timegm(time.gmtime())

    def latch(self) -> Timestamp:
        """This is the workhorse function for keeping track of the time.

        This function latches the system time and creates a frozen Timestamp
        object that can be reused at later time.
        """
        # Retrieve the UTC date and time---this is preferred over datetime.utcnow(),
        # as the latter returns a naive datetime object, with tzinfo set to None.
        utc_datetime = datetime.datetime.now(datetime.timezone.utc)
        # Calculate the UTC offset.
        offset = self._utc_offset()
        # Add the offset to the UTC datetime and setup the tzinfo so that
        # the offset is included by default in the string representation.
        local_datetime = utc_datetime + datetime.timedelta(seconds=offset)
        local_datetime = local_datetime.replace(tzinfo=tzoffset("Local", offset))
        seconds = utc_datetime.timestamp() - self._timestamp_offset
        return Timestamp(utc_datetime, local_datetime, seconds)
