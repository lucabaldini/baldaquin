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
import pytest

from baldaquin import logger, BALDAQUIN_TEST_DATA, BALDAQUIN_ROOT
from baldaquin.pkt import PacketFile
from baldaquin.plasduino.protocol import AnalogReadout, DigitalTransition
from baldaquin.plt_ import plt, setup_gca


PENDULUM_RUN = 396
PENDULUM_DATA_FOLDER = BALDAQUIN_TEST_DATA / f'0101_000{PENDULUM_RUN}'


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


@pytest.mark.skip
def test_pendulum_process():
    """Test the pendulum post-processing code.

    This was done to debug issue https://github.com/lucabaldini/baldaquin/issues/50
    """
    sys.path.append(str(BALDAQUIN_ROOT / 'plasduino' / 'apps'))
    sys.dont_write_bytecode = True
    pendulum = importlib.import_module('plasduino_pendulum')
    sys.dont_write_bytecode = False
    file_path = PENDULUM_DATA_FOLDER / f'0101_000{PENDULUM_RUN}_data.dat'
    with PacketFile(DigitalTransition).open(file_path) as input_file:
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


def transit_velocity(transit_time: np.array, pendulum_length: float, gate_distance: float,
                     flag_width: float) -> np.array:
    """Calculate the average transit velocity based on the transit time.

    Arguments
    ---------
    transit_time : array_like
        The flag transit time.

    pendulum_length : float
        The pendulum length.

    gate_distance : float
        The distance between the suspension point an the optical gate.

    flag_width : float
        The width of the measuring flag.
    """
    return flag_width / transit_time * pendulum_length / gate_distance


def pendulum_amplitude(transit_time: np.array, pendulum_length: float, gate_distance: float,
                       flag_width: float) -> np.array:
    """Calculate the approximate oscillation amplitude based on the transit time.

    Arguments
    ---------
    transit_time : array_like
        The flag transit time.

    pendulum_length : float
        The pendulum length.

    gate_distance : float
        The distance between the suspension point an the optical gate.

    flag_width : float
        The width of the measuring flag.
    """
    g = 9.81
    v = transit_velocity(transit_time, pendulum_length, gate_distance, flag_width)
    return np.arccos(1. - v**2. / 2. / g / pendulum_length)


def period_model(theta, T0):
    """Fitting model for the period as a function of the amplitude.
    """
    return T0 * (1. + theta**2 / 16. + 11. / 3072. * theta**4.)


def test_pendulum_plot():
    """Test a data file taken with the pendulum.
    """
    mass = 0.330
    pendulum_length = 1.111 # 110.9--111.3 cm
    gate_distance = 1.151
    flag_width = 0.0194

    file_path = PENDULUM_DATA_FOLDER / f'0101_000{PENDULUM_RUN}_data_proc.txt'
    time_, period, transit_time = np.loadtxt(file_path, delimiter=',', unpack=True)
    energy = 0.5 * mass * transit_velocity(transit_time, pendulum_length, gate_distance, flag_width)**2.
    amplitude = pendulum_amplitude(transit_time, pendulum_length, gate_distance, flag_width)
    energy_loss = np.diff(energy) / (0.5 * (energy[:-1] + energy[1:]))

    plt.figure('Period')
    plt.plot(time_, period, 'o')
    setup_gca(xlabel='Time [s]', ylabel='Period [s]', grids=True)

    plt.figure('Transit time')
    plt.plot(time_, transit_time, 'o')
    setup_gca(xlabel='Time [s]', ylabel='Transit time [s]', grids=True)

    plt.figure('Amplitude')
    plt.plot(amplitude, period, 'o')
    plt.plot(amplitude, period_model(amplitude, 2.115))
    setup_gca(xlabel='Amplitude [rad]', ylabel='Period [s]', grids=True)

    plt.figure('Energy')
    plt.plot(time_, energy, 'o')
    setup_gca(xlabel='Period [s]', ylabel='Energy [J]', grids=True)

    plt.figure('Energy loss')
    plt.plot(time_[1:], energy_loss, 'o')
    setup_gca(xlabel='Period [s]', ylabel='Fractional energy loss', grids=True)


if __name__ == '__main__':
    test_pendulum_plot()
    plt.show()
