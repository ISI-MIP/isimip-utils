"""
Simplified version of Django'd cached_property
https://github.com/django/django/blob/main/django/utils/functional.py
"""


class cached_property:

    name = None

    def __init__(self, func):
        self.func = func

    def __set_name__(self, owner, name):
        if self.name is None:
            self.name = name
        else:
            raise TypeError("Cannot assign the same cached_property to two different names")

    def __get__(self, instance, cls=None):
        if instance is None:
            return self
        value = instance.__dict__[self.name] = self.func(instance)
        return value
