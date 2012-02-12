Re-run command-line every time any files are updated in the current directory
or its subdirectories.

Usage
=====

::

    rerun [command]

e.g::

    rerun python -m unittest mypackage.mymodule

will rerun your tests every time you save your source code. Handy for seeing
the new test results in a console window after you hit 'save' in your editor,
without having to change window focus.

For options, see::

    rerun --help

It detects changes to files by polling file modification times once per second.
On detecting any changes, it clears the terminal and then reruns the given
command once.

It ignores directories called .svn, .git, .hg, .bzr, build and dist.
It ignores files ending with .pyc or .pyo.


Dependencies
============

Tested on WindowsXP, Windows 7, MacOSX, and Ubuntu.

Runs under Python2.7 or 3.2.

No other dependencies.


Install
=======

::

    pip install rerun

See Also
========

Polling for modification times isn't ideal, but in practice I haven't noticed
it burden my machine in project directories containing hundreds of files.

Thanks
======

The idea came from the bash command 'watch', and inspiration for this
implementation came from an old blog post by Jeff Winkler, whos website
http://jeffwinkler.net seems to have now died.

Contact
=======

Jonathan Hartley, tartley@tartley.com

