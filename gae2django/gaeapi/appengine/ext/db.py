import base64
import cPickle
import logging
import os
import random
import re
import time
import types

from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import manager
from django.db.models.query import QuerySet
from django.db import transaction
from django.utils.hashcompat import md5_constructor

# Use the system (hardware-based) random number generator if it exists.
# Taken from django.contrib.sessions.backends.base
if hasattr(random, 'SystemRandom'):
    randrange = random.SystemRandom().randrange
else:
    randrange = random.randrange
MAX_SESSION_KEY = 18446744073709551616L     # 2 << 63


class Query(QuerySet):

    def filter(self, *args, **kwds):
        if kwds:
            return super(Query, self).filter(*args, **kwds)
        property_operator, value = args
        if isinstance(value, basestring):
            where = u'%s \'%s\'' % (property_operator,
                                    value.replace("'", "''"))
        else:
            where = '%s %r' % (property_operator, value)
        self.query.add_extra(None, None, [where], None, None, None)

    def _filter(self, *args, **kwds):
        return super(Query, self).filter(*args, **kwds)

    def order(self, prop):
        self.query.add_ordering(prop)

    def get(self, *args, **kwds):
        if kwds:
            return super(Query, self).get(*args, **kwds)
        return list(self)[0]

    def ancestor(self, ancestor):
        raise NotImplementedError

    def fetch(self, limit, offset=0):
        return list(self)[offset:limit]


class BaseManager(manager.Manager):

    def __iter__(self):
        return self.iterator()

    def _filter(self, *args, **kwds):
        return self.get_query_set()._filter(*args, **kwds)

    def count(self, limit=None):
        return super(BaseManager, self).count()

    def order(self, *args, **kwds):
        return super(BaseManager, self).order_by(*args, **kwds)

    def get_query_set(self):
        return Query(self.model)


class BaseModelMeta(models.base.ModelBase):

    def __new__(cls, name, bases, attrs):
        new_cls = super(BaseModelMeta, cls).__new__(cls, name, bases, attrs)
        new_cls.objects = BaseManager()
        new_cls.objects.model = new_cls
        new_cls._default_manager = new_cls.objects
        return new_cls


class Model(models.Model):

    __metaclass__ = BaseModelMeta

    gae_key = models.CharField(max_length=64, blank=True, null=True,
                               unique=True)
    gae_parent_ctype = models.ForeignKey(ContentType,
                                         blank=True, null=True)
    gae_parent_id = models.PositiveIntegerField(blank=True, null=True)
    gae_ancestry = models.CharField(max_length=500, blank=True, null=True)
    parent = generic.GenericForeignKey('gae_parent_ctype',
                                       'gae_parent_id')

    class Meta:
        abstract = True

    def __init__(self, *args, **kwds):
        # keywords for GenericForeignKeys don't work with abstract classes:
        # http://code.djangoproject.com/ticket/8309
        if 'parent' in kwds:
            parent = kwds['parent']
            ctype = ContentType.objects.get_for_model(parent.__class__)
            kwds['gae_parent_ctype'] = ctype
            kwds['gae_parent_id'] = parent.id
            kwds['gae_ancestry'] = ''.join(['@%s@' % prnt.key()
                                            for prnt in parent.get_ancestry()])

            del kwds['parent']
        if 'key' in kwds:
            kwds['gae_key'] = kwds['key']
            del kwds['key']
        if 'key_name' in kwds:
            kwds['gae_key'] = kwds['key_name']
            del kwds['key_name']
        super(Model, self).__init__(*args, **kwds)

    @classmethod
    def get_or_insert(cls, key, **kwds):
        try:
            return cls.objects.get(gae_key=key)
        except cls.DoesNotExist:
            kwds['gae_key'] = key
            new = cls(**kwds)
            new.save()
            return new

    @classmethod
    def get_by_key_name(cls, keys, parent=None):
        if type(keys) not in [types.ListType, types.TupleType]:
            keys = [keys]
        result = []
        for key in keys:
            try:
                kwds = {'gae_key': str(key)}
                if parent is not None:
                    kwds['gae_ancestry__icontains'] = str(parent.key())
                result.append(cls.objects.get(**kwds))
            except cls.DoesNotExist:
                result.append(None)
        if len(keys) == 1:
            return result[0]
        return result

    @classmethod
    def get_by_id(cls, id_, parent=None):
        # Ignore parent, we've got an ID
        ret = []
        if type(id_) not in (types.ListType, types.TupleType):
            id_ = [id_]
        for i in id_:
            try:
                ret.append(cls.objects.get(id=i))
            except cls.DoesNotExist:
                ret.append(None)
        if len(id_) == 1:
            return ret[0]
        else:
            return ret

    @classmethod
    def kind(cls):
        # Return the table name here. It should be the expected output...
        return cls._meta.db_table

    @classmethod
    def all(cls):
        return cls.objects.all()

    @classmethod
    def properties(cls):
        props = {}
        [props.setdefault(field.name, field) for field in cls._meta.fields
         if not field.name.startswith('gae_')]
        return props

    def key(self):
        return Key(self)

    def put(self):
        return self.save()

    def save(self):
        if not self.key:
            try:
                pid = os.getpid()
            except AttributeError:
                pid = 1
            self.key = md5_constructor("%s%s%s%s"
                                       % (randrange(0, MAX_SESSION_KEY),
                                          pid, time.time(),
                                          self.__name__)).hexdigest()
        super(Model, self).save()

    @classmethod
    def gql(cls, clause, *args, **kwds):
        from google.appengine.ext import db
        query = db.GqlQuery('SELECT * FROM %s %s' % (cls.__name__,
                                                     clause), *args, **kwds)
        query._real_cls = cls
        return query

    @classmethod
    def get(cls, keys):
        if type(keys) not in [types.ListType, types.TupleType]:
            keys = [keys]
        instances = [cls.get_by_key_name(key) for key in keys]
        if len(keys) == 1:
            return instances[0]
        else:
            return instances

    def parent_key(self):
        return self.parent.key()

    def get_ancestry(self):
        """Returns parent objects."""
        yield self
        parent = self.parent
        while parent:
            yield parent
            parent = parent.parent


def _adjust_keywords(kwds):
    required = kwds.get('required', False)
    kwds['null'] = not required
    kwds['blank'] = not required
    if 'required' in kwds:
        del kwds['required']
    if 'choices' in kwds:
        kwds['choices'] = [(a, a) for a in kwds['choices']]
    return kwds


class StringProperty(models.CharField):

    def __init__(self, *args, **kwds):
        kwds = _adjust_keywords(kwds)
        kwds['max_length'] = 500
        super(StringProperty, self).__init__(*args, **kwds)


class TextProperty(models.TextField):

    def __init__(self, *args, **kwds):
        kwds = _adjust_keywords(kwds)
        super(TextProperty, self).__init__(*args, **kwds)


class BooleanProperty(models.BooleanField):

    def __init__(self, *args, **kwds):
        kwds = _adjust_keywords(kwds)
        super(BooleanProperty, self).__init__(*args, **kwds)


class UserProperty(models.ForeignKey):

    def __init__(self, *args, **kwds):
        kwds = _adjust_keywords(kwds)
        super(UserProperty, self).__init__(User, *args, **kwds)


class DateTimeProperty(models.DateTimeField):

    def __init__(self, *args, **kwds):
        kwds = _adjust_keywords(kwds)
        super(DateTimeProperty, self).__init__(*args, **kwds)


class ListProperty(models.TextField):

    __metaclass__ = models.SubfieldBase

    def __init__(self, type_, *args, **kwds):
        kwds = _adjust_keywords(kwds)
        super(models.TextField, self).__init__()

    def get_db_prep_value(self, value):
        return base64.encodestring(cPickle.dumps(value))

    def to_python(self, value):
        if type(value) in [types.ListType, types.TupleType]:
            return value
        if value is None:
            return []
        try:
            return cPickle.loads(base64.decodestring(value))
        except EOFError:
            return []


Email = str
Blob = str
Link = str
Text = unicode


class ReferenceProperty(models.ForeignKey):

    def __init__(self, other, *args, **kwds):
        kwds = _adjust_keywords(kwds)
        if 'collection_name' in kwds:
            kwds['related_name'] = kwds['collection_name']
            del kwds['collection_name']
        super(ReferenceProperty, self).__init__(other, *args, **kwds)


class BlobProperty(models.TextField):

    def __init__(self, *args, **kwds):
        kwds = _adjust_keywords(kwds)
        super(BlobProperty, self).__init__(*args, **kwds)


class LinkProperty(models.URLField):

    def __init__(self, *args, **kwds):
        kwds = _adjust_keywords(kwds)
        super(LinkProperty, self).__init__(*args, **kwds)


class EmailProperty(models.EmailField):

    def __init__(self, *args, **kwds):
        kwds = _adjust_keywords(kwds)
        super(EmailProperty, self).__init__(*args, **kwds)


class IntegerProperty(models.IntegerField):

    def __init__(self, *args, **kwds):
        kwds = _adjust_keywords(kwds)
        super(IntegerProperty, self).__init__(*args, **kwds)

from django import forms as djangoforms


class _QueryIterator(object):

    def __init__(self, results):
        self._results = results
        self._idx = -1

    def __iter__(self):
        return self

    def next(self):
        self._idx += 1
        if self._results.count() > self._idx:
            return self._results[self._idx]
        else:
            raise StopIteration


class GqlQuery(object):

    def __init__(self, sql, *args, **kwds):
        from gaeapi.appengine.ext import gql
        #print sql, args, kwds
        self._sql = sql
        self._gql = gql.GQL(sql)
        self._real_cls = None
        self._args = []
        self._kwds = {}
        if args or kwds:
            self.bind(*args, **kwds)
        self._cursor = None
        self._idx = -1
        self._results = None

    def __iter__(self):
        if self._results is None:
            self._execute()
        return _QueryIterator(self._results)

    def _resolve_arg(self, value):
        from gaeapi.appengine.ext import gql
        if isinstance(value, basestring):
            return self._kwds[value]
        elif isinstance(value, int):
            return self._args[value-1]
        elif isinstance(value, gql.Literal):
            return value.Get()
        else:
            raise Error('Unhandled args %s' % item)

    def _execute(self):
        from gaeapi.appengine.ext import gql
        if self._cursor:
            raise Error('Already executed.')
        # Make sql local just for traceback
        sql = self._sql
        from django.db import models
        # First, let's see if the class is explicitely given.
        # E.g. Model.gql('xxx') set's _real_cls.
        cls = self._real_cls
        if cls is None:
            for xcls in models.get_models():
                if xcls.__name__ == self._gql._entity \
                or xcls._meta.db_table in self._sql:
                    cls = xcls
                    break
        if not cls:
            raise Error('Class not found.')
        q = cls.objects
        #print '-'*10
        #print "xx", sql, self._args, self._kwds
        ancestor = None
        for key, value in self._gql.filters().items():
            #print key, value
            kwd, op = key
            if op == '=':
                if cls._meta.get_field(kwd).rel:
                    rel_cls = cls._meta.get_field(kwd).rel.to
                else:
                    rel_cls = None
                for xop, val in value:
                    # FIXME: Handle lists...
                    item = val[0]

                    if isinstance(item, gql.Literal):
                        print 'Literal', item
                        item = item.Get()
                        print '-->', item
                    elif isinstance(item, basestring):
                        print 'Keyword', item
                        item = self._kwds[item]
                        print '-->', item
                    elif isinstance(item, int):
                        print 'Positional', item
                        item = self._args[item-1]
                        print '-->', item
                    else:
                        raise Error('Unhandled args %s' % item)
#                    if rel_cls:
#                        # FIXME: Handle lists
#                        try:
#                            item = rel_cls.objects.get(id=item)
#                        except rel_cls.DoesNotExist:
#                            continue
                    q = q._filter(**{kwd: item})
            elif op == 'is' and kwd == -1: # ANCESTOR
                if ancestor:
                    raise Error('Ancestor already defined: %s' % ancestor)
                item = value[0][1][0]
                if isinstance(item, basestring):
                    ancestor = self._kwds[item]
                elif isinstance(item, int):
                    ancestor = self._args[item-1]
                else:
                    raise Error('Unhandled args %s' % item)
                pattern = '@%s@' % ancestor.key()
                q = q._filter(**{'gae_ancestry__contains': pattern})
            elif op == '>':
                item = self._resolve_arg(value[0][1][0])
                q = q._filter(**{'%s__gt' % kwd: item})
            elif op == '<':
                item = self._resolve_arg(value[0][1][0])
                q = q._filter(**{'%s__lt' % kwd: item})
            else:
                raise Error('Unhandled operator %s' % op)
        orderings = []
        for field, direction in self._gql.orderings():
            if direction != 1:
                field = '-%s' % field
            orderings.append(field)
        if orderings:
            q = q.order_by(*orderings)
        self._results = q

    def bind(self, *args, **kwds):
        self._kwds = kwds
        self._args = args
        self._results = None

    def fetch(self, limit, offset=0):
        if self._results is None:
            self._execute()
        return self._results[offset:limit]

    def count(self, limit=None):
        if self._results is None:
            self._execute()
        idx = self._idx
        c = len(list(self._results))
        self._idx = idx
        return c

    def get(self):
        if self._results is None:
            self._execute()
        if self._results:
            return self._results[0]
        return None


class Key(object):

    def __init__(self, obj):
        self.obj = obj

    def __str__(self):
        return '%s_%s' % (self.obj.__class__.__name__,
                          self.obj.id)

    def __cmp__(self, other):
        return cmp(str(self), str(other))

    @classmethod
    def from_path(cls, kind, id_):
        return '%s_%s' % (kind, id)

    def id(self):
        return self.obj.id

    def parent(self):
        return self.obj.parent.key()


# Errors


class Error(Exception):
    """db.Error"""


class BadArgumentError(Error):
    """A bad argument was given to a query method."""


class BadFilterError(Error):
    """A filter string in the query is invalid."""


class BadKeyError(Error):
    """The provided key string is not a valid key."""


class BadPropertyError(Error):
    """The property could not be created because its name is not a string."""


class BadQueryError(Error):
    """The query string is not a valid query."""


class BadRequestError(Error):
    """Request to the datastore service has one or more invalid properties."""


class BadValueError(Error):
    """Invalid value for the property type."""


class ConfigurationError(Error):
    """A property is not configured correctly."""


class DuplicatePropertyError(Error):
    """A model definition has more than one property with the same name."""


class InternalError(Error):
    """There was an error internal to the datastore service."""


class KindError(Error):
    """Model class that does not match the entity."""


class NotSavedError(Error):
    """Object is not saved."""


class PropertyError(Error):
    """The referenced model property does not exist on the data object."""


class ReservedWordError(Error):
    """A model defines a property whose name is disallowed."""


class Rollback(Error):
    """Indicates that a function in a transaction wants to roll back."""


class TransactionFailedError(Error):
    """The transaction or datastore operation could not be committed."""


class CapabilityDisabledError(Error):
    """Datastore functionality is not available."""


# Functions


def get(keys):
    raise NotImplementedError


def put(models):
    if type(models) not in [types.ListType, types.TupleType]:
        models = [models]
    keys = []
    for model in models:
        model.save()
        keys.append(model.key)
    if len(keys) > 1:
        return keys
    elif len(keys) == 1:
        return keys[0]
    return None


def delete(models):
    if type(models) not in [types.ListType, types.TupleType]:
        models = [models]
    for model in models:
        model.delete()


@transaction.commit_on_success
def run_in_transaction(func, *args, **kwds):
    return func(*args, **kwds)
