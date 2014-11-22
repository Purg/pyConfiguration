__author__ = 'Purg'


### Configuration object errors ###############################################

class ConfigurationError (Exception):
    """
    Base class for errors dealing with Configuration objects.
    """
    pass


class ConfigurationInvalidItemKeyTypeError (ConfigurationError):
    """
    Exception for when an invalid item key for option access is provided.
    """

    def __init__(self):
        super(ConfigurationInvalidItemKeyTypeError, self).__init__(
            "Invalid access key provided must be of type str, "
            "ConfigurationOption or Configuration."
        )


class ConfigurationKeyNotPresentError (ConfigurationError):
    """ Exception for when a given key name is not present in a configuration
    """

    def __init__(self, key):
        super(ConfigurationKeyNotPresentError, self).__init__(
            "No such key '%s' in this configuration"
            % key
        )


class ConfigurationDotNotationSetError (ConfigurationError):
    """ Exception for when setting a new configuration options via dot notation
    """

    def __init__(self, key):
        super(ConfigurationDotNotationSetError, self).__init__(
            "Attempted to option to key '%s'. This is already reserved in this "
            "configuration class/instance."
            % key
        )


### ConfigurationOption object errors #########################################

class ConfigurationOptionError (ConfigurationError):
    """
    Base exception class for ConfigurationOption errors.
    """
    pass


class ConfigurationOptionDoesNotExistError (ConfigurationOptionError):
    """
    Exception for when an option does not exist
    """
    pass
