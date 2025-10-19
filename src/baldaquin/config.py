# Copyright (C) 2022--2025 the baldaquin team.
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

"""Configuration facilities.
"""

import datetime
import json
from pathlib import Path
from typing import Any

from .env import BALDAQUIN_DATA, BALDAQUIN_ENCODING
from .logging_ import logger


class ConfigurationParameter:

    """Class representing a configuration parameter.

    This is a simple attempt at putting in place a generic configuration mechanism
    where we have some control on the values we are passing along.

    A configuration parameter is fully specified by its name, type and value, and
    When setting the latter, we make sure that the its type matches.
    Additional, we can specify simple conditions on the parameters that are
    then enforced at runtime.

    Arguments
    ---------
    name : str
        The parameter name.

    type_ : type
        The parameter type.

    value : anything
        The parameter value.

    intent : str
        The intent of the parameter, acting as a comment in the corresponding
        configuration file.

    units : str, optional
        The units for the configuration parameter.

    fmt : str, optional
        An optional format string for the preferred rendering the parameter value.

    constraints : dict, optional
        A dictionary containing optional specifications on the parameter value.
    """

    # Do not remove the following comments, they are used by sphinx to generate the
    # documentation, see https://stackoverflow.com/questions/31561895
    # Start definition of valid constraints.
    _VALID_CONSTRAINTS = {
        int: ("choices", "step", "min", "max"),
        float: ("min", "max"),
        str: ("choices",)
    }
    # End definition of valid constraints.

    def __init__(self, name: str, type_: type, value: Any, intent: str,
                 units: str = None, fmt: None = None, **constraints) -> None:
        """Constructor.
        """
        self.name = name
        self.type = type_
        self.value = None
        self.intent = intent
        self.units = units
        self.fmt = fmt
        for key in tuple(constraints):
            if key not in self._VALID_CONSTRAINTS.get(self.type, ()):
                raise RuntimeError(f"Invalid spec ({key}) for {self.name} ({self.type})")
        self.constraints = constraints
        self.set_value(value)

    def _check_range(self, value: Any) -> None:
        """Generic function to check that a given value is within a specified range.
        """
        if "min" in self.constraints and value < self.constraints["min"]:
            raise RuntimeError(f"Value {value} is too small for {self}")
        if "max" in self.constraints and value > self.constraints["max"]:
            raise RuntimeError(f"Value {value} is too large for {self}")

    def _check_choices(self, value: Any) -> None:
        """Generic function to check that a parameter value is within the
        allowed choices.
        """
        if "choices" in self.constraints and value not in self.constraints["choices"]:
            raise RuntimeError(f"Unexpected choice {value} for {self}")

    def _check_step(self, value: int) -> None:
        """Generic function to check the step size for an integer.
        """
        delta = value - self.constraints.get("min", 0)
        if "step" in self.constraints and delta % self.constraints["step"] != 0:
            raise RuntimeError(f"Invalid value {value} for {self}")

    def set_value(self, value: Any) -> None:
        """Set the parameter value.

        Note that this is where all the runtime checking is performed.
        """
        # Make sure that the value we are passing is of the right type.
        if not isinstance(value, self.type):
            raise RuntimeError(f"Invalid type {value} ({type(value).__name__}) for {self}")
        # Make all the necessary checks on the constraints, if necessary.
        if self.constraints:
            if self.type is int:
                self._check_choices(value)
                self._check_range(value)
                self._check_step(value)
            elif self.type is float:
                self._check_range(value)
            elif self.type is str:
                self._check_choices(value)
        # And if we made it all the way to this point we're good to go :-)
        self.value = value

    def formatted_value(self) -> str:
        """Return the formatted parameter value (as a string).
        """
        if self.fmt is None:
            return f"{self.value}"
        return f"{self.value:{self.fmt}}"

    def pretty_print(self) -> str:
        """Return a pretty-printed string representation of the parameter.
        """
        text = f"{self.name:.<30} {self.formatted_value()}"
        if self.units:
            text += f" {self.units}"
        return text

    def __str__(self):
        """String formatting.
        """
        return f'{self.__class__.__name__} "{self.name}" ({self.type.__name__}, {self.constraints})'


class ConfigurationSectionBase(dict):

    """Base class for a single section of a configuration object. (Note this class
    is not meant to be instantiated, but rather subclassed, overriding the proper
    class variables as explained below.)

    The basic idea, here, is that specific configuration classes simply override
    the ``TITLE`` and ``_PARAMETER_SPECS`` class members, the latter encoding
    the name, type and default values for all the configuration parameters, as well
    as optional help strings and constraints.

    The class interface is fairly minimal, with support to set, and retrieve
    parameter values, and for string formatting.
    """

    TITLE = None
    _PARAMETER_SPECS = ()

    def __init__(self) -> None:
        """Constructor.
        """
        super().__init__()
        # Parse the parameters specs. The basic rule, here, is that if the last
        # element in the spec tuple is a dictionary, we are interpreting it the
        # map of constraints for the parameter, which is otherwise empty.
        # Everything else represent the constructor arguments, in order.
        for specs in self._PARAMETER_SPECS:
            if isinstance(specs[-1], dict):
                args, constraints = specs[:-1], specs[-1]
            else:
                args, constraints = specs, {}
            parameter = ConfigurationParameter(*args, **constraints)
            self[parameter.name] = parameter

    def set_value(self, parameter_name, value) -> None:
        """Update the value of a configuration parameter.
        """
        try:
            # Note all the runtime checking happens in ConfigurationParameter.set_value()
            self[parameter_name].set_value(value)
        except KeyError as exc:
            raise RuntimeError(f'Unknown parameter "{parameter_name}" for '
                               f'{self.__class__.__name__} "{self.TITLE}"') from exc

    def value(self, parameter_name) -> Any:
        """Return the value for a given parameter.
        """
        return self[parameter_name].value

    def formatted_value(self, parameter_name) -> str:
        """Return the formatted value for a given parameter.
        """
        return self[parameter_name].formatted_value()

    def as_dict(self):
        """Return a view on the configuration in the form of a {name: value} dictionary
        representing the underlying configuration parameters.

        This is used downstream to serialize the configuration and writing it to
        file.
        """
        return {parameter.name: parameter.value for parameter in self.values()}

    def __str__(self) -> str:
        """String formatting.
        """
        data = "".join(f"{param.pretty_print()}\n" for param in self.values())
        return f"---------------{self.TITLE:-<25}\n{data}"


class LoggingConfigurationSection(ConfigurationSectionBase):

    """Configuration section for the logging.
    """

    TITLE = "Logging"
    _LOGGING_LEVELS = ("TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL")
    _PARAMETER_SPECS = (
        ("terminal_level", str, "DEBUG", "Terminal logging level", dict(choices=_LOGGING_LEVELS)),
        ("file_level", str, "DEBUG", "File logging level", dict(choices=_LOGGING_LEVELS))
    )


class BufferingConfigurationSection(ConfigurationSectionBase):

    """Configuration section for the packet buffering.
    """

    TITLE = "Buffering"
    _PARAMETER_SPECS = (
        ("flush_size", int, 100, "Flush size", dict(min=1)),
        ("flush_timeout", float, 10., "Flush timeout", "s", ".3f", dict(min=1.))
    )


class MulticastConfigurationSection(ConfigurationSectionBase):

    """Configuration section for the packet multicasting.
    """

    TITLE = "Multicast"
    _PARAMETER_SPECS = (
        ("enabled", bool, False, "Enable multicast"),
        ("ip_address", str, "127.0.0.1", "IP address"),
        ("port", int, 20004, "Port", dict(min=1024, max=65535))
    )


class Configuration(dict):

    """Class describing a configuration object, that is, a dictionary of
    instances of ConfigurationSectionBase subclasses.

    Configuration objects provide file I/O through the JSON protocol. One
    important notion, here, is that configuration objects are always created
    in place with all the parameters set to their default values, and then updated
    from a configuration file. This ensures that the configuration is always
    valid, and provides an effective mechanism to be robust against updates of
    the configuration structure.
    """

    def __init__(self, *sections: ConfigurationSectionBase) -> None:
        """Constructor.
        """
        super().__init__()
        for section in sections:
            self.add_section(section)

    def add_section(self, section: ConfigurationSectionBase) -> None:
        """Add a section to the configuration.
        """
        self[section.TITLE] = section

    def update_from_file(self, file_path: str) -> None:
        """Update the configuration dictionary from a JSON file.

        Note we try and catch here all the possible exceptions while updating a
        file, and if anything happens during the update we create a timestamped
        copy of the original file so that the thing can be debugged at later time.
        The contract is that the update always proceeds to the end, and all the
        fields that can be legitimately updated get indeed updated.
        """
        logger.info(f"Updating configuration from {file_path}...")
        with open(file_path, encoding=BALDAQUIN_ENCODING) as input_file:
            data = json.load(input_file)
        errors = False
        for title, section_data in data.items():
            try:
                section = self[title]
            except KeyError:
                logger.warning(f'Unknown configuration section "{title}"')
                errors = True
                continue
            for parameter_name, value in section_data.items():
                try:
                    section.set_value(parameter_name, value)
                except RuntimeError as exc: # noqa: PERF203
                    logger.warning(exc)
                    errors = True
        if errors:
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S.%f")
            file_name = f"{Path(file_path).name}.backup.{timestamp}"
            dest = BALDAQUIN_DATA / file_name
            logger.warning(f"Error(s) during update, copying original file to {dest}...")

    def as_dict(self) -> dict:
        """Return a view on the configuration in the form of a dictionary that
        can be used for serialization.
        """
        return {title: section.as_dict() for title, section in self.items()}

    def to_json(self, indent: int = 4) -> str:
        """Encode the configuration into JSON to be written to file.
        """
        return json.dumps(self.as_dict(), indent=indent)

    def save(self, file_path: str) -> None:
        """Dump the configuration dictionary to a JSON file.
        """
        logger.info(f"Writing configuration dictionary to {file_path}...")
        with open(file_path, "w", encoding=BALDAQUIN_ENCODING) as output_file:
            output_file.write(self.to_json())

    def __str__(self):
        """String formatting.
        """
        text = "".join(f"{section}" for section in self.values())
        return text.strip("\n")


class UserApplicationConfiguration(Configuration):

    """Base class for a generic user application configuration.
    """

    _USER_APPLICATION_SECTION_TITLE = "User Application"
    _PARAMETER_SPECS = ()

    def __init__(self) -> None:
        """Constructor.
        """
        super().__init__()
        self.add_section(LoggingConfigurationSection())
        self.add_section(BufferingConfigurationSection())
        self.add_section(MulticastConfigurationSection())

        class _UserApplicationConfigurationSection(ConfigurationSectionBase):

            TITLE = self._USER_APPLICATION_SECTION_TITLE
            _PARAMETER_SPECS = self._PARAMETER_SPECS

        self.add_section(_UserApplicationConfigurationSection())

    def overwrite_section(self, section: ConfigurationSectionBase) -> None:
        """Overwrite a section in the configuration.
        """
        if section.TITLE not in self:
            raise RuntimeError(f'Unknown section "{section.TITLE}" for '
                               f'{self.__class__.__name__}')
        self[section.TITLE] = section

    def logging_section(self):
        """Return the logging section of the configuration.
        """
        return self[LoggingConfigurationSection.TITLE]

    def buffering_section(self):
        """Return the buffering section of the configuration.
        """
        return self[BufferingConfigurationSection.TITLE]

    def multicast_section(self):
        """Return the multicast section of the configuration.
        """
        return self[MulticastConfigurationSection.TITLE]

    def application_section(self):
        """Return the user application section of the configuration.
        """
        return self[self._USER_APPLICATION_SECTION_TITLE]
