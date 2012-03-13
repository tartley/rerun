import itertools
import os
import platform
import stat
import sys
import subprocess
import time

from .options import get_parser, parse_args, validate


SKIP_DIRS = ['.svn', '.git', '.hg', '.bzr', 'build', 'dist']
SKIP_EXT = ['.pyc', '.pyo']

try:
    # Python2
    filterfalse = itertools.ifilterfalse
except AttributeError:
    # Python3
    filterfalse = itertools.filterfalse


def is_ignorable(filename, ignores):
    '''
    Returns True if filename is in 'ignores' or ends with a SKIP_EXT
    '''
    return (
        any(os.path.basename(filename) == i for i in ignores) or
        any(filename.endswith(skip) for skip in SKIP_EXT)
    )


def get_file_mtime(filename):
    return os.stat(filename)[stat.ST_MTIME]


def skip_dirs(dirs, skips):
    for skip in skips:
        if skip in dirs:
            dirs.remove(skip)


file_stat_cache = {}

def has_file_changed(filename):
    '''
    Has the given file changed since last invocation?
    '''
    mtime = get_file_mtime(filename)
    if (
        filename not in file_stat_cache or
        file_stat_cache[filename] != mtime
    ):
        file_stat_cache[filename] = mtime
        return True
    return False


def get_changed_files(ignores):
    '''
    Walks subdirs of cwd, looking for files which have changed since last
    invocation.
    '''
    changed_files = []
    for root, dirs, files in os.walk('.'):
        skip_dirs(dirs, ignores)
        for filename in files:
            fullname = os.path.join(root, filename)
            if has_file_changed(fullname):
                changed_files.append(fullname)
    return changed_files


def clear_screen():
    if platform.system().lower().startswith('win'):
        os.system('cls')
    else:
        os.system('clear')



def mainloop(options):
    first_time = True
    while True:
        changed_files = list(filterfalse(
            lambda filename: is_ignorable(filename, options.ignore),
            get_changed_files(options.ignore)
        ))
        if changed_files:
            clear_screen()
            if options.verbose and not first_time:
                print('\n'.join(sorted(changed_files)))
            subprocess.call(options.command)
        time.sleep(1)
        first_time = False


def main():
    # setup.py install/develop creates an executable that calls 'main()'
    mainloop(
        validate(
            parse_args(
                get_parser('rerun', SKIP_DIRS, SKIP_EXT), sys.argv[1:]
            )
        )
    )

