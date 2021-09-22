#!/usr/bin/python
  
"""
developer skype: alec_host
"""

import os
import sys

import Customer

import CustomerRegistrationDbHelper

sys.path.append('/usr/local/lib/freknur/engine/conn')
from db_helper import _get_user_db,_get_customer_bal_db
from Utils import Utils

class CustomerRegistrationModel():

    def _customer_registration_api(self,content,conn):

        j_string = None

        try:
            if(conn is not None):
                #-..
                customer_registration_db_helper = CustomerRegistrationDbHelper()
                #-.routine call.
                user_exist = _get_user_db(msisdn,conn)
                #-.routine call.
                user_uid = _get_uid_db(conn)

                if(int(user_exist) == 0):
                    #-.routine call.
                    customer_registration_db_helper._customer_registration_db(Customer.Customer(user_uid,content['msisdn'],content['passwd']),conn)

                    j_string = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"Wallet activated successful"}
                else:
                    j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"Already registered"}
        except Exception, e:
            logger.error(e)
            raise

        return j_string


