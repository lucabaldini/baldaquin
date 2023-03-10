# Copyright (C) 2023 the baldaquin team.
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


"""DAQ control for XMAPS.
"""

from baldaquin.app import UserApplicationBase
from baldaquin.event import EventHandlerBase
from baldaquin.runctrl import RunControl


class XmapEventHandler(EventHandlerBase):

    """
    """

    def process_event(self):
        """
        """
        print(1)


class XmapsUserApp(UserApplicationBase):

    """
    """

    EVENT_HANDLER_CLASS = XmapEventHandler

    def process_event(self):
        """
        """
        print(2)



class XmapsRunControl(RunControl):

    """Specialized XMAPS run control.
    """




if __name__ == '__main__':
    rc = XmapsRunControl()
    app = XmapsUserApp()
    rc.set_user_application(app)
    rc.set_stopped()
    rc.set_running()
