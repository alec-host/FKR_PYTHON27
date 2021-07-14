#!/usr/bin/python2

import os
import re
import sys
import json
import MySQLdb
import logging
import signal
import Queue

from conn.model import _read_loan_request_queue_sys,_queue_loan_sys,_acitivity_log_sys
from conn.db_helper import create_connection,close_connection,NoResultException
from conn.configs.freknur_settings import loan_params

log = logging.getLogger()

def handleLoanRequest():
	try:
		while True:
                        db = create_connection()
			"""
			-.get loan request list.
			"""
			items = json.loads(_read_loan_request_queue_sys(db))
			"""
			-.loop through each in the list
			"""
                        if(len(items) > 0):
			        for item in items:
                                        amount = int(item['amount'])
                                        min_allowed_loan  = int(loan_params['min_loan'])
                                        max_allowed_loan  = int(loan_params['max_loan'])
				        """
				        -.check for loan allowed.
				        """
				        if(amount >= min_allowed_loan and amount <= max_allowed_loan):
                                                if(int(item['has_collateral']) == 0 or int(item['has_collateral']) == 1):
                                                        """
                                                        -.queue loan & mark as processed.
                                                        """
                                                        result = _queue_loan_sys(item['reference_no'],item['msisdn'],str(item['amount']),item['approved_by'],item['has_collateral'],db)
                                                        """
                                                        -.activity description.
                                                        """
                                                        activity = "A LOAN REQUEST OF "+str(amount)+" HAS BEEN MADE."
                                                        """
                                                        -.check result.
                                                        """
                                                        if(result['ERROR'] == "0" and result['RESULT'] == "SUCCESS"):
                                                                """
                                                                -.log user activity.
                                                                """                                                    
                                                                _acitivity_log_sys(item['msisdn'],activity,db)
                                        else:
					        """
					        -.json output.
					        """				
                                                resp = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"Loan limits: MINIMUM : "+str(min_allowed_loan)+" MAXIMUM : "+str(max_allowed_loan)}

                                                print(resp)
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
				close connection.
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
		handleLoanRequest()
        except KeyboardInterrupt:
                exit(0)
