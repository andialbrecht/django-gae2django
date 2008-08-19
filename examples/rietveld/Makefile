default:
	@echo "Run 'make all' to fetch required sources to run this example."

all: codereview static templates django appengine_hook __init__.py manage.py settings.py dev.db

clean: clean_local clean_external

clean_external: clean_rietveld clean_django

clean_rietveld:
	rm -rf codereview static templates

clean_django:
	rm -rf django

clean_local:
	unlink appengine_hook
	rm -f __init__.py settings.py manage.py dev.db

appengine_hook:
	ln -s ../../appengine_hook .

__init__.py:
	touch __init__.py

manage.py:
	cp ../../manage.py .

settings.py:
	sed "s/'appengine_hook',/'appengine_hook',\n    'codereview',/g" ../../settings.py  > settings.py

dev.db:
	./manage.py syncdb

codereview:
	svn co http://rietveld.googlecode.com/svn/trunk/codereview

static:
	svn co http://rietveld.googlecode.com/svn/trunk/static

templates:
	svn co http://rietveld.googlecode.com/svn/trunk/templates

django:
	svn co http://code.djangoproject.com/svn/django/trunk/django