RERUN

    http://bitbucket.org/tartley/rerun

    Only currently tested on WindowsXP with Python2.7.

USAGE

    rerun [command]

    e.g:
    rerun python -m unittest package.testmodule
    rerun python -m unittest --verbose package.testmodule.testclass.testmethod

    If 'command' is not given, it defaults to 'nosetests', a Python unit test
    running utility.

DESCRIPTION

    A command-line Python script to re-run the given command whenever it
    detects changes to any file in the current directory or its
    subdirectories.

    Rerun requires that Python is installed and on the PATH.

    It detects changes to files by polling once per second. On each poll, it
    walks the files in the current directory and all recursive subdirs. For
    each file, it checks the size and modification time. On detecting any
    changes, it clears the terminal and then reruns the given command once.

    It ignores directories called .svn, .git, .hg, .bzr, build and dist.
    It ignores files ending with .pyc or .pyo.

INSTALL

    Put the file rerun.py on the PATH.

    On Windows, you might need to associate the .py extension with your Python
    executable. In order to be able to type 'rerun' instead of 'rerun.py',
    you might like to add '.py' to the PATHEXT environment variable.

THANKS

    The idea came from the bash command 'watch', and inspiration for this
    improved implementation came from an old blog post by Jeff Winkler, whos
    website http://jeffwinkler.net seems to have now died.

CONTACT

    I'd love to hear about it if you have problems with this script, or ideas
    on how it could be better.

    Jonathan Hartley, tartley@tartley.com

