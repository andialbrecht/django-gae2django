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

import unittest

from gae2django.models import RegressionTestModel as TestModel

class DatastoreModelTest(unittest.TestCase):

    # Class methods

    def test_get(self):
        item1 = TestModel(key_name='test1')
        item1.put()
        self.assertEqual(TestModel.get('test1'), item1)
        self.assertEqual(TestModel.get('foo'), None)
        self.assertEqual(TestModel.get(['test1', 'test2']), [item1, None])
        item2 = TestModel(key_name='test2')
        item2.put()
        self.assertEqual(TestModel.get(['test1', 'test2']), [item1, item2])
        item1.delete()
        item2.delete()

    def test_get_by_id(self):
        item1 = TestModel(key_name='test1')
        item1.put()
        self.assertEqual(TestModel.get_by_id(item1.key().id()), item1)
        self.assertEqual(TestModel.get_by_id(-1), None)
        self.assertEqual(TestModel.get_by_id([item1.key().id(), -1]),
                         [item1, None])
        item2 = TestModel(key_name='test2')
        item2.put()
        self.assertEqual(TestModel.get_by_id([item1.key().id(),
                                              item2.key().id()]),
                         [item1, item2])
        item1.delete()
        item2.delete()


    def test_get_by_key_name(self):
        self.assertEqual(TestModel.get_by_key_name('foo'), None)
        self.assertEqual(TestModel.get_by_key_name(['foo', 'bar']),
                         [None, None])
        item1 = TestModel(key_name='test1')
        item1.put()
        self.assertEqual(TestModel.get_by_key_name('test1'), item1)
        self.assertEqual(TestModel.get_by_key_name(['test1', 'test2']),
                         [item1, None])
        item2 = TestModel(key_name='test2')
        item2.put()
        self.assertEqual(TestModel.get_by_key_name(['test1', 'test2']),
                         [item1, item2])
        item1.delete()
        item2.delete()
