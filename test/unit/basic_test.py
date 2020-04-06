#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Unit test
"""

import server4_api
import unittest


class TestServer4Api(unittest.TestCase):
	""" Unit test """

	def __init(self):
		self.__api = server4_api.Server4Api(config_file='test/example/serverapi.cfg')


	def test_10_select(self):
		""" select """

		self.__init()
		self.__api.dql.select(table_name='test_table', where_dict={'id':1}, limit=5)


	def test_20_insert(self):
		""" insert """

		self.__init()
		self.__api.dml.insert(table_name='test_table', value_dict={'value_str':'aa', 'value_int':10})
		self.__api.dml.insert_id()


	def test_30_delete(self):
		""" delete """

		self.__init()
		self.__api.dml.delete(table_name='test_table', where_dict={'id':10})


	def test_40_response(self):
		""" response """

		self.__init()
		self.__api.response.ok()
		self.__api.response.no_content()
		self.__api.response.redirect()
		self.__api.response.bad_request()
		self.__api.response.not_found()
		self.__api.response.server_error()


	def test_50_cache(self):
		""" cache """

		self.__init()
		self.__api.cache.set('aaa', 10)
		self.__api.cache.get('aaa')
		self.__api.cache.incr('aaa')
		self.__api.cache.decr('aaa')
