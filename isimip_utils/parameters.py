"""Utility functions for the work with parameters and placeholders."""
from itertools import product
from pathlib import Path
from typing import Any


def get_permutations(parameters: dict[str, list]) -> tuple[tuple]:
    """Generate all permutations from parameter value lists.

    Args:
        parameters (dict[str, list]): Dictionary mapping parameter names to lists of values.

    Returns:
        Tuple of tuples representing all possible combinations of parameter values.
    """
    return tuple(product(*parameters.values()))


def get_placeholders(parameters: dict[str, list], permutation: tuple) -> dict:
    """Convert a permutation tuple into a dictionary of placeholders.

    Args:
        parameters (dict[str, list]): Dictionary mapping parameter names to lists of values.
        permutation (tuple): Tuple of values representing one permutation.

    Returns:
        Dictionary mapping parameter names to their values in this permutation.
    """
    return dict(zip(parameters.keys(), permutation, strict=True))


def join_parameters(parameters: dict[str, list[str]], max_count: int = 5,
                    max_label: str = 'various') -> dict[str, str]:
    """Join parameter values into strings, with fallback for large value sets.

    Args:
        parameters (dict[str, list[str]]): Dictionary mapping parameter names to lists of values.
        max_count (int): Maximum number of values to join (default: 5).
        max_label (str): Label to use when value count exceeds max_count (default: 'various').

    Returns:
        Dictionary mapping parameter names to joined strings or max_label.
    """
    return {
        key: (max_label if len(values) > max_count else '+'.join(values))
        for key, values in parameters.items()
    }


def copy_placeholders(*placeholder_args: dict, **kwargs: Any) -> dict:
    """Merge multiple placeholder dictionaries and additional kwargs.

    Args:
        *placeholder_args (dict): Variable number of placeholder dictionaries to merge.
        **kwargs (Any): Additional key-value pairs to add to the result.

    Returns:
        Dictionary containing all merged placeholders.
    """
    placeholders = {
        key: value
        for placeholder_arg in placeholder_args
        for key, value in placeholder_arg.items()
    }
    placeholders.update(**kwargs)
    return placeholders


def apply_placeholders(path_template: str | Path, placeholders: dict) -> Path:
    """Apply placeholders to a string or path, ensuring that the name of the path is lower case

    Args:
        path_template (str | Path): Path template as string or path.
        placeholders (dict): Placeholder dictionary.

    Returns:
        Path with the applied placeholders.
    """
    try:
        path = str(path_template).format(**placeholders)
    except KeyError as e:
        raise RuntimeError(f'Some of the placeholders are missing ({e}).') from e

    path = Path(path)
    return path.with_stem(path.stem.lower())
