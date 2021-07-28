"""
developer skype: alec_host
"""

import os
import sys
import time
import signal
import json
import eventlet
import logging
import MySQLdb
import MySQLdb.cursors

import redis

from datetime import datetime

from RedisHelper import RedisHelper

from db_helper import _get_last_insert_id_db,_acitivity_log_db
from configs.freknur_settings import logger,mysql_params
from db_conn import DB,NoResultException

eventlet.monkey_patch()

db = DB()

class SellGrainDbHelper():

    """
    -=================================================
    -.new asset purchase request.
    -=================================================
    """
    def _record_sell_request_db(self,this,conn):

        j_string = None
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        uid = this.uid
        msisdn = this.msisdn
        asset_name = this.asset_name
        price = this.price
        qty = this.qty
        total_cost = this.total_cost
        activity = this.activity

        try:
            qry = """
                  INSERT
                  INTO
                 `db_freknur_investment`.`tbl_sale_request`
                  (`msisdn`,`uid`,`description`,`unit_price`,`no_of_grain_sold`,`cost`,`date_created`)
                  VALUES
                  ('%s','%s','%s','%s','%s','%s','%s')
                  """ % (msisdn,uid,asset_name,price,qty,total_cost,date)

            params = ()

            db.execute_query(conn, qry, params)
            conn.commit()

            j_string = _get_last_insert_id_db(conn)

            if(int(j_string) > 0):
                _acitivity_log_db(msisdn,activity,conn)
        except Exception, e:
            logger.error(e)
            raise

        return j_string
