import argparse
import os
import tempfile
from pathlib import Path

import pytest

from isimip_utils.cli import (
    ArgumentParser,
    parse_dict,
    parse_filelist,
    parse_list,
    parse_locations,
    parse_parameters,
    parse_path,
    parse_version,
)


def test_parse_dict():
    result = parse_dict("key=value1,value2")
    assert result == {"key": ["value1", "value2"]}


def test_parse_list():
    result = parse_list("a,b,c")
    assert result == ["a", "b", "c"]


def test_parse_version():
    result = parse_version("20230101")
    assert result == "20230101"


def test_parse_version_invalid():
    with pytest.raises(argparse.ArgumentTypeError):
        parse_version("invalid")


def test_parse_path():
    result = parse_path("~/test")
    assert isinstance(result, Path)


def test_parse_locations():
    result = parse_locations('https://example.com /opt/test ~/test')
    assert result == ['https://example.com', Path('/opt/test'), Path('~/test').expanduser()]


def test_parse_locations_none():
    result = parse_locations('')
    assert result == []


def test_parse_filelist():
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("/path/to/file1\n")
        f.write("#comment\n")
        f.write("/path/to/file2\n")
        temp_file = f.name

    try:
        result = parse_filelist(temp_file)
        assert "/path/to/file1" in result
        assert "/path/to/file2" in result
        assert "#comment" not in result
    finally:
        os.unlink(temp_file)


def test_parse_filelist_none():
    result = parse_filelist(None)
    assert result == []


def test_parse_parameters():
    result = parse_parameters('egg=spam,foo,bar')
    assert result == {'egg': ['spam', 'foo', 'bar']}


def test_parse_parameters_none():
    result = parse_parameters('')
    assert result == {}


def test_argument_parser():
    parser = ArgumentParser()
    parser.add_argument("--test", default="default")

    args = parser.parse_args([])
    assert args.test == "default"


def test_argument_parser_with_config(tmp_path):
    config_file = tmp_path / "isimip.toml"
    config_file.write_text("[test]\ntest = \"config_value\"\n")

    # Temporarily change the config files list to use our test config
    original_config_files = ArgumentParser.config_files
    ArgumentParser.config_files = [str(config_file)]

    try:
        parser = ArgumentParser(prog="test")
        parser.add_argument("--test", default="default")

        args = parser.parse_args([])
        assert args.test == "config_value"
    finally:
        ArgumentParser.config_files = original_config_files


def test_argument_parser_with_env():
    os.environ["ISIMIP_TEST"] = "env_value"

    try:
        parser = ArgumentParser()
        parser.add_argument("--test", default="default")

        args = parser.parse_args([])
        assert args.test == "env_value"
    finally:
        del os.environ["ISIMIP_TEST"]
