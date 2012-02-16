from os.path import join
import stat
from unittest import TestCase

from mock import Mock, patch

from rerun.main import (
    __version__, get_changed_files, clear_screen, get_file_mtime, get_parser,
    has_file_changed, is_ignorable, main, mainloop, parse_args, skip_dirs,
    SKIP_EXT, validate
)


class Test_Rerun(TestCase):

    @patch('sys.stderr')
    def assert_get_parser_error(self, args, expected, mock_stderr):
        parser = get_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(args)
        self.assertIn(expected, mock_stderr.write.call_args[0][0])


    def test_get_parser_version(self):
        self.assert_get_parser_error(['--version'], 'v%s' % (__version__,))


    def test_get_parser_command(self):
        parser = get_parser()
        options = parser.parse_args('command is this'.split())
        self.assertEqual(options.command, ['command', 'is', 'this'])


    def test_get_parser_command_with_options_in_it(self):
        parser = get_parser()
        options = parser.parse_args('ls --color'.split())
        self.assertEqual(options.command, ['ls', '--color'])


    def test_get_parser_verbose(self):
        parser = get_parser()
        options = parser.parse_args('--verbose command is this'.split())
        self.assertTrue(options.verbose)
        self.assertEqual(options.command, ['command', 'is', 'this'])


    def test_get_parser_ignore(self):
        parser = get_parser()
        parser.exit = Mock()
        options = parser.parse_args('--ignore abc command is this'.split())
        self.assertEqual(options.ignore, ['abc'])
        self.assertEqual(options.command, ['command', 'is', 'this'])


    def test_get_parser_ignore_default(self):
        parser = get_parser()
        options = parser.parse_args('command is this'.split())
        self.assertEqual(options.ignore, [])


    def test_get_parser_ignore_multiple(self):
        parser = get_parser()
        options = parser.parse_args(
            '--ignore abc --ignore def command is this'.split())
        self.assertEqual(options.ignore, ['abc', 'def'])
        self.assertEqual(options.command, ['command', 'is', 'this'])


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


    @patch('rerun.main._exit')
    def test_validate_requires_command(self, mock_exit):
        options = Mock()
        options.command = []
        validate(options)
        self.assertEqual(mock_exit.call_args, (('No command specified.',), ))


    @patch('rerun.main.os')
    def test_get_file_stats(self, mock_os):
        def mock_stat(filename):
            self.assertEquals(filename, 'hello')
            return mock_filestat
        mock_os.stat = mock_stat
        mock_filestat = {stat.ST_MTIME: 'mymtime'}

        time = get_file_mtime('hello')

        self.assertEquals(time, 'mymtime')


    def test_skip_dirs_modifies_in_place(self):
        dirs = ['a', 'b', 'c', 'd', 'e', 'f'] 
        skip_dirs(dirs, ['b', 'd', 'f'])
        self.assertEquals(dirs, ['a', 'c', 'e'])


    def test_is_ignorable(self):
        self.assertFalse(is_ignorable('h.txt', []))


    def test_is_ignorable_for_ignored(self):
        self.assertTrue(is_ignorable('h.txt', ['h.txt']))


    def test_is_ignorable_for_ignored_with_same_ending(self):
        self.assertFalse(is_ignorable('gh.txt', ['h.txt']))


    def test_is_ignorable_works_on_basename(self):
        self.assertTrue(is_ignorable(r'somedir/h.txt', ['h.txt']))


    def test_is_ignorable_for_extension(self):
        self.assertTrue(is_ignorable('h' + SKIP_EXT[0], []))


    @patch('rerun.main.get_file_mtime')
    def test_has_file_changed_return_value(self, mock_get_file_stats):
        file_stats = ['mon', 'mon', 'tue', 'tue']
        mock_get_file_stats.side_effect = lambda _: file_stats.pop(0)

        self.assertTrue(has_file_changed('filename'))
        self.assertFalse(has_file_changed('filename'))
        self.assertTrue(has_file_changed('filename'))
        self.assertFalse(has_file_changed('filename'))


    @patch('rerun.main.has_file_changed')
    @patch('rerun.main.os')
    def test_get_changed_files(self, mock_os, mock_changed):
        mock_os.walk.return_value = [
            ('root1', list('dirs1'), list('files')),
        ]
        mock_os.path.join = join
        # one bool for each file in ['f' 'i' 'l' 'e' 's']
        has_file_changed_values = [
            True, False, False, False, True,   # 1st & last file changed
        ]
        mock_changed.side_effect = lambda _: has_file_changed_values.pop(0)

        actual = get_changed_files([])

        self.assertEqual(actual, ['root1/f', 'root1/s'])
        # must call has_file_changed for every file, cannot short-circuit
        self.assertEquals(mock_changed.call_count, 5)


    @patch('rerun.main.os')
    @patch('rerun.main.skip_dirs')
    def test_get_changed_files_calls_skip_dirs(self, mock_skip_dirs, mock_os):
        mock_os.walk.return_value = [
            ('root1', list('dirs1'), list('files')),
            ('root2', list('dirs2'), list('files')),
        ]
        ignoreds = []

        get_changed_files(ignoreds)

        self.assertEqual(
            mock_skip_dirs.call_args_list,
            [
                ((list('dirs1'), ignoreds), ),
                ((list('dirs2'), ignoreds), ),
            ]
        )


    @patch('rerun.main.platform')
    @patch('rerun.main.subprocess')
    def test_clear_screen(self, mock_subprocess, mock_platform):
        mock_platform.system.return_value = 'win32'
        clear_screen()
        self.assertEquals(mock_subprocess.call.call_args[0], ('cls',))

        mock_platform.system.return_value = 'win64'
        clear_screen()
        self.assertEquals(mock_subprocess.call.call_args[0], ('cls',))

        mock_platform.system.return_value = 'Darwin'
        clear_screen()
        self.assertEquals(mock_subprocess.call.call_args[0], ('clear',))

        mock_platform.system.return_value = 'unknown'
        clear_screen()
        self.assertEquals(mock_subprocess.call.call_args[0], ('clear',))


    @patch('rerun.main.time')
    def run_mainloop(self, mock_time):

        # make time.sleep raise StopIteration so that we can end the
        # 'while True' loop in main()
        def mock_sleep(seconds):
            self.assertEquals(seconds, 1)
            raise StopIteration()

        mock_time.sleep = mock_sleep
        options = Mock()

        with self.assertRaises(StopIteration):
            mainloop(options)


    @patch('rerun.main.get_changed_files')
    @patch('rerun.main.clear_screen')
    @patch('rerun.main.subprocess')
    def test_mainloop_no_changes(
        self, mock_subprocess, mock_clear_screen, mock_get_changed_files,
    ):
        mock_get_changed_files.return_value = []

        self.run_mainloop()

        self.assertFalse(mock_clear_screen.called)
        self.assertFalse(mock_subprocess.call.called)


    @patch('rerun.main.get_changed_files')
    @patch('rerun.main.is_ignorable')
    @patch('rerun.main.clear_screen')
    @patch('rerun.main.subprocess')
    def test_mainloop_with_changes(
        self, mock_subprocess, mock_clear_screen, mock_is_ignorable,
        mock_get_changed_files,
    ):
        mock_get_changed_files.return_value = ['somefile']
        mock_is_ignorable.return_value = False

        self.run_mainloop()

        self.assertTrue(mock_clear_screen.called)
        self.assertTrue(mock_subprocess.call.called)


    @patch('rerun.main.get_changed_files')
    @patch('rerun.main.is_ignorable')
    @patch('rerun.main.clear_screen')
    @patch('rerun.main.subprocess')
    def test_mainloop_with_ignorable_changes(
        self, mock_subprocess, mock_clear_screen, mock_is_ignorable,
        mock_get_changed_files,
    ):
        mock_get_changed_files.return_value = ['somefile']
        mock_is_ignorable.return_value = True

        self.run_mainloop()

        self.assertFalse(mock_clear_screen.called)
        self.assertFalse(mock_subprocess.call.called)


    @patch('rerun.main.sys.argv', [1, 2, 3])
    @patch('rerun.main.get_parser')
    @patch('rerun.main.parse_args')
    @patch('rerun.main.validate')
    @patch('rerun.main.mainloop')
    def test_main(
        self, mock_mainloop, mock_validate, mock_parse_args, mock_get_parser
    ):

        main()

        self.assertEqual(mock_get_parser.call_args, ((), ))
        self.assertEqual(
            mock_parse_args.call_args,
            ((mock_get_parser.return_value, [2, 3]),)
        )
        self.assertEqual(
            mock_validate.call_args,
            ((mock_parse_args.return_value, ),)
        )
        self.assertEqual(
            mock_mainloop.call_args,
            ((mock_validate.return_value, ),)
        )

