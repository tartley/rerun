'''
rerun [command]

Poll for changes to any files in cwd or subdirs.
On seeing changes, run the given command (defaults to 'nosetests'.) 

http://bitbucket.org/tartley/rerun

Only tested on WindowsXP, Python 2.7.

By Jonathan Hartley, http://tartley.com
Thanks to Jeff Winkler for the original formulation, http://jeffwinkler.net
'''

import os
import stat
import sys
import time


# skip these directories
SKIP_DIRS = ['.svn', '.git', '.hg', '.bzr', 'build', 'dist']
# skip files with these extensions
SKIP_EXT = ['.pyc', '.pyo']


# the command to be rerun
# populated from all args on the command-line
command = None


def process_command_line(argv):
    global command
    if len(argv) > 1:
        command = ' '.join(argv[1:])
    else:
        command = 'nosetests'


def skip_dirs(dirs):
    for skip in SKIP_DIRS:
        if skip in dirs:
            dirs.remove(skip)


def filter_files(files):
    for filename in files:
        if not any(filename.endswith(skip) for skip in SKIP_EXT):
            yield filename


def get_file_stats(filename):
    stats = os.stat(filename)
    size = stats[stat.ST_SIZE]
    modification_time = stats[stat.ST_MTIME]
    return size, modification_time


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
    invokation.
    '''
    changed = False
    for root, dirs, files in os.walk('.'):
        skip_dirs(dirs)
        for filename in filter_files(files):
            changed |= has_file_changed(os.path.join(root, filename))

    return changed


def main():
    process_command_line(sys.argv)
    while True:
        if any_files_changed():
            os.system('cls')
            os.system(command)
        time.sleep (1)


if __name__ == '__main__':
    main()
