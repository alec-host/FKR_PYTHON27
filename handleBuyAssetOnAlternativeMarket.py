#!/usr/bin/python2
  
import os
import re
import sys
import json
import MySQLdb
import logging
import signal
import Queue

from conn.model import _read_sell_request_on_market_queue_sys,_get_asset_master_sys,_get_customer_bal_sys,_purchase_asset_on_market_sys,\
                       _get_handling_fee_sys,_acitivity_log_sys,_delete_alternative_market_request_sys,_delete_from_redis_cache_api
from conn.db_helper import create_connection,close_connection,NoResultException,create_redis_connection,redis_access_key
from conn.configs.freknur_settings import loan_params

from conn.purchaseGrain.PurchaseGrainModel import PurchaseGrainModel

log = logging.getLogger()

def handleSellAssetRequest():
    try:
        purchase_grain_model = PurchaseGrainModel()
        while True:
            db = create_connection()
            rd = create_redis_connection()
            """
             -.get list.
            """
            items = json.loads(_read_sell_request_on_market_queue_sys(db))
            """
            -.loop through each in the list
            """
            if(len(items) > 0):
                """
                -.routine call.
                """
                fee,lower,upper,markup,offer = _get_handling_fee_sys(db)

                for item in items:
                    uid    = item['asset_id']
                    msisdn = item['msisdn']
                    name   = item['asset_name']
                    price  = item['unit_price']
                    qty    = item['qty']
                    cost   = item['cost']

                    content = {"uid":uid,"msisdn":msisdn,"name":name,"price":price,"qty":qty,"cost":cost}
                    """
                    -.routine call.
                    """
                    asset_data = _get_asset_master_sys(uid,db)
                    """
                    -.calc fee.
                    """
                    handling_fee = (float(price) * float(qty)) * markup
                    """
                    -.routine call.
                    """
                    bal,ref = _get_customer_bal_sys(msisdn,db)
                    """
                    -.calc wallet bal.
                    """
                    wallet_bal = float(bal) - float(cost)
                    """
                    -.do we have sufficient bal?
                    """
                    if(float(wallet_bal) >= 0):
                        """
                        -.check uid.
                        """
                        if(uid is not None):
                            """
                            -.activity description.
                            """
                            activity = "PURCHASE OF "+str(qty)+" "+str(name)+" "+"SHARES IN ALTERNATIVE MARKET @ COST OF "+str((price*qty))+" HAS BEEN MADE."
                            """
                            -.handle purchase process.
                            """
                            #result = _purchase_asset_on_market_sys(msisdn,float(qty),name,uid,float(price),float(wallet_bal),float(cost),float(handling_fee),db)
                            
                            result = purchase_grain_model._handle_processing_alt_purchase_request_sys(content,float(wallet_bal),float(handling_fee),db)

                            if(result is not None):
                                """
                                -.check result.
                                """
                                if(result['ERROR'] == "0" and result['RESULT'] == "SUCCESS"):
                                    """
                                    -.record user activity.
                                    """                            
                                    #_acitivity_log_sys(msisdn,activity,db)
                                    """
                                    -.get keys.
                                    """
                                    key_1 = redis_access_key()[0]+str(result['DATA'])
                                    key_2 = redis_access_key()[1]+str(result['DATA'])
                                    """
                                    -.reset cache.
                                    """
                                    _delete_from_redis_cache_api(key_1,rd)
                                    _delete_from_redis_cache_api(key_2,rd)
                                else:
                                    """
                                    -.record user activity.
                                    """
                                    _acitivity_log_sys(msisdn,result['MESSAGE'].upper(),db)
                    else:
                        """
                        -.activity description.
                        """                        
                        activity = "CUSTOMER "+str(msisdn)+" HAS INSUFFICIENT BALANCE TO COMPLETE PURCHASE OF SHARE[S] IN ALTERNATIVE MARKET."
                        """
                        -.record user activity.
                        """
                        _acitivity_log_sys(msisdn,activity,db)
                        """
                        -.delete purchase log.
                        """
                        _delete_alternative_market_request_sys(msisdn,db)

                                    
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
                close_connection(db)
        except MySQLdb.Error, e:
            log.error(e)

"""
-.main method.
"""
if __name__ == '__main__':
    try:
        handleSellAssetRequest()
    except KeyboardInterrupt:
        exit(0)
