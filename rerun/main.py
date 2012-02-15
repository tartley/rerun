import argparse
import os
import platform
import stat
import sys
import subprocess
import time

from . import __doc__, __version__

SKIP_DIRS = ['.svn', '.git', '.hg', '.bzr', 'build', 'dist']
SKIP_EXT = ['.pyc', '.pyo']

HELP_COMMAND = '''
Command to execute. The first command line arg that rerun doesn't recognise
(including anything that doesn't start with '-') marks the start of the command.
All args from there onwards are considered to be part of the given command,
even if they match args that rerun recognises (e.g. -v.)
'''
HELP_VERBOSE = '''
Display the names of changed files before the command output.
'''
HELP_IGNORE = '''
File or directory to ignore. Any directories of the given name (and
their subdirs) are excluded from the search for changed files. Any modification
to files of the given name are ignored. The given value is compared to
basenames, so for example, "--ignore=def" will skip the contents of directory
"abc/def/" and will ignore file "/ghi/def". Can be specified multiple times.
'''
EPILOG = '''
Always ignores directories: {}
Always ignores files with extensions: {}

Documentation & downloads: http://pypi.python.org/pypi/%(prog)s/

Version {}
'''.format(', '.join(SKIP_DIRS), ', '.join(SKIP_EXT), __version__)


def get_parser():
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--color')
    parser.add_argument('--verbose', '-v',
        default=False, action='store_true', help=HELP_VERBOSE)
    parser.add_argument('--ignore', '-i',
        action='append', default=[], help=HELP_IGNORE)
    parser.add_argument('--version',
        action='version', version='%(prog)s v' + __version__)
    parser.add_argument('command', nargs=argparse.REMAINDER, help=HELP_COMMAND)
    return parser


def parse_args(parser, args):
    return parser.parse_args(args)


def _exit(message):
    sys.stderr.write(message + '\n')
    sys.exit(2)


def validate(options):
    if len(options.command) == 0:
        _exit('No command specified.')
    return options


def get_file_mtime(filename):
    return os.stat(filename)[stat.ST_MTIME]


def skip_dirs(dirs, skips):
    for skip in skips:
        if skip in dirs:
            dirs.remove(skip)


def skip_file(filename, ignores):
    return (
        any(os.path.basename(filename) == i for i in ignores) or
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


def changed_files(ignores):
    '''
    Walks subdirs of cwd, looking for files which have changed since last
    invokation.
    '''
    changed = []
    for root, dirs, files in os.walk('.'):
        skip_dirs(dirs, ignores)
        for filename in files:
            fullname = os.path.join(root, filename)
            if skip_file(fullname, ignores):
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
                print('\n'.join(sorted(changed)))
            subprocess.call(options.command)
        time.sleep(1)
        first_time = False


def main():
    mainloop(
        validate(
            parse_args(
                get_parser(), sys.argv[1:]
            )
        )
    )

