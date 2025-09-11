import re


def find_files(base_path, pattern):
    files = []
    for path in sorted(base_path.rglob("*")):
        match = re.search(str(pattern), str(path))
        if match:
            files.append(dict(path=path, **match.groupdict()))

    return files
