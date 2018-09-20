from contextlib import contextmanager
import os
import platform
import sys
try:
    # Python <= 2.6
    import unittest2 as unittest
except ImportError:
    # Python >= 2.7
    import unittest

from mock import Mock, call, patch

from rerun import __version__
from rerun.options import get_current_shell, get_parser, parse_args, validate


def get_stream_argparse_writes_version_to():
    '''
    Argparse in Python 3.4 stdlib writes version number to stdout,
    whereas argparse from PyPI writes to stderr.
    '''
    is_python3 = sys.version_info[:2] >= (3, 0)
    return 'sys.stdout' if is_python3 else 'sys.stderr'


@contextmanager
def env_vars(**variables):
    orig = dict(os.environ)
    for name, value in dict(variables).items():
        if value is None:
            os.environ.pop(name, 0)
            del variables[name]
    os.environ.update(variables)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(orig)


class Test_Options(unittest.TestCase):

    def assert_get_parser_error(self, args, expected, stream):
        parser = get_parser('prog', ['ignored-dirs'], ['exts'])
        with self.assertRaises(SystemExit):
            parser.parse_args(args)
        self.assertEqual(stream.write.call_args, call(expected))


    def test_get_parser_defaults(self):
        parser = get_parser('prog', ['ignored-dirs'], ['exts'])
        options = parser.parse_args(['command is this'])
        self.assertEqual(options.ignore, ['ignored-dirs'])
        self.assertEqual(options.interactive, False)


    def test_get_parser_version(self):
        with patch(get_stream_argparse_writes_version_to()) as mock_stream:
            self.assert_get_parser_error(
                ['--version'], 'prog v%s\n' % (__version__,), mock_stream)


    def test_get_parser_one_command(self):
        parser = get_parser('prog', ['ignored-dirs'], ['exts'])
        options = parser.parse_args(['single command arg'])
        self.assertEqual(options.command, 'single command arg')


    @patch('sys.stderr')
    def test_get_parser_should_error_on_more_than_1_command(self, mock_stderr):
        with patch('sys.stderr') as mock_stderr:
            self.assert_get_parser_error(
                ['one', 'two'],
                'prog: error: unrecognized arguments: two\n',
                mock_stderr
            )

    def test_get_parser_command_with_options_in_it(self):
        parser = get_parser('prog', ['ignored-dirs'], ['exts'])
        options = parser.parse_args(['ls --color'])
        self.assertEqual(options.command, 'ls --color')


    def test_get_parser_verbose(self):
        parser = get_parser('prog', ['ignored-dirs'], ['exts'])
        options = parser.parse_args(['--verbose', 'command is this'])
        self.assertTrue(options.verbose)
        self.assertEqual(options.command, 'command is this')


    def test_get_parser_ignore(self):
        parser = get_parser('prog', ['ignored-dirs'], ['exts'])
        parser.exit = Mock()
        options = parser.parse_args(['--ignore', 'abc', 'command is this'])
        self.assertEqual(options.ignore, ['ignored-dirs', 'abc'])
        self.assertEqual(options.command, 'command is this')


    def test_get_parser_ignore_multiple(self):
        parser = get_parser('prog', ['ignored-dirs'], ['exts'])
        options = parser.parse_args([
            '--ignore', 'abc', '--ignore', 'def', 'command is this'
        ])
        self.assertEqual(options.ignore, ['ignored-dirs', 'abc', 'def'])
        self.assertEqual(options.command, 'command is this')


    def test_get_parser_interactive(self):
        parser = get_parser('prog', ['ignored-dirs'], ['exts'])
        parser.exit = Mock()
        options = parser.parse_args(['--interactive', 'command is this'])
        self.assertEqual(options.interactive, True)


    def test_parse_args(self):
        parser = Mock()
        args = Mock()

        options = parse_args(parser, args)

        self.assertEqual(parser.parse_args.call_args, ((args,),))
        self.assertEqual(options, parser.parse_args.return_value)


    @unittest.skipIf(platform.system() != 'Windows', 'Not on Windows.')
    def test_get_current_shell_returns_none_on_Windows(self):
        self.assertEqual(get_current_shell(), None)


    @unittest.skipIf(platform.system() == 'Windows', 'On Windows.')
    def test_get_current_shell_returns_shell_env_var(self):
        with env_vars(SHELL='myshell'):
            self.assertEqual(get_current_shell(), 'myshell')


    @unittest.skipIf(platform.system() == 'Windows', 'On Windows.')
    @patch('rerun.options.pwd.getpwuid')
    def test_get_current_shell_falls_back_to_default_shell(self, mock_getpwuid):
        mock_getpwuid.return_value.pw_shell = 'myshell'
        with env_vars(SHELL=None):
            self.assertEqual(get_current_shell(), 'myshell')


    def test_validate_returns_given_options(self):
        options = Mock()
        options.command = [0]
        response = validate(options)
        self.assertIs(response, options)


    @patch('rerun.options._exit')
    def test_validate_requires_command(self, mock_exit):
        options = Mock()
        options.command = []
        validate(options)
        self.assertEqual(mock_exit.call_args, (('No command specified.',), ))


    @patch('rerun.options.get_current_shell', Mock(return_value='myshell'))
    def test_validate_sets_shell(self):
        options = Mock()
        options.command = [0]
        response = validate(options)
        self.assertEqual(response.shell, 'myshell')

