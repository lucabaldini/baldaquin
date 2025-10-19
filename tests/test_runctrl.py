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

"""Test suite for runctrl.py
"""

import time

import pytest

from baldaquin.env import BALDAQUIN_SCRATCH
from baldaquin.pkt import PacketStatistics
from baldaquin.runctrl import FiniteStateMachineBase, InvalidFsmTransitionError, RunReport
from baldaquin.timeline import Timeline


def test_finite_state_machine():
    """This creates a mock FSM where all the relevant hooks are no-op, and tests
    for the proper states after transitions, as well as the exceptions signaling
    the invalid ones.
    """
    # Create a virtual FSM.
    fsm = FiniteStateMachineBase()
    # Override all the necessary hooks to that we can actually have transitions.
    fsm.setup = lambda: True
    fsm.teardown = lambda: True
    fsm.start_run = lambda: True
    fsm.stop_run = lambda: True
    fsm.pause = lambda: True
    fsm.stop = lambda: True
    fsm.resume = lambda: True
    # Start in the RESET state.
    assert fsm.is_reset()
    with pytest.raises(InvalidFsmTransitionError):
        fsm.set_running()
    with pytest.raises(InvalidFsmTransitionError):
        fsm.set_reset()
    with pytest.raises(InvalidFsmTransitionError):
        fsm.set_paused()
    # Transition to STOPPED.
    fsm.set_stopped()
    assert fsm.is_stopped()
    with pytest.raises(InvalidFsmTransitionError):
        fsm.set_stopped()
    with pytest.raises(InvalidFsmTransitionError):
        fsm.set_paused()
    # Transition to RUNNING.
    fsm.set_running()
    assert fsm.is_running()
    with pytest.raises(InvalidFsmTransitionError):
        fsm.set_reset()
    # Transition to PAUSED.
    fsm.set_paused()
    assert fsm.is_paused()
    with pytest.raises(InvalidFsmTransitionError):
        fsm.set_reset()
    # And now back to back and forth from/to STOPPED and to the RESET state...
    fsm.set_running()
    fsm.set_stopped()
    fsm.set_running()
    fsm.set_paused()
    fsm.set_stopped()
    fsm.set_reset()
    assert fsm.is_reset()


def test_report():
    """Small unit test for the run report.
    """
    # Create a report.
    timeline = Timeline()
    start_timestamp = timeline.latch()
    time.sleep(0.5)
    stop_timestamp = timeline.latch()
    stats = PacketStatistics(10, 10, 100)
    report = RunReport("0.3.1", 101, 66, start_timestamp, stop_timestamp,
                       "Test project", "TestApplication", stats)

    # Make sure that the serialization/deserialization roundtrips.
    kwargs = report.to_dict()
    twin = RunReport.from_dict(**kwargs)
    assert twin == report
    assert twin.baldaquin_version == report.baldaquin_version
    assert twin.test_stand_id == report.test_stand_id
    assert twin.run_id == report.run_id
    assert twin.start_timestamp == report.start_timestamp
    assert twin.stop_timestamp == report.stop_timestamp
    assert twin.application_name == report.application_name
    assert twin.statistics == report.statistics

    # Test the file IO.
    file_path = BALDAQUIN_SCRATCH / "test_report.json"
    report.save(file_path)
    twin = RunReport.load(file_path)
    assert twin == report
    assert twin.baldaquin_version == report.baldaquin_version
    assert twin.test_stand_id == report.test_stand_id
    assert twin.run_id == report.run_id
    assert twin.start_timestamp == report.start_timestamp
    assert twin.stop_timestamp == report.stop_timestamp
    assert twin.application_name == report.application_name
    assert twin.statistics == report.statistics
