#!/usr/bin/python
"""
developer skype: alec_host
"""

import os
import sys

import PurchaseGrain

sys.path.append('/usr/local/lib/freknur/engine/conn')
from RedisHelper import RedisHelper
from db_helper import _get_user_db,_is_wallet_suspended_db,_get_customer_bal_db,_existing_purchase_request,_del_processed_purchase_request,_get_handling_fee_db,_get_asset_master_db,_alternate_existing_request
from PurchaseGrainDbHelper import PurchaseGrainDbHelper

class PurchaseGrainModel():
    """
    -=================================================
    -.method: record purchase request (trade).
    -=================================================
    """
    def _record_purchase_request_api(self,content,conn):

        SYSTEM_LOG_MSG = "A REQUEST TO PURCHASE " + content['no_of_unit'] + " " + str(content['description'])+" HAS BEEN BY CLIENT: " + str(content['msisdn'])

        purchase_grain_db_helper = PurchaseGrainDbHelper()

        j_string = None
        #-.routine call.
        processed_cnt = _existing_purchase_request(content['msisdn'],content['uid'],"1",conn)
        if(int(processed_cnt) > 0):
            #-.routine call.
            _del_processed_purchase_request(content['msisdn'],conn)

        #-.routine call.
        user_exist = _get_user_db(content['msisdn'],conn)
        #-.routine call.
        is_wallet_suspended = _is_wallet_suspended_db(content['msisdn'],conn)
        #-.routine call.
        asset_data = _get_asset_master_db(content['uid'],conn)
        #-.routine call.
        unprocessed_cnt = _existing_purchase_request(content['msisdn'],content['uid'],"0",conn)
        #-.routine call.
        fee,lower,upper,markup,offer = _get_handling_fee_db(conn)
        #-.routine call.
        balance,reference = _get_customer_bal_db(content['msisdn'],conn)
        
        if(float(content['no_of_unit']) >= float(lower) and float(content['no_of_unit']) <= float(upper)):
            if(float(content['no_of_unit']) <= float(asset_data[1])):
                if(float(balance) >= float(content['cost'])):
                    if(int(unprocessed_cnt) == 0):
                        if(int(user_exist) == 1):
                            if(int(is_wallet_suspended) == 0):
                                #-.routine call.
                                output = purchase_grain_db_helper._record_purchase_request_db(PurchaseGrain.PurchaseGrain(content['uid'],content['msisdn'],content['description'],content['price'],\
                                                                                              content['no_of_unit'],content['cost'],SYSTEM_LOG_MSG),conn)
                                if(int(output) > 0):
                                    j_string = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"Request has been received & queued for processing."}
                            else:
                                j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"You account has been suspended."}
                        else:
                            j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"User does not exist."}
                    else:
                        j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"You have a similar pending purchase request. Kindly wait for it to be processed."}
                else:
                    j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"Transaction cannot be completed. Insufficient balance."}
            else:
                j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"Transaction cannot be completed."}
        else:
            j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"The minimum and maximum shares that can be bought is: "+str(lower)+", "+str(upper)+" respectively."}


        return j_string


    """
    -=================================================
    -.method: record purchase request (market).
    -=================================================
    """
    def _record_alt_purchase_request_api(self,content,conn):

        SYSTEM_LOG_MSG = "PURCHASE REQUEST OF " + content['no_of_unit'] + " " + str(content['description'])+" ON ALTERNATE MAKET HAS BEEN BY CLIENT: " + str(content['msisdn'])

        purchase_grain_db_helper = PurchaseGrainDbHelper()

        #-.routine call.
        user_exist = _get_user_db(content['msisdn'],conn)
        #-.routine call.
        balance,reference = _get_customer_bal_db(content['msisdn'],conn)
        #-.routine call.
        fee,lower,upper,markup,offer = _get_handling_fee_db(conn)
        #-.routine call.
        unprocessed_cnt = _alternate_existing_request(content['msisdn'],content['uid'],"0",conn)

        if(int(user_exist) == 1):
            if(float(content['no_of_unit']) >= float(lower) and float(content['no_of_unit']) <= float(upper)):
                if(int(unprocessed_cnt) == 0):
                    if(float(balance) >= float(content['cost'])):
                        output = purchase_grain_db_helper._record_alt_purchase_request_db(PurchaseGrain.PurchaseGrain(content['uid'],content['msisdn'],content['description'],content['price'],\
                                                                                          content['no_of_unit'],content['cost'],SYSTEM_LOG_MSG),conn)
                        if(int(output) > 0):
                            j_string = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"Request has been received."}
                    else:
                        j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"Transaction cannot be completed. Insufficient balance."}
                else:
                    j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"You have a similar pending purchase request. Kindly wait for it to be processed."}
            else:
                j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"The minimum and maximum shares that can be bought is."+str(lower)+", "+str(upper)+" respectively."}
        else:
            j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"User does not exist."}

        return j_string


    """
    -=================================================
    -.method: record purchase request (market).
    -=================================================
    """
    def _handle_processing_alt_purchase_request_sys(self,content,wallet_bal,fee_earned,conn):

        SYSTEM_LOG_MSG = "PURCHASE OF "+str(content['qty'])+" "+str(content['name'])+" "+"SHARES IN ALTERNATIVE MARKET @ COST OF "+str((float(content['price']) * float(content['qty'])))+" HAS BEEN MADE."

        redis_helper = RedisHelper()

        rd = redis_helper.create_redis_connection()

        #-.get keys.
        key_1 = redis_helper.redis_access_key()[0]+str(content['msisdn'])
        key_2 = redis_helper.redis_access_key()[1]+str(content['msisdn'])
        key_3 = redis_helper.redis_access_key()[2]+str(content['msisdn'])
        #-.reset cache.
        redis_helper._delete_from_redis_cache(key_1,rd)
        redis_helper._delete_from_redis_cache(key_2,rd)
        redis_helper._delete_from_redis_cache(key_3,rd)

        purchase_grain_db_helper = PurchaseGrainDbHelper()
        
        j_string = purchase_grain_db_helper._handle_processing_alt_purchase_request_db(PurchaseGrain.PurchaseGrain(content['uid'],content['msisdn'],content['name'],\
                                                                                       content['price'],content['qty'],content['cost'],SYSTEM_LOG_MSG),wallet_bal,fee_earned,conn)


        return j_string
