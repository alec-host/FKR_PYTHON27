#!/usr/bin/python2
  
import os
import re
import sys
import json
import MySQLdb
import logging
import signal
import Queue

from conn.loan.LoanModel import LoanModel

from conn.model import _loan_payment_sys,_read_payment_list_sys,_acitivity_log_sys,_delete_from_redis_cache_api
from conn.configs.freknur_settings import loan_params,accounting_params
from conn.db_helper import create_connection,close_connection,NoResultException,create_redis_connection,redis_access_key

log = logging.getLogger()

def repayLoan():
        try:
                while True:
                        db = create_connection()
                        rd = create_redis_connection()
                        #-.routine call.
                        items = json.loads(_read_payment_list_sys(db))
                        #-.list not empty.
                        if(len(items) > 0):
                                for item in items:
                                        #-.routine call.
                                        result =_loan_payment_sys(item['msisdn'],item['amount'],item['transaction_no'],db)
                                        #-.trx particulars.
                                        activity = "A PAYMENT OF "+str(item['amount']) + " HAS BEEN MADE. " + str(result['MESSAGE'])
                                        #-.check result.
                                        if(result['ERROR'] == "0" and result['RESULT'] == "SUCCESS"):
                                                #-.log activity.
                                                _acitivity_log_sys(item['msisdn'],activity,db)
                                                #-.get keys.
                                                key_1 = redis_access_key()[0]+str(item['msisdn'])
                                                key_2 = redis_access_key()[1]+str(item['msisdn'])
                                                key_3 = redis_access_key()[3]+str(item['msisdn'])
                                                key_4 = redis_access_key()[4]+str(item['msisdn'])
                                                #-.reset cache.
                                                _delete_from_redis_cache_api(key_1,rd)
                                                _delete_from_redis_cache_api(key_2,rd)
                                                _delete_from_redis_cache_api(key_3,rd)
                                                _delete_from_redis_cache_api(key_4,rd)
                                                #-.search string.
                                                substring = "Movement complete."
                                                #-.perform clean up.
                                                if(substring in str(result['MESSAGE'])):
                                                        loan_model = LoanModel()
                                                        #-.routine call.
                                                        loan_model._del_processed_loan_request_sys(str(item['msisdn']),db)
        except MySQLdb.Error, e:
                log.error(e)
        except Exception, ex:
                log.error(ex)
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
                repayLoan()
        except KeyboardInterrupt:
                exit(0);
