from os.path import join
import stat
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from mock import call, Mock, patch

from rerun.rerun import (
    act, get_changed_files, clear_screen, get_file_mtime, has_file_changed,
    is_ignorable, main, mainloop, skip_dirs, SKIP_DIRS, SKIP_EXT, step
)


class Test_Rerun(unittest.TestCase):

    @patch('rerun.rerun.os')
    def test_get_file_stats(self, mock_os):
        def mock_stat(filename):
            self.assertEqual(filename, 'hello')
            return mock_filestat
        mock_os.stat = mock_stat
        mock_filestat = {stat.ST_MTIME: 'mymtime'}

        time = get_file_mtime('hello')

        self.assertEqual(time, 'mymtime')


    def test_skip_dirs_modifies_in_place(self):
        dirs = ['a', 'b', 'c', 'd', 'e', 'f'] 
        skip_dirs(dirs, ['b', 'd', 'f'])
        self.assertEqual(dirs, ['a', 'c', 'e'])


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


    @patch('rerun.rerun.get_file_mtime')
    def test_has_file_changed_return_value(self, mock_get_file_stats):
        file_stats = ['mon', 'mon', 'tue', 'tue']
        mock_get_file_stats.side_effect = lambda _: file_stats.pop(0)

        self.assertTrue(has_file_changed('filename'))
        self.assertFalse(has_file_changed('filename'))
        self.assertTrue(has_file_changed('filename'))
        self.assertFalse(has_file_changed('filename'))


    @patch('rerun.rerun.is_ignorable')
    @patch('rerun.rerun.has_file_changed')
    @patch('rerun.rerun.os')
    def test_get_changed_files(self, mock_os, mock_changed, mock_ignorable):

        def fake_has_changed(relname):
            return relname in ['root/f', 'root/l', 'root/s']
        mock_changed.side_effect = fake_has_changed

        def fake_is_ignorable(relname, _):
            return relname in ['root/l']
        mock_ignorable.side_effect = fake_is_ignorable

        mock_os.walk.return_value = [
            ('root', list('dirs'), list('files')),
        ]
        mock_os.path.join = join

        actual = get_changed_files([])

        self.assertEqual(actual, [join('root', 'f'), join('root', 's')])
        # has_file_changed must be called for every file, cannot short-circuit
        # or else it will fail to update some files' modification times,
        # and generate false positives on later calls to step.
        self.assertEqual(mock_changed.call_count, 5)


    @patch('rerun.rerun.os')
    @patch('rerun.rerun.skip_dirs')
    def test_get_changed_files_calls_skip_dirs(self, mock_skip_dirs, mock_os):
        mock_os.walk.return_value = [
            ('root1', list('dirs1'), list('files1')),
            ('root2', list('dirs2'), list('files2')),
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


    @patch('rerun.rerun.platform')
    @patch('rerun.rerun.os.system')
    def test_clear_screen(self, mock_system, mock_platform):
        mock_platform.system.return_value = 'Windows'
        clear_screen()
        self.assertEqual(mock_system.call_args[0], ('cls',))

        mock_platform.system.return_value = 'win32'
        clear_screen()
        self.assertEqual(mock_system.call_args[0], ('cls',))

        mock_platform.system.return_value = 'win64'
        clear_screen()
        self.assertEqual(mock_system.call_args[0], ('cls',))

        mock_platform.system.return_value = 'Darwin'
        clear_screen()
        self.assertEqual(mock_system.call_args[0], ('clear',))

        mock_platform.system.return_value = 'unknown'
        clear_screen()
        self.assertEqual(mock_system.call_args[0], ('clear',))


    @patch('rerun.rerun.clear_screen')
    @patch('rerun.rerun.sys.stdout')
    @patch('rerun.rerun.subprocess.call')
    def test_act_calls_each_thing_in_order(
        self, mock_call, mock_stdout, mock_clear
    ):
        options = Mock(command='mycommand', shell='myshell')

        act(['mychanges'], options, False)

        self.assertTrue(mock_clear.called)
        self.assertEqual(
            mock_stdout.write.call_args_list,
            [call('mycommand'), call('\n'), call('mychanges'), call('\n')]
        )
        self.assertEqual(
            mock_call.call_args,
            call(options.command, shell=True, executable='myshell')
        )


    @patch('rerun.rerun.clear_screen')
    @patch('rerun.rerun.sys.stdout')
    @patch('rerun.rerun.subprocess.call')
    def test_act_on_first_time_doesnt_print_changed_files(
        self, mock_call, mock_stdout, mock_clear
    ):
        options = Mock(command='mycommand', shell='myshell')

        act(['mychanges'], options, True)

        self.assertEqual(
            mock_stdout.write.call_args_list,
            [call('mycommand'), call('\n')]
        )


    @patch('rerun.rerun.clear_screen')
    @patch('rerun.rerun.sys.stdout')
    @patch('rerun.rerun.subprocess.call')
    def test_act_without_verbose_doesnt_print_changed_files(
        self, mock_call, mock_stdout, mock_clear
    ):
        options = Mock(command='mycommand', shell='myshell', verbose=False)

        act(['mychanges'], options, False)

        self.assertEqual(
            mock_stdout.write.call_args_list,
            [call('mycommand'), call('\n')]
        )


    @patch('rerun.rerun.get_changed_files')
    @patch('rerun.rerun.act')
    @patch('rerun.rerun.time.sleep', Mock())
    def test_step_calls_act_if_changed_files(self, mock_act, mock_changed):
        mock_changed.return_value = ['mychanges']
        options = Mock(ignore=[])

        step(options)
        
        self.assertEqual(
            mock_act.call_args,
            call(['mychanges'], options, False)
        )

    @patch('rerun.rerun.get_changed_files')
    @patch('rerun.rerun.act')
    @patch('rerun.rerun.time.sleep', Mock())
    def test_step_doesnt_call_act_if_no_changed_files(self, mock_act, mock_changed):
        mock_changed.return_value = []
        options = Mock(ignore=[])

        step(options)
        
        self.assertIsNone(mock_act.call_args)


    @patch('rerun.rerun.get_changed_files')
    @patch('rerun.rerun.act')
    @patch('rerun.rerun.time.sleep', Mock())
    def test_step_passes_first_time_to_act(self, mock_act, mock_changed):
        mock_changed.return_value = ['mychanges']
        options = Mock(ignore=[])

        step(options, first_time=True)
        
        self.assertEqual(
            mock_act.call_args,
            call(['mychanges'], options, True)
        )


    @patch('rerun.rerun.step')
    def test_mainloop_calls_step_with_first_time_then_repeatedly_without(
        self, mock_step
    ):
        actions = [None, None, ZeroDivisionError]

        def raise_next_action(options, first_time=False):
            action = actions.pop(0)
            if action:
                raise action()

        mock_step.side_effect = raise_next_action

        options = Mock()
        with self.assertRaises(ZeroDivisionError):
            mainloop(options)

        self.assertEqual(
            mock_step.call_args_list,
            [
                call(options, first_time=True),
                call(options),
                call(options),
            ]
        )


    @patch('rerun.rerun.sys.argv', [1, 2, 3])
    @patch('rerun.rerun.get_parser')
    @patch('rerun.rerun.parse_args')
    @patch('rerun.rerun.validate')
    @patch('rerun.rerun.mainloop')
    def test_main(
        self, mock_mainloop, mock_validate, mock_parse_args, mock_get_parser
    ):

        main()

        self.assertEqual(
            mock_get_parser.call_args,
            (('rerun', SKIP_DIRS, SKIP_EXT), )
        )
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

