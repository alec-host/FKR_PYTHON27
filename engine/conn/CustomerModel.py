#!/usr/bin/python
  
"""
developer skype: alec_host
"""

import os

import Customer


from db_helper import _get_user_db,_get_uid_db,_get_customer_bal_db
from CustomerDbHelper import CustomerDbHelper

class CustomerModel():
    """
    -=================================================
    -.methid: create customer.
    -=================================================      
    """
    def _registration_api(self,content,conn):
        j_string = None
        if(conn is not None):
            #-..
            customer_db_helper = CustomerDbHelper()
            #-.routine call.
            user_exist = _get_user_db(content['msisdn'],conn)
            #-.routine call.
            user_uid = _get_uid_db(conn)

            if(int(user_exist) == 0):
                #-.routine call.
                customer_db_helper._registration_db(Customer.Customer(user_uid,content['msisdn'],content['passwd']),conn)
                
                j_string = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"Wallet activated successful"}
            else:
                j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"Already registered"}

        return j_string

    """
    -=================================================
    -.method: comprehensive customer statement.
    -=================================================      
    """
    def _get_comprehensive_wallet_statement_api(self,msisdn,conn):
        j_string = None
        #-..
        customer_db_helper = CustomerDbHelper()
        #-.routine call.
        user_exist = _get_user_db(msisdn,conn)
        
        if(int(user_exist) == 1):
            #-.routine call.
            j_string = customer_db_helper._get_comprehensive_wallet_statement_db(Customer.Customer(0,msisdn,0),conn)
        else:
            j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"User does not exist."}
        
        return j_string


    """
    -=================================================
    -.method: customer mini statement.
    -=================================================
    """
    def _get_mini_loan_statement_api(self,msisdn,conn):
        j_string = None
        #-..
        customer_db_helper = CustomerDbHelper()
        #-.routine call.
        user_exist = _get_user_db(msisdn,conn)

        if(int(user_exist) == 1):
            #-.routine call.
            j_string = customer_db_helper._get_mini_loan_statement_db(Customer.Customer(0,msisdn,0),conn)
        else:
            j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"User does not exist."}

        return j_string


    """
    -=================================================
    -.method: customer mini statement.
    -=================================================
    """
    def _get_customer_balance_api(self,msisdn,conn):
        j_string = None
        #-..
        customer_db_helper = CustomerDbHelper()
        #-.routine call.
        user_exist = _get_user_db(msisdn,conn)

        if(int(user_exist) == 1):
            #-.routine call.
            j_string = customer_db_helper._get_customer_balance_db(Customer.Customer(0,msisdn,0),conn)
        else:
            j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"User does not exist."}

        return j_string    


    """
    -=================================================
    -.method: customer asset statement.
    -=================================================
    """
    def _get_mini_asset_statement_api(self,msisdn,conn):
        j_string = None
        #-..
        customer_db_helper = CustomerDbHelper()
        #-.routine call.
        user_exist = _get_user_db(msisdn,conn)

        if(int(user_exist) == 1):
            #-.routine call.
            j_string = customer_db_helper._get_mini_asset_statement_db(Customer.Customer(0,msisdn,0),conn)
        else:
            j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"User does not exist."}

        return j_string



    """
    -=================================================
    -.method: shop inventory list.
    -=================================================
    """
    def _shop_inventory_list_api(self,content,conn):

        j_string = None

        customer_db_helper = CustomerDbHelper()
        #-.routine call.
        user_exist = _get_user_db(content['msisdn'],conn)

        if(conn is not None):
            if(int(user_exist) == 1):
                #-.routine call.
                j_string = customer_db_helper._shop_inventory_list_db(Customer.Customer(0,content['msisdn'],0),conn)
            else:
                j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"User does not exist."}

        return j_string
