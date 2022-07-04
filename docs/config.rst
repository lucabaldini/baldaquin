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


.. code-block:: python

    class SillyConfiguration(ConfigurationBase):

        TITLE = 'Just a test configuration'
        PARAMETER_SPECS = (
            ('enabled', 'bool', True, 'Enable connection', {}),
            ('ip_address', 'str', '127.0.0.1', 'IP address', {}),
            ('port', 'int', 20004, 'UDP port', dict(min=1024, max=65535)),
            ('timeout', 'float', 10., 'Connection timeout [s]', dict(min=0.))
        )


One can then instantiate an object of this concrete class, which will come up
set up and ready to use, with all the default parameter values.

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


Module documentation
--------------------

.. automodule:: baldaquin.config
