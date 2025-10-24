.. _config:

:mod:`~baldaquin.config` --- Configuration
==========================================

The module provides facilities to create, modify, read and write configuration
objects. The basic ideas behind the mechanism implemented here is that:

* configurations are split into sections; more specifically, top-level configuration
  objects are instances of the :class:`Configuration <baldaquin.config.Configuration>`
  class, and each section is an instance of a class inheriting from the abstract
  base class :class:`ConfigurationSectionBase <baldaquin.config.ConfigurationSectionBase>`.
* the configuration section contains a full set of default values for the configuration
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


Declaring configuration sections
--------------------------------

The module comes with a number of pre-defined configuration sections that are
generally useful. Basically, all you have to do is to inherit from the abstract
base class :class:`ConfigurationSectionBase <baldaquin.config.ConfigurationSectionBase>`
and override the ``TITLE`` and ``_PARAMETER_SPECS`` top-level class members.

.. literalinclude:: ../src/baldaquin/config.py
   :pyobject: MulticastConfigurationSection

.. literalinclude:: ../src/baldaquin/config.py
   :pyobject: BufferingConfigurationSection

.. literalinclude:: ../src/baldaquin/config.py
   :pyobject: LoggingConfigurationSection

The ``TITLE`` thing is pretty much self-explaining; ``PARAMETER_SPECS`` is
supposed to be an iterable of tuples matching the
:class:`ConfigurationParameter <baldaquin.config.ConfigurationParameter>`
constructor, namely:

1. the parameter name (``str``);
2. the parameter type (``type``);
3. the default value---note its type should match that indicated by the previous field;
4. a string expressing the intent of the parameter;
5. an optional string indicating the physical units of the parameter value (optional);
6. an optional format string for the preferred text rendering of the value (optional);
7. an optional dictionary encapsulating the constraints on the possible parameter
   values (optional).

The rules for parsing the specifications are simple: if the last element of the
tuple is a dictionary we take it as containing all the keyword arguments for the
corresponding parameters; all the other elements are taken to be positional arguments,
in the order specified above. (Note only the first four elements are mandatory.)

The supported constraints are listed in the ``_VALID_CONSTRAINTS`` class variable
of the :class:`ConfigurationParameter <baldaquin.config.ConfigurationParameter>`
class, and they read:

.. literalinclude:: ../src/baldaquin/config.py
   :start-after: # Start definition of valid constraints.
   :end-before: # End definition of valid constraints.

(And if you look this closely enough you will recognize that the constraints
are designed so that the map naturally to the GUI widgets that might be used
to control the configuration, e.g., spin boxes for integers, and combo boxes for
strings to pulled out of a pre-defined list.) Constraints are generally checked and
runtime, and a ``RuntimeError`` is raised if any problem occurs.



Declaring configuration objects
-------------------------------

You can simply take it from here, and declare fully-fledged configuration objects
by just instantiating the :class:`Configuration <baldaquin.config.Configuration>`
class, passing the configuration sections you want to include as arguments.

That said, given how baldaquin is structured, your configuration will likely
contain a number of sections that are common to all the applications (e.g., logging,
buffering, multicasting) and one or more section that is specific to the particular
user application at hand. This common use case is handled by the
:class:`UserApplicationConfiguration <baldaquin.config.UserApplicationConfiguration>`
class, which is again a base class for usable application configuration objects.

By default it comes with no parameters in the user application section, but you
can change that by overriding the ``_PARAMETER_SPECS`` class variable, just like
you did for the configuration sections.

Once you have a concrete class defined, you can instantiate an object, which will
come up set up and ready to use, with all the default parameter values.

>>> config = UserApplicationConfiguration()
>>> print(config)
----------Logging-------------
terminal_level...... INFO
file_enabled........ True
file_level.......... INFO
----------Buffering-----------
max_size............ 1000000
flush_size.......... 100
flush_timeout....... 10.000 s
----------Multicast-----------
enabled............. False
ip_address.......... 127.0.0.1
port................ 20004
----------User Application----

Programmatically, you can retrieve the value of a specific parameter through the
:meth:`value() <baldaquin.config.ConfigurationSectionBase.value()>` class method, and update
the value with :meth:`set_value() <baldaquin.config.ConfigurationSectionBase.set_value()>`.


The :meth:`save() <baldaquin.config.Configuration.save()>` method allows to
dump the (JSON-encoded) content of the configuration into file looking like

.. code-block:: json

  {
      "Logging": {
          "terminal_level": "INFO",
          "file_enabled": true,
          "file_level": "INFO"
      },
      "Buffering": {
          "max_size": 1000000,
          "flush_size": 100,
          "flush_timeout": 10.0
      },
      "Multicast": {
          "enabled": false,
          "ip_address": "127.0.0.1",
          "port": 20004
      },
      "User Application": {}
  }

and this is the basic mechanism through which applications will interact with configuration objects,
with :meth:`update_from_file() <baldaquin.config.Configuration.update_from_file()>`
allowing to update an existing configuration from a JSON file with the proper format.

.. note::

   Keep in mind that configurations are never `read` from file---they come
   to life with all the parameters set to their default values, and then they
   can be `updated` from a JSON file.

   When you think about, this makes extending and/or modifying existing
   configurations much easier as, once the concrete class is changed, all
   existing configuration files are automatically updated transparently, and
   in case one edits a file by hand, any mistake will be promptly signaled
   (and corrected) without compromising the validity of the configuration object.


Module documentation
--------------------

.. automodule:: baldaquin.config
