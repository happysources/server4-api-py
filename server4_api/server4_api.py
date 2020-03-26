#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Server 4 API
"""

import os
import time
import configparser
import response_api
from validate_data import validate_str, validate_int, validate_float,\
	validate_email, validate_ip, validate_array
from logni import log

MYSQLWRAPPER = 1
MEMCACHEWRAPPER = 1

try:
	import mysqlwrapper
except ImportError as import_err:
	log.debug('mysqlwrapper import error=%s', import_err, priority=4)
	MYSQLWRAPPER = 0

try:
	import memcachewrapper
except ImportError as import_err:
	log.debug('memcachewrapper import error=%s', import_err, priority=4)
	MEMCACHEWRAPPER = 0


def _test_input_param_input(def_dict, value_dict):

	error_type = None
	error_msg = None

	if not value_dict or not def_dict:
		error_type = 'type_error'
		error_msg = 'Parametrs must be a input'

	if len(value_dict) > len(def_dict):
		error_type = 'length_error'
		error_msg = 'Undefinied params'

	return error_type, error_msg


def _length_error(error_msg, error_type):

	for length_str in (' expected value less than ', ' expected value greater than ',\
		' expected at least ', ' expected at most '):
		if error_msg.find(length_str) > -1:
			error_type = 'length_error'

	return error_type


def _read_config(config_file):
	""" read config """

	if not os.path.isfile(config_file):
		return None

	# config
	config = configparser.ConfigParser()
	config.read(config_file)

	return config


def _db_init(config):
	""" db init """

	cursor = {}

	if 'db' not in config.sections():
		return cursor

	if not MYSQLWRAPPER:
		log.error('mysqlwrapper import error', priority=3)
		return cursor

	# read only cursor
	cursor['dql'] = _db_cursor(config, 'dql')

	# dml (modify) cursor
	cursor['dml'] = _db_cursor(config, 'dml')

	return cursor



def _db_cursor(config=None, user_type='dql'):
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



class Server4Api(object):
	""" Server API """

	def __init__(self, config_file='serverapi.cfg'):
		""" api init """

		self._pylint_fixed = 0
		config = _read_config(config_file)

		# server name + env
		self.server = {\
			'name': config.get('server', 'server_name'),\
			'env' : os.environ.get('H4_ENV', 'local'),\
		}

		# dbg mesg
		log.debug('Server4Api="%s", env="%s", config="%s" init',\
			(self.server['name'], self.server['env'], config_file), priority=1)

		# db
		self.__db_cursor(config)

		# cache
		self.cache = None
		if 'memcache' in config.sections():

			if not MEMCACHEWRAPPER:
				log.error('memcachewrapper import error', priority=3)
			else:
				self.cache = memcachewrapper.MemcacheWrapper(\
					config.get('memcache', 'host'),\
					config.getint('memcache', 'port'),\
					self.server['name'],\
					config.getint('memcache', 'debug'))

		# response api
		self.response = response_api.ResponseAPI(self.server['name'])

		# data init
		self.data_init()

		# dbg mesg
		log.info('Server4Api="%s", env="%s", config="%s" init',\
			(self.server['name'], self.server['env'], config_file), priority=2)


	def __db_cursor(self, config):
		""" db cursor """

		self.__cursor = _db_init(config)
		self.dql = self.__cursor.get('dql')
		self.dml = self.__cursor.get('dml')

		# todo: del
		self._cursor = self.__cursor


	def data_init(self):
		""" data init """

		self._pylint_fixed = 0

		return


	def time_ms(self, start_time=0):
		""" time ms """

		self._pylint_fixed = 0

		timems = int((time.time() - start_time) * 1000)
		if timems == 0:
			timems = 1

		return timems


	# --- DIAL ---

	def db_dial_id(self, table_name='', col_id='', col_value='', order_by=None):
		""" Convert data from table to strurcture {id:value} (max limit 1000) """
		return self.__db_dial(table_name, col_id, col_value, 'id_value', order_by)

	def db_dial_value(self, table_name='', col_id='', col_value='', order_by=None):
		""" Convert data from table to strurcture {value:id} (max limit 1000) """
		return self.__db_dial(table_name, col_id, col_value, 'value_id', order_by)

	def __db_dial(self, table_name='', col_id='', col_value='', dial_type='id_value', order_by=None):
		""" Convert data from table to strurcture {id:value} (max limit 1000) """

		# order by
		__order_by = ''
		if order_by:
			__order_by = ' ORDER BY `%s` ' % order_by

		# select data from table
		found = self.db_execute_dql('SELECT `%s`, `%s` FROM %s %s LIMIT 1000' % \
			(col_id, col_value, table_name, __order_by))

		if found == 0:
			return {}

		ret = {}
		data = self.db_fetchall_dql()
		for line in data:

			if dial_type == 'id_value':
				ret[line[col_value]] = line[col_id]
				continue

			ret[line[col_id]] = line[col_value]

		return ret


	# --- MYSQL DATABASE ---



	def db_select(self, table_name, where_dict, column_list=(), limit=0):
		""" db select """

		if 'dql' not in self.__cursor:
			log.error('mysql cursor="%s" not exist', ('dql',), priority=2)
			return (0, None)

		return self.__cursor['dql'].select(table_name, where_dict, column_list, limit)


	def db_update(self, table_name, value_dict, where_dict, limit=0):
		""" db update """

		if 'dml' not in self.__cursor:
			log.error('mysql cursor="%s" not exist', ('dml',), priority=2)
			return 0

		return self.__cursor['dml'].update(table_name, value_dict, where_dict, limit)


	def db_insert(self, table_name, value_dict):
		""" db insert """

		if 'dml' not in self.__cursor:
			log.error('mysql cursor="%s" not exist', ('dml',), priority=2)
			return 0

		return self.__cursor['dml'].insert(table_name, value_dict)

	def db_replace(self, table_name, value_dict):
		""" db replace """

		if 'dml' not in self.__cursor:
			log.error('mysql cursor="%s" not exist', ('dml',), priority=2)
			return 0

		return self.__cursor['dml'].replace(table_name, value_dict)

	def db_insert_id(self):
		""" db insert id """

		if 'dml' not in self.__cursor:
			log.error('mysql cursor="%s" not exist', ('dml',), priority=2)
			return 0

		return self.__cursor['dml'].insert_id()


	def db_delete(self, table_name=None, where_dict=None, limit=0):
		""" db delete """

		if not where_dict:
			where_dict = {}

		if 'dml' not in self.__cursor:
			log.error('mysql cursor="%s" not exist', ('dml',), priority=2)
			return 0

		return self.__cursor['dml'].delete(table_name, where_dict, limit)


	def db_execute_dml(self, sql, param=()):
		""" db sql """

		if 'dml' not in self.__cursor:
			log.error('mysql cursor="%s" not exist', ('dml',), priority=2)
			return []

		return self.__cursor['dml'].execute(sql, param)

	def db_execute_dql(self, sql, param=()):
		""" db sql """

		if 'dql' not in self.__cursor:
			log.error('mysql cursor="%s" not exist', ('dql',), priority=2)
			return []

		return self.__cursor['dql'].execute(sql, param)


	def db_fetchall_dql(self):
		""" db fetchall """

		if 'dql' not in self.__cursor:
			log.error('mysql cursor="%s" not exist', ('dql',), priority=2)
			return []

		return self.__cursor['dql'].fetchall()

	def db_fetchone_dql(self):
		""" db fetchall """

		if 'dql' not in self.__cursor:
			log.error('mysql cursor="%s" not exist', ('dql',), priority=2)
			return []

		return self.__cursor['dql'].fetchone()


	def db_now(self):
		""" db now """
		self._pylint_fixed = 0
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
					raise ValueError(('Unknown parametr {param_name}').format(\
						param_name=param_name))

				param_type = _def.get('type', 'str')
				param_value = value_dict.get(param_name)

				if param_type in ('int', 'integer', 'number'):
					validate_ret = validate_int(param_value, _def.get('min'),\
						_def.get('max'), _def.get('req'), param_name)

				elif param_type == 'float':
					validate_ret = validate_float(param_value, _def.get('min'),\
						_def.get('max'), _def.get('req'), param_name)

				elif param_type in ('email', 'mail'):
					validate_ret = validate_email(param_value, _def.get('req'),\
						param_name)

				elif param_type == 'ip':
					validate_ret = validate_ip(param_value, _def.get('req'),\
						param_name)

				elif param_type == 'array':
					validate_ret = validate_array(param_value, _def.get('array'),\
						_def.get('req'), param_name)

				else:
					validate_ret = validate_str(param_value, _def.get('min'),\
						_def.get('max'), _def.get('req'), param_name)

				if not validate_ret:
					raise ValueError(('{param_name} is false validate').format(\
						param_name=param_name))


		except TypeError as type_err:
			error_type = 'type_error'
			error_msg = str(type_err)

		except ValueError as value_err:
			error_type = 'value_error'
			error_msg = str(value_err)

			# length error
			error_type = _length_error(error_msg, error_type)

		if error_type:
			return self.response.bad_request(\
				message='[%s] %s' % (error_type, str(error_msg).strip()),\
				time_ms=self.time_ms(start_time),\
				error_dict={'type': error_type, 'message': str(error_msg).strip()})

		return {'status':{'code':0}}
