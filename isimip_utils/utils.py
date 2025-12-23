"""Additional utility functions for ISIMIP tools."""
from collections.abc import Callable
from pathlib import Path
from typing import Any

from .exceptions import ValidationError


class Singleton:
    """Base class for implementing the singleton pattern.

    Ensures only one instance of a class exists. Subclasses will share
    a single instance with a 'data' attribute initialized as an empty dict.
    """
    _instance: Any = None

    def __new__(cls) -> 'Singleton':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.data = {}
        return cls._instance


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


def exclude_path(exclude: list[str] | None, path: Path | str) -> bool:
    """Check if a path should be excluded based on exclude patterns.

    Args:
        exclude (list[str] | None): List of exclude patterns (strings). Path is excluded if it
            starts with any pattern.
        path (Path | str): Path to check for exclusion.

    Returns:
        True if path should be excluded, False otherwise.
    """
    if exclude:
        for exclude_string in exclude:
            if str(path).startswith(exclude_string):
                return True
    return False


def include_path(include: list[str] | None, path: Path | str) -> bool:
    """Check if a path should be included based on include patterns.

    Args:
        include (list[str] | None): List of include patterns (strings). Path is included if it
            starts with any pattern, or if include list is None/empty.
        path (Path | str): Path to check for inclusion.

    Returns:
        True if path should be included, False otherwise.
    """
    if include:
        for include_string in include:
            if str(path).startswith(include_string):
                return True
        return False
    else:
        return True


def validate_lat(lat: float) -> None:
    """Validate latitude value is within valid range.

    Args:
        lat (float): Latitude value to validate.

    Raises:
        ValidationError: If latitude is outside -90 to 90 range.
    """
    try:
        if lat < -90:
            raise ValidationError(f'lat={lat} must be > -90')
        elif lat > 90:
            raise ValidationError(f'lat={lat} must be < 90')
    except TypeError as e:
        raise ValidationError(f'lat={lat} is a valid number') from e


def validate_lon(lon: float) -> None:
    """Validate longitude value is within valid range.

    Args:
        lon (float): Longitude value to validate.

    Raises:
        ValidationError: If longitude is outside -180 to 180 range.
    """
    try:
        if lon < -180:
            raise ValidationError(f'lon={lon} must be > -180')
        elif lon > 180:
            raise ValidationError(f'lon={lon} must be < 180')
    except TypeError as e:
        raise ValidationError(f'lon={lon} is a valid number') from e


def get_min_value(values):
    """Get the minimal value of the input values, excluding None and using None as default.

    Args:
        values (list): Input values.

    Returns:
        Minimal value
    """
    return min([v for v in values if v is not None], default=None)


def get_max_value(values):
    """Get the maximum value of the input values, excluding None and using None as default.

    Args:
        values (list): Input values.

    Returns:
        Maximum value
    """
    return max([v for v in values if v is not None], default=None)
