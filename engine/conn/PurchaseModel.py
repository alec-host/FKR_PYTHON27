import os

import Wallet


from db_helper import _get_user_db,_get_customer_bal_db
from PurchaseGrainDbHelper import PurchaseGrainDbHelper
from Utils import Utils

class PurchaseModel():
    """
    -=================================================
    -.method: withdraw cash.
    -=================================================
    """
    def _record_purchase_request_api(self,content,conn):

        SYSTEM_LOG_MSG = str(content['amount'])+" HAS BEEN WITHDRWN FROM ACCOUNT: " + str(content['msisdn'])

        purchase_grain_db_helper = PurchaseGrainDbHelper()
        utils = Utils()

        j_string = None
        #-.routine call.
        processed_cnt = _existing_purchase_request(content['msisdn'],uid,"1",conn)
        if(int(processed_cnt) > 0):
            #-.routine call.
            _del_processed_purchase_request(content['msisdn'],conn)

        #-.routine call.
        user_exist = _get_user_db(content['msisdn'],conn)
        #-.routine call.
        asset_data = _get_asset_master_db(uid,conn)
        #-.routine call.
        unprocessed_cnt = _existing_purchase_request(content['msisdn'],uid,"0",conn)
        #-.routine call.
        fee,lower,upper,markup,offer = _get_handling_fee_db(conn)
        #-.routine call.
        balance,reference = _get_customer_bal_db(msisdn,conn)
        
        if(float(qty) >= float(lower) and float(qty) <= float(upper)):
            if(float(qty) <= float(asset_data[1])):
                if(float(bal) >= float(total_cost)):
                    if(int(unprocessed_cnt) == 0):
                        if(int(user_exist) == 1):
                            #-.routine call.
                            j_string = purchase_grain_db_helper._record_withdraw_transaction_db(Wallet.Wallet(0,content['msisdn'],content['amount'],0,SYSTEM_LOG_MSG),conn)
                        else:
                            j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"User does not exist."}
                    else:
                        j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"You have a similar pending purchase request. Kindly wait for it to be processed."}
                else:
                    j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"Transaction cannot be completed. Insufficient balance."}
            else:
                j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"Transaction cannot be completed."}
        else:
             j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"The minimum and maximum shares that can be bought is."+str(lower)+", "+str(upper)+" respectively."}


        return j_string
