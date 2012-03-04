import argparse
import sys

from . import __doc__, __version__


HELP_COMMAND = '''
Command to execute. The first command line arg that rerun doesn't recognise
(including anything that doesn't start with '-') marks the start of the command.
All args from there onwards are considered to be part of the given command,
even if they look like args that rerun would otherwise recognise, e.g. -v.
'''
HELP_VERBOSE = '''
Display the names of changed files before the command output.
'''
HELP_IGNORE = '''
File or directory to ignore. Any directories of the given name (and
their subdirs) are excluded from the search for changed files. Any modification
to files of the given name are ignored. The given value is compared to
basenames, so for example, "--ignore=def" will skip the contents of directory
"./abc/def/" and will ignore file "./ghi/def". Can be specified multiple times.
'''
EPILOG = '''
Always ignores directories: {}
Always ignores files with extensions: {}

Documentation & downloads: http://pypi.python.org/pypi/%(prog)s/

Version {}
'''


def get_parser(name, skip_dirs, skip_ext):
    parser = argparse.ArgumentParser(
        description=__doc__,
        prog=name,
        epilog=EPILOG.format(
            ', '.join(skip_dirs), ', '.join(skip_ext), __version__),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
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

