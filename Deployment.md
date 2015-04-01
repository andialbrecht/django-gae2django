# Deployment #

Deploying an application that uses `gae2django` is pretty much the same as with
other Django applications and described in this [document](http://docs.djangoproject.com/en/dev/howto/deployment/).

You only have to take care, that `gae2django.install()` is called **before** any Django import.

So, for example, when using WSGI to deploy your application, your main WSGI file will look like this

```
import os
import sys

import gae2django
gae2django.install()

os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

```