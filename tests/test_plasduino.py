# Copyright (C) 2025 the baldaquin team.
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

"""Test suite for the plasduino project.
"""

import importlib
import sys

import numpy as np

from baldaquin import logger, BALDAQUIN_TEST_DATA, BALDAQUIN_ROOT
from baldaquin.pkt import PacketFile
from baldaquin.plasduino.protocol import AnalogReadout, DigitalTransition
from baldaquin.plt_ import plt, setup_gca


PENDULUM_DATA_FOLDER = BALDAQUIN_TEST_DATA / '0101_000389'


def test_protocol():
    """Test the protocol.
    """
    readout = AnalogReadout(0xa2, 1, 1000, 255)
    logger.info(readout)
    logger.info(AnalogReadout.text_header('Something [a. u.]'))
    logger.info(readout.to_text())
    transition = DigitalTransition(0xa1, 1, 1000000)
    logger.info(transition)
    logger.info(DigitalTransition.text_header())
    logger.info(transition.to_text())


def test_pendulum_process():
    """Test a data file taken with the pendulum.
    """
    sys.path.append(str(BALDAQUIN_ROOT / 'plasduino' / 'apps'))
    sys.dont_write_bytecode = True
    pendulum = importlib.import_module('plasduino_pendulum')
    sys.dont_write_bytecode = False
    with PacketFile(DigitalTransition).open(PENDULUM_DATA_FOLDER / '0101_000389_data.dat') as input_file:
            data = input_file.read_all()

    # Post-process with the simple method.
    oscillations = pendulum.Pendulum._postprocess_data_simple(data)
    simple_time = np.array([oscillation.average_time for oscillation in oscillations])
    simple_period = np.array([oscillation.period for oscillation in oscillations])
    simple_transit_time = np.array([oscillation.transit_time for oscillation in oscillations])

    # Post-process with the smoothed method.
    oscillations = pendulum.Pendulum._postprocess_data_smooth(data)
    smooth_time = np.array([oscillation.average_time for oscillation in oscillations])
    smooth_period = np.array([oscillation.period for oscillation in oscillations])
    smooth_transit_time = np.array([oscillation.transit_time for oscillation in oscillations])

    plt.figure('Simple processing: period')
    plt.plot(simple_time, simple_period, label='Simple')
    plt.plot(smooth_time, smooth_period, label='Smooth')
    setup_gca(xlabel='Time [s]', ylabel='Period [s]', grids=True, legend=True)
    plt.figure('Simple processing: transit time')
    plt.plot(simple_time, simple_transit_time, label='Simple')
    plt.plot(smooth_time, smooth_transit_time, label='Smooth')
    setup_gca(xlabel='Time [s]', ylabel='Period [s]', grids=True, legend=True)


def test_pendulum_plot():
    """Test a data file taken with the pendulum.
    """
    plt.figure('Period')
    t, T, dt = np.loadtxt(PENDULUM_DATA_FOLDER / '0101_000389_data_proc.txt', delimiter=',', unpack=True)
    plt.plot(t, T, 'o')
    setup_gca(xlabel='Time [s]', ylabel='Period [s]', grids=True)


if __name__ == '__main__':
    test_pendulum_process()
    test_pendulum_plot()
    plt.show()