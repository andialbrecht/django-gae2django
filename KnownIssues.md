# Known Issues and Limitations #

## Datastore API ##

`GqlQuery` supports item deletion, but Django's `QuerySet` doesn't.
> Consider converting query results into lists if you use item deletion
> in your code.
> For example, replace
```
    results = models.MyModel.all()
    del results[limit:]
```
> with
```
    results = models.MyModel.all()
    results = list(results)
    del results[limit:]
```

## Memcache API ##

`memcache.flush_al()` always returns `False`, no items are flushed.
> This is due a limitation in Django's cache module that doesn't provides
> a list of items saved in the cache.

`memcache.get_stats()`:
> Returns a directory as described in the API docs, but all values are 0.


## Users API ##

`get_current_user()` returns `None` if the current user isn't authenticated.
> A Django application would expect an `AnonymousUser` object here.

## Rietveld Example ##

  * The Rietveld example currently only works with Django 1.1.2

### Performance Improvements ###

On all gae\_ancestry fields:

```
create index idx_gg on codereview_comment using btree (gae_ancestry varchar_pattern_ops)
```