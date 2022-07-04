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

import calendar
from dataclasses import dataclass
import datetime
import time



class tzoffset(datetime.tzinfo):

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

    def __init__(self, name : str, offset : float):
        """Constructor.
        """
        self.name = name
        self.offset = datetime.timedelta(seconds=offset)

    def utcoffset(self, dt):
        """Return the UTC offset.
        """
        return self.offset



@dataclass
class Timestamp:

    """Small utility class to represent a timezone-aware timestamp.

    A Timestamp encodes three basic pieces of information:

    * a datetime object in the UTC time zone;
    * a datetime object in the local time zone;
    * a timestamp in seconds, relative to the origin of the parent timeline.
    """

    utc_datetime: datetime.datetime
    local_datetime: datetime.datetime
    seconds: float

    @staticmethod
    def _dt_to_str(dt):
        """Utility function to convert a datetime object into a string.
        """
        return dt.isoformat(timespec='microseconds')

    def utc_datetime_string(self):
        """Return a string representation of the UTC datetime.
        """
        return self._dt_to_str(self.utc_datetime)

    def local_datetime_string(self):
        """Return a string representation of the UTC datetime.
        """
        return self._dt_to_str(self.local_datetime)



class Timeline:

    """Class representing a continuos timeline.
    """

    POSIX_ORIGIN = datetime.datetime(1970, 1, 1)

    def __init__(self, origin='1970-01-01 00:00:00'):
        """Constructor.
        """
        self.origin = datetime.datetime.fromisoformat(origin)
        self._timestamp_offset = (self.origin - self.POSIX_ORIGIN).total_seconds()

    @staticmethod
    def utc_offset():
        """Return the local UTC offset in s, considering the DST.

        See https://stackoverflow.com/questions/3168096 for more details on why
        this is a sensible way to calculate this.
        """
        return calendar.timegm(time.localtime()) - calendar.timegm(time.gmtime())

    def timestamp(self):
        """This is the workhorse function for keeping track of the time.
        """
        # Retrieve the UTC date and time---this is preferred over datetime.utcnow(),
        # as the latter returns a naive datetime object, with tzinfo set to None.
        utc_datetime = datetime.datetime.now(datetime.timezone.utc)
        # Calculate the UTC offset.
        offset = self.utc_offset()
        # Add the offset to the UTC datetime and setup the tzinfo so that
        # the offset is included by default in the string representation.
        local_datetime = utc_datetime + datetime.timedelta(seconds=offset)
        local_datetime = local_datetime.replace(tzinfo=tzoffset('Local', offset))
        seconds = utc_datetime.timestamp() - self._timestamp_offset
        return Timestamp(utc_datetime, local_datetime, seconds)
