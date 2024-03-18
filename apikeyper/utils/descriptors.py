import inspect


class RestrictedSetter:
    def __init__(self, name, initial=None, allowed_types=None, preferred_type=None, condition=None, exception=None, exception_args=None):
        self.name = '_' + name
        self.initial = initial

        # Ensure `allowed_types` is a tuple or list
        if not isinstance(allowed_types, (tuple, list)):
            allowed_types = (allowed_types,)

        self.allowed_types = allowed_types
        self.preferred_type = preferred_type
        self.condition = condition
        self.exception = exception
        self.exception_args = exception_args or {}

    def __get__(self, obj, objtype=None):
        return getattr(obj, self.name, self.initial)

    def __set__(self, obj, value):
        if self.condition and not self.condition(obj):
            if self.exception:
                raise self.exception(**self.exception_args)
            raise PermissionError("Condition for setting property not met.")

        caller_frame = inspect.stack()[1]
        caller_self = caller_frame.frame.f_locals.get('self', None)
        if caller_self is None or caller_self.__class__ != obj.__class__:
            raise PermissionError("Property can only be set within class methods.")

        if (self.allowed_types and not isinstance(value, self.allowed_types)) and value is not None:
            raise TypeError(f"Value must be of type {', '.join([t.__name__ for t in self.allowed_types])}, got type {type(value).__name__}.")

        if self.preferred_type and not isinstance(value, self.preferred_type):
            value = self.preferred_type(value)

        setattr(obj, self.name, value)

    def __delete__(self, obj):
        setattr(obj, self.name, self.initial)
