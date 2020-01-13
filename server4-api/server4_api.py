#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Server 4 API

$ apt-get install python3 python3-mysqldb
"""

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

		# config
		config = configparser.ConfigParser()
		config.read(config_file)

		return config


	def __db_init(self, config):
		""" db init """

		# db config
		db_user = config.get('db', 'user')
		db_passwd = config.get('db', 'passwd')
		db_db = config.get('db', 'db')
		db_host = config.get('db', 'host')

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


	def db_select(self, sql='', param=()):
		""" db select """

		if param:
			found = self._cursor.execute(sql % param)
		else:
			found = self._cursor.execute(sql)

		if found == 0:
			return found, None

		return found, self._cursor.fetchall()


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

	AI = Server4Api(config_file='etc/serverapi.cfg')
	pprint.pprint(API.db_select('SELECT * FROM cz_data LIMIT 2'))
