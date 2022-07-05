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

"""Test suite for core/config.py
"""

import os

from baldaquin import BALDAQUIN_DATA
from baldaquin.config import ConfigurationParameter, ConfigurationBase


class SillyConfiguration(ConfigurationBase):

    TITLE = 'Just a test configuration'
    PARAMETER_SPECS = (
        ('enabled', 'bool', True, 'Enable connection', {}),
        ('ip_address', 'str', '127.0.0.1', 'IP address', {}),
        ('port', 'int', 20004, 'UDP port', dict(min=1024, max=65535)),
        ('timeout', 'float', 10., 'Connection timeout [s]', dict(min=0.))
    )



def _test_base_match(type_name, value, **constraints):
    """Base test function where we expect the parameter to match the input value.
    """
    p = ConfigurationParameter('parameter', type_name, value, **constraints)
    assert p.value == value

def _test_base_mismatch(type_name, value, **constraints):
    """Base test function where we expect the parameter to match the input value.
    """
    p = ConfigurationParameter('parameter', type_name, value, **constraints)
    assert p.value == None

def test_parameter_bool():
    """Test possible setting for int parameters.
    """
    for value in (True, False):
        _test_base_match('bool', value)
    for value in (1, 1., 'test'):
        _test_base_mismatch('bool', value)

def test_parameter_int(value=100):
    """Test possible setting for int parameters.
    """
    _test_base_match('int', 100)
    _test_base_match('int', 100, min=0, max=1000)
    _test_base_mismatch('int', 100, min=200)
    _test_base_mismatch('int', 100, max=0)
    _test_base_match('int', 100, choices=(99, 100, 101))
    _test_base_mismatch('int', 100, choices=(99, 101))
    _test_base_match('int', 100, step=10)
    _test_base_mismatch('int', 100, step=13)
    _test_base_match('int', 100, min=87, step=13)

def test_parameter_float(value=1.):
    """Test possible setting for int parameters.
    """
    _test_base_match('float', 1.)
    _test_base_match('float', 1., min=0., max=10.)
    _test_base_mismatch('float', 1., min=10.)
    _test_base_mismatch('float', 1., max=0.)

def test_parameter_str():
    """Test possible setting for int parameters.
    """
    _test_base_match('str', 'howdy?')
    _test_base_match('str', 'eggs', choices=('eggs', 'cheese'))
    _test_base_mismatch('str', 'ham', choices=('eggs', 'cheese'))
    for value in (True, 1, 1.):
        _test_base_mismatch('str', value)

def test_configuration():
    """Test an actual, fully-fledged configuration.
    """
    config = SillyConfiguration()
    print(config)
    file_path = os.path.join(BALDAQUIN_DATA, 'test_config.json')
    config.save(file_path)
    config.update(file_path)
    assert config.value('port') == 20004
    config.update_value('port', 3)
    assert config.value('port') == 20004
    config.update_value('port', 20003)
    config.save(file_path)
    config = SillyConfiguration()
    config.update(file_path)
    assert config.value('port') == 20003
