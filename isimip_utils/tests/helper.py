import json
import re
import subprocess
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock


def call(cmd):
    print(cmd)
    return subprocess.check_output(cmd, shell=True).decode()


def normalize_whitespace(string):
    return re.sub(r'\s+', ' ', string).strip()


def assert_multiline_strings_equal(a, b):
    for a_line, b_line in zip(a.strip().splitlines(), b.strip().splitlines(), strict=True):
        assert normalize_whitespace(a_line) == normalize_whitespace(b_line), (a_line, b_line)


def mock_json(url, *args, **kwargs):
    mock_response = MagicMock()
    mock_path = Path(url.replace('https://protocol.isimip.org', 'testing/protocol/output'))

    if mock_path.exists():
        with mock_path.open() as fp:
            mock_response.status_code = 200
            mock_response.json.return_value = json.load(fp)
    else:
        mock_response.status_code = 404
        mock_response.json.return_value = None

    return mock_response


def mock_content(url, *args, **kwargs):
    mock_response = MagicMock()
    mock_path = Path(url.replace('https://protocol.isimip.org', 'testing/protocol/output'))

    if mock_path.exists():
        data = mock_path.read_bytes()

        mock_response.status_code = 200
        mock_response.raw = BytesIO(data)
        mock_response.content = data
        mock_response.iter_content.return_value = [data]

    else:
        mock_response.status_code = 404
        mock_response.raw = BytesIO()
        mock_response.content = b""
        mock_response.iter_content.return_value = []

    return mock_response
