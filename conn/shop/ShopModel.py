#!/usr/bin/python 
"""
developer skype: alec_host
"""
import os
import sys
import ast
import json
import uuid

import Shop
import Image

from urllib import unquote

sys.path.append('/usr/local/lib/freknur/engine/conn')
from db_helper import _get_user_db,_get_customer_bal_db
from RedisHelper import RedisHelper
from ShopDbHelper import ShopDbHelper
from configs.freknur_settings import redis_pubsub_params
from Utils import Utils

class ShopModel():
    """
    -=================================================
    -.method: create inventory item.
    -=================================================
    """
    def _create_inventory_item_api(self,content,conn):

        j_string = None
        item_uid = str(uuid.uuid4().fields[-1])[:5]
        if(content):
            shop_db_helper = ShopDbHelper()
            #-.routine call.
            j_string = shop_db_helper._create_inventory_item_db(Shop.Shop(item_uid,content['name'],content['qty'],content['price'],0),conn)
        else:
            j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"The operation has failed"}

        return j_string

    """
    -=================================================
    -.method: modify inventory item.
    -=================================================
    """
    def _modify_inventory_item_api(self,content,conn):

        j_string = None
        if(content):
            shop_db_helper = ShopDbHelper()
            #-.routine call.
            j_string = shop_db_helper._modify_inventory_item_db(Shop.Shop(content['product_uid'],0,content['qty'],0,content['total']),conn)
        else:
            j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"The operation has failed"}

        return j_string

    """
    -=================================================
    -.method: update inventory item image path.
    -=================================================
    """
    def _post_inventory_item_image_path_api(self,content,conn):

        j_string = None
        if(content):
            shop_db_helper = ShopDbHelper()
            #-.routine call.
            j_string = shop_db_helper._post_inventory_item_image_path_db(Image.Image(content['uid'],unquote(content['path'])),conn)
        else:
            j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"The operation has failed"}

        return j_string    
            
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
