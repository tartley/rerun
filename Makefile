# This Makefile is just a cheatsheet to remind me of some commonly used
# commands. I'm generally executing these on OSX with up-to-date gnu binaries
# on the PATH, or on Ubuntu, or on WindowsXP/7 with Cygwin binaries foremost on
# the PATH.

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


virtualenv:
	if [ ! -d $(HOME)/.virtualenvs/$(NAME) ]; then cd ~/.virtualenvs; virtualenv $(NAME); fi
	# Make tries to run the following in a new bash session, which fails
	# Even if it could be made to work, we need it to work in current process
	# so that it can set windows env.vars.
		# "%HOME%\.virtualenvs\$(NAME)\Scripts\activate"
	# So there is no point doing the following:
		# pip install -r requirements_dev.txt

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
# Note that setup.py should not import py2exe at module level
# this would prevent any setup.py command being used unless py2exe was installed

