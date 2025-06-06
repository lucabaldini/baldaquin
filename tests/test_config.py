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

"""Test suite for config.py
"""

import json

import pytest

from baldaquin import logger, DEFAULT_CHARACTER_ENCODING
from baldaquin import BALDAQUIN_DATA
from baldaquin import config


def _test_base_match(type_name, value, **constraints):
    """Base test function where we expect the parameter to match the input value.
    """
    p = config.ConfigurationParameter('parameter', type_name, value, '', **constraints)
    assert p.value == value


def _test_base_mismatch(type_name, value, **constraints):
    """Base test function where we expect the parameter to match the input value.
    """
    with pytest.raises(RuntimeError) as info:
        config.ConfigurationParameter('parameter', type_name, value, '', **constraints)
    logger.info(info.value)


def test_print_parameters():
    """Print some parameters.
    """
    print(config.ConfigurationParameter('timeout', float, 10., 'timeout'))
    print(config.ConfigurationParameter('timeout', float, 10., 'timeout', 's', '.6f', min=0.))


def test_parameter_bool():
    """Test possible setting for int parameters.
    """
    for value in (True, False):
        _test_base_match(bool, value)
    for value in (1, 1., 'test'):
        _test_base_mismatch(bool, value)


def test_parameter_int(value=100):
    """Test possible settings for int parameters.
    """
    _test_base_match(int, 100)
    _test_base_match(int, 100, min=0, max=1000)
    _test_base_mismatch(int, 100, min=200)
    _test_base_mismatch(int, 100, max=0)
    _test_base_match(int, 100, choices=(99, 100, 101))
    _test_base_mismatch(int, 100, choices=(99, 101))
    _test_base_match(int, 100, step=10)
    _test_base_mismatch(int, 100, step=13)
    _test_base_match(int, 100, min=87, step=13)


def test_parameter_float(value=1.):
    """Test possible settings for int parameters.
    """
    _test_base_match(float, 1.)
    _test_base_match(float, 1., min=0., max=10.)
    _test_base_mismatch(float, 1., min=10.)
    _test_base_mismatch(float, 1., max=0.)


def test_parameter_str():
    """Test possible settings for int parameters.
    """
    _test_base_match(str, 'howdy?')
    _test_base_match(str, 'eggs', choices=('eggs', 'cheese'))
    _test_base_mismatch(str, 'ham', choices=('eggs', 'cheese'))
    for value in (True, 1, 1.):
        _test_base_mismatch(str, value)


def test_format():
    """Test the formatted_value() method of the ConfigurationParameter class.
    """
    p = config.ConfigurationParameter('timeout', float, 10., 'timeout', 's', '.6f')
    print(p.value)
    print(p.formatted_value())


def test_configuration_sections():
    """Test the configuration sections.
    """
    section = config.LoggingConfigurationSection()
    print(section)
    section.set_value('terminal_level', 'DEBUG')
    assert section.value('terminal_level') == 'DEBUG'
    with pytest.raises(RuntimeError) as info:
        section.set_value('terminal_level', 'PHONY')
    logger.info(info.value)
    assert section.value('terminal_level') == 'DEBUG'
    section.set_value('terminal_level', 'INFO')
    assert section.value('terminal_level') == 'INFO'
    with pytest.raises(RuntimeError) as info:
        section.set_value('dummy', 'PHONY')
    logger.info(info.value)
    print(section.as_dict())
    section = config.BufferingConfigurationSection()
    print(section)
    section = config.MulticastConfigurationSection()
    print(section)


def test_application_configuration():
    """Test on the basic baldaquin configuration.
    """
    conf = config.UserApplicationConfiguration()
    print(conf)
    file_path = BALDAQUIN_DATA / 'baldaquin.cfg'
    conf.save(file_path)
    conf['Logging'].set_value('terminal_level', 'CRITICAL')
    print(conf)
    assert conf['Logging'].value('terminal_level') == 'CRITICAL'
    conf.update_from_file(file_path)
    print(conf)
    assert conf['Logging'].value('terminal_level') == 'DEBUG'


def _write_configuration_dict(file_path: str, data: dict) -> None:
    """Utility function to write a configuration dictionary to disk.
    """
    logger.info(f'Writing configuration dictionary to {file_path}...')
    logger.info(data)
    with open(file_path, 'w', encoding=DEFAULT_CHARACTER_ENCODING) as output_file:
        output_file.write(json.dumps(data, indent=4))


def test_resilience():
    """Test the resilience of the configuration mechanism to format changes.
    """
    conf = config.UserApplicationConfiguration()
    print(conf)
    file_path = BALDAQUIN_DATA / 'resilience.cfg'
    # Add an unknown section.
    data = conf.as_dict()
    data['Fake'] = {'fake_field': 3}
    _write_configuration_dict(file_path, data)
    conf.update_from_file(file_path)
    # Add an unknown field in a legitimate section.
    data = conf.as_dict()
    data['Logging'] = {'fake_field': 3}
    _write_configuration_dict(file_path, data)
    conf.update_from_file(file_path)
    # Set a wrong value for a legitimate parameter.
    data = conf.as_dict()
    data['Logging'] = {'terminal_level': 'FAKE'}
    _write_configuration_dict(file_path, data)
    conf.update_from_file(file_path)
