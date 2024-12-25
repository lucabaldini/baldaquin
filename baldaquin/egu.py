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

"""Engineering units and converters.
"""

import numpy as np


class ConversionBase:

    """Abstract base class for a generic conversion.
    """

    def _conversion_function(self, raw) -> None:
        """Conversion function, to be reimplemented in derived classes.
        """
        raise NotImplementedError

    def __call__(self, raw):
        """Special dunder method for executing the actual conversion.
        """
        return self._conversion_function(raw)



class LinearConversion(ConversionBase):

    """Linear conversion.
    """

    def __init__(self, slope: float, intercept: float = 0) -> None:
        """Constructor.
        """
        self.slope = slope
        self.intercept = intercept

    def _conversion_function(self, raw):
        """Overloaded method.
        """
        return self.slope * raw + self.intercept



class PolynomialConversion(ConversionBase):

    """Polynomial conversion.
    """

    pass



class SplineConversion(ConversionBase):

    """Polynomial conversion.
    """

    def __init__(self, x, y, k: int = 3) -> None:
        """Constructor.
        """
        pass



if __name__ == '__main__':
    c = LinearConversion(2., 1.)
    raw = np.linspace(0., 1., 11)
    val = c(raw)
    print(raw, val)
