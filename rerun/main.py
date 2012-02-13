'''
rerun <command>

Polls for changes to any file under the current directory and runs <command>
whenever it finds any.

See README for details.
'''
import argparse
import os
import platform
import stat
import sys
import subprocess
import time

from . import VERSION

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

HELP_COMMAND = '''\
Command to execute
'''
HELP_VERBOSE = '''\
Display the names of changed files before the command output.
'''
HELP_IGNORE = '''\
File or directory to ignore. Any directories of the given name (and
their subdirs) are excluded from the search for changed files. Any modification
to files of the given name are ignored. The given value is compared to
basenames, so for example, "--ignore=def" will skip the contents of directory
"abc/def/" and will ignore file "/ghi/def". Can be specified multiple times.'''


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', nargs='+', help=HELP_COMMAND)
    parser.add_argument('--verbose',
        default=False, action='store_true', help=HELP_VERBOSE)
    parser.add_argument('--ignore', action='append', default=[], help=HELP_IGNORE)
    parser.add_argument('--version',
        action='version', version='%(prog)s v' + VERSION)
    return parser


def parse_command_line(parser, args):
    options = parser.parse_args(args)
    options.command = ' '.join(options.command)
    return options


def get_file_mtime(filename):
    return os.stat(filename)[stat.ST_MTIME]


def skip_dirs(dirs, skips):
    for skip in skips:
        if skip in dirs:
            dirs.remove(skip)


def skip_file(filename, ignoreds):
    return (
        any(os.path.basename(filename) == i for i in ignoreds) or
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
        subprocess.call('cls')
    else:
        subprocess.call('clear')


def mainloop(options):
    first_time = True
    while True:
        changed = changed_files(options.ignore)
        if changed:
            clear_screen()
            if options.verbose and not first_time:
                print('\n'.join(changed))
            subprocess.call(options.command, shell=True)
        time.sleep(1)
        first_time = False


def main():
    mainloop(
        parse_command_line( get_parser(), sys.argv[1:] )
    )

