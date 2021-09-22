#!/usr/bin/python
  
"""
developer skype: alec_host
"""

import os
import sys
import logging
import MySQLdb
import MySQLdb.cursors

from datetime import datetime

sys.path.append('/usr/local/lib/freknur/engine/conn')
from db_helper import _get_last_record_db
from configs.freknur_settings import logger
from db_conn import DB,NoResultException

db = DB()

class AssetConfDbHelper():

    """
    -=================================================
    -.method: assest configs.
    -=================================================
    """
    def _get_asset_config_params_db(self,conn):

        recordet = None
        try:
            sql = """
                      SELECT
                     `trx_fee` AS fee,`min_limit`,`max_limit`,`currency`
                      FROM 
                     `db_freknur_investment`.`tbl_config` 
                      """
            params = ()
            
            recordset = db.retrieve_all_data_params(conn,sql,params)
            
        except Exception,e:
            logger.error(e)
            raise

        return recordset


    """
    -=================================================
    -.method: create asset config info.
    -=================================================
    """
    def _create_asset_config_db(self,params,conn):

        j_string = None
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        fee = params.transaction_fee
        min_limit = params.minimum_limit
        max_limit = params.maximum_limit
        currency  = params.currency

        try:
            sql = """
                  INSERT
                  INTO
                 `db_freknur_investment`.`tbl_config`
                  (`trx_fee`,`min_limit`,`max_limit`,`currency`,`time_stamp`)
                  VALUES
                  ('%s','%s','%s','%s','%s')
                  """ % (fee,min_limit,max_limit,currency,date)

            params = ()
            
            db.execute_query(conn, sql, params)
            
            conn.commit()
            
            last_record = _get_last_record_db("config",conn)
            
            j_string = last_record

        except Exception,e:
            logger.error(e)
            raise

        return j_string


    """
    -=================================================
    -.method: modify asset config info.
    -=================================================
    """
    def _modify_asset_config_db(self,params,conn):

        j_string = None
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        uid = params.uid
        fee = params.transaction_fee
        min_limit = params.minimum_limit
        max_limit = params.maximum_limit
        currency  = params.currency

        try:
            sql = """
                  UPDATE
                 `db_freknur_investment`.`tbl_config`
                  SET
                 `trx_fee` = '%s', `min_limit` = '%s', `max_limit` = '%s',`currency` = '%s',`time_stamp` = '%s'
                  WHERE
                 `cnf_id` = '%s'
                  """ % (fee,min_limit,max_limit,currency,date,uid)

            params = ()
            
            db.execute_query(conn, sql, params)
            
            conn.commit()
            
            j_string = {"Result":"OK"}

        except Exception,e:
            logger.error(e)
            raise

        return j_string
