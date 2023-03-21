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

import pytest

from loguru import logger

#from baldaquin.app import UserAppNoOp
from baldaquin.runctrl import FsmState, FiniteStateMachine, RunControlBase,\
    InvalidFsmTransitionError



def test_finite_state_machine():
    """This creates a mock FSM where all the relevant hooks are no-op, and tests
    for the proper states after transitions, as well as the exceptions signaling
    the invalid ones.
    """
    # Create a virtual FSM.
    fsm = FiniteStateMachine()
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


def __test_no_op():
    """
    """
    rc = RunControl()
    app = UserAppNoOp()
    rc.set_user_application(app)
    rc.set_stopped()
    rc.set_running()
    rc.set_stopped()
    rc.set_reset()
