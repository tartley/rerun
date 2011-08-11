none:
	@echo "'make install' works on my machine, but probably won't on yours."

install:
	chmod 755 rerun.py
	cp -p rerun.py ~/docs/bin
	ln -s ~/docs/bin/rerun.py ~/docs/bin/rerun

