#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Server 4 API

$ apt-get install python3 python3-mysqldb
"""

import os.path
import time
import configparser
import MySQLdb
import MySQLdb.cursors


class Server4Api(object):
	""" Object API """

	def __init__(self, config_file='serverapi.cfg'):
		""" api init """

		config = self.__read_config(config_file)
		self._cursor = self.__db_init(config)

		self.data_init()


	def __read_config(self, config_file):
		""" read config """

		if not os.path.isfile(config_file):
			return None

		# config
		config = configparser.ConfigParser()
		config.read(config_file)

		return config


	def __db_init(self, config):
		""" db init """

		cursor = {}

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

		# db connect
		database = MySQLdb.connect(\
			host=db_host,\
			user=db_user,\
			passwd=db_passwd,\
			db=db_db,\
			cursorclass=MySQLdb.cursors.DictCursor)

		# db cursor
		return database.cursor()


	def data_init(self):
		""" data init """

		return


	def __db_execute(self, sql='', param=(), cursor=None):
		""" db select """

		if not cursor:
			return 0, None

		if param:
			found = cursor.execute(sql % param)
		else:
			found = cursor.execute(sql)

		if found == 0:
			return found, None

		return found, cursor.fetchall()


	def db_select(self, sql='', param=()):
		""" db select """
		return self.__db_execute(sql, param, self._cursor['dql'])

	def db_sql(self, sql, param=()):
		""" db sql """
		return self.__db_execute(sql, param, self._cursor['dml'])

	def db_update(self, sql, param=()):
		""" db update """
		return self.db_sql(sql, param)

	def db_insert(self, sql, param=()):
		""" db insert """
		return self.db_sql(sql, param)

	def db_delete(self, sql, param=()):
		""" db delete """
		return self.db_sql(sql, param)


	def db_close(self):
		""" db close """

		for cursor_name in self._cursor:
			self._cursor[cursor_name].close()


	def time_ms(self, start_time=0):
		""" time ms """

		timems = int((time.time() - start_time) * 1000)
		if timems == 0:
			timems = 1

		return timems


	def dial_name(self, data, found):
		""" dial name """

		ret = {}
		if found == 0:
			return ret

		for line in data:
			ret[line['name']] = line['id']

		return ret


if __name__ == '__main__':

	import pprint

	API = Server4Api(config_file='etc/serverapi.cfg')
	pprint.pprint(API.db_select('SELECT * FROM cz_data LIMIT 2'))
