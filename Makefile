# This Makefile is just a cheatsheet to remind me of some commonly used
# commands. I'm generally executing these from:
# 	- Linux Bash, or
# 	- OSX with up-to-date gnu binaries (Homebrew coreutils) on the PATH, or
# 	- WindowsXP/7 Cmd with Cygwin binaries foremost on the PATH.

NAME=rerun

test:
	python -m unittest discover rerun/tests
.PHONY: test

test-2.6:
	unit2-2.6 discover .
.PHONY: test-2.6

pylint:
	pylint *.py
.PHONY: pylint

tags:
	ctags -R --languages=python .
.PHONY: tags

clean:
	rm -rf build dist MANIFEST .tox $(NAME).egg-info
	find . -name '*.py[oc]' -exec rm {} \;
.PHONY: clean

# create executable entry points in our python or virtualenv's bin dir
develop:
	python setup.py develop
.PHONY: develop

sdist: clean
	python setup.py sdist --formats=zip,gztar
.PHONY: sdist

register: clean
	python setup.py sdist --formats=zip,gztar register 
.PHONY: register
 
upload: clean
	python setup.py sdist --formats=zip,gztar register upload
.PHONY: upload

