#!/usr/bin/python

"""
developer skype: alec_host
"""

import os
import sys

import Wallet

sys.path.append('/usr/local/lib/freknur/engine/conn')
from db_helper import _get_user_db,_is_wallet_suspended_db,_get_customer_bal_db
from WalletDbHelper import WalletDbHelper
from Utils import Utils

class WalletModel():
    """
    -=================================================
    -.method: withdraw cash.
    -=================================================
    """
    def _record_withdraw_transaction_api(self,content,conn):

        SYSTEM_LOG_MSG = str(content['amount'])+" HAS BEEN WITHDRWN FROM ACCOUNT: " + str(content['msisdn'])

        wallet_db_helper = WalletDbHelper()
        utils = Utils()

        j_string = None
        #-.routine call.
        balance,ref = _get_customer_bal_db(content['msisdn'],conn)
        #-.routine call.
        user_exist = _get_user_db(content['msisdn'],conn)
        #-.is wallet a/c suspended.
        is_wallet_suspended = _is_wallet_suspended_db(content['msisdn'],conn)

        if(int(user_exist) == 1):
            if(int(is_wallet_suspended) == 0):
                if(float(balance) >= float(content['amount'])):
                    if(float(content['amount']) > 0 and utils.is_number(content['amount']) == True):
                        #-.routine call.
                        j_string = wallet_db_helper._record_withdraw_transaction_db(Wallet.Wallet(0,content['msisdn'],content['amount'],0,SYSTEM_LOG_MSG),conn)
                    else:
                        j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"Invalid input."}
                else:
                    j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"Insufficient Balance:."}
            else:
                j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"Your account has been suspended."}
        else:
            j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"You are not a registered user."}

        return j_string


    """
    -=================================================
    -.method: inter-wallet cash transfer.
    -=================================================
    """
    def  _peer_2_peer_wallet_transfer_api(self,content,conn):

        SYSTEM_LOG_MSG = str(content['amount'])+" HAS BEEN MOVED FROM: "+str(content['msisdn'])+" TO BENEFICIARY:"+str(content['beneficiary_msisdn'])

        wallet_db_helper = WalletDbHelper()
        utils = Utils()

        j_string = None
        #-.routine call.
        user_exist_1 = _get_user_db(content['msisdn'],conn)
        user_exist_2 = _get_user_db(content['beneficiary_msisdn'],conn)
        #-.routine call.
        balance,ref = _get_customer_bal_db(content['msisdn'],conn)
        #-.is wallet a/c suspended.
        is_wallet_suspended = _is_wallet_suspended_db(content['msisdn'],conn)

        if(int(user_exist_1) == 1):
            if(int(is_wallet_suspended) == 0):
                if(int(user_exist_2) == 1):
                    if(utils.is_number(content['amount']) == True):
                        if(float(content['amount']) > 0):
                            if(float(balance) >= float(content['amount'])):
                                #-.routine call.
                                j_string = wallet_db_helper._peer_2_peer_wallet_transfer_db(Wallet.Wallet(0,content['msisdn'],content['amount'],content['beneficiary_msisdn'],SYSTEM_LOG_MSG),conn)
                            else:
                                j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"Insufficient Balance:."}
                        else:
                            j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"Amount has to be greater than ZERO."}
                    else:
                        j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"Invalid input."}
                else:
                    j_string = {"ERROR":"1","RESULT":"FAILED","MESSAGE":"BENEFICIARY account do not exist."}
            else:
                j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"Your account has been suspended."}
        else:
            j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"You are not a registered user."}

        return j_string




    """
    -=================================================
    -.method:deactivate wallete a/c.
    -=================================================
    """
    def _suspend_wallet_account_api(self,content,conn):

        if(content is not None):
            SYSTEM_LOG_MSG = "Wallet a/c for client: "+str(content['msisdn'])+ " has been suspended."
            if(conn is not None):
                #-.routine call.
                user_exist = _get_user_db(content['msisdn'],conn)
                if(int(user_exist) == 1):
                    wallet_db_helper = WalletDbHelper()
                    if(str(content['head']) == "freeze"):
                        #-.routine call.
                        wallet_db_helper._suspend_wallet_account_db(Wallet.Wallet(0,content['msisdn'],0,0,SYSTEM_LOG_MSG),conn)
                    else:
                        #-.routine call.
                        wallet_db_helper._unsuspend_wallet_account_db(Wallet.Wallet(0,content['msisdn'],0,0,SYSTEM_LOG_MSG),conn)

                    j_string = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"Wallet a/c has been suspended."}
                else:
                    j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"You are not a registered user."}

        return j_string
