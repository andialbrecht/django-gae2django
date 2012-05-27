#
# Copyright 2012 Andi Albrecht <albrecht.andi@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Implements google.appengine.api.taskqueue."""

# Note: taskqueue API is not fully covered yet.
# TODO(andi): Add Django tasks implementation as suggested by Martin
# von Loewis (see http://code.google.com/p/django-tasks/)

import httplib
import uuid
import urllib
import urlparse


class TaskBase(object):
    """Task implementation."""

    def __init__(self, payload=None, **kw):
        self.payload = payload
        self.name = kw.get('name', None)
        self.method = kw.get('method', 'POST')
        self.url = kw.get('url', None)
        self.headers = kw.get('headers', {})
        if 'Content-Type' not in self.headers:
            self.headers['Content-Type'] = 'text/plain'
        self.params = kw.get('params', None)
        self.countdown = kw.get('countdown', 0)
        self.eta = kw.get('eta', None)
        self.retry_options = kw.get('retry_options', None)
        self.target = kw.get('target', None)

    def add(self, queue_name='default', transactional=False):
        if self.name is None:
            self.name = str(uuid.uuid4())
        self._execute()

    def _execute(self):
        # Implementations must override this method.
        raise NotImplementedError


class Task(TaskBase):

    def _execute(self):
        if self.method == 'POST':
            if self.payload is not None:
                body = self.payload
            elif self.params is not None:
                body = urllib.urlencode(self.params)
            else:
                body = None
            url = self.url
        else:
            splitted = list(urlparse.urlparse(self.url))
            if self.params is not None:
                splitted[4] = urllib.urlencode(self.params)
            url = urlparse.urlunparse(splitted)
        conn = httplib.HTTPConnection(urlparse.urlparse(url)[1])
        conn.request(self.method, url, body, self.headers)
        conn.getresponse()


def add(*args, **kwargs):
    """Add a task to the queue."""
    task = Task(*args, **kwargs)
    task.add()
