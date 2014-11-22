# coding=utf-8
"""
Python configuration encapsulation
==================================
Configuration objects that may container options or sub-configuration layers.

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

from __future__ import print_function

from . import errors
from .ConfigurationOption import ConfigurationOption


__all__ = [
    "Configuration",
]


class Configuration (object):
    """
    Container of options and sub-configurations

    Options may be accessed and set by either methods, bracket notation or
    dot notation. To use dot notation for getting/setting, the naming of the
    option must not conflict with named components of python class/instance
    (error raised).

    Option descriptions / comments may only be set via the set_option method or
    by accessing a set option.

    """

    def __init__(self, name=None):
        """ Initialize a new configuration block

        :param name: A name or None
        :type name: None or str

        """
        # because of use of __getattr__
        self.__dict__['_Configuration__name'] = name
        self.__dict__['_Configuration__options'] = {}

    @property
    def name(self):
        return self.__name

    def __repr__(self):
        return "Configuration{%s}" % self.name

    @staticmethod
    def __key_name(item):
        # given may be a string, ConfigurationOption or a Configuration. Extract
        # name and compare against our option keys (names).
        if isinstance(item, (Configuration, ConfigurationOption)):
            item_name = item.name
        elif isinstance(item, str):
            item_name = item
        else:
            raise errors.ConfigurationInvalidItemKeyTypeError()
        return item_name

    def get_option(self, key):
        """ option getter helper function
        """
        item_name = self.__key_name(key)
        if item_name in self.__options:
            return self.__options[item_name]
        else:
            raise errors.ConfigurationKeyNotPresentError(item_name)

    def set_option(self, key, value, descr=None):
        if isinstance(value, (Configuration, ConfigurationOption)):
            self.__options[key] = value
            if descr:
                self.__options[key].description = descr
        else:
            self.__options[key] = ConfigurationOption(key, value, descr)

    def __getitem__(self, key):
        """ option bracket access """
        return self.get_option(key)

    def __setitem__(self, key, value):
        """ Option bracket setter """
        return self.set_option(key, value)

    def __getattr__(self, key):
        """ Dot notation """
        return self.get_option(key)

    def __setattr__(self, key, value):
        # Check that we're not setting class or instance names
        if key in self.__dict__ or key in self.__class__.__dict__:
            raise errors.ConfigurationDotNotationSetError(key)
        self.set_option(key, value)

    def __contains__(self, item):
        return self.__key_name(item) in self.__options

    def __iter__(self):
        for k in self.__options:
            yield k

    def __len__(self):
        return len(self.__options)

    # TODO: Merge functionality
    # def __add__(self, other):
    #     if not isinstance(other, Configuration):
    #         raise ValueError("Cannot combine with something that is not "
    #                          "another Configuration instance.")
    #     c = Configuration(name='+'.join((self.name, other.name)))
    #     for s in self:
    #         for o in s:
    #             setattr(getattr(c, s()), o.name, o())
    #     for s in other:
    #         for o in s:
    #             setattr(getattr(c, s()), o.name, o())
    #     return c
    #
    # def __iadd__(self, other):
    #     if not isinstance(other, Configuration):
    #         raise ValueError("Cannot combine with something that is not "
    #                          "another Configuration instance.")
    #     for s in other:
    #         for o in s:
    #             setattr(getattr(self, s()), o.name, o())
    #     return self

    # TODO: Copy/Deepcopy methods
    # def __copy__(self):
    #     pass
    # def __deepcopy__(self, memo=None):
    #     pass



# TODO: Move the following to the io submodule + assert that to-file
#       configurations are strictly two levels (configuration of configurations
#       of only options) in order to fit INI format.
# def load_ini_configuration(*in_files, **kwds):
#     """ Load a configuration from one or more INI files.
#
#     The order in which files are specified matters. If multiple files in the
#     list have the same sections/options, the last file that defines them will
#     take precedence.
#
#     :param in_file: Files to initialize a Configuration object from.
#     :type in_file: tuple of str
#     :param partial_load_error: Flag telling us to error when input files are
#         only partially loaded. This is False by default (logging module warning
#         issued instead).
#     :type partial_load_error: bool
#
#     :return: Configuration object based on the input files
#     :rtype:
#
#     """
#     log = logging.getLogger('pyConfig.load_ini_configuration')
#
#     partial_load_error = kwds.get("partial_load_error", False)
#
#     scp_config = SafeConfigParser()
#     files_read = scp_config.read(in_files)
#     if set(in_files) != set(files_read):
#         if partial_load_error:
#             def log_func(msg):
#                 raise RuntimeError(msg)
#         else:
#             log_func = log.warn
#         log_func("Failed to load all given input files")
#
#     config = Configuration()
#     for sect in scp_config.sections():
#         for opt in scp_config.options(sect):
#             setattr(getattr(config, sect), opt, scp_config.get(sect, opt))
#     return config
#
#
# def save_ini_configuration(config, out_file):
#     """ Save a configuration to file using SafeConfigParser (INI file format)
#
#     :param config: Configuration object to save
#     :type config: Configuration
#     :param out_file: Output file path
#     :type out_file: str
#
#     :return: True if save was successful, false otherwise.
#     :rtype: bool
#
#     """
#     p = SafeConfigParser()
#     for s in config:
#         if s:
#             p.add_section(s())
#             for o in s:
#                 p.set(s(), o.name, o())
#     p.write(open(out_file, 'w'))
