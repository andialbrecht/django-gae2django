gae2django is a Django helper application that provides an implementation of Google's App Engine API based on pure Django.

The helper makes it easier to re-use applications originally designed for [Google's App Engine](http://code.google.com/appengine/) environment in a Django environment.

(If you want to run existing Django applications in Google's App Engine environment, then [Google App Engine Helper for Django](http://code.google.com/p/google-app-engine-django/) is the right choice for you...)


### Implemented APIs ###

  * Datastore API
  * Memcache API
  * URL fetch API
  * Users API
  * Mail API
  * XMPP API (as a stub implementation that does nothing)

### How to Use the Helper ###

  * add `gae2django` to `INSTALLED_APPS`
  * add `gae2django.middleware.FixRequestUserMiddleware` to `MIDDLEWARE_CLASSES` below `AuthenticationMiddleware`
  * at the top of manage.py add

```
     import gae2django
     gae2django.install()
```

This installs a drop-in replacement for the `google.appengine` module.


### A practical example: The code review tool Rietveld on native Django ###

`gae2django` comes with a practical example and proof of concept: In the `examples` directory you'll find instruction on how to set up Rietveld, the code review tool available at http://codereview.appspot.com, to run with `gae2django` on native Django.
Refer to the [README](http://django-gae2django.googlecode.com/svn/trunk/examples/rietveld/README) or [detailed instructions](http://code.google.com/appengine/articles/pure_django.html).


For known issues and limitations of the ported APIs see KnownIssues.

Please join the [mailing list](http://groups.google.com/group/gae2django) for gae2django related questions.

This project is in a very early stage of development. So don't expect that things always work as expected. Feel free to [contribute](Contribute.md)!