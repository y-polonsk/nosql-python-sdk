#
# Copyright (C) 2018, 2019 Oracle and/or its affiliates. All rights reserved.
#
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl
#
# Please see LICENSE.txt file included in the top-level directory of the
# appropriate download for a copy of the license and additional information.
#

import unittest
from datetime import datetime
from decimal import Decimal
from struct import pack
from time import time

from borneo import (
    Consistency, GetRequest, IllegalArgumentException, PutRequest, State,
    TableLimits, TableNotFoundException, TableRequest, TimeToLive)
from parameters import table_name, timeout
from test_base import TestBase


class TestGet(unittest.TestCase, TestBase):
    @classmethod
    def setUpClass(cls):
        TestBase.set_up_class()
        table_ttl = TimeToLive.of_hours(16)
        create_statement = (
            'CREATE TABLE ' + table_name + '(fld_sid INTEGER, fld_id INTEGER, \
fld_long LONG, fld_float FLOAT, fld_double DOUBLE, fld_bool BOOLEAN, \
fld_str STRING, fld_bin BINARY, fld_time TIMESTAMP(7), fld_num NUMBER, \
fld_json JSON, fld_arr ARRAY(STRING), fld_map MAP(STRING), \
fld_rec RECORD(fld_id LONG, fld_bool BOOLEAN, fld_str STRING), \
PRIMARY KEY(SHARD(fld_sid), fld_id)) USING TTL ' + str(table_ttl))
        create_request = TableRequest().set_statement(
            create_statement).set_table_limits(TableLimits(5000, 5000, 50))
        cls._result = TestBase.table_request(create_request, State.ACTIVE)
        global row, tb_expect_expiration, hour_in_milliseconds
        row = {'fld_sid': 1, 'fld_id': 1, 'fld_long': 2147483648,
               'fld_float': 3.1414999961853027, 'fld_double': 3.1415,
               'fld_bool': True, 'fld_str': '{"name": u1, "phone": null}',
               'fld_bin': bytearray(pack('>i', 4)),
               'fld_time': datetime.now(), 'fld_num': Decimal(5),
               'fld_json': {'a': '1', 'b': None, 'c': '3'},
               'fld_arr': ['a', 'b', 'c'],
               'fld_map': {'a': '1', 'b': '2', 'c': '3'},
               'fld_rec': {'fld_id': 1, 'fld_bool': False, 'fld_str': None}}
        put_request = PutRequest().set_value(row).set_table_name(table_name)
        cls._handle.put(put_request)
        tb_expect_expiration = table_ttl.to_expiration_time(
            int(round(time() * 1000)))
        hour_in_milliseconds = 60 * 60 * 1000

    @classmethod
    def tearDownClass(cls):
        TestBase.tear_down_class()

    def setUp(self):
        TestBase.set_up(self)
        self.key = {'fld_sid': 1, 'fld_id': 1}
        self.get_request = GetRequest().set_key(self.key).set_table_name(
            table_name).set_timeout(timeout)

    def tearDown(self):
        TestBase.tear_down(self)

    def testGetSetIllegalKey(self):
        self.assertRaises(IllegalArgumentException, self.get_request.set_key,
                          'IllegalKey')
        self.get_request.set_key({'fld_sid': 1})
        self.assertRaises(IllegalArgumentException, self.handle.get,
                          self.get_request)
        self.get_request.set_key({'fld_id': 1})
        self.assertRaises(IllegalArgumentException, self.handle.get,
                          self.get_request)

    def testGetSetIllegalKeyFromJson(self):
        self.assertRaises(ValueError, self.get_request.set_key_from_json,
                          'IllegalJson')
        self.get_request.set_key_from_json('{"invalid_field": "key"}')
        self.assertRaises(IllegalArgumentException, self.handle.get,
                          self.get_request)

    def testGetSetIllegalTableName(self):
        self.assertRaises(IllegalArgumentException,
                          self.get_request.set_table_name, {'name': table_name})
        self.get_request.set_table_name('IllegalTable')
        self.assertRaises(TableNotFoundException, self.handle.get,
                          self.get_request)

    def testGetSetIllegalConsistency(self):
        self.assertRaises(IllegalArgumentException,
                          self.get_request.set_consistency,
                          'IllegalConsistency')

    def testGetSetIllegalTimeout(self):
        self.assertRaises(IllegalArgumentException,
                          self.get_request.set_timeout, 'IllegalTimeout')
        self.assertRaises(IllegalArgumentException,
                          self.get_request.set_timeout, 0)
        self.assertRaises(IllegalArgumentException,
                          self.get_request.set_timeout, -1)

    def testGetWithoutKey(self):
        self.get_request.set_key(None)
        self.assertRaises(IllegalArgumentException, self.handle.get,
                          self.get_request)

    def testGetGets(self):
        self.assertEqual(self.get_request.get_key(), self.key)

    def testGetIllegalRequest(self):
        self.assertRaises(IllegalArgumentException, self.handle.get,
                          'IllegalRequest')

    def testGetNormal(self):
        result = self.handle.get(self.get_request)
        self.assertEqual(result.get_value(), row)
        actual_expiration = result.get_expiration_time()
        actual_expect_diff = actual_expiration - tb_expect_expiration
        self.assertGreater(actual_expiration, 0)
        self.assertLess(actual_expect_diff, hour_in_milliseconds)
        self.assertEqual(result.get_read_kb(), 1)
        self.assertEqual(result.get_read_units(), 2)
        self.assertEqual(result.get_write_kb(), 0)
        self.assertEqual(result.get_write_units(), 0)

    def testGetEventual(self):
        self.get_request.set_consistency(Consistency.EVENTUAL)
        result = self.handle.get(self.get_request)
        self.assertEqual(result.get_value(), row)
        self.assertIsNotNone(result.get_version())
        actual_expiration = result.get_expiration_time()
        actual_expect_diff = actual_expiration - tb_expect_expiration
        self.assertGreater(actual_expiration, 0)
        self.assertLess(actual_expect_diff, hour_in_milliseconds)
        self.assertEqual(result.get_read_kb(), 1)
        self.assertEqual(result.get_read_units(), 1)
        self.assertEqual(result.get_write_kb(), 0)
        self.assertEqual(result.get_write_units(), 0)

    def testGetNonExisting(self):
        self.get_request.set_key({'fld_sid': 2, 'fld_id': 2})
        result = self.handle.get(self.get_request)
        self.assertIsNone(result.get_value())
        self.assertIsNone(result.get_version())
        self.assertEqual(result.get_expiration_time(), 0)
        self.assertEqual(result.get_read_kb(), 1)
        self.assertEqual(result.get_read_units(), 2)
        self.assertEqual(result.get_write_kb(), 0)
        self.assertEqual(result.get_write_units(), 0)


if __name__ == '__main__':
    unittest.main()
