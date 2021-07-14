#!/usr/bin/python2

import os
import re
import sys
import json
import MySQLdb
import logging
import signal
import Queue

from conn.model import _defaulter_list_sys,_calc_loan_penalty_sys
from conn.configs.freknur_settings import loan_params
from conn.db_helper import create_connection,close_connection,NoResultException

log = logging.getLogger()

def processLoanOverduePenalty():
	try:
		
		while True:
                        db = create_connection()
			"""
			-.get loan request list.
			"""
			items = json.loads(_defaulter_list_sys(db))
			"""
			-.loop through each in the list
			"""
			if(len(items) > 0):
				for item in items:
					"""
					-.10 roll count.
					"""
					if(int(item['roll_count']) >= 0 and int(item['roll_count']) < int(loan_params['roll_cnt'])):
						"""
						-.calc penalty logic.
						"""					
						_calc_loan_penalty_sys(item['principle'],loan_params['duration'],loan_params['interest'],item['msisdn'],db)
	except MySQLdb.Error, e:
		log.error(e)
	except Exception, e:
		log.error(e)
	finally:
		try:
			if(not db):
				exit(0)
			else:
				"""
				close MySQL connection.
				"""
                                if(db is not None):
                                        close_connection(db)
		except MySQLdb.Error, e:
			log.error(e)
			
"""
-.main method.
"""	
if __name__ == '__main__':
	try:
		processLoanOverduePenalty()
	except KeyboardInterrupt:
		exit();
