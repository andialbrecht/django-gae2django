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


import unittest

from mock import patch, Mock

from gae2django.gaeapi.appengine.api import taskqueue


class TaskqueueTest(unittest.TestCase):

    def test_add(self):
        with patch('httplib.HTTPConnection') as mock_http:
            mock_conn = Mock()
            mock_conn.request = Mock()
            mock_http.return_value = mock_conn
            taskqueue.add(url='http://example.com/foo',
                          params={'key': 'thekey'},
                          queue_name='test')
            mock_http.assert_called_with('example.com')
            mock_conn.request.assert_called_with(
                'POST', 'http://example.com/foo', 'key=thekey',
                {'Content-Type': 'text/plain'})
