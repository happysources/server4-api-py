#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Server 4 API

$ apt-get install python3 python3-mysqldb
"""

import os.path
import time
import configparser
import mysqlwrapper


class Server4Api(object):
	""" Server API """

	def __init__(self, config_file='serverapi.cfg'):
		""" api init """

		config = self.__read_config(config_file)
		self.__cursor = self.__db_init(config)

		self.data_init()


	def data_init(self):
		""" data init """

		return


	def __read_config(self, config_file):
		""" read config """

		if not os.path.isfile(config_file):
			return None

		# config
		config = configparser.ConfigParser()
		config.read(config_file)

		return config


	def time_ms(self, start_time=0):
		""" time ms """

		timems = int((time.time() - start_time) * 1000)
		if timems == 0:
			timems = 1

		return timems


	def db_dial_id(self, table_name='', col_id='', col_value=''):
		""" Convert data from table to strurcture {id:value} (max limit 100) """
		return self.__db_dial(table_name, col_id, col_value, 'id_value')

	def db_dial_value(self, table_name='', col_id='', col_value=''):
		""" Convert data from table to strurcture {value:id} (max limit 100) """
		return self.__db_dial(table_name, col_id, col_value, 'value_id')

	def __db_dial(self, table_name='', col_id='', col_value='', dial_type='id_value'):
		""" Convert data from table to strurcture {id:value} (max limit 100) """

		# select data from table
		found, data = self.db_select(table_name=table_name, where_dict={},\
			column_list=[col_id, col_value], limit=100)

		if found == 0:
			return {}

		ret = {}
		for line in data:

			if dial_type == 'id_value':
				ret[line[col_value]] = line[col_id]
				continue

			ret[line[col_id]] = line[col_value]

		return ret


	# --- MYSQL DATABASE ---

	def __db_init(self, config):
		""" db init """

		cursor = {}

		if 'db' not in config.sections():
			return cursor

		# read only cursor
		cursor['dql'] = self.__db_cursor(config, 'dql')

		# dml (modify) cursor
		cursor['dml'] = self.__db_cursor(config, 'dml')

		return cursor


	def __db_cursor(self, config=None, user_type='dql'):
		""" db cursor """

		if not config:
			return None

		user = 'user_%s' % user_type
		passwd = 'passwd_%s' % user_type

		# db config
		db_user = config.get('db', user)
		db_passwd = config.get('db', passwd)
		db_db = config.get('db', 'db')
		db_host = config.get('db', 'host')

		if not db_user:
			return None

		db_param = {\
			'dict_cursor':1,\
			'autocommit':1,\
			'dummy':1,\
			'charset':config.get('db', 'charset'),\
			'port':config.getint('db', 'port'),\
			'debug':config.getint('db', 'debug'),\
		}

		# db connect
		database = mysqlwrapper.Connect(\
			user=db_user,\
			passwd=db_passwd,\
			db=db_db,\
			host=db_host,\
			param=db_param)

		# db cursor
		return database.cursor()


	def db_select(self, table_name, where_dict, column_list=[], limit=0):
		""" db select """
		return self.__cursor['dql'].select(table_name, where_dict, column_list, limit)

	def db_update(self, table_name, value_dict, where_dict, limit=0):
		""" db update """
		return self.__cursor['dml'].update(table_name, value_dict, where_dict, limit)

	def db_insert(self, table_name, value_dict):
		""" db insert """
		return self.__cursor['dml'].insert(table_name, value_dict)

	def db_delete(self, table_name=None, where_dict={}, limit=0):
		""" db delete """
		return self.__cursor['dml'].delete(table_name, where_dict, limit)

	def db_execute_dml(self, sql, param=()):
		""" db sql """
		return self.__cursor['dml'].execute(sql, param)

	def db_execute_dql(self, sql, param=()):
		""" db sql """
		return self.__cursor['dql'].execute(sql, param)

	def db_close(self):
		""" db close """

		for cursor_name in self.__cursor:
			self.__cursor[cursor_name].close()
