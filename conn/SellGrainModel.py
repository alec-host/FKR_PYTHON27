#!/usr/bin/python
"""
developer skype: alec_host
"""

import os

import SellGrain


from db_helper import _get_user_db,_get_customer_bal_db,_existing_sell_request,_get_handling_fee_db,_get_asset_master_db,_get_asset_owner_db
from SellGrainDbHelper import SellGrainDbHelper

class SellGrainModel():
    """
    -=================================================
    -.method: record purchase request.
    -=================================================
    """
    def _record_sell_request_api(self,content,conn):

        SYSTEM_LOG_MSG = "INTENTION TO SELL "+str(content['no_of_unit'])+" "+str(content['description'])+" SHARE[S] @ COST OF "+str(content['cost'])+" THROUGH THE ALTERNATIVE MARKET."

        sell_grain_db_helper = SellGrainDbHelper()

        j_string = None
        #-.routine call.
        has_pending_request = _existing_sell_request(content['msisdn'],content['uid'],conn)
        #-.routine call.
        user_exist = _get_user_db(content['msisdn'],conn)
        #-.routine call.
        asset_data = _get_asset_master_db(content['uid'],conn)
        #-.routine call.
        seller_asset = _get_asset_owner_db(content['msisdn'],content['uid'],conn)
        #-.routine call.
        fee,lower,upper,markup,offer = _get_handling_fee_db(conn)
        #-.routine call.
        balance,reference = _get_customer_bal_db(content['msisdn'],conn)
        #-.calc price markup.
        price_markup = (float(content['price']) + (float(content['price']) * float(markup)))

        if(float(seller_asset[0]) >= float(content['no_of_unit'])):
            current_price = asset_data[0]
            total_cost = (float(price_markup) * float(content['no_of_unit']))
            if(int(has_pending_request) == 0):
                if(int(user_exist) == 1):
                    #-.routine call.
                    output = sell_grain_db_helper._record_sell_request_db(SellGrain.SellGrain(content['uid'],content['msisdn'],content['description'],price_markup,content['no_of_unit'],total_cost,SYSTEM_LOG_MSG),conn)
                    if(int(output) > 0):
                        j_string = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"Your sell request of "+str(content['description'])+" has been received successfully."}
                else:
                    j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"User does not exist."}
            else:
                j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"Operation cannot be completed, you have a similar pending sell request of "+str(content['description'])+"."}
        else:
            j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"Invalid, transaction has failed. "+str(float(seller_asset[0]))+"  "+str(float(content['no_of_unit']))}

        
        return j_string
