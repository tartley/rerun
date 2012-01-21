RERUN

    http://bitbucket.org/tartley/rerun

    Tested on WindowsXP, Windows 7, MacOSX, and Ubuntu
    Runs under Python2.7 or 3.2.

USAGE

    rerun [command]

    e.g::

        rerun python -m unittest mypackage.mymodule

    will rerun your tests every time you save your source code.

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

    On most operating systems, just copy or symlink the script somewhere on
    your PATH, e.g::
    
        ln -s path/to/rerun.py ~/bin/rerun

    On Windows, you might need to associate the .py extension with your Python
    executable, so you can run by typing "rerun.py" instead of
    "python rerun.py". If you add '.py' to your PATHEXT environment variable,
    then you can run by typing just "rerun".

THANKS

    The idea came from the bash command 'watch', and inspiration for this
    improved implementation came from an old blog post by Jeff Winkler, whos
    website http://jeffwinkler.net seems to have now died.

CONTACT

    I'd love to hear about it if you have problems with this script, or ideas
    on how it could be better.

    Jonathan Hartley, tartley@tartley.com

