#!/usr/bin/python2

import os
import re
import sys
import json
import MySQLdb
import logging
import signal
import Queue

from conn.model import _read_loan_payout_queue_sys,_dispatch_loan_sys,_record_loan_transaction_sys,\
                       _record_loan_fee_sys,_acitivity_log_sys,_log_dispatched_loan_sys,_get_collateral_log_sys,\
                       _calc_loan_amount_with_interest_rebate_sys,_delete_from_redis_cache_api

from conn.configs.freknur_settings import loan_params,accounting_params

from conn.db_helper import create_connection,close_connection,NoResultException,create_redis_connection,redis_access_key

log = logging.getLogger()

def moveLoanAmountToWallet():	
        try:
		
		while True:
                        db = create_connection()
                        rd = create_redis_connection()
			"""
			-.get loan request list.
			"""
			items = json.loads(_read_loan_payout_queue_sys(db))
                        #print(items)
                        if(len(items) > 0):
			        """
		    	        -.loop through each in the list
			        """
			        for item in items:		
				        """
				        -.calc loan handling fees.
				        """
				        handle_fee = int(item['amount']) * float(loan_params['loan_fee'])
				        """
				        -.calc amount loaned.
				        """
				        loan_amount = int(item['amount']) - float(handle_fee)
				        """
				        -.does the loan comes with security?
				        """
                                        if(int(item['has_collateral']) == 0):
                                                """
                                                -.calc interest amount.
                                                """
				                interest_amount = (float(loan_params['interest']) * int(item['amount']))
                                        else:
                                                """
                                                -.routine call.
                                                """
                                                collateral_log     = _get_collateral_log_sys(item['msisdn'],db)

                                                collateral_amount  = float(collateral_log[1])
                                                collateral_percent = float(collateral_log[2])
                                                rebase_rate        = float(loan_params['rebase'])
                                                loan_interest_rate = float(loan_params['interest'])
                                                """
                                                -.calc interest amount.
                                                """
                                                interest_amount = _calc_loan_amount_with_interest_rebate_sys(collateral_amount,loan_amount,rebase_rate,loan_interest_rate,collateral_percent)
				        """
				        -.calc repayment amount = (principle+interest).
				        """
				        repayment_amount = (int(item['amount']) + interest_amount)
				        """
				        -.log trx affecting utility a/c.
				        """
				        _record_loan_transaction_sys(str(item['amount']),item['msisdn'],item['reference_no'],str(accounting_params['accounts'].split(',')[1]),str(accounting_params['debit']),db)
				        """
				        -.log loan fee.
				        """
				        _record_loan_fee_sys(item['msisdn'],item['reference_no'],str(handle_fee),str(accounting_params['accounts'].split(',')[3]),db)	
				        """
				        -.update wallet bal & log the transaction.
				        """
				        result =_dispatch_loan_sys(item['reference_no'],item['msisdn'],str(item['amount']),str(loan_amount),str(repayment_amount),str(interest_amount),loan_params['duration'],loan_params['notify_1'],db)
                                        """
                                        -.particulars.
                                        """
                                        if(int(item['has_collateral']) == 0):
                                                activity = "UNSECURED LOAN: AMOUNT OF "+str(loan_amount)+" HAS BEEN MOVED TO CLIENT WALLET A/C. REPAYMENT AMOUNT: "+str(repayment_amount)
                                        else:
                                                activity = "SECURED LOAN: AMOUNT OF "+str(loan_amount)+" HAS BEEN MOVED TO CLIENT WALLET A/C. REPAYMENT AMOUNT: "+str(repayment_amount)
                                        """
                                        -.check result.
                                        """
                                        if(result['ERROR'] == "0" and result['RESULT'] == "SUCCESS"):
                                                """
                                                -.report the loan in temp lookup table.
                                                """
                                                _log_dispatched_loan_sys(item['msisdn'],repayment_amount,interest_amount,db)
                                                """
                                                -.get key.
                                                """
                                                key_1 = redis_access_key()[0]+str(item['msisdn'])
                                                key_2 = redis_access_key()[1]+str(item['msisdn'])
                                                """
                                                -.reset cache.
                                                """
                                                _delete_from_redis_cache_api(key_1,rd)
                                                _delete_from_redis_cache_api(key_2,rd)
                                                """
                                                -.log use activity.
                                                """
                                                _acitivity_log_sys(item['msisdn'],activity,db)	
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
                                        print(db)
		except MySQLdb.Error, e:
			log.error(e)
			
"""
-.main method.
"""	
if __name__ == '__main__':
	try:
		moveLoanAmountToWallet()
	except KeyboardInterrupt:
		exit(0);
