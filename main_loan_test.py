#!/usr/bin/env python27

import os
import sys
import json
import MySQLdb
import logging
import signal
import Queue
import requests

from urllib import unquote
from conn.LoanModel import LoanModel
from conn.WalletModel import WalletModel
from conn.SellGrainModel import SellGrainModel
from conn.PurchaseGrainModel import PurchaseGrainModel
from conn.DataGridModel import DataGridModel
from conn.CustomerModel import CustomerModel
#-from conn.DataGridModel import DataGridModel
from conn.db_helper import create_connection,close_connection,NoResultException,create_redis_connection,redis_access_key
from conn.model import _read_redis_cache_api

loan_model =  LoanModel()
wallet_model = WalletModel()
purchase_grain_model = PurchaseGrainModel()
sell_grain_model = SellGrainModel()


data_grid_model = DataGridModel()


customer_model = CustomerModel()

db = create_connection()

log = logging.getLogger()


try:
    content = json.loads(json.dumps({"msisdn":"254707132162","amount":"1"}))
    #content = json.loads(json.dumps({"msisdn":"254707132162","amount":"1000","collateral_percentage":"50p","has_collateral":"1"}))
    
    content = json.loads(json.dumps({"msisdn":"254707132162","amount":"1","beneficiary_msisdn":"2547AAA"}))

    #content['msisdn'],content['uid'],content['description'],content['price'],content['no_of_unit'],content['cost']
    content = json.loads(json.dumps({"msisdn":"2547071321602","uid":"20200","description":"AfricaTest","price":"5","no_of_unit":"1","cost":"5"}))

    content = json.loads(json.dumps({"search":"254707132162","lower_max": 10,"lower_min": 0,"code": "STMT"}))


    content = json.loads(json.dumps({"msisdn":"254707132162","lower_max": 0,"lower_min": 0}))

    #result = loan_model._record_unsecured_loan_request_api(content,db)
    #result = loan_model._record_secured_loan_request_api(content,db)
    #result = wallet_model._record_withdraw_transaction_api(content,db)
    #result = wallet_model._peer_2_peer_wallet_transfer_api(content,db)
    #result = purchase_grain_model._record_purchase_request_api(content,db)
    #result = sell_grain_model._record_sell_request_api(content,db)

    #result = data_grid_model._get_customer_list_api(content,db)

    #result = customer_model._get_mini_loan_statement_api("254707132162",db)

    #result = data_grid_model._get_general_account_list_api(content,db)
    
    #-result = loan_model._del_processed_loan_request_sys("254707132162",db)


    #-result = data_grid_model._shop_inventory_list_api(content,db)
    rd = create_redis_connection()
    print(redis_access_key())
    key = redis_access_key()[3]+str("254707132162")
    #-.read cache.
    result = _read_redis_cache_api(key,rd)
    print(result)
except MySQLdb.Error, e:
    log.error(e)
except Exception, e:
    log.error(e)
finally:
    try:
        if(not db):
            exit(0)
        else:
            close_connection(db)
    except MySQLdb.Error, e:
        log.error(e)
