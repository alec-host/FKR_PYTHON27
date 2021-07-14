#!/usr/bin/python2

import os
import re
import sys
import json
import MySQLdb
import logging
import signal
import Queue

from conn.model import _loan_due_list_sys,_loan_due_alert_handler_sys,_flag_as_defaulter_sys
from conn.configs.freknur_settings import loan_params
from conn.db_helper import create_connection,close_connection,NoResultException

log = logging.getLogger()

def processLoanDueAlert():
	try:
                hour_val = 0
		while True:
                        db = create_connection()
                        """
                        -.get loan request list.
                        """
                        items = json.loads(_loan_due_list_sys(db))                    
			"""
			-.loop through each in the list
			"""
			if(len(items) > 0):
				for item in items:
                                        """
                                        -.get appropriate hour interval.
                                        """
                                        if(int(item['notification_count']) == 0):
                                                hour_val = int(loan_params['notify_1'])
                                        elif(int(item['notification_count']) == 1): 
                                                hour_val = int(loan_params['notify_2'])
                                        elif(int(item['notification_count']) == 2):
                                                hour_val = int(loan_params['notify_3'])
                                        elif(int(item['notification_count']) == 3):
                                                hour_val = int(loan_params['notify_3'])
					"""
					-.loan due notification logic.
					"""
                                        if(int(item['notification_count']) >= 0 and int(item['notification_count']) <= 3):
					        resp = _loan_due_alert_handler_sys(
                                                        str(item['id']),
                                                        str(item['diff']),
                                                        str(item['notification_count']),
                                                        int(hour_val),
                                                        str(item['msisdn']),
                                                        item['repayment_amount'],
                                                        item['expected_repayment_date'].replace("'",""),
                                                        db)
                                        else:
                                                resp = _flag_as_defaulter_sys(
                                                        str(item['id']),
                                                        str(item['msisdn']),
                                                        item['repayment_amount'],
                                                        item['expected_repayment_date'].replace("'",""),
                                                        int(loan_params['duration']),
                                                        db)
	except MySQLdb.Error, e:
		log.error(e)
	except Exception, e:
		log.error(e)
	finally:
		try:
			if(not db):
				exit(0)
			else:	
                                if(db is not None):
                                        close_connection(db)
		except MySQLdb.Error, e:
			log.error(e)
			
"""
-.main method.
"""	
if __name__ == '__main__':
	try:
		processLoanDueAlert()
	except KeyboardInterrupt:
		exit(0)
