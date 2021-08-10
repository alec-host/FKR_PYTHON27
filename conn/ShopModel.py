#!/usr/bin/python 
"""
developer skype: alec_host
"""
import os
import ast
import json

from db_helper import _get_user_db,_get_customer_bal_db

from conn.RedisHelper import RedisHelper
from conn.configs.freknur_settings import redis_pubsub_params

from Utils import Utils

class ShopModel():
    """
    -=================================================
    -.method: withdraw cash.
    -=================================================
    """
    def _record_shop_sale_api(self,content,conn):
        
        utils = Utils()

        j_string = None
        #-.routine call.
        balance,ref = _get_customer_bal_db(content['msisdn'],conn)
        #-.routine call.
        user_exist = _get_user_db(content['msisdn'],conn)

        if(int(user_exist) == 1):
            if(float(balance) >= float(content['grand_total'])):
                if(int(float(balance)) > 0 and utils.is_number(content['grand_total']) == True):
                    redis_helper = RedisHelper()
                    rd = redis_helper.create_redis_connection()

                    payload = json.dumps(content)
                    #-.routine call.
                    redis_helper._publish_redis(redis_pubsub_params['SHOP_PUBSUB'],ast.literal_eval(payload),rd)

                    j_string = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"Your order has been received."}
                else:
                    j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"Invalid input."}
            else:
                j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"Insufficient Balance."}
        else:
            j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"You are not a registered user."}

        return j_string
