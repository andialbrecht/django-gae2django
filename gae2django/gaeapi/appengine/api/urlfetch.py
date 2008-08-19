#
# Copyright 2008 Andi Albrecht <albrecht.andi@gmail.com>
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

"""Implements the URL fetch API.

http://code.google.com/appengine/docs/urlfetch/
"""

# Constants
GET = 'GET'
POST = 'POST'
HEAD = 'HEAD'
PUT = 'PUT'
DELETE = 'DELETE'

def fetch(url, payload=None, method=GET, headers={}, allow_truncated=False):
  raise NotImplementedError


class Response(object):
  content = None
  content_was_truncated = False
  status_code = -1
  headers = None


class Error(Exception):
  """Base class for all URL fetch exceptions."""


class InvalidURLError(Error):
  """Invalid URL."""


class DownloadError(Error):
  """Download failed."""


class ResponseTooLargeError(Error):
  """Unused."""