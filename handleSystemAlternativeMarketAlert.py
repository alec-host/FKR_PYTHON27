#!/usr/bin/python2
  
import os
import re
import sys
import json
import requests 
import MySQLdb
import logging
import signal
import Queue

from conn.model import _read_sell_request_on_market_queue_sys,_alert_to_seller_on_market_sys,_get_asset_master_sys,_get_customer_bal_sys,_purchase_asset_on_market_sys,_get_handling_fee_sys,_acitivity_log_sys
from conn.db_helper import create_connection,close_connection,NoResultException
from conn.configs.freknur_settings import loan_params

log = logging.getLogger()

def handleAlertToSeller():
    try:
        while True:
            db = create_connection() 
            """
             -.get loan request list.
            """
            items = json.loads(_read_sell_request_on_market_queue_sys(db))
            #---print(items)
            """
            -.loop through each in the list
            """
            if(len(items) > 0):
                """
                -.routine call.
                """
                fee,lower,upper,markup,offer = _get_handling_fee_sys(db)
                
                for item in items:
                    _id      = item['_id']
                    uid      = item['asset_id']
                    msisdn   = item['msisdn']
                    name     = item['asset_name']
                    duration = 1  
                    price    = item['unit_price']
                    qty      = item['qty']
                    cost     = item['cost']
                    """
                    -.routine call.
                    """
                    asset_data = _get_asset_master_sys(uid,db)
                    """
                    -.calc fee.
                    """
                    handling_fee = (float(asset_data[0]) * float(qty)) * markup
                    """
                    -.calc offer price.
                    """
                    offer_price = price - (price*offer)
                    """
                    -.check uid is not None.
                    """
                    if(uid is not None):
                        """
                        -.activity description.
                        """
                        activity = "AN ALERT TO CLIENT: "+str(msisdn)+". WITH AN OFFFER TO BUY "+str(qty)+" "+str(name.upper())+" ASSET(S)."      
                        """
                        -.trigger an alert to seller.
                        """    
                        result = _alert_to_seller_on_market_sys(msisdn,name,duration,offer_price,"",db)
                        """
                        -.check if not empty.
                        """
                        if(result is not None):
                            """
                            -.check result.
                            """
                            if(result['ERROR'] == "0" and result['RESULT'] == "SUCCESS"):
                                """
                                -.record user activity.
                                """                            
                                _acitivity_log_sys(msisdn,activity,db)
                                """
                                -.place a bid offer to seller.
                                """
                                api_url = "http://localhost:5000/getWalletBalanceApi/"
                                data    = {'asset_id': uid, 'asset_name': name, 'owner_msisdn': msisdn, 'bidder_msisdn': '254000000000', 'qty': qty, 'bid_price': offer_price}
                                headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                                r = requests.post(api_url, data=json.dumps(data), headers=headers)

                                print(r.json())
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
                    #print(db)
        except MySQLdb.Error, e:
            log.error(e)

"""
-.main method.
"""
if __name__ == '__main__':
    try:
        handleAlertToSeller()
    except KeyboardInterrupt:
        exit(0)
