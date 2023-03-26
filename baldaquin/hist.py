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

"""Histogram facilities.
"""

import numpy as np

from baldaquin.plt_ import matplotlib, plt, setup_gca, PlotCard



class InvalidShapeError(RuntimeError):

    """RuntimeError subclass to signal an invalid shape while operating with arrays.
    """

    def __init__(self, expected, actual):
        """Constructor.
        """
        super().__init__(f'Invalid array shape: {expected} expected, got {actual}')




class HistogramBase:

    """Base class for an n-dimensional histogram.

    This interface to histograms is profoundly different for the minimal
    numpy/matplotlib approach, where histogramming methods return bare
    vectors of bin edges and counts.

    Note that this base class is not meant to be instantiated directly, and
    the interfaces to concrete histograms of specific dimensionality are
    defined in the sub-classes.

    Parameters
    ----------
    binning : n-dimensional tuple of arrays
        the bin edges on the different axes.

    labels : n-dimensional tuple of strings
        the text labels for the different axes.
    """

    PLOT_OPTIONS = {}

    def __init__(self, binning, labels):
        """Constructor.
        """
        # Quick check on the binning and label tuples---we need N + 1 labels
        # for an N-dimensional histogram.
        if not len(labels) == len(binning) + 1:
            msg = f'Length mismatch between binning ({len(binning)}) and labels ({len(labels)})'
            raise RuntimeError(msg)
        # The binning is not supposed to change ever, so we turn it into a tuple...
        self.binning = tuple(binning)
        # ...while the labels might conceivably be changed after the fact, hence a list.
        self.labels = list(labels)
        # Initialize all the relevant arrays.
        self._shape = tuple(len(bins) - 1 for bins in self.binning)
        self.content = self._zeros()
        self.entries = self._zeros()
        self._sumw2 = self._zeros()

    def _zeros(self, dtype : type = float):
        """Return an array of zeros of the proper shape for the underlying
        histograms quantities.
        """
        return np.zeros(shape=self._shape, dtype=dtype)

    def reset(self) ->  None:
        """Reset the histogram.
        """
        self.content = self._zeros()
        self.entries = self._zeros()
        self._sumw2 = self._zeros()

    def bin_centers(self, axis : int = 0) -> np.array:
        """Return the bin centers for a specific axis.
        """
        return 0.5 * (self.binning[axis][1:] + self.binning[axis][:-1])

    def bin_widths(self, axis : int = 0) -> np.array:
        """Return the bin widths for a specific axis.
        """
        return np.diff(self.binning[axis])

    def errors(self) -> np.array:
        """Return the errors on the bin content.
        """
        return np.sqrt(self._sumw2)

    def set_axis_label(self, axis : int, label : str) -> None:
        """Set the label for a given axis.
        """
        self.labels[axis] = label

    @staticmethod
    def calculate_axis_statistics(bin_centers : np.array, content : np.array) -> dict:
        """Calculate the basic statistics (normalization, mean and rms) for a
        given set of binned data.
        """
        sumw = content.sum()
        mean = (bin_centers * content).sum() / sumw
        rms = ((bin_centers - mean)**2. * content).sum() / sumw
        return {'Sum of weights': sumw, 'Mean':  mean, 'RMS': rms}

    def _check_array_shape(self, data : np.array) -> None:
        """Check the shape of a given array used to update the histogram.
        """
        if data.shape == self._shape:
            raise InvalidShapeError(self._shape, data.shape)

    def set_errors(self, errors : np.array) -> None:
        """Set the proper value for the _sumw2 underlying array, given the
        errors on the bin content.
        """
        self._check_array_shape(errors)
        self._sumw2 = errors**2.

    def fill(self, *values, weights=None):
        """Fill the histogram from unbinned data.

        Note this method is returning the histogram instance, so that the function
        call can be chained.
        """
        # Add a check on the length of the values arrays>
        if weights is None:
            weights = np.ones(values[0].shape, dtype=float)
        values = np.vstack(values).T
        content, _ = np.histogramdd(values, bins=self.binning, weights=weights)
        entries, _ = np.histogramdd(values, bins=self.binning)
        _sumw2, _ = np.histogramdd(values, bins=self.binning, weights=weights**2.)
        self.content += content
        self.entries += entries
        self._sumw2 += _sumw2
        return self

    def set_content(self, content : np.array, entries : np.array = None, errors : np.array = None):
        """Set the bin contents programmatically from binned data.

        Note this method is returning the histogram instance, so that the function
        call can be chained.
        """
        self._check_array_shape(errors)
        self.content = content
        if entries is not None:
            self._check_array_shape(entries)
            self.entries = entries
        if errors is not None:
            self.set_errors(errors)
        return self

    @staticmethod
    def bisect(binning : np.array, values : np.array, side : str = 'left') -> np.array:
        """Return the indices corresponding to a given array of values for a
        given binning.
        """
        return np.searchsorted(binning, values, side) - 1

    def find_bin(self, *coords):
        """Find the bin corresponding to a given set of "physical" coordinates
        on the histogram axes.

        This returns a tuple of integer indices that can be used to address
        the histogram content.
        """
        return tuple(self.bisect(binning, value) for binning, value in zip(self.binning, coords))

    def find_bin_value(self, *coords):
        """Find the histogram content corresponding to a given set of "physical"
        coordinates on the histogram axes.
        """
        return self.content[self.find_bin(*coords)]

    def normalization(self, axis : int = None):
        """return the sum of weights in the histogram.
        """
        return self.content.sum(axis)

    def empty_copy(self):
        """Create an empty copy of a histogram.
        """
        return self.__class__(*self.binning, *self.labels)

    def copy(self):
        """Create a full copy of a histogram.
        """
        hist = self.empty_copy()
        hist.set_content(self.content.copy(), self.entries.copy())
        return hist

    def __add__(self, other):
        """Histogram addition.
        """
        hist = self.empty_copy()
        hist.set_content(self.content + other.content, self.entries + other.entries,
            np.sqrt(self._sumw2 + other._sumw2))
        return hist

    def __sub__(self, other):
        """Histogram subtraction.
        """
        hist = self.empty_copy()
        hist.set_content(self.content - other.content, self.entries + other.entries,
            np.sqrt(self._sumw2 + other._sumw2))
        return hist

    def __mul__(self, value):
        """Histogram multiplication by a scalar.
        """
        hist = self.empty_copy()
        hist.set_content(self.content * value, self.entries, self.errors() * value)
        return hist

    def __rmul__(self, value):
        """Histogram multiplication by a scalar.
        """
        return self.__mul__(value)

    def _plot(self, **kwargs) -> None:
        """No-op plot() method, to be overloaded by derived classes.
        """
        raise NotImplementedError(f'_plot() not implemented for {self.__class__.__name__}')

    def plot(self, **kwargs) -> None:
        """Plot the histogram.
        """
        for key, value in self.PLOT_OPTIONS.items():
            kwargs.setdefault(key, value)
        self._plot(**kwargs)
        setup_gca(xlabel=self.labels[0], ylabel=self.labels[1])



class Histogram1d(HistogramBase):

    """A one-dimensional histogram.
    """

    PLOT_OPTIONS = dict(lw=1.25, alpha=0.4, histtype='stepfilled')

    def __init__(self, xbinning : np.array, xlabel : str = '', ylabel : str ='Entries/bin') -> None:
        """Constructor.
        """
        HistogramBase.__init__(self, (xbinning, ), [xlabel, ylabel])

    def current_stats(self) -> dict:
        """Calculate the basic binned statistics for the histogram.
        """
        return self.calculate_axis_statistics(self.bin_centers(0), self.content)

    def stat_box(self) -> None:
        """Draw a stat box for the histogram.
        """
        PlotCard(self.current_stats()).draw()

    def _plot(self, **kwargs):
        """Overloaded make_plot() method.
        """
        plt.hist(self.bin_centers(0), self.binning[0], weights=self.content, **kwargs)



class Histogram2d(HistogramBase):

    """A two-dimensional histogram.
    """

    PLOT_OPTIONS = dict(cmap=plt.get_cmap('hot'))
    # pylint: disable=invalid-name

    def __init__(self, xbinning, ybinning, xlabel='', ylabel='', zlabel='Entries/bin'):
        """Constructor.
        """
        # pylint: disable=too-many-arguments
        HistogramBase.__init__(self, (xbinning, ybinning), [xlabel, ylabel, zlabel])

    def _plot(self, logz=False, **kwargs):
        """Overloaded make_plot() method.
        """
        x, y = (v.flatten() for v in np.meshgrid(self.bin_centers(0), self.bin_centers(1)))
        bins = self.binning
        w = self.content.T.flatten()
        if logz:
            # Hack for a deprecated functionality in matplotlib 3.3.0
            # Parameters norm and vmin/vmax should not be used simultaneously
            # If logz is requested, we intercent the bounds when created the norm
            # and refrain from passing vmin/vmax downstream.
            vmin = kwargs.pop('vmin', None)
            vmax = kwargs.pop('vmax', None)
            kwargs.setdefault('norm', matplotlib.colors.LogNorm(vmin, vmax))
        plt.hist2d(x, y, bins, weights=w, **kwargs)
        color_bar = plt.colorbar()
        if self.labels[2] is not None:
            color_bar.set_label(self.labels[2])

    def slice(self, bin_index : int, axis : int = 0):
        """Return a slice of the two-dimensional histogram along the given axis.
        """
        hist = Histogram1d(self.binning[axis], self.labels[axis])
        hist.set_content(self.content[:, bin_index], self.entries[:, bin_index])
        return hist

    def slices(self, axis : int = 0):
        """Return all the slices along a given axis.
        """
        return tuple(self.slice(bin_index, axis) for bin_index in range(self._shape[axis]))

    def hslice(self, bin_index : int):
        """Return the horizontal slice for a given bin.
        """
        return self.slice(bin_index, 0)

    def hslices(self):
        """Return a list of all the horizontal slices.
        """
        return self.slices(0)

    def hbisect(self, y : float):
        """Return the horizontal slice corresponding to a given y value.
        """
        return self.hslice(self.bisect(self.binning[1], y))

    def vslice(self, bin_index):
        """Return the vertical slice for a given bin.
        """
        return self.slice(bin_index, 1)

    def vslices(self):
        """Return a list of all the vertical slices.
        """
        return self.slices(1)

    def vbisect(self, x):
        """Return the vertical slice corresponding to a given y value.
        """
        return self.vslice(self.bisect(self.binning[0], x))
