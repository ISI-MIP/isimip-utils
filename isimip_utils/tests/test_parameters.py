from pathlib import Path

import pytest

from isimip_utils.parameters import (
    apply_placeholders,
    copy_placeholders,
    get_permutations,
    get_placeholders,
    join_parameters,
)

parameters = {
    'model': ['model_a', 'model_b'],
    'variable': ['x', 'y', 'z']
}


def test_get_permutations():
    assert get_permutations(parameters) == (
        ('model_a', 'x'),
        ('model_a', 'y'),
        ('model_a', 'z'),
        ('model_b', 'x'),
        ('model_b', 'y'),
        ('model_b', 'z')
    )


def test_get_placeholders():
    assert get_placeholders(parameters, ('model_a', 'x')) == {
        'model': 'model_a',
        'variable': 'x'
    }


def test_join_parameters():
    assert join_parameters(parameters) == {
        'model': 'model_a+model_b',
        'variable': 'x+y+z'
    }


def test_join_parameters_max_count():
    assert join_parameters(parameters, 2) == {
        'model': 'model_a+model_b',
        'variable': 'various'
    }


def test_join_parameters_max_count_label():
    assert join_parameters(parameters, 2, 'label') == {
        'model': 'model_a+model_b',
        'variable': 'label'
    }


def test_copy_placeholders():
    assert copy_placeholders({'foo': 'bar'}, {'egg': 'spam'}) == {
        'foo': 'bar',
        'egg': 'spam'
    }


def test_apply_placeholders():
    assert apply_placeholders('{foo}_{egg}', {'foo': 'bar', 'egg': 'spam'}) == Path('bar_spam')


def test_apply_placeholders_error():
    with pytest.raises(RuntimeError):
        apply_placeholders('{foo}_{egg}', {'foo': 'bar'})
