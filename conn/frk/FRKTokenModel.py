#!/usr/bin/python

"""
developer skype: alec_host
"""

import os
import sys
import json

import FRKToken

from FRKTokenDbHelper import FRKTokenDbHelper

sys.path.append('/usr/local/lib/freknur/engine/conn')
from db_helper import _get_user_db,_is_wallet_suspended_db,_get_customer_bal_db

class FRKTokenModel():

    """
    -=================================================
    -.method: fkr token transaction.
    -=================================================
    """
    def _record_frk_transaction_api(self,content,conn):

        j_string = None
        #-.routine call.
        user_exist = _get_user_db(content['msisdn'],conn)
        #-.routine call.
        balance,reference = _get_customer_bal_db(content['msisdn'],conn)
        #-.routine call.
        is_wallet_suspended = _is_wallet_suspended_db(content['msisdn'],conn)

        frk_token_db_helper = FRKTokenDbHelper()

        if(int(user_exist) == 1):
            if(int(is_wallet_suspended) == 0):
                #-.routine call.
                j_string = frk_token_db_helper._record_frk_transaction_db(FRKToken.FRKToken(content['msisdn'],content['amount'],"FKR_"+str(content['trx_unique_id']),content['account_type'].upper().strip()),conn)
            else:
                j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"You account has been suspended."}
        else:
            j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"User does not exist."}

        return j_string
