#!/usr/bin/env python2.7
from glob import glob
import os
from os.path import join
import re
import sys

from setuptools import setup, find_packages

# this file should not import from our local source


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
        install_requires.append("argparse >= 1.2.1")

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
            'console_scripts': ['%s = %s.main:main' % (NAME, NAME)],
            'gui_scripts': [],
        },
        install_requires=install_requires,
        packages=find_packages(exclude=('*.tests',)),
        #include_package_data=True,
        #package_data={
            #'package.subpackage': ['globs'],
            #NAME: get_package_data('data')
        #},
        #exclude_package_data={
            #'package.subpackage': ['globs']
        #},
        #data_files=[
            # ('install-dir', ['files-relative-to-setup.py']),
        #], 
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
        zip_safe=True,
    )


if __name__ == '__main__':
    setup(**get_sdist_config())

