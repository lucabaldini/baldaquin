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

"""Test suite for timeline.py
"""

import time

from baldaquin.timeline import Timeline, Timestamp


def test_default_timeline():
    """The timestamp seconds of the default timeline should be essentially
    identical to time.time()---mind the two things are necessarily cached at
    different times.
    """
    timeline = Timeline()
    tstamp = timeline.latch()
    delta = tstamp.seconds - time.time()
    assert abs(delta) < 0.001


def test_offset_timeline(origin="1971-01-01"):
    """Test a timeline with a 1-year offset with respect to the POSIX time.
    """
    timeline = Timeline(origin)
    tstamp = timeline.latch()
    delta = tstamp.seconds - time.time()
    assert abs(delta + 3600. * 24 * 365) < 0.001


def test_offset_timeline_leap(origin="1973-01-01"):
    """Test a timeline with a 3-year offset with respect to the POSIX time,
    including one leap year.
    """
    timeline = Timeline(origin)
    tstamp = timeline.latch()
    delta = tstamp.seconds - time.time()
    assert abs(delta + 3600. * 24 * (3 * 365 + 1)) < 0.001


def test_serialization():
    """Test the serialization/deserialization facilities.
    """
    # Create a timeline and a timestamp.
    timeline = Timeline()
    timestamp = timeline.latch()
    # Serialize...
    kwargs = timestamp.to_dict()
    # ... and deserialize.
    twin = Timestamp.from_dict(**kwargs)
    # The two things should be identical.
    assert twin == timestamp
    assert twin.utc_datetime == timestamp.utc_datetime
    assert twin.local_datetime == timestamp.local_datetime
    assert twin.seconds == timestamp.seconds
    assert id(twin) != id(timestamp)
    # And, just for fun, make sure a different timestamp is really different.
    impostor = timeline.latch()
    assert impostor != timestamp
