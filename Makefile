none:
	@echo "'make install' works on my machine, but probably won't on yours."

install:
	cp rerun.py ../../bin
	chmod 755 ../../bin/rerun.py

