import os
import sys


def is_release():
    running_ext = os.path.splitext(os.path.basename(sys.argv[0]))[1]
    return running_ext == ".exe"
