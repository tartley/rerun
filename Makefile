# This Makefile is just a cheatsheet to remind me of some commonly used
# commands. I'm generally executing these on OSX with up-to-date gnu binaries
# on the PATH, or on Ubuntu, or on WindowsXP/7 with Cygwin binaries foremost on
# the PATH.

test:
	python -m unittest discover rerun/tests
.PHONY: test

pylint:
	pylint rerun.py
.PHONY: pylint

tags:
	ctags -R --languages=python .
.PHONY: tags

clean:
	rm -rf build dist MANIFEST
	find . -name '*.py[oc]' -exec rm {} \;
.PHONY: clean


# sdist: clean
# 	python setup.py sdist --formats=zip,gztar
# .PHONY: sdist
# 
# register: clean
# 	python setup.py sdist --formats=zip,gztar register 
# .PHONY: release
# 
# upload: clean
# 	python setup.py sdist --formats=zip,gztar register upload
# .PHONY: release


# runsnake is a GUI visualiser for the output of cProfile
# http://www.vrplumber.com/programming/runsnakerun/
# profile:
# 	${PYTHON} -O -m cProfile -o profile.out ${NAME}
# 	runsnake profile.out
# .PHONY: profile

# py2exe:
# 	rm -rf dist/${NAME}-${RELEASE}.* build
# 	${PYTHON} setup.py --quiet py2exe
# .PHONY: py2exe

