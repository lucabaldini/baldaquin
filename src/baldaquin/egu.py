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

from __future__ import annotations

from numbers import Number

import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline

from .logging_ import logger
from .plt_ import plt, setup_gca


class ConversionBase:

    """Abstract base class for a generic conversion.
    """

    # pylint: disable=too-few-public-methods

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

    # pylint: disable=too-few-public-methods

    def __init__(self, slope: float, intercept: float = 0) -> None:
        """Constructor.
        """
        self.slope = slope
        self.intercept = intercept

    def _conversion_function(self, raw):
        """Overloaded method.
        """
        return self.slope * raw + self.intercept


# class PolynomialConversion(ConversionBase):
#
#     """Polynomial conversion.
#     """
#
#     pass


class SplineConversion(ConversionBase):

    """Spline conversion.

    This is performing a simple spline interpolation of the physical values vs. the
    raw values.

    Arguments
    ---------
    raw : array_like
        The array of raw values.

    physical : array_like
        The array of physical values

    k : int (default 3)
        The degree of the interpolating spline.
    """

    def __init__(self, raw: np.array, physical: np.array, k: int = 3) -> None:
        """Constructor.
        """
        self._raw, self._physical = self._process_input(raw, physical)
        self._spline = InterpolatedUnivariateSpline(self._raw, self._physical, k=k)

    @staticmethod
    def _process_input(raw, physical) -> tuple[np.array, np.array]:
        """Sort and remove duplicates from the input arrays.

        In order for us to be able to build the spline, the x (raw) values must
        be passed in ascending order, and the y (physical) values must be (potentially)
        shuffled accordingly.

        Looking around on the internet, it seems like simply checking if an array
        is sorted is almost as expensive as calling argsort or unique, see, e.g.,
        https://github.com/numpy/numpy/issues/8392
        and therefore we just go ahead and re-sort everything and remove duplicates
        even when there is nothing to do.
        """
        raw, _index = np.unique(raw, return_index=True)
        physical = physical[_index]
        return raw, physical

    @staticmethod
    def read_data(file_path: str, col_raw: int = 0, col_physical: int = 1, **kwargs):
        """Read data from file.

        Arguments
        ---------
        file_path : str
            The path to the input text file containing the data.

        col_raw : int
            The index of the column containing the raw values.

        col_physical : int
            The index of the column containing the physical values.

        kwrargs : dict
            optional keyword arguments passed to ``np.loadtxt()``
        """
        logger.info(f"Reading conversion data from {file_path}...")
        raw, physical = np.loadtxt(file_path, usecols=(col_raw, col_physical),
                                   unpack=True, **kwargs)
        logger.info(f"Done, {len(raw)} data point(s) found.")
        return raw, physical

    @classmethod
    def from_file(cls, file_path: str, col_raw: int = 0, col_physical: int = 1,
                  k: int = 3) -> None:
        """Read the data points for the spline from a file.
        """
        data = cls.read_data(file_path, col_raw, col_physical)
        return cls(*data, k)

    def plot(self):
        """Plot the interpolating spline.
        """
        plt.plot(self._raw, self._physical)
        setup_gca(xlabel="Raw units", ylabel="Physical units")

    def _conversion_function(self, raw):
        """Overloaded method.
        """
        # If we are passing a single number, we cast the value to float in order to
        # avoid getting a 0-dim array as output from the spline evaluation, which
        # would potentially be a nuisance to handle downstream.
        if isinstance(raw, Number):
            return float(self._spline(raw))
        return self._spline(raw)


class ThermistorConversion(SplineConversion):

    """Specific conversion for a thermistor.
    """

    def __init__(self, temperature: np.array, resistance: np.array, shunt_resistance: float,
                 adc_num_bits: int, k: int = 3) -> None:
        """Constructor.
        """
        # pylint: disable=too-many-arguments
        adc = (2**adc_num_bits - 1) * shunt_resistance / (resistance + shunt_resistance)
        super().__init__(adc, temperature, k)

    @classmethod
    def from_file(cls, file_path: str, shunt_resistance: float, adc_num_bits: int,
                  col_temperature: int = 0, col_resistance: int = 1, k: int = 3) -> None:
        """Read the data points for the spline from file.
        """
        # pylint: disable=arguments-renamed, too-many-arguments
        data = cls.read_data(file_path, col_temperature, col_resistance)
        return cls(*data, shunt_resistance, adc_num_bits, k)
