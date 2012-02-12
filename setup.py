from glob import glob
import importlib
import os
from os.path import join
from pprint import pprint
import sys

from setuptools import setup, find_packages


NAME = 'rerun'
VERSION= importlib.import_module(NAME).VERSION


def read_description(filename):
    '''
    Read given textfile and return (first_para, rest_of_document)
    '''
    with open(filename) as fp:
        text = fp.read()
    paras = text.split('\n\n')
    return paras[0], '\n\n'.join(paras[1:])


def get_package_data(topdir, excluded=set()):
    retval = []
    for dirname, subdirs, files in os.walk(join(NAME, topdir)):
        for x in excluded:
            if x in subdirs:
                subdirs.remove(x)
        retval.append(join(dirname[len(NAME)+1:], '*.*'))
    return retval


def get_data_files(dest, source):
    retval = []
    for dirname, subdirs, files in os.walk(source):
        retval.append(
            (join(dest, dirname[len(source)+1:]), glob(join(dirname, '*.*')))
        )
    return retval


def get_sdist_config():
    description, long_description = read_description('README.txt')
    return dict(
        name=NAME,
        version=VERSION,
        description=description,
        long_description=long_description,
        url='http://bitbucket.org/tartley/gloopy',
        license='New BSD',
        author='Jonathan Hartley',
        author_email='tartley@tartley.com',
        keywords='console command-line development testing tests',
        entry_points = {
            'console_scripts': ['rerun = rerun.main:main'],
            'gui_scripts': [],
        },
        packages=find_packages(exclude=('*.tests',)),
        #data_files=get_data_files('share/doc/rerun', 'docs/html'),
        #package_data={
            #NAME:
                #get_package_data('data') +
                #['examples/*.py']
        #},
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
            #'Operating System :: Microsoft :: Windows :: Windows NT/2000',
            'Operating System :: MacOS :: MacOS X',
            #'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            #'Programming Language :: Python :: 3',
            #'Programming Language :: Python :: 3.2',
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

