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

from baldaquin.app import UserAppNoOp
from baldaquin.runctrl import RunControl


def test_no_op():
    """
    """
    rc = RunControl()
    app = UserAppNoOp()
    rc.set_user_application(app)
    rc.set_stopped()
    rc.set_running()
    rc.set_stopped()
    rc.set_reset()
