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

"""Test suite for egu.py
"""

import numpy as np

from baldaquin import egu
from baldaquin.plasduino import PLASDUINO_SENSORS


def test_linear(slope: float = 2., intercept: float = 1.):
    """Test a simple linear conversion.
    """
    converter = egu.LinearConversion(slope, intercept)
    raw = np.linspace(0., 1., 11)
    physical = converter(raw)
    assert np.allclose(physical, slope * raw + intercept)


def test_thermistor():
    """Test a spline conversion.
    """
    file_path = PLASDUINO_SENSORS / "NXFT15XH103FA2B.dat"
    _ = egu.ThermistorConversion.from_file(file_path, 10., 10, col_resistance=2)
