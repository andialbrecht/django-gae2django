RIETVELDREV=650

default:
	@echo "Run 'make all' to fetch required sources to run this example."

all: static templates codereview django gae2django dev.db
	@echo "Run './manage.py runserver 127.0.0.1:8000' to run Rietveld."

clean: clean_local clean_external

clean_external: clean_rietveld clean_django

clean_rietveld:
	rm -rf codereview static templates upload.py

clean_django:
	unlink django

clean_local:
	unlink gae2django
	rm -f dev.db

gae2django:
	ln -s ../../gae2django .

dev.db:
	./manage.py syncdb

codereview:
	svn co http://rietveld.googlecode.com/svn/trunk/codereview@$(RIETVELDREV)

static: upload.py
	svn co http://rietveld.googlecode.com/svn/trunk/static@$(RIETVELDREV)

upload.py:
	svn export http://rietveld.googlecode.com/svn/trunk/upload.py@$(RIETVELDREV)
	patch -p0 < patches/upload.diff
	patch -p0 < patches/account-login-links.diff
	patch -p0 < patches/download.link.diff

templates:
	svn co http://rietveld.googlecode.com/svn/trunk/templates@$(RIETVELDREV)

django:
	ln -s ../../django .