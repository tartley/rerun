try:
    import unittest2 as unittest
except ImportError:
    import unittest

from mock import call, Mock, patch

from rerun import __version__
from rerun.options import get_parser, parse_args, validate


class Test_Options(unittest.TestCase):

    @patch('sys.stderr')
    def assert_get_parser_error(self, args, expected, mock_stderr):
        parser = get_parser('prog', ['dirs'], ['exts'])
        with self.assertRaises(SystemExit):
            parser.parse_args(args)
        self.assertIn(expected, mock_stderr.write.call_args[0][0])


    def test_get_parser_version(self):
        self.assert_get_parser_error(['--version'], 'v%s' % (__version__,))


    def test_get_parser_one_command(self):
        parser = get_parser('prog', ['dirs'], ['exts'])
        options = parser.parse_args(['single command arg'])
        self.assertEqual(options.command, 'single command arg')


    @patch('sys.stderr')
    def test_get_parser_should_error_on_more_than_one_command(self, mock_stderr):
        self.assert_get_parser_error(
            ['one', 'two'],
            'prog: error: unrecognized arguments: two\n'
        )

    def test_get_parser_command_with_options_in_it(self):
        parser = get_parser('prog', ['dirs'], ['exts'])
        options = parser.parse_args(['ls --color'])
        self.assertEqual(options.command, 'ls --color')


    def test_get_parser_verbose(self):
        parser = get_parser('prog', ['dirs'], ['exts'])
        options = parser.parse_args(['--verbose', 'command is this'])
        self.assertTrue(options.verbose)
        self.assertEqual(options.command, 'command is this')


    def test_get_parser_ignore(self):
        parser = get_parser('prog', ['dirs'], ['exts'])
        parser.exit = Mock()
        options = parser.parse_args(['--ignore', 'abc', 'command is this'])
        self.assertEqual(options.ignore, ['dirs', 'abc'])
        self.assertEqual(options.command, 'command is this')


    def test_get_parser_ignore_default(self):
        parser = get_parser('prog', ['dirs'], ['exts'])
        options = parser.parse_args(['command is this'])
        self.assertEqual(options.ignore, ['dirs'])


    def test_get_parser_ignore_multiple(self):
        parser = get_parser('prog', ['dirs'], ['exts'])
        options = parser.parse_args([
            '--ignore', 'abc', '--ignore', 'def', 'command is this'
        ])
        self.assertEqual(options.ignore, ['dirs', 'abc', 'def'])
        self.assertEqual(options.command, 'command is this')


    def test_parse_args(self):
        parser = Mock()
        args = Mock()

        options = parse_args(parser, args)

        self.assertEqual(parser.parse_args.call_args, ((args,),))
        self.assertEqual(options, parser.parse_args.return_value)


    def test_validate(self):
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

