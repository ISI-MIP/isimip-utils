def parse_filelist(filelist_file):
    if filelist_file:
        with open(filelist_file) as f:
            filelist = set([line for line in f.read().splitlines() if (line and not line.startswith('#'))])
    else:
        filelist = None

    return filelist
