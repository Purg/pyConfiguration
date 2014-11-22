class ConfigurationOption (object):
    """
    A single option / value pair.
    """

    def __init__(self, name, value=None, description=None):
        self.__o_name = name
        self.__o_value = value
        self.__o_description = description

    def __call__(self):
        """
        :return: Shortcut for getting this option's value in native format
        """
        return self.__o_value

    def __repr__(self):
        if self.description:
            return "ConfigurationOption{%s, %s, %s}" \
                   % (self.name, self.value, self.description)
        else:
            return "ConfigurationOption{%s, %s}" \
                   % (self.name, self.value)

    def __str__(self):
        return self.str

    def __int__(self):
        return self.int

    def __float__(self):
        return self.float

    def __bool__(self):
        """ Python 3.x boolean attribute
        """
        return self.bool

    def __nonzero__(self):
        """ Python 2.x boolean attribute
        """
        return self.bool

    @property
    def name(self):
        """
        :return: Name of the option
        :rtype: str
        """
        return self.__o_name

    @property
    def value(self):
        """
        :return: Option value in native format
        """
        return self.__o_value

    @value.setter
    def value(self, v):
        """
        Set the value of this option.
        :param v: New value
        """
        self.__o_value = v

    @property
    def description(self):
        """
        :return: Description of the option, the comment
        :rtype: str
        """
        return self.__o_description

    @description.setter
    def description(self, descr):
        """
        Set the description/comment for this option
        :param descr: New description for this option
        :type descr: str or None
        """
        self.__o_description = descr

    ### Type Cast parameters ###

    @property
    def str(self):
        """
        :return:Option value as a string
        :rtype: str
        """
        return str(self.value)

    @property
    def int(self, base=10):
        """
        :return: Option value as an int
        :rtype: int
        :raises ValueError: Option value could not be cast to an int.
        """
        return int(self.value, base)

    @property
    def float(self):
        """
        :return: Option value as a float
        :rtype: float
        :raises ValueError: Option value could not be cast to an int
        """
        return float(self.value)

    @property
    def bool(self):
        """
        :return: Option value as a boolean
        :rtype: bool
        :raises ValueError: Option value could not be cast to a boolean
        """
        return bool(self.value)
