import itertools
import os
import platform
import signal
import stat
import sys
import subprocess
import time

from .options import get_parser, parse_args, validate


SKIP_DIRS = [
    '.svn', '.git', '.hg', '.bzr',
    '.cache', 'build', 'dist', 'node_modules',
]
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
    return os.lstat(filename)[stat.ST_MTIME]


def skip_dirs(dirs, skips):
    for skip in skips:
        if skip in dirs:
            dirs.remove(skip)


file_stat_cache = {}

def has_file_changed(filename):
    '''
    Has the given file changed since last invocation?
    '''
    try:
        mtime = get_file_mtime(filename)
    except FileNotFoundError:
        del file_stat_cache[filename]
        return True

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
            relname = os.path.join(root, filename)
            if (
                has_file_changed(relname) and
                not is_ignorable(relname, ignores)
            ):
                changed_files.append(relname)
    return changed_files


def clear_screen():
    if platform.system().lower().startswith('win'):
        os.system('cls')
    else:
        os.system('clear')


def run_command_in_shell(command, shell):
    subprocess.call(command, shell=True, executable=shell)


def run_command_in_interactive_shell(command, shell):
    try:
        subprocess.call([shell, '-i', '-c', command])
    finally:
        # The terminal was attached to the interactive shell we just
        # started, and left in limbo when that shell terminated. Retrieve
        # it for this process group, so that we can still print and recieve
        # keypresses.
        os.tcsetpgrp(0, os.getpgrp())


def run_command(command, shell, interactive):
    if interactive:
        run_command_in_interactive_shell(command, shell)
    else:
        run_command_in_shell(command, shell)


def act(changed_files, options, first_time):
    '''
    Runs the user's specified command.
    '''
    clear_screen()
    print(options.command)
    if options.verbose and not first_time:
        print(', '.join(sorted(changed_files)))
    # Launch the user's given command in an interactive shell, so that aliases
    # & functions are interpreted just as when the user types at a terminal.
    run_command(options.command, options.shell, options.interactive)


def step(options, first_time=False):
    changed_files = get_changed_files(options.ignore)
    if changed_files:
        act(changed_files, options, first_time)
    time.sleep(0.2)


def mainloop(options):
    step(options, first_time=True)
    while True:
        step(options)


def main():
    # This fn exposed as a command-line entry point by setup.py install/develop.

    # Ignore SIGTTOU, which we receive after subprocesses launching interactive
    # shells (which take our terminal with them) terminate (leaving the terminal
    # in limbo.) If we ignore the resulting SIGTTOU, then we can get the
    # terminal back and proceed. See
    # http://stackoverflow.com/questions/25099895/from-python-start-a-shell-that-can-interpret-functions-and-aliases
    signal.signal(signal.SIGTTOU, signal.SIG_IGN)

    mainloop(
        validate(
            parse_args(
                get_parser('rerun', SKIP_DIRS, SKIP_EXT), sys.argv[1:]
            )
        )
    )

