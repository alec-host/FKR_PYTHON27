#!/usr/bin/python
  
"""
developer skype: alec_host
"""

import os
import sys
import time
import signal
import json
import eventlet
import logging
import MySQLdb
import MySQLdb.cursors

import redis

from datetime import datetime

from RedisHelper import RedisHelper
from db_helper import _acitivity_log_db
from configs.freknur_settings import logger,mysql_params
from db_conn import DB,NoResultException

eventlet.monkey_patch()

db = DB()

class WalletDbHelper():
    """
    -.===============================================
    -.method:peer to peer wallet transfer.
    -.===============================================
    """
    def _peer_2_peer_wallet_transfer_db(self,this,conn):
                
        j_string = None

        msisdn = this.msisdn
        amount = this.amount
        beneficiary_msisdn = this.beneficiary_msisdn
        activity = this.activity

        try:
            sql = """CALL `db_freknur_loan`.`sProcWalletToWalletTransfer`(%s,%s,%s,%s)"""
            params = (amount,bal,msisdn,beneficiary_msisdn,)
            output = db.retrieve_all_data_params(conn,sql,params)
            
            #conn.commit()
            for data in output:
                j_string = json.loads(data.get('_JSON'))

            if(int(j_string['ERROR']) == 0):

                redis_helper = RedisHelper()

                rd = redis_helper.create_redis_connection()
                #-.get keys.
                key_1 = redis_helper.redis_access_key()[0]+str(msisdn)
                key_2 = redis_helper.redis_access_key()[4]+str(msisdn)
                #-.reset cache.
                redis_helper._delete_from_redis_cache(key_1,rd)
                redis_helper._delete_from_redis_cache(key_2,rd)
                #-.routine call.
                _acitivity_log_db(msisdn,activity,conn)
        except Exception, e:
            logger.error(e)
            raise
        
        return j_string


    """
    -=================================================
    -.method:deposit cash.
    -=================================================
    """
    def _wallet_deposit_db(self,this,conn):
        j_string = None
        try:
            j_string = {"ERROR":"0","RESULT":"SUCESS","MESSAGE":"Under construction"}
        except Exception, e:
            logger.error(e)
            raise

        return j_string


    """
    -=================================================
    -.method:record withdraw transaction.
    -=================================================
    """
    def _record_withdraw_transaction_db(self,this,conn):

        j_string = None

        msisdn = this.msisdn
        amount = this.amount
        activity = this.activity

        try:
            sql = """CALL """+mysql_params['db']+""".`sProcWithdrawECash`(%s,%s)"""
            params = (amount,msisdn,)
            output = db.retrieve_all_data_params(conn,sql,params)

            #conn.commit()
            for data in output:
                j_string = json.loads(data.get('_JSON'))

            if(int(j_string['ERROR']) == 0):

                redis_helper = RedisHelper()

                rd = redis_helper.create_redis_connection()
                #-.get keys.
                key_1 = redis_helper.redis_access_key()[0]+str(msisdn)
                key_2 = redis_helper.redis_access_key()[4]+str(msisdn)
                #-.reset cache.
                redis_helper._delete_from_redis_cache(key_1,rd)
                redis_helper._delete_from_redis_cache(key_2,rd)
                #-.routine call.
                _acitivity_log_db(msisdn,activity,conn)                
        except Exception, e:
            logger.error(e)
            raise
        
        return j_string
