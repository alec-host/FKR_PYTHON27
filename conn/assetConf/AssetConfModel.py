#!/usr/bin/python
  
"""
developer skype: alec_host
"""

import os
import json

import AssetConf

from AssetConfDbHelper import AssetConfDbHelper

class AssetConfModel():

    """
    -=================================================
    -.method: assest configs.
    -=================================================
    """
    def _get_asset_config_params_api(self,conn):

        asset_conf_db_helper = AssetConfDbHelper()
        #-.routine call.
        recordset = asset_conf_db_helper._get_asset_config_params_db(conn)

        if(len(recordset) == 0):
            j_string = json.dumps({"ERROR":"1","RESULT":"FAIL","DATA":recordset,"MESSAGE":"No configs has been setup."})
        else:
            j_string = json.dumps({"ERROR":"0","RESULT":"SUCCESS","DATA":recordset,"MESSAGE":"System configs found."})

        return j_string


    """
    -=================================================
    -.method: create asset config info.
    -=================================================
    """
    def _create_asset_config_api(self,content,conn):

        j_string = None

        if(conn is not None):
            asset_conf_db_helper = AssetConfDbHelper()
            #-.routine call.
            j_string = asset_conf_db_helper._create_asset_config_db(AssetConf.AssetConf(config_id,content['trx_fee'],content['min_limit'],content['max_limit'],content['currency']),conn)
        else:
            j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"Action has failed: no db connection."}

        return j_string


    """
    -=================================================
    -.method: modify asset config info.
    -=================================================
    """
    def _modify_asset_config_api(self,content,conn):

        j_string = None

        if(conn is not None):
            asset_conf_db_helper = AssetConfDbHelper()
            #-.routine call.
            j_string = asset_conf_db_helper._modify_asset_config_db(AssetConf.AssetConf(content['cnf_id'],content['trx_fee'],content['min_limit'],content['max_limit'],content['currency']),conn)
        else:
            j_string = {"ERROR":"1","RESULT":"FAIL","MESSAGE":"Action has failed: no db connection."}

        return j_string
