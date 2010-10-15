RERUN

    http://bitbucket.org/tartley/rerun

    A command-line script to re-run the given command whenever it detects
    changes to any file in the current directory, or in subdirectories of that.

    Rerun requires that Python is installed and on the PATH. Only tested on
    Windows with Python2.7.

    It detects changes to files by polling once per second. On each poll, it
    walks the files in the current directory and all recursive subdirs. For
    each file, it checks the size and modification time. On detecting any
    changes, it clears the terminal and then reruns the given command once.

    It ignores directories called .svn, .git, .hg, .bzr, build and dist.
    It ignores files ending with .pyc or .pyo.


USAGE

    rerun [command]

    e.g:
    rerun python -m unittest package.testmodule
    rerun python -m unittest --verbose package.testmodule.testclass.testmethod

    If 'command' is not given, it defaults to 'nosetests', a Python unit test
    running utility.


THANKS

    This is an improved version of an idea I first saw implemented by Jeff
    Winkler, whos website http://jeffwinkler.net seems to have now died.


CONTACT

    I'd love to hear about it if you have issues with this script, or ideas on
    how it could be better.

    Jonathan Hartley, tartley@tartley.com

