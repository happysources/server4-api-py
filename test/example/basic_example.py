#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Example for Server API
"""

import sys
import pprint
sys.path.append('/usr/local/lib/python3/dist-packages')
sys.path.append('server4_api')

import server4_api

API = server4_api.Server4Api(config_file='test/example/serverapi.cfg')

print()
print('select:')
pprint.pprint(API.dql.select(table_name='test_table', where_dict={'id':1}, limit=5))

print()
print('execute:')
pprint.pprint(API.dql.query('SELECT * FROM test_table LIMIT 1'))
pprint.pprint(API.dml.query('SELECT * FROM test_table LIMIT 2'))

print()
print('dial:')
pprint.pprint(API.db_dial_id('test_table', 'id', 'value_str'))
pprint.pprint(API.db_dial_value('test_table', 'id', 'value_str'))
