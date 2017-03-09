import argparse
import os
import platform
try:
    import pwd
except ImportError:
    # Can't import on Windows
    pwd = None
import sys

from . import __doc__, __version__


HELP_COMMAND = '''
Command to execute. The first command line arg that rerun doesn't recognise
(including anything that doesn't start with '-') marks the start of the command.
All args from there onwards are considered to be part of the given command,
even if they look like args that rerun would otherwise recognise, e.g. -v.
'''
HELP_IGNORE = '''
File or directory to ignore. Any directories of the given name (and
their subdirs) are excluded from the search for changed files. Any modification
to files of the given name are ignored. The given value is compared to
basenames, so for example, "--ignore=def" will skip the contents of directory
"./abc/def/" and will ignore file "./ghi/def". Can be specified multiple times.
'''
HELP_INTERACTIVE = '''
Run the command in an interactive shell. This allows the use of shell aliases
and functions, but is slower, less reliable and noisier on stdout/stderr,
because it sources ~/.bashrc and the like before running the command.
Not available on Windows.
'''
HELP_VERBOSE = '''
Display the names of changed files before the command output.
'''
EPILOG = '''
Always ignores directories: {skip_dirs}
Always ignores files with extensions: {skip_exts}

Documentation & downloads: http://pypi.python.org/pypi/%(prog)s/

Version {version}
'''


def get_parser(name, skip_dirs, skip_exts):
    parser = argparse.ArgumentParser(
        description=__doc__,
        prog=name,
        epilog=EPILOG.format(
            skip_dirs=', '.join(skip_dirs),
            skip_exts=', '.join(skip_exts),
            version=__version__,
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--ignore', '-i',
        action='append', default=skip_dirs, help=HELP_IGNORE)
    parser.add_argument('--interactive', '-I',
        default=False, action='store_true', help=HELP_INTERACTIVE)
    parser.add_argument('--verbose', '-v',
        default=False, action='store_true', help=HELP_VERBOSE)
    parser.add_argument('--version',
        action='version', version='%(prog)s v' + __version__)
    parser.add_argument('command', help=HELP_COMMAND)
    return parser


def parse_args(parser, args):
    return parser.parse_args(args)


def _exit(message):
    sys.stderr.write(message + '\n')
    sys.exit(2)


def get_current_shell():
    '''
    Gets the shell executable that was used to launch rerun.
    We use this to launch the user's given command, so that it gets
    interpreted the same way it would if the user typed it at a prompt.
    On Windows return None, so subprocess just uses its default 'cmd' shell.
    '''
    if pwd is None or platform.system() == 'Windows':
        return None
    else:
        # parent shell of this process,
        # or fallback to user's default shell from /etc/passwd
        return os.environ.get('SHELL', pwd.getpwuid(os.getuid()).pw_shell)


def validate(options):
    if len(options.command) == 0:
        _exit('No command specified.')
    options.shell = get_current_shell()
    return options

