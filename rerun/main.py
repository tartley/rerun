#!/usr/bin/env python2.7
'''
rerun <command>

Polls for changes to any file under the current directory and runs <command>
whenever it finds any.

See README for details.
'''
import os
import platform
import stat
from subprocess import call
import sys
import time

USAGE = '''
rerun [<options>] <command>

Clears the screen and runs the given command whenever files change in the
current directory or subdirectories. Works by polling every second for file
modification time or size changes.

Options may contain:

    --verbose|-v     List changed files before <command> output.
    --ignore|-i <d>  Directory to ignore
'''

SKIP_DIRS = ['.svn', '.git', '.hg', '.bzr', 'build', 'dist']
SKIP_EXT = ['.pyc', '.pyo']


class Options(object):
    command = None
    verbose = None
    ignoreds = SKIP_DIRS


def process_command_line(argv, **_):
    options = Options()

    while argv:
        if argv[0] in ['--verbose', '-v']:
            options.verbose = True
            argv = argv[1:]
        elif argv[0] in ['--ignore', '-i']:
            options.ignoreds.append(argv[1])
            argv = argv[2:]
        else:
            break

    if not argv:
        sys.exit(USAGE)

    options.command = ' '.join(argv)

    return options


def get_file_mtime(filename):
    return os.stat(filename)[stat.ST_MTIME]


def skip_dirs(dirs, skips):
    for skip in skips:
        if skip in dirs:
            dirs.remove(skip)


def skip_file(filename, ignoreds):
    return (
        any(os.path.normpath(filename).endswith(i) for i in ignoreds) or
        any(filename.endswith(skip) for skip in SKIP_EXT)
    )


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


def changed_files(ignoreds):
    '''
    Walks subdirs of cwd, looking for files which have changed since last
    invokation.
    '''
    changed = []
    for root, dirs, files in os.walk('.'):
        skip_dirs(dirs, ignoreds)
        for filename in files:
            fullname = os.path.join(root, filename)
            if skip_file(fullname, ignoreds):
                continue
            if has_file_changed(fullname):
                changed.append(fullname)

    return changed


def clear_screen():
    if platform.system().startswith('win'):
        call('cls')
    else:
        call('clear')


def main(args=None):
    options = process_command_line(args or sys.argv[1:])
    while True:
        changed = changed_files(options.ignoreds)
        if changed:
            clear_screen()
            if options.verbose:
                print('\n'.join(changed))
            call(options.command, shell=True)
        time.sleep(1)


if __name__ == '__main__':
    main()

