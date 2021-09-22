#!/usr/bin/python
"""
developer skype: alec_host
"""

import os
import sys
import json
import logging
import MySQLdb
import MySQLdb.cursors

from datetime import datetime

sys.path.append('/usr/local/lib/freknur/engine/conn')
from db_helper import _get_last_insert_id_db,_acitivity_log_db
from configs.freknur_settings import logger,mysql_params
from db_conn import DB,NoResultException

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
        old_price = this.old_price
        price = this.price
        qty = this.qty
        total_cost = this.total_cost
        activity = this.activity

        try:
            qry = """
                  INSERT
                  INTO
                 `db_freknur_investment`.`tbl_sale_request`
                  (`msisdn`,`uid`,`description`,`unit_price_no_markup`,`unit_price`,`no_of_grain_sold`,`cost`,`date_created`)
                  VALUES
                  ('%s','%s','%s','%s','%s','%s','%s','%s')
                  """ % (msisdn,uid,asset_name,old_price,price,qty,total_cost,date)

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


    """
    -=================================================
    -.sell request list.
    -=================================================
    """
    def _get_sale_request_list_db(self,msisdn,is_owner,conn,limit=1000):

        recordset = None

        try:
            if(int(is_owner) == 1):
                sql = """
                      SELECT
                      SUM(`no_of_grain_sold`) AS QTY,`description`,`uid`,`unit_price_no_markup`,`unit_price`,sum((`no_of_grain_sold`*`unit_price`)) AS total_cost
                      FROM
                     `db_freknur_investment`.`tbl_sale_request`
                      WHERE
                     `msisdn` = %s
                      GROUP BY `uid`,`unit_price_no_markup`,`description`,`unit_price`,`uid`
                      -- GROUP BY `uid`,`description`,`uid`
                      LIMIT %s;
                      """
            else:
                sql = """
                      SELECT
                      SUM(`no_of_grain_sold`) AS QTY,`description`,`uid`,`unit_price`,sum((`no_of_grain_sold`*`unit_price`)) AS total_cost
                      FROM
                     `db_freknur_investment`.`tbl_sale_request`
                      WHERE
                     `msisdn` != %s
                      GROUP BY `uid`,`description`,`unit_price`,`uid`
                      -- GROUP BY `uid`,`description`,`uid`
                      LIMIT %s;
                      """
            params = (msisdn,limit,)
            
            recordset = db.retrieve_all_data_params(conn,sql,params)
        except Exception,e:
            logger.error(e)
            raise

        return recordset


    """
    -=================================================
    -.delete own sell request
    -=================================================
    """
    def _delete_own_sale_requet_db(self,content,conn):

        j_string = None
        asset_id = content['uid']
        msisdn   = content['msisdn']
        #-.particulars.
        activity = "A SELL REQUEST HAS BEEN WITHDRAWN BY OWNER."
        try:
            sql = """
                  DELETE
                  FROM
                 `db_freknur_investment`.`tbl_sale_request_queue`
                  WHERE
                 `uid` = '%s' AND `msisdn` = '%s'
                  """ % (asset_id,msisdn)

            params = ()

            db.execute_query(conn, sql, params)
            
            conn.commit()

            qry = """
                  DELETE
                  FROM
                 `db_freknur_investment`.`tbl_sale_request`
                  WHERE
                 `uid` = '%s' AND `msisdn` = '%s'
                  """ % (asset_id,msisdn)

            params = ()

            db.execute_query(conn, qry, params)
            
            j_string = {"ERROR":"0","RESULT":"SUCCESS","MESSAGE":"The request has been deleted."}
            
            conn.commit()
            
            #-.log activity.
            _acitivity_log_db(msisdn,activity,conn)
        except Exception,e:
            logger.error(e)
            raise

        return j_string
