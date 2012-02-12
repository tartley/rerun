from glob import glob
import importlib
import os
from os.path import join
from pprint import pprint
import sys

from distutils.command.install import INSTALL_SCHEMES
from setuptools import setup, find_packages


VERSION= importlib.import_module('rerun').VERSION


def read_description(filename):
    '''
    Read given textfile and return (2nd_para, 3rd_para to end)
    '''
    with open(filename) as fp:
        text = fp.read()
    paras = text.split('\n\n')
    return paras[1], '\n\n'.join(paras[2:])


def get_package_data(topdir, excluded=set()):
    retval = []
    for dirname, subdirs, files in os.walk(join('rerun', topdir)):
        for x in excluded:
            if x in subdirs:
                subdirs.remove(x)
        retval.append(join(dirname[len('rerun') + 1:], '*.*'))
    return retval


def get_data_files(dest, source):
    retval = []
    for dirname, subdirs, files in os.walk(source):
        retval.append(
            (join(dest, dirname[len(source)+1:]), glob(join(dirname, '*.*')))
        )
    return retval


def get_sdist_config():
    description, long_description = read_description('README')

    # Make data files always install to the same location as source. Without
    # this, 'pip install' puts data files in the root of the virtualenv.
    # This is to make the LICENSE file install next to the source.
    for scheme in INSTALL_SCHEMES.values():
        scheme['data'] = scheme['purelib']

    return dict(
        name='rerun',
        version=VERSION,
        description=description,
        long_description=long_description,
        url='http://bitbucket.org/tartley/gloopy',
        author='Jonathan Hartley',
        author_email='tartley@tartley.com',
        keywords='console command-line development testing tests',
        entry_points = {
            'console_scripts': ['rerun = rerun.main:main'],
            'gui_scripts': [],
        },
        packages=find_packages(exclude=('*.tests',)),
        # include_package_data=True,
        # package_data={ 
            # 'mypackage.subpackage': ['globs'],
            # 'rerun': get_package_data('data')
        #},
        data_files=[
            # ('install-dir', ['files-relative-to-setup.py']),
            ('rerun', ['LICENSE']),
        ], 
        # see classifiers http://pypi.python.org/pypi?:action=list_classifiers
        classifiers=[
            #'Development Status :: 1 - Planning',
            #'Development Status :: 2 - Pre-Alpha',
            #'Development Status :: 3 - Alpha',
            'Development Status :: 4 - Beta',
            #'Development Status :: 5 - Production/Stable',
            #'Development Status :: 6 - Mature',
            #'Development Status :: 7 - Inactive',
            'Intended Audience :: Developers',
            #'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: BSD License',
            'Natural Language :: English',
            'Operating System :: Microsoft :: Windows :: Windows NT/2000',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: POSIX :: Linux',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: Implementation :: CPython',
        ],    
    )


def main():
    config = get_sdist_config()

    if '--verbose' in sys.argv:
        pprint(config)
    if '--dry-run' in sys.argv:
        return

    setup(**config)


if __name__ == '__main__':
    main()

