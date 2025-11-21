from subprocess import check_call


def call(cmd):
    print(cmd)
    check_call(cmd, shell=True)
