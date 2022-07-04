.. _config:

:mod:`baldaquin.config` --- Configuration
=========================================

The module provides the abstract base class
:class:`ConfigurationBase <baldaquin.config.ConfigurationBase>`
that users can inherit from in order to create concrete configuration objects
with JSON I/O capabilities. This provides a convenient mechanism to create and
update configuration objects suiting any specific need.

The basic ideas behind the mechanism implemented here is that:

* each specific configuration has its own concrete class inheriting
  from :class:`ConfigurationBase <baldaquin.config.ConfigurationBase>`
  (which is achieved with no boilerplate code);
* the class contains a full set of default values for the configuration
  parameters, so that any instance of a configuration object is guaranteed to
  be valid at creation time---and, in addition, to remain valid as the parameter
  values are updated through the lifetime of the object;
* type consistency is automatically enforced whenever a parameter is set or
  updated;
* a minimal set of optional constraints can be enforced on any of the parameters;
* a configuration object can be serialized/deserialized in JSON format so that
  it can be written to file, and the parameter values can be updated from file.

In the remaining of this section we shall see how to declare, instantiate and
interact with concrete configuration objects.


Declaring a concrete configuration class
----------------------------------------

A simple, and yet fully functional, concrete configuration class for an
hypothetical network connection might look like the following snippet---all
you really have to do is to override the ``TITLE`` and ``PARAMETER_SPECS``
top-level class members.

.. code-block:: python

    class SillyConfiguration(ConfigurationBase):

        TITLE = 'Just a test configuration'
        PARAMETER_SPECS = (
            ('enabled', 'bool', True, 'Enable connection', {}),
            ('ip_address', 'str', '127.0.0.1', 'IP address', {}),
            ('port', 'int', 20004, 'UDP port', dict(min=1024, max=65535)),
            ('timeout', 'float', 10., 'Connection timeout [s]', dict(min=0.))
        )

While the ``TITLE`` thing is pretty much self-explaining, the parameter specification
deserves some more in-depth explanation. ``PARAMETER_SPECS`` is supposed to be
an iterable of 5-element tuples matching the
:class:`ConfigurationParameter <baldaquin.config.ConfigurationParameter>`
constructor, namely:

1. the paramater name (str);
2. the `name` of the parameter type (str);
3. the default value---note its type should match that indicated by the previous name;
4. an optional string expressing the intent of the parameter;
5. an optional dictionary encapsulating the constraints on the parameter values.

In this case we are saying that the integer ``port`` parameter should be
within 1024 and 65535, and that the floating-point ``timeout`` parameter should
be positive.

The supported optional constraints for the various data types are:

* ``choices``, ``step``, ``min`` and ``max`` for integers;
* ``min`` and ``max`` for floats;
* ``choices`` for strings.

(And if you look this closely enough you will recognize that the constraints
are designed so that the map naturally to the GUI widgets that might be used
to control the configuration, e.g., spin boxes for integers, and combo boxes for
strings to pulled out of a pre-defined list.)


Once you have a concrete class defined, you can instantiate an object, which will
come up set up and ready to use, with all the default parameter values.

>>> config = SillyConfiguration()
>>> print(configuration)
--------------------------------------------------------------------------------
Just a test configuration
--------------------------------------------------------------------------------
enabled.............: True
ip_address..........: 127.0.0.1
port................: 20004 {'min': 1024, 'max': 65535}
timeout.............: 10.0 {'min': 0.0}
--------------------------------------------------------------------------------

The :meth:`ConfigurationBase.write() <baldaquin.config.ConfigurationBase.write()>`
class method allows to encode the content of the configuration into a JSON
file looking like

.. code-block:: json

  {
      "enabled": {
          "name": "enabled",
          "type_name": "bool",
          "value": true,
          "intent": "Enable connection",
          "constraints": {}
      },
      "ip_address": {
          "name": "ip_address",
          "type_name": "str",
          "value": "127.0.0.1",
          "intent": "IP address",
          "constraints": {}
      },
      "port": {
          "name": "port",
          "type_name": "int",
          "value": 20003,
          "intent": "UDP port",
          "constraints": {
              "min": 1024,
              "max": 65535
          }
      },
      "timeout": {
          "name": "timeout",
          "type_name": "float",
          "value": 10.0,
          "intent": "Connection timeout [s]",
          "constraints": {
              "min": 0.0
          }
      }
  }

and this is the basic mechanism through which applications will interact with
configuration objects, with
:meth:`ConfigurationBase.read() <baldaquin.config.ConfigurationBase.read()>`
allowing to update an existing configuration from a JSON file with the proper
format.


Module documentation
--------------------

.. automodule:: baldaquin.config
