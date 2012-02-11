pylint:
	pylint rerun.py
.PHONY: pylint

test:
	python -m unittest discover tests
.PHONY: test

tags:
	ctags -R --languages=python .
.PHONY: tags

