#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Example for Server API
"""

import sys
import pprint
sys.path.append('server4-api')

import server4_api

API = server4_api.Server4Api(config_file='test/example/serverapi.cfg')
pprint.pprint(API.db_select(table_name='test_table', where_dict={'id':1}, limit=5))
pprint.pprint(API.db_execute_dml('SELECT * FROM test_table LIMIT 5'))
pprint.pprint(API.db_execute_dql('SELECT * FROM test_table LIMIT 5'))
