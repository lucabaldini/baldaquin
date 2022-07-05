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

"""Configuration facilities.
"""

import enum
import json
import os
from typing import Any

from loguru import logger



class ParameterValidationError(enum.IntEnum):

    """Enum class for the possible errors occurring while checking the input
    parameter values.
    """

    PARAMETER_VALID = 0
    INVALID_TYPE = enum.auto()
    NUMBER_TOO_SMALL = enum.auto()
    NUMBER_TOO_LARGE = enum.auto()
    INVALID_CHOICE = enum.auto()
    INVALID_STEP = enum.auto()
    GENERIC_ERROR = enum.auto()



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

    type_name : str
        The name of the parameter type.

    value : anything
        The parameter value.

    intent : str (optional)
        The intent of the parameter, acting as a comment in the corresponding
        configuration file.

    constraints : dict (optional)
        A dictionary containing optional specifications on the parameter value.
    """

    VALID_CONSTRAINTS = {
        'int' : ('choices', 'step', 'min', 'max'),
        'float' : ('min', 'max'),
        'str': ('choices',)
    }

    def __init__(self, name : str, type_name : str, value : Any, intent : str = None,
        **constraints) -> None:
        """Constructor.
        """
        self.name = name
        self.type_name = type_name
        self.value = None
        self.intent = intent
        for key in tuple(constraints):
            if key not in self.VALID_CONSTRAINTS.get(self.type_name, ()):
                logger.warning(f'Invalid spec ({key}) for {self.name} ({self.type_name})...')
                constraints.pop(key)
        self.constraints = constraints
        self.set_value(value)

    def not_set(self) -> bool:
        """Return true if the parameter value is not set.
        """
        return self.value is None

    def _validation_error(self, value : Any, error_code : ParameterValidationError) \
        -> ParameterValidationError:
        """Utility function to log a parameter error (and forward the error code).
        """
        logger.error(f'Value {value} invalid for {self.name} {self.constraints}: {error_code.name}')
        logger.error('Parameter value will not be set')
        return error_code

    def _check_range(self, value : Any) -> ParameterValidationError:
        """Generic function to check that a given value is within a specified range.

        This is used for validating int and float parameters.
        """
        if 'min' in self.constraints and value < self.constraints['min']:
            return self._validation_error(value, ParameterValidationError.NUMBER_TOO_SMALL)
        if 'max' in self.constraints and value > self.constraints['max']:
            return self._validation_error(value, ParameterValidationError.NUMBER_TOO_LARGE)
        return ParameterValidationError.PARAMETER_VALID

    def _check_choice(self, value : Any) -> ParameterValidationError:
        """Generic function to check that a parameter value is within the
        allowed choices.
        """
        if 'choices' in self.constraints and value not in self.constraints['choices']:
            return self._validation_error(value, ParameterValidationError.INVALID_CHOICE)
        return ParameterValidationError.PARAMETER_VALID

    def _check_step(self, value : int) -> ParameterValidationError:
        """Generic function to check the step size for an integer.
        """
        delta = value - self.constraints.get('min', 0)
        if 'step' in self.constraints and delta % self.constraints['step'] != 0:
            return self._validation_error(value, ParameterValidationError.INVALID_STEP)
        return ParameterValidationError.PARAMETER_VALID

    def _check_int(self, value : int) -> ParameterValidationError:
        """Validate an integer parameter value.

        Note we check the choice specification first, and all the others after that
        (this is relevant as, if you provide inconsistent conditions the order
        becomes relevant).
        """
        for check in (self._check_choice, self._check_range, self._check_step):
            error_code = check(value)
            if error_code != ParameterValidationError.PARAMETER_VALID:
                return error_code
        return ParameterValidationError.PARAMETER_VALID

    def _check_float(self, value : float) -> ParameterValidationError:
        """Validate a floating-point parameter value.
        """
        return self._check_range(value)

    def _check_str(self, value : str) -> ParameterValidationError:
        """Validate a string parameter value.
        """
        return self._check_choice(value)

    def set_value(self, value : Any) -> ParameterValidationError:
        """Set the paramater value.
        """
        # Make sure that type(value) matches the expectations.
        if value.__class__.__name__ != self.type_name:
            return self._validation_error(value, ParameterValidationError.INVALID_TYPE)
        # If a validator is defined for the specific parameter type, apply it.
        func_name = f'_check_{self.type_name}'
        if hasattr(self, func_name):
            error_code = getattr(self, func_name)(value)
            if error_code:
                return error_code
        # And if we made it all the way to this point we're good to go :-)
        self.value = value
        return ParameterValidationError.PARAMETER_VALID

    def __str__(self):
        """String formatting.
        """
        return f'{self.name:.<20}: {self.value} {self.constraints if len(self.constraints) else ""}'



class ConfigurationBase(dict):

    """Base class for configuration data structures.

    The basic idea, here, is that specific configuration classes simply override
    the ``TITLE`` and ``PARAMETER_SPECS`` class members. ``PARAMETER_SPECS``, particulalry,
    encodes the name, types and default values for all the configuration parameters,
    as well optional help strings and parameter constraints.

    Configuration objects provide file I/O through the JSON protocol. One
    important notion, here, is that configuration objects are always created
    in place with all the parameters set to their default values, and then updated
    from a configuration file. This ensures that the configuration is always
    valid, and provides an effective mechanism to be robust against updates of
    the configuration structure.
    """

    TITLE = 'Configuration'
    PARAMETER_SPECS = []

    def __init__(self) -> None:
        """Constructor.
        """
        super().__init__()
        for *args, constraints in self.PARAMETER_SPECS:
            self.add_parameter(*args, **constraints)

    def add_parameter(self, *args, **kwargs) -> None:
        """Add a new parameter to the configuration.
        """
        parameter = ConfigurationParameter(*args, **kwargs)
        self[parameter.name] = parameter

    def value(self, key) -> Any:
        """Return the value for a given parameter.
        """
        return self[key].value

    def update_value(self, key, value) -> ParameterValidationError:
        """Update the value of a configuration parameter.
        """
        return self[key].set_value(value)

    def update(self, file_path : str) -> None:
        """Update the configuration parameters from a JSON file.
        """
        logger.info(f'Updating configuration from {file_path}...')
        with open(file_path, 'r') as input_file:
            data = json.load(input_file)
        for key, param_dict in data.items():
            self.update_value(key, param_dict['value'])

    def to_json(self) -> str:
        """Encode the configuration into JSON to be written to file.
        """
        data = {key: value.__dict__ for key, value in self.items()}
        return json.dumps(data, indent=4)

    def save(self, file_path) -> None:
        """Dump the configuration to a JSON file.
        """
        logger.info(f'Writing configuration to {file_path}...')
        with open(file_path, 'w') as output_file:
            output_file.write(self.to_json())

    @staticmethod
    def terminal_line(character : str = '-', default_length : int = 50) -> str:
        """Concatenate a series of characters as long as the terminal line.

        Note that we need the try/except block to get this thing working into
        pytest---see https://stackoverflow.com/questions/63345739
        """
        try:
            return character * os.get_terminal_size().columns
        except OSError:
            return character * default_length

    @staticmethod
    def title(text : str) -> str:
        """Pretty-print title.
        """
        line = ConfigurationBase.terminal_line()
        return f'{line}\n{text}\n{line}'

    def __str__(self) -> str:
        """String formatting.
        """
        title = self.title(self.TITLE)
        data = ''.join(f'{param}\n' for param in self.values())
        line = self.terminal_line()
        return f'{title}\n{data}{line}'
