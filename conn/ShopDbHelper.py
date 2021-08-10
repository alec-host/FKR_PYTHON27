#!/usr/bin/python
  
"""
developer skype: alec_host
"""

import os
import sys
import time
import signal
import json
import decimal
import eventlet
import logging
import MySQLdb
import MySQLdb.cursors

from datetime import datetime


from Utils import Utils

from db_helper import _get_user_db,_get_uid_db
from configs.freknur_settings import logger,mysql_params
from db_conn import DB,NoResultException

eventlet.monkey_patch()

db = DB()


class ShopDbHelper():
    """
    -=================================================
    -.create new customer.
    -=================================================
    """
    def _record_shop_sale_db(self,content,conn):

        date   = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        uid    = content.uid
        msisdn = content.msisdn
        qty    = content.qty
        price  = content.price

        total  = (float(qty) * float(price))

        try:
            qry = """
                  INSERT
                  INTO
                 `db_freknur_inventory`.`tbl_sales`
                  (`product_id`,`qty`,`total`,`msisdn`,`date_created`)
                  VALUES
                  ('%s','%s','%s','%s','%s')
                  """ % (uid,qty,total,msisdn,date)

            params = ()

            db.execute_query(conn, qry, params)
        except Exception, e:
            logger.error(e)
            raise
