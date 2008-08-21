import base64
import cPickle
import logging
import os
import random
import re
import time

from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import manager
from django.db import transaction
from django.utils.hashcompat import md5_constructor

# Use the system (hardware-based) random number generator if it exists.
# Taken from django.contrib.sessions.backends.base
if hasattr(random, 'SystemRandom'):
    randrange = random.SystemRandom().randrange
else:
    randrange = random.randrange
MAX_SESSION_KEY = 18446744073709551616L     # 2 << 63


class BaseManager(manager.Manager):

    def count(self, limit=None):
        return super(BaseManager, self).count()

    def order(self, *args, **kwds):
        return super(BaseManager, self).order_by(*args, **kwds)


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
            del kwds['parent']
        if 'key' in kwds:
            kwds['gae_key'] = kwds['key']
            del kwds['key']
        super(Model, self).__init__(*args, **kwds)

    @classmethod
    def get_or_insert(cls, key, **kwds):
        try:
            return cls.objects.get(gae_key=key)
        except cls.DoesNotExist:
            kwds['key'] = key
            new = cls(**kwds)
            new.save()
            return new

    @classmethod
    def get_by_key_name(cls, key):
        try:
            return cls.objects.get(gae_key=key)
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_by_id(cls, id, parent=None):
        # Ignore parent, we've got an ID
        return cls.objects.get(id=id)

    @classmethod
    def kind(cls):
        return cls._meta.db_table

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
    def gql(cls, clause, *args):
        from google.appengine.ext import db
        return db.GqlQuery('SELECT * FROM %s %s' % (cls.__name__,
                                                    clause), *args)

    @classmethod
    def get(cls, keys):
        return [cls.get_by_key_name(key) for key in keys]


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
        try:
            return cPickle.loads(base64.decodestring(value))
        except EOFError:
            return []


Email = str


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

class GqlQuery(object):

    def __init__(self, sql, *args):
        from gaeapi.appengine.ext import gql
        self._sql = sql
        self._gql = gql.GQL(sql)
        self._args = None
        if args:
            self.bind(args)
        self._cursor = None
        self._idx = -1
        self._results = None

    def __iter__(self):
        if self._results is None:
            self._execute()
        self._idx += 1
        if self._results.count() > self._idx:
            yield self._results[self._idx]
        else:
            raise StopIteration

    def _execute(self):
        from gaeapi.appengine.ext import gql
        if self._cursor:
            raise Exception, 'Already executed.'
        # Make sql local just for traceback
        sql = self._sql
        from django.db import models
        cls = None
        for xcls in models.get_models():
            if xcls.__name__ == self._gql._entity \
            or xcls._meta.db_table in self._sql:
                cls = xcls
                break
        if not cls:
            raise Exception, 'Class not found.'
        q = cls.objects
        for key, value in self._gql.filters().items():
            kwd, op = key
            if op == '=':
                if cls._meta.get_field(kwd).rel:
                    rel_cls = cls._meta.get_field(kwd).rel.to
                else:
                    rel_cls = None
                for xop, val in value:
                    for item in val:
                        if isinstance(item, gql.Literal):
                            item = item.Get()
                        if rel_cls:
                            # FIXME: Handle lists
                            try:
                                item = rel_cls.objects.get(id=val[0])
                            except rel_cls.DoesNotExist:
                                continue
                        q = q.filter(**{kwd:item})
        self._results = q

    def bind(self, *args, **kwds):
        self._args = args

    def fetch(self, limit, offset):
        if self._results is None:
            self._execute()
        return self._results[offset:limit]

    def count(self, limit):
        idx = self._idx
        c = len(list(self._results))
        self._idx = idx
        return c


@transaction.commit_on_success
def run_in_transaction(func, *args, **kwds):
    return func(*args, **kwds)


class Key(object):

    def __init__(self, obj):
        self.obj = obj

    @classmethod
    def from_path(cls, kind, id_):
        return '%s_%s' % (kind, id)

    def id(self):
        return self.obj.id