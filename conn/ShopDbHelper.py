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

from db_helper import _get_user_db,_get_uid_db,_get_last_record_db
from configs.freknur_settings import logger,mysql_params
from db_conn import DB,NoResultException

eventlet.monkey_patch()

db = DB()


class ShopDbHelper():

    """
    -=================================================
    -.create a inventory record.
    -=================================================
    """
    def _create_inventory_item_db(self,content,conn):
        j_string = None
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        uid   = content.uid
        name  = content.name
        qty   = content.qty
        price = content.price        
        try:
            sql = """
                      INSERT 
                      INTO
                     `db_freknur_inventory`.`tbl_inventory`
                      (`item_uid`,`item_name`,`qty_in`,`unit_price`,`date_created`)
                      VALUES
                      ('%s','%s','%s','%s','%s')
                      ON
                      DUPLICATE KEY
                      UPDATE `date_modified` = '%s'
                      """ % (uid,name,qty,price,date,date)

            params = ()

            db.execute_query(conn, sql, params)
            
            conn.commit()
            
            last_record = _get_last_record_db("inventory",conn)
            
            j_string = last_record
        except Exception,e:
            logger.error(e)
            raise
        
        return j_string

    """
    -=================================================
    -.modify inventory item.
    -=================================================
    """
    def _modify_inventory_item_db(self,content,conn):
        j_string = None
        uid   = content.uid
        qty   = content.qty
        total = content.total
        try:
            sql = """
                  UPDATE
                 `db_freknur_inventory`.`tbl_sales`
                  SET
                 `qty` = %s,
                 `total` = %s
                  WHERE
                 `product_uid` = '%s' AND `is_archived` = '0'
                  """ % (qty,total,product_uid)

            params = ()

            db.execute_query(conn, sql, params)
            
            j_string = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"Item has been modified."}
            
            conn.commit()
        except Exception,e:
                logger.error(e)
                raise

        return j_string


    """
    -=================================================
    -.save image path.
    -=================================================
    """
    def _post_inventory_item_image_path_db(self,content,conn):
        j_string = None
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        uid = content.uid
        path = content.path 
        try:
            sql = """
                  UPDATE
                 `db_freknur_inventory`.`tbl_inventory`
                  SET
                 `item_image` = '%s',
                 `date_modified` = '%s'
                  WHERE
                 `item_uid` = '%s'
                  """ % (path,date,uid)

            params = ()

            db.execute_query(conn, sql, params)

            j_string = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"Image path has been updated."}

            conn.commit()

        except Exception,e:
            logger.error(e)
            raise

        return j_string

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
