#!/usr/bin/env python2.7
'''
rerun

Tested on Python 2.7 & 3.2, on Ubuntu, WindowsXP, Windows7 and OSX.

Thanks to Jeff Winkler for the original formulation, http://jeffwinkler.net
See also project 'watchdog', which does the same thing but better, by hooking
into OS-level file change notifications, instead of polling.

By Jonathan Hartley, http://tartley.com
'''
import os
import platform
import stat
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


def get_file_stats(filename):
    stats = os.stat(filename)
    size = stats[stat.ST_SIZE]
    modification_time = stats[stat.ST_MTIME]
    return size, modification_time


def skip_dirs(dirs, skips):
    for skip in skips:
        if skip in dirs:
            dirs.remove(skip)


def skip_file(filename, ignoreds):
    return (
        any(os.path.normpath(filename) == ignored for ignored in ignoreds) or
        any(filename.endswith(skip) for skip in SKIP_EXT)
    )


file_stats = {}

def has_file_changed(filename):
    '''
    Has the given file changed since last invocation?
    '''
    size, mtime = get_file_stats(filename)
    if (
        filename not in file_stats or
        file_stats[filename] != (size, mtime)
    ):
        file_stats[filename] = (size, mtime)
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
    if platform.system() == 'Darwin':
        os.system('clear')
    else:
        os.system('cls')


def main():
    options = process_command_line(sys.argv[1:])
    while True:
        changed = changed_files(options.ignoreds)
        if changed:
            clear_screen()
            if options.verbose:
                print('\n'.join(changed))
            os.system(options.command)
        time.sleep(1)


if __name__ == '__main__':
    main()

