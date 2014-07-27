#!/usr/bin/env python2.7
from glob import glob
import os
from os.path import join
import re
import sys

from setuptools import setup, find_packages

# setup.py should not import non-stdlib modules, other than setuptools, at
# module level, since this prevents setup.py from running until they are
# installed. Installing 'py2exe' should not be required just to do a 'setup.py
# sdist'.

# setup.py should not import from our local source (pip needs to be able to
# import setup.py before our dependencies have been installed)


NAME = 'rerun'

def read_description(filename):
    '''
    Read given textfile and return (2nd_para, 3rd_para to end)
    '''
    with open(filename) as fp:
        text = fp.read()
    paras = text.split('\n\n')
    return paras[1], '\n\n'.join(paras[2:])


def read_version(filename):
    '''
    Manually parse the version string so that we don't have to import anything
    from local source, which (along with its dependencies) will not always be
    present, e.g. setuptools must install our dependencies first, but can't
    know what they are until after it has run this setup.py.
    '''
    with open(filename, "rt") as filehandle:
        content = filehandle.read()
    match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]$", content, re.M)
    if match:
        return match.group(1)
    else:
        raise RuntimeError(
            "Can't read version from %s:\n%s" % (filename, content)
        )


def get_package_data(topdir, excluded=set()):
    retval = []
    for dirname, subdirs, files in os.walk(join(NAME, topdir)):
        for x in excluded:
            if x in subdirs:
                subdirs.remove(x)
        retval.append(join(dirname[len(NAME) + 1:], '*.*'))
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

    install_requires = []
    if sys.version_info < (2, 7):
        install_requires.append("argparse == 1.2.1")

    return dict(
        name=NAME,
        version=read_version(join(NAME, 'version.py')),
        description=description,
        long_description=long_description,
        url='http://pypi.python.org/pypi/%s/' % (NAME,),
        author='Jonathan Hartley',
        author_email='tartley@tartley.com',
        keywords='console command-line development testing tests',
        entry_points = {
            'console_scripts': ['{0} = {0}.{0}:main'.format(NAME)],
            'gui_scripts': [],
        },
        install_requires=install_requires,
        packages=find_packages(exclude=('*.tests',)),
        # see classifiers http://pypi.python.org/pypi?:action=list_classifiers
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Natural Language :: English',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: POSIX :: Linux',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.0',
            'Programming Language :: Python :: 3.1',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: Implementation :: CPython',
        ],
        zip_safe=True,
    )


def main():
    config = {}
    config.update(get_sdist_config())
    setup(**config)


if __name__ == '__main__':
    main()

