'''
rerun [command]

Poll for changes to any files in cwd or subdirs.
On seeing changes, run the given command (defaults to 'nosetests'.) 

By Jonathan Hartley, tartley@tartley.com
'''

import os
import stat
import sys
import time


# skip these directories
SKIP_DIRS = ['.svn', '.git', '.hg', '.bzr', 'build', 'dist']
# skip files with these extensions
SKIP_EXT = ['.pyc', '.pyo']


def process_command_line(argv):
    # The command to be rerun is created from the command-line
    if len(argv) > 1:
        command = ' '.join(argv[1:])
    else:
        command = 'nosetests'
    return command


def skip_dirs(dirs):
    for dirname in SKIP_DIRS:
        if dirname in dirs:
            dirs.remove(dirname)


def extension_ok(filename):
    return not any(filename.endswith(ext) for ext in SKIP_EXT)


def get_file_stats(filename):
    stats = os.stat(filename)
    return stats[stat.ST_SIZE], stats[stat.ST_MTIME]


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
 

def any_files_changed():
    '''
    Walks subdirs of cwd, looking for files which have changed since last
    invocation.
    '''
    # it's important we don't short circuit on finding the first
    # changed file. We must call has_file_changed on all files in
    # order for it to update its index in prep for future scans
    changed = False
    for root, dirs, files in os.walk('.'):
        skip_dirs(dirs)
        for filename in filter(extension_ok, files):
            changed |= has_file_changed(os.path.join(root, filename))
    return changed


def clear_screen():
    if sys.platform.startswith('win'):
        os.system('cls')
    else:
        os.system('clear')
        

def main():
    command = process_command_line(sys.argv)
    while True:
        if any_files_changed():
            clear_screen()
            os.system(command)
        time.sleep(1)


if __name__ == '__main__':
    main()
