# coding=utf-8
"""
Python configuration encapsulation
==================================

Designed for easy dynamic access. Currently adheres to the INI file format of
a single layer of sections, with each section containing option/value pairs.

Configuration and section objects have no callable methods in order to allow
simple dynamic access (the option classes have functions to access option name
and value casting).

Plans
-----
Move away from INI file format and into nested structure configuration, allowing
ability to nest sections (ConfigItem base class, options + sections are
children).

License (MIT)
=============
Copyright (c) 2014 Paul Tunison

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

from ConfigParser import SafeConfigParser
import logging


__all__ = [
    "Configuration",
    "load_ini_configuration",
    "save_ini_configuration",
]


class ConfigOption (object):
    """ Light encapsulation of a configuration option
    """

    def __init__(self, name, value=None, description=None):
        self.__option_name = name
        self.__option_value = value
        self.__option_description = description

    def __call__(self):
        """
        :return: Option value in native format
        """
        return self.__option_value

    @property
    def name(self):
        return self.__option_name

    @property
    def description(self):
        return self.__option_description

    @description.setter
    def description(self, value):
        self.__option_description = str(value)

    def __repr__(self):
        return "ConfigOption{%s, %s}" % (self.__option_name,
                                         self.__option_value)

    @property
    def str(self):
        """
        :return: Option value as a string
        :rtype: str
        """
        return str(self.__option_value)

    @property
    def __str__(self):
        return self.str

    @property
    def int(self):
        """
        :return: Option value as an int
        :rtype: int
        """
        return int(self.__option_value)

    def __int__(self):
        return self.int

    @property
    def float(self):
        """
        :return: Option value as a float
        :rtype: float
        """
        return float(self.__option_value)

    def __float__(self):
        return self.float

    @property
    def bool(self):
        """
        :return: Option value as a boolean
        :rtype: bool
        """
        return bool(self.__option_value)

    def __nonzero__(self):
        return self.bool


class ConfigSection (object):
    """ Light encapsulation of a configuration section """

    def __init__(self, name):
        # preventing infinite loop with presence of get/setattr functions
        self.__dict__['_ConfigSection__section_name'] = name
        self.__dict__['_ConfigSection__section_options'] = {}

    def __repr__(self):
        return "ConfigSection{%s, %s}" % (self.__section_name,
                                          self.__section_options.values())

    def __call__(self):
        return self.__section_name

    def __contains__(self, opt):
        if isinstance(opt, ConfigOption):
            return opt in self.__section_options.values()
        # else assuming its a key
        return opt in self.__section_options

    def __getattr__(self, opt):
        """ Get the value of an option in this section """
        return self.__section_options[opt]

    def __setattr__(self, key, value):
        """ Set the given key and value to this section """
        if not isinstance(value, ConfigOption):
            value = ConfigOption(key, value)
        self.__section_options[key] = value

    def __iter__(self):
        for v in self.__section_options.itervalues():
            yield v

    def __len__(self):
        return len(self.__section_options)


class Configuration (object):
    """
    Configuration encapsulation object with IO capabilities based on INI file
    configuration.

    Uses the SafeConfigCommentParser object for IO.

    """

    def __init__(self, name=None):
        """
        Initialize a new configuration.

        Optionally, a configuration file path may be provided to initialize
        from. When this is done, we cannot infer the option value types, so all
        options are loaded in as strings.

        """
        self.__dict__['_Configuration__name'] = name or "Configuration"
        self.__dict__['_Configuration__sections'] = {}

    def __get_section(self, sect):
        if sect not in self.__sections:
            self.__sections[sect] = ConfigSection(sect)
        return self.__sections[sect]

    def __repr__(self):
        return "Configuration{%s, %s}" % (self.__name,
                                          self.__sections.values())

    def __str__(self):
        ret_str = "{{ Configuration - %s }}\n" % self.__name
        for s in self:
            ret_str += "[%s]\n" % s()
            for o in s:
                ret_str += "  %s = %s\n" % (o.name, o())
        return ret_str

    def __call__(self):
        return self.__name

    def __getattr__(self, item):
        """ dot access """
        return self.__get_section(item)

    def __getitem__(self, item):
        """ bracket access """
        return self.__get_section(item)

    def __contains__(self, item):
        if isinstance(item, ConfigSection):
            return item in self.__sections.values()
        # else assuming its a section key
        return item in self.__sections

    def __iter__(self):
        for v in self.__sections.itervalues():
            yield v

    def __add__(self, other):
        if not isinstance(other, Configuration):
            raise ValueError("Cannot combine with something that is not "
                             "another Configuration instance.")
        c = Configuration(name='+'.join((self(), other())))
        for s in self:
            for o in s:
                setattr(getattr(c, s()), o.name, o())
        for s in other:
            for o in s:
                setattr(getattr(c, s()), o.name, o())
        return c

    def __iadd__(self, other):
        if not isinstance(other, Configuration):
            raise ValueError("Cannot combine with something that is not "
                             "another Configuration instance.")
        for s in other:
            for o in s:
                setattr(getattr(self, s()), o.name, o())
        return self

    def __len__(self):
        return len(self.__sections)


def load_ini_configuration(*in_files, **kwds):
    """ Load a configuration from one or more INI files.

    The order in which files are specified matters. If multiple files in the
    list have the same sections/options, the last file that defines them will
    take precedence.

    :param in_file: Files to initialize a Configuration object from.
    :type in_file: tuple of str
    :param partial_load_error: Flag telling us to error when input files are
        only partially loaded. This is False by default (logging module warning
        issued instead).
    :type partial_load_error: bool

    :return: Configuration object based on the input files
    :rtype:

    """
    log = logging.getLogger('pyConfig.load_ini_configuration')

    partial_load_error = kwds.get("partial_load_error", False)

    scp_config = SafeConfigParser()
    files_read = scp_config.read(in_files)
    if set(in_files) != set(files_read):
        if partial_load_error:
            def log_func(msg):
                raise RuntimeError(msg)
        else:
            log_func = log.warn
        log_func("Failed to load all given input files")

    config = Configuration()
    for sect in scp_config.sections():
        for opt in scp_config.options(sect):
            setattr(getattr(config, sect), opt, scp_config.get(sect, opt))
    return config


def save_ini_configuration(config, out_file):
    """ Save a configuration to file using SafeConfigParser (INI file format)

    :param config: Configuration object to save
    :type config: Configuration
    :param out_file: Output file path
    :type out_file: str

    :return: True if save was successful, false otherwise.
    :rtype: bool

    """
    p = SafeConfigParser()
    for s in config:
        if s:
            p.add_section(s())
            for o in s:
                p.set(s(), o.name, o())
    p.write(open(out_file, 'w'))
