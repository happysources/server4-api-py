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
import response_api
from validate_data import validate_str, validate_int, validate_float


def _test_input_param_input(def_dict, value_dict):

	error_type = None
	error_msg = None

	if not value_dict or not def_dict:
		error_type = 'type_err'
		error_msg = 'Parametrs must be a input'

	if len(value_dict) > len(def_dict):
		error_type = 'length_error'
		error_msg = 'Undefinied params'

	return error_type, error_msg


def _read_config(config_file):
	""" read config """

	if not os.path.isfile(config_file):
		return None

	# config
	config = configparser.ConfigParser()
	config.read(config_file)

	return config



class Server4Api(object):
	""" Server API """

	def __init__(self, config_file='serverapi.cfg'):
		""" api init """

		config = _read_config(config_file)
		self.__cursor = self.__db_init(config)
		self.response = response_api.ResponseAPI()

		self.data_init()


	def data_init(self):
		""" data init """

		return



	def time_ms(self, start_time=0):
		""" time ms """

		timems = int((time.time() - start_time) * 1000)
		if timems == 0:
			timems = 1

		return timems


	# --- DIAL ---

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


	def db_select(self, table_name, where_dict, column_list=(), limit=0):
		""" db select """
		return self.__cursor['dql'].select(table_name, where_dict, column_list, limit)

	def db_update(self, table_name, value_dict, where_dict, limit=0):
		""" db update """
		return self.__cursor['dml'].update(table_name, value_dict, where_dict, limit)

	def db_insert(self, table_name, value_dict):
		""" db insert """
		return self.__cursor['dml'].insert(table_name, value_dict)

	def db_insert_id(self):
		""" db insert id """
		return self.__cursor['dml'].insert_id()

	def db_delete(self, table_name=None, where_dict=None, limit=0):
		""" db delete """

		if not where_dict:
			where_dict = {}

		return self.__cursor['dml'].delete(table_name, where_dict, limit)

	def db_execute_dml(self, sql, param=()):
		""" db sql """
		return self.__cursor['dml'].execute(sql, param)

	def db_execute_dql(self, sql, param=()):
		""" db sql """
		return self.__cursor['dql'].execute(sql, param)

	def db_now(self):
		""" db now """
		return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

	def db_close(self):
		""" db close """

		for cursor_name in self.__cursor:
			self.__cursor[cursor_name].close()


	# --- INPUT PARAMS

	def test_input_param(self, def_dict, value_dict):
		""" test input param """

		start_time = time.time()

		# test for input value
		error_type, error_msg = _test_input_param_input(def_dict, value_dict)

		try:
			for param_name in value_dict.keys():
				_def = def_dict.get(param_name)
				if not _def:
					raise ValueError(('Unknown parametr {param_name}').format(param_name=param_name))

				param_type = _def.get('type', 'str')
				param_value = value_dict.get(param_name)

				if param_type == 'int':
					validate_int(param_value, _def.get('min'), _def('max'), _def('req'), param_name)

				elif param_type == 'float':
					validate_float(param_value, _def.get('min'), _def('max'), _def('req'), param_name)

				elif param_type == 'email':
					validate_str(param_value, 3, 100, _def('req'), param_name)
					#validate_email(param_value, _def('req'), param_name)
					continue

				elif param_type == 'array' and _def('req') and param_value not in _def('array'):
					raise ValueError(('{param_name} value out of array').format(param_name=param_name))

				validate_str(param_value, _def.get('min'), _def.get('max'), _def('req'), param_name)

		except TypeError as type_err:
			error_type = 'type_error'
			error_msg = str(type_err)

		except ValueError as value_err:
			error_type = 'value_error'
			error_msg = str(value_err)

		if error_type:
			return self.response.bad_request(\
				message='[%s] %s' % (error_type, str(error_msg).strip()),\
				time_ms=self.time_ms(start_time),\
				error_dict={'type': error_type, 'message': str(error_msg).strip()})

		return {'status':{'code':0}}
