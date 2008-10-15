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

from gae2django.gaeapi.appengine.ext import db
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

    def test_get_or_insert(self):
        item1 = TestModel.get_or_insert('test1', xstring='foo')
        self.assert_(isinstance(item1, TestModel))
        test = TestModel.get_or_insert('test1')
        self.assertEqual(item1, test)
        self.assertEqual(item1.xstring, 'foo')
        item1.delete()

    def test_all(self):
        self.assertEqual(len(TestModel.all()), 0)
        item1 = TestModel.get_or_insert('test1')
        self.assertEqual(len(TestModel.all()), 1)
        self.assert_(item1 in TestModel.all())
        item1.delete()

    def test_gql(self):
        item1 = TestModel.get_or_insert('test1', xstring='foo')
        item2 = TestModel.get_or_insert('test2', xstring='foo')
        results = TestModel.gql('WHERE xstring = \'foo\'')
        self.assertEqual(results.count(), 2)
        self.assert_(item1 in results)
        self.assert_(item2 in results)
        item1.delete()
        item2.delete()

    def test_kind(self):
        self.assertEqual(TestModel.kind(), TestModel._meta.db_table)

    def test_properties(self):
        props = TestModel.properties()
        self.assert_('xstring' in props)
        self.assert_(isinstance(props['xstring'], db.StringProperty))
        self.assert_('gae_parent_id' not in props)

    # Instance methods
