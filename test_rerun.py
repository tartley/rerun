
from mock import patch
from unittest import TestCase, main as unittest_main

from os.path import join
import stat

from rerun import (
    any_files_changed, clear_screen, extension_ok, get_file_stats,
    has_file_changed, main, process_command_line, skip_dirs,
)


class Test_Rerun(TestCase):

    def test_process_command_line(self):
        self.assertEquals(
            process_command_line(['rerun.py', 'hello', 'there']),
            'hello there'
        )


    def test_skip_dirs_modifies_in_place(self):
        dirs = ['a', '.svn', 'b', '.git', 'c', '.hg', 'd', '.bzr',
                'e', 'build', 'f', 'dist', 'g', ]
        skip_dirs(dirs)
        self.assertEquals(dirs, list('abcdefg'))


    def test_extension_ok(self):
        for filename in ['a.pyo', 'a.pyc']:
            self.assertFalse(extension_ok(filename))
        for filename in ['a.py', 'Makefile']:
            self.assertTrue(extension_ok(filename))


    @patch('rerun.os')
    def test_get_file_stats(self, mock_os):
        def mock_stat(filename):
            self.assertEquals(filename, 'hello')
            return mock_filestat
        mock_os.stat = mock_stat
        mock_filestat = {stat.ST_SIZE: 123, stat.ST_MTIME: 'mtime'}

        size, time = get_file_stats('hello')

        self.assertEquals(size, 123)
        self.assertEquals(time, 'mtime')


    @patch('rerun.get_file_stats')
    def test_has_file_changed_return_value(self, mock_get_file_stats):
        file_stats = [
            (123, 'monday'),
            (123, 'monday'),
            (999, 'monday'),
            (999, 'tuesday'),
            (999, 'tuesday'),
        ]
        mock_get_file_stats.side_effect = lambda _: file_stats.pop(0)

        self.assertTrue(has_file_changed('filename'))
        self.assertFalse(has_file_changed('filename'))
        self.assertTrue(has_file_changed('filename'))
        self.assertTrue(has_file_changed('filename'))
        self.assertFalse(has_file_changed('filename'))


    @patch('rerun.os.walk')
    @patch('rerun.skip_dirs')
    @patch('rerun.has_file_changed')
    def test_any_files_changed_return_value(
        self, mock_has_file_changed, mock_skip_dirs, mock_walk
    ):
        walk_values = [
            [('root1', 'dirs', 'files')],
            [('root2', 'dirs', 'files')],
            [('root3', 'dirs', 'files')],
        ]
        mock_walk.side_effect = lambda _: walk_values.pop(0)

        # one bool for each file in ['f' 'i' 'l' 'e' 's']
        has_file_changed_values = [
            False, False, False, False, False, # should return false
            False, False, False, False, True,  # should return true
            True, False, False, False, False,  # should return true
        ]
        mock_has_file_changed.side_effect = \
            lambda _: has_file_changed_values.pop(0)

        self.assertFalse(any_files_changed())
        self.assertTrue(any_files_changed())
        self.assertTrue(any_files_changed())

        # must call has_file_changed for every file, cannot short-circuit
        self.assertEquals(mock_has_file_changed.call_count, 15)


    @patch('rerun.os.walk')
    @patch('rerun.skip_dirs')
    @patch('rerun.has_file_changed')
    def test_any_files_changed_skips_dirs(
        self, mock_has_file_changed, mock_skip_dirs, mock_walk
    ):
        mock_has_file_changed.return_value = False

        walk_values = [
            [('root1', list('dirs1'), 'files')],
            [('root2', list('dirs2'), 'files')],
            [('root3', list('d3'), 'files')],
        ]
        mock_walk.side_effect = lambda _: walk_values.pop(0)

        any_files_changed()
        any_files_changed()
        any_files_changed()

        self.assertEquals(
            [args[0][0] for args in mock_skip_dirs.call_args_list],
            [ list('dirs1'), list('dirs2'), list('d3'), ],
        )


    @patch('rerun.os.walk')
    @patch('rerun.skip_dirs')
    @patch('rerun.has_file_changed')
    def test_any_files_changed_filter_files(
        self, mock_has_file_changed, mock_skip_dirs, mock_walk
    ):
        mock_has_file_changed.return_value = False

        files = ['f1', 'f2.pyc', 'f3.pyo', 'f4.py']
        walk_values = [
            [('root', 'dirs', files)],
        ]
        mock_walk.side_effect = lambda _: walk_values.pop(0)

        any_files_changed()

        self.assertEquals(
            [args[0][0] for args in mock_has_file_changed.call_args_list],
            [join('root', 'f1'), join('root', 'f4.py')]
        )


    @patch('rerun.sys')
    @patch('rerun.os.system')
    def test_clear_screen(self, mock_system, mock_sys):
        mock_sys.platform = 'win32'
        clear_screen()
        self.assertEquals(mock_system.call_args[0], ('cls',))

        mock_sys.platform = 'win64'
        clear_screen()
        self.assertEquals(mock_system.call_args[0], ('cls',))

        mock_sys.platform = 'notwin'
        clear_screen()
        self.assertEquals(mock_system.call_args[0], ('clear',))


    @patch('rerun.time')
    @patch('rerun.sys')
    def assert_main(self, mock_process_command_line, mock_sys, mock_time):
        # make time.sleep raise a DieError so that we can end the 'while True'
        # loop in main()
        class DieError(AssertionError):
            pass

        def mock_sleep(seconds):
            self.assertEquals(seconds, 1)
            raise DieError()

        mock_time.sleep = mock_sleep

        with self.assertRaises(DieError):
            main()

        self.assertEquals(
            mock_process_command_line.call_args[0][0],
            mock_sys.argv
        )


    @patch('rerun.any_files_changed')
    @patch('rerun.clear_screen')
    @patch('rerun.process_command_line')
    @patch('rerun.os.system')
    def test_main(
        self, mock_system, mock_process_command_line, mock_clear_screen,
        mock_any_files_changed
    ):
        mock_process_command_line.return_value = 'command'

        mock_any_files_changed.return_value = False
        self.assert_main(mock_process_command_line)
        self.assertFalse(mock_clear_screen.called)
        self.assertFalse(mock_system.called)

        mock_any_files_changed.return_value = True
        self.assert_main(mock_process_command_line)
        self.assertTrue(mock_clear_screen.called)
        self.assertEquals(mock_system.call_args[0], ('command',))



if __name__ == '__main__':
    unittest_main()

