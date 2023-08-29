def parse_filelist(filelist_file):
    if filelist_file:
        with open(filelist_file) as f:
            filelist = {line for line in f.read().splitlines() if (line and not line.startswith('#'))}
    else:
        filelist = None

    return filelist


def exclude_path(exclude, path):
    if exclude:
        for exclude_string in exclude:
            if str(path).startswith(exclude_string):
                return True
    return False


def include_path(include, path):
    if include:
        for include_string in include:
            if str(path).startswith(include_string):
                return True
        return False
    else:
        return True
