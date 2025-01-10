# Copyright (C) 2024 the baldaquin team.
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

"""Plasduino shield information.

See the old plasduino repo for all the gory details:
https://bitbucket.org/lbaldini/plasduino/src/main/shields/
"""


class Lab1:

    """Hardware description for the Lab1 shield, version 2.
    """

    # pylint: disable=too-few-public-methods

    VERSION = 2
    # Analog inputs for the temperature measurements.
    ANALOG_PIN_1 = 0
    ANALOG_PIN_2 = 1
    ANALOG_PINS = (ANALOG_PIN_1, ANALOG_PIN_2)
    SHUNT_RESISTANCE = 10.  # kOhm
    # Digital inputs for the time measurements.
    DIGITAL_PIN_1 = 0
    DIGITAL_PIN_2 = 0
    DIGITAL_PINS = (DIGITAL_PIN_1, DIGITAL_PIN_2)
