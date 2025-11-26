import re
import subprocess


def call(cmd):
    print(cmd)
    return subprocess.check_output(cmd, shell=True).decode()


def normalize_whitespace(string):
    return re.sub(r'\s+', ' ', string).strip()


def assert_multiline_strings_equal(a, b):
    for a_line, b_line in zip(a.strip().splitlines(), b.strip().splitlines(), strict=True):
        assert normalize_whitespace(a_line) == normalize_whitespace(b_line)
