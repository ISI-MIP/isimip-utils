from collections.abc import Callable
from typing import Any


class cached_property:
    """Decorator that converts a method into a cached property.

    The property value is computed once and then cached as an instance attribute.
    Subsequent accesses return the cached value without re-computing.

    Simplified version of
    [Django's cached_property](https://github.com/django/django/blob/main/django/utils/functional.py).
    """

    name: str | None = None

    def __init__(self, func: Callable) -> None:
        self.func = func

    def __set_name__(self, owner: type, name: str) -> None:
        if self.name is None:
            self.name = name
        else:
            raise TypeError("Cannot assign the same cached_property to two different names")

    def __get__(self, instance: Any, cls: type | None = None) -> Any:
        if instance is None:
            return self
        value = instance.__dict__[self.name] = self.func(instance)
        return value
