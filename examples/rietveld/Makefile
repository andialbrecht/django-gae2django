default:
	@echo "Run 'make all' to fetch required sources to run this example."

all: static templates codereview django gae2django manage.py dev.db
	@echo "Run './manage.py runserver' to run Rietveld."

clean: clean_local clean_external

clean_external: clean_rietveld clean_django

clean_rietveld:
	rm -rf codereview static templates

clean_django:
	rm -rf django

clean_local:
	unlink gae2django
	rm -f manage.py dev.db

gae2django:
	ln -s ../../gae2django .

manage.py:
	cp ../../manage.py .

dev.db:
	./manage.py syncdb

codereview:
	svn co http://rietveld.googlecode.com/svn/trunk/codereview
	patch -p0 < patches/library.diff
	patch -p0 < patches/views.diff

static:
	svn co http://rietveld.googlecode.com/svn/trunk/static
	patch -p0 < patches/upload.diff

templates:
	svn co http://rietveld.googlecode.com/svn/trunk/templates

django:
	svn co http://code.djangoproject.com/svn/django/trunk/django